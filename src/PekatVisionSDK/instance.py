"""Python module for communication with PEKAT VISION 3.10.2 and higher."""

import base64
import json
import os
import platform
import secrets
import socket
import string
import subprocess
import sys
from functools import cached_property
from multiprocessing import shared_memory
from pathlib import Path
from typing import Any, List, Literal, Optional, Tuple, Union, get_args

import netifaces
import numpy as np
import requests
from numpy.typing import NDArray
from packaging import version

from .errors import (
    DistNotExistsError,
    DistNotFoundError,
    InvalidDataTypeError,
    InvalidResponseTypeError,
    NoConnectionError,
    PekatNotStartedError,
    PortIsAllocatedError,
    ProjectNotFoundError,
)
from .result import Result

StrOrPathLike = Union[str, os.PathLike]
ResponseType = Literal["context", "image", "annotated_image", "heatmap"]
UrlEndpoint = Literal[
    "analyze_image",
    "analyze_raw_image",
    "analyze_image_shared_memory",
]

ALLOWED_RESPONSE_TYPES = get_args(ResponseType)


def _get_local_addresses() -> List[str]:
    return [
        addr["addr"]
        for interface in netifaces.interfaces()
        for addr in netifaces.ifaddresses(interface).get(
            netifaces.InterfaceType.AF_INET,
            [],
        )
    ]


class Instance:
    """A class for starting or connecting to a PEKAT VISION project."""

    def __init__(
        self,
        project_path: Optional[StrOrPathLike] = None,
        dist_path: Optional[StrOrPathLike] = None,
        port: Optional[int] = None,
        host: str = "127.0.0.1",
        *,
        already_running: bool = False,
        disable_code: bool = False,
        tutorial_only: bool = False,
        context_in_body: bool = False,
        wait_for_init_model: bool = False,
        ping: bool = True,
        gpu: int = 0,
    ) -> None:
        """Create an Instance object for communication with PEKAT VISION.

        Arguments:
            project_path: Path to an existing project.
                Ignored if `already_running` is `True`.
            dist_path: Path to PEKAT VISION installation folder.
                Ignored if `already_running` is `True`.
            port: Port of the project.
            host: IP address of the project.
                Set to `"0.0.0.0"` to listen on all interfaces.
            already_running: Whether the project is already running.
                If the project is not already running, project will be started.
            disable_code: Disable code module.
                Ignored if `already_running` is `True`.
            tutorial_only: Only allow Anomaly module and force tutorial.
                Ignored if `already_running` is `True`.
            context_in_body: Whether to send the `context` `dict`  in the response body.
                Set to `True` if the resulting context is larger than 4KB.
            wait_for_init_model: Whether to wait for all models to be initialized before returning the [Instance][PekatVisionSDK.Instance] object.
                Ignored if `already_running` is `True`.
            ping: Whether to send a ping request to `HOST:PORT/ping` upon creating
                the instance.
            gpu: Which GPU to start project on.
                Ignored if `already_running` is `True`.

        Raises:
            DistNotExistsError: If `dist_path` does not exist.
            DistNotFoundError: If no PEKAT VISION was found in the default installation directory.
            PortIsAllocatedError: If the specified port is already used by another process.
            ValueError: If not `already_running` and project path is `None`.
            RuntimeError: If the created process has no `stdout`.
            ProjectNotFoundError: If the project was not found in the specified location.
            PekatNotStartedError: If PEKAT VISION couldn't start a project.
        """
        self.project_path = Path(project_path).expanduser() if project_path else None
        self.dist_path = Path(dist_path) if dist_path else None

        self.host = host
        self.already_running = already_running
        self.disable_code = disable_code
        self.tutorial_only = tutorial_only
        self.context_in_body = context_in_body
        self.wait_for_init_model = wait_for_init_model
        self.gpu = gpu

        self._shm = shared_memory.SharedMemory(create=True, size=1)
        self._shm_arr = np.ndarray((1,), dtype=np.uint8, buffer=self._shm.buf)

        self.session = requests.Session()  # Session for all requests

        self.process: Optional[subprocess.Popen] = None
        self.stop_key: Optional[str] = None

        self._rng = np.random.default_rng()

        self.__stopping = False

        self._is_local = self.host in [
            *_get_local_addresses(),
            "127.0.0.1",
            "localhost",
        ]
        if port is None:
            self.port = self._find_free_ports()
            self.port_is_defined = False
        else:
            self.port = port
            self.port_is_defined = True

        if not already_running:
            self._start_instance()

        if ping:
            self.ping()

    def __del__(self) -> None:
        if not self.already_running:
            self.stop()
        self._shm.close()

    @cached_property
    def server_version(self) -> version.Version:
        """Get the version of the PEKAT VISION server.

        Returns `Version("0.0.0")` if PEKAT VISION server's version is < 3.18.0.
        """
        url = f"http://{self.host}:{self.port}/version"
        response = self.session.get(url, timeout=20)
        try:
            return version.parse(response.text)
        except version.InvalidVersion:
            return version.Version("0.0.0")

    @cached_property
    def _can_use_shm(self) -> bool:
        """Check if shared memory analysis is supported."""
        return self._is_local and self.server_version >= version.parse("3.18.0")

    def _get_dist_path(self) -> Path:
        if self.dist_path:
            if self.dist_path.exists():
                return self.dist_path
            raise DistNotExistsError(self.dist_path)

        if platform.system() == "Windows":
            pekat_install_parent_dir = Path(os.environ["PROGRAMFILES"])
            pekat_install_base_name = "PEKAT VISION "
        elif platform.system() == "Linux":
            pekat_install_parent_dir = Path("/opt/PEKAT")
            pekat_install_base_name = "pekat-vision-"
        else:
            raise DistNotFoundError

        installed_pekats = sorted(
            pekat_install_parent_dir.glob(f"{pekat_install_base_name}*"),
            key=lambda x: version.parse(x.name.split(pekat_install_base_name)[1]),
            reverse=True,
        )

        if installed_pekats:
            return installed_pekats[0]

        raise DistNotFoundError

    @staticmethod
    def _find_free_ports() -> int:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("localhost", 0))
        _, port = s.getsockname()
        s.close()
        return port

    @staticmethod
    def _random_string(string_length: int) -> str:
        letters = string.ascii_lowercase
        return "".join(secrets.choice(letters) for _ in range(string_length))

    def _check_project(self) -> bool:
        if self.project_path is None:
            return False
        return (self.project_path / "pekat_package.json").exists()

    def _start_instance(self) -> None:
        if self.project_path is None:
            raise ValueError(self.project_path)
        if not self._check_project():
            raise ProjectNotFoundError(self.project_path)

        dist_path = self._get_dist_path()
        server_path = dist_path / "pekat_vision" / "pekat_vision"
        self.stop_key = self._random_string(10)

        params = [
            server_path,
            "-data",
            self.project_path,
            "-port",
            str(self.port),
            "-host",
            self.host,
            "-stop_key",
            self.stop_key,
        ]

        if self.gpu:
            params += ["-gpu", str(self.gpu)]

        # add other arguments
        if self.disable_code:
            params += ["-disable_code", self.disable_code]
        if self.tutorial_only:
            params += ["-tutorial_only", self.tutorial_only]

        self.process = subprocess.Popen(
            params,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        stop_init_model = not self.wait_for_init_model
        server_running = False

        if self.process.stdout is None:
            msg = "Process stdout is None"
            raise RuntimeError(msg)

        # wait for start
        while True:
            next_line = self.process.stdout.readline().decode()  # type: ignore[union-attr]
            if next_line == "" and self.process.poll() is not None:
                break
            sys.stdout.flush()

            if "__SERVER_RUNNING__" in next_line:
                server_running = True
            if "STOP_INIT_MODEL" in next_line:
                stop_init_model = True
            if server_running and stop_init_model:
                return None

            if "OSError: [Errno 48] Address already in use" in next_line:
                if self.port_is_defined:
                    raise PortIsAllocatedError(self.port)
                self.port = self._find_free_ports()
                return self._start_instance()

        raise PekatNotStartedError

    def _construct_url(
        self,
        path: UrlEndpoint,
        response_type: ResponseType,
        **kwargs: Any,  # noqa: ANN401
    ) -> str:
        url = f"http://{self.host}:{self.port}/{path}?response_type={response_type}"

        other_args = "&".join(f"{key}={value}" for key, value in kwargs.items())

        if other_args:
            url = f"{url}&{other_args}"

        if self.context_in_body:
            url = f"{url}&context_in_body"

        return url

    def _response_to_result(
        self,
        response: requests.Response,
        response_type: ResponseType,
    ) -> Result:
        if response_type == "context":
            return Result(None, response.json())

        if self.context_in_body:
            image_len_str = response.headers.get("ImageLen")
            if not image_len_str:
                return Result(None, response.json())
            image_len = int(image_len_str)
            img_bytes = response.content[:image_len]
            context_json = response.content[image_len:].decode()
        else:
            img_bytes = response.content
            context_base64 = response.headers.get("ContextBase64utf")
            if context_base64 is None:
                return Result(None, response.json())
            context_json = base64.b64decode(context_base64)

        return Result(img_bytes, json.loads(context_json))

    def _analyze_numpy(
        self,
        image: NDArray[np.uint8],
        response_type: ResponseType,
        data: Optional[str] = None,
        timeout: float = 20,
    ) -> Result:
        """Send numpy array to the running project and get the results."""
        height, width = image.shape[:2]
        url = self._construct_url(
            "analyze_raw_image",
            response_type,
            data=data,
            height=height,
            width=width,
        )

        response = self.session.post(
            url,
            data=image.tobytes(),
            headers={"Content-Type": "application/octet-stream"},
            timeout=timeout,
        )

        return self._response_to_result(response, response_type)

    def _analyze_numpy_shm(
        self,
        image: NDArray[np.uint8],
        response_type: ResponseType,
        data: Optional[str] = None,
        timeout: float = 20,
    ) -> Result:
        """Send the numpy array through a shared memory to the running project and get the results.

        This method will run if the project is running locally.
        """
        height, width = image.shape[:2]

        if self._shm_arr.shape != image.shape:
            self._shm.close()
            self._shm = shared_memory.SharedMemory(create=True, size=image.nbytes)
            self._shm_arr = np.ndarray(
                image.shape,
                dtype=image.dtype,
                buffer=self._shm.buf,
            )
        self._shm_arr[:] = image[:]

        url = self._construct_url(
            "analyze_image_shared_memory",
            response_type,
            data=data,
            height=height,
            width=width,
            name=self._shm.name,
        )

        response = self.session.post(
            url,
            timeout=timeout,
        )

        return self._response_to_result(response, response_type)

    def _analyze_bytes(
        self,
        image: bytes,
        response_type: ResponseType,
        data: Optional[str] = None,
        timeout: float = 20,
    ) -> Result:
        """Send bytes to the running project and get the results."""
        url = self._construct_url(
            "analyze_image",
            response_type,
            data=data,
        )

        response = self.session.post(
            url,
            data=image,
            headers={"Content-Type": "application/octet-stream"},
            timeout=timeout,
        )

        return self._response_to_result(response, response_type)

    def _analyze_file(
        self,
        image: Path,
        response_type: ResponseType,
        data: Optional[str] = None,
        timeout: float = 20,
    ) -> Result:
        """Send bytes from a file to the running project and get the results."""
        return self._analyze_bytes(image.read_bytes(), response_type, data, timeout)

    def analyze(
        self,
        image: Union[NDArray[np.uint8], bytes, StrOrPathLike],
        response_type: ResponseType = "context",
        data: Optional[str] = None,
        timeout: float = 20,
    ) -> Result:
        """Send an image to the running project and get the results.

        `response_type` will affect the `image` of the returned [`Result`][PekatVisionSDK.Result]:

        - `"context"`: context only, `Result.image_bytes` will be `None`.
        - `"image"`: `Result.image_bytes` will contain the processed image.
        - `"annotated_image"`: `Result.image_bytes` will contain the processed image with drawn detected rectangles.
        - `"heatmap"`: `Result.image_bytes` will contain the layered heatmaps of the processed image.

        In order to decode the image in `Result.image_bytes`, use [`get_decoded_image`][PekatVisionSDK.Result.get_decoded_image].

        Arguments:
            image: Path to the image, encoded image bytes or numpy image.
            response_type: Type of response data.
            data: Data to be added to the query.
                Project will be able to access this under the `"data"` key in `context`.
            timeout: Timeout in seconds for the analyze request.

        Raises:
            InvalidResponseTypeError: If `response_type` is not any of the allowed response types.
            InvalidDataTypeError: If `image` is not any of the allowed data types.
            requests.exceptions.Timeout: Upon timeout.

        Returns:
            A tuple of image and `context`.
                If `response_type` is `"context"`, then the returned image is `None`.
        """
        if response_type not in ALLOWED_RESPONSE_TYPES:
            raise InvalidResponseTypeError(response_type)

        if isinstance(image, (str, os.PathLike)):
            return self._analyze_file(Path(image), response_type, data, timeout)
        if isinstance(image, bytes):
            return self._analyze_bytes(image, response_type, data, timeout)
        if isinstance(image, np.ndarray):
            if self._can_use_shm:
                return self._analyze_numpy_shm(image, response_type, data, timeout)
            return self._analyze_numpy(image, response_type, data, timeout)

        raise InvalidDataTypeError(type(image))

    def send_random(
        self,
        shape: Tuple[int, ...] = (512, 512, 3),
        response_type: ResponseType = "context",
        data: Optional[str] = None,
        timeout: float = 20,
    ) -> Result:
        """Send random data for analysis.

        Arguments:
            shape: Shape of the image to be sent.
            response_type: Type of response data.
            data: Data to be added to the query.
                Project will be able to access this under the `"data"` key in `context`.
            timeout: Timeout in seconds for the analyze request.

        Raises:
            Exception: Same as [`Instance.analyze`][PekatVisionSDK.Instance.analyze]

        Returns:
            A tuple of image and `context`.
                If `response_type` is `"context"`, then the returned image is `None`.
        """
        return self.analyze(
            self._rng.integers(0, 256, shape, dtype=np.uint8),
            response_type,
            data,
            timeout,
        )

    def stop(self, timeout: float = 5) -> None:
        """Stop the project if it's running and not stopping already.

        It can only stop the project if [`already_running`][PekatVisionSDK.Instance]
        was set to `False`.

        Arguments:
            timeout: Timeout in seconds to kill process.

        Raises:
            NoConnectionError: Upon timeout.
        """
        # only own subprocess (PEKAT) can be stopped
        if not self.process or self.__stopping or self.stop_key is None:
            return

        self.__stopping = True

        try:
            self.session.get(
                url=f"http://{self.host}:{self.port}/stop?key={self.stop_key}",
                timeout=timeout,
            )
        except requests.exceptions.Timeout as e:
            raise NoConnectionError from e

    def ping(self, timeout: float = 5) -> requests.Response:
        """Ping the project to check if it's running.

        Arguments:
            timeout: Timeout in seconds to ping.

        Raises:
            NoConnectionError: Upon timeout.

        Returns:
            Ping response.
        """
        try:
            return self.session.get(
                url=f"http://{self.host}:{self.port}/ping",
                timeout=timeout,
            )
        except requests.exceptions.Timeout as e:
            raise NoConnectionError from e
