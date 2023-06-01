# PEKAT VISION api
#
# A Python module for communication with PEKAT VISION 3.10.2 and higher
#
# Author: developers@pekatvision.com
# Date:   18 May 2023
# Web:    https://github.com/pekat-vision

import atexit
import base64
import json
import os
import platform
import random
import socket
import string
import subprocess
import sys
from pathlib import Path
from typing import Literal, Optional, Tuple, Union

import numpy as np
import requests
from numpy.typing import NDArray

StrOrPathLike = Union[str, os.PathLike]


class DistNotFound(Exception):
    def __str__(self):
        return "PEKAT VISION dist not found"


class DistNotExists(Exception):
    def __str__(self):
        return "PEKAT VISION dist not exists"


class PortIsAllocated(Exception):
    def __str__(self):
        return "Port is allocated"


class InvalidData(Exception):
    def __str__(self):
        return "Invalid input data. Allowed types are the file path (string) or image in numpy array"


class InvalidResponseType(Exception):
    def __str__(self):
        return "Invalid response type (context, image, annotated_image)"


class CannotBeTerminated(Exception):
    def __str__(self):
        return "Already running instance cannot be terminated"


class ProjectNotFound(Exception):
    def __init__(self, path: StrOrPathLike):
        self.path = path

    def __str__(self):
        return "Project not found. Check path {}.".format(self.path)


class PekatNotStarted(Exception):
    def __str__(self):
        return "Pekat not started from unknown reason"


class OpenCVImportError(Exception):
    def __str__(self):
        return "You need opencv-python installed for this type of response_type"


class NoConnection(Exception):
    def __str__(self):
        return "Could not establish connection with running instance."


class Instance:
    def __init__(
            self,
            project_path: Optional[StrOrPathLike] = None,
            dist_path: Optional[StrOrPathLike] = None,
            port: Optional[int] = None,
            host: str = '127.0.0.1',
            already_running: bool = False,
            password: Optional[str] = None,
            api_key: Optional[str] = None,
            disable_code: bool = False,
            tutorial_only: bool = False,
            context_in_body: bool = False,
            wait_for_init_model: bool = False,
            ping: bool = True,
            gpu: int = 0,
    ):
        """
        Create instance of interface for communication

        :param project_path: Path to project. It is ignored is already_running=True
        :type project_path: StrOrPathLike | None
        :param dist_path: path to PEKAT VISION binaries. It is ignored is already_running=True
        :type dist_path: StrOrPathLike | None
        :param port:
        :type port: int | None
        :param host:
        :type host: str
        :param already_running: Instance will not be created. It joins to existing one. Raises NoConnection if ping fails.
        :type already_running: bool
        :param password: access to client gui
        :type password: str
        :param api_key: api key - more in PEKAT VISION doc
        :type api_key: str
        :param disable_code: disable module code
        :type disable_code: bool
        :param tutorial_only: allow only Anomoly of Surface tutorial
        :type tutorial_only: bool
        :param context_in_body: receive context in body instead of header
        :type context_in_body: bool
        :param wait_for_init_model: wait for all models to load before returning the Instance object
        :type wait_for_init_model: bool
        :param ping: ping the address to check whether the Instance is running
        :type ping: bool
        :param gpu: which GPU to start project on. It is ignored is already_running=True
        :type gpu: int
        """
        self.project_path = Path(project_path) if project_path else None
        self.dist_path = Path(dist_path) if dist_path else None

        self.host = host
        self.already_running = already_running
        self.password = password
        self.api_key = api_key
        self.disable_code = disable_code
        self.tutorial_only = tutorial_only
        self.context_in_body = context_in_body
        self.wait_for_init_model = wait_for_init_model
        self.gpu = gpu

        if port is None:
            self.port = self.__find_free_ports()
            self.port_is_defined = False
        else:
            self.port = port
            self.port_is_defined = True

        if not already_running:
            self.__start_instance()
            atexit.register(self.stop)

        if ping:
            self.ping()

        self.__stopping = False

    def analyze(self, image: Union[NDArray[np.uint8], StrOrPathLike], response_type: Literal['annotated_image', 'context', 'heatmap'] = 'context', data: Optional[str] = None, timeout: float = 20) -> Union[Tuple[NDArray[np.uint8], dict], dict]:
        """
        Send image to PEKAT VISION. PEKAT VISION return result of recognition.
        :param image: numpy image or path to image file
        :type image: NDArray[np.uint8] | StrOrPathLike
        :param response_type: more in PEKAT VISION doc
        :type response_type: str
        :param data: adds data to the query - more in PEKAT VISION doc
        :type data: str | None
        :param timeout: seconds to request timeout
        :type timeout: float
        :return: results of recognition based on response_type
        :rtype: (NDArray[np.uint8], dict) | dict
        """
        image_path = None
        numpy_image = None

        if isinstance(image, StrOrPathLike):
            image_path = Path(image)
        elif isinstance(image, np.ndarray):
            numpy_image = image
        else:
            raise InvalidData()

        if response_type not in ['annotated_image', 'context', 'heatmap']:
            raise InvalidResponseType

        query = 'response_type={}'.format(response_type)
        url = 'http://{}:{}'.format(self.host, self.port)

        if self.api_key:
            query += '&api_key={}'.format(self.api_key)

        if data:
            query += '&data={}'.format(data)

        if self.context_in_body:
            query += '&context_in_body'

        if image_path is not None:
            image_data = image_path.read_bytes()
            response = requests.post(
                url='{}/analyze_image?{}'.format(url, query),
                data=image_data,
                timeout=timeout,
                headers={'Content-Type': 'application/octet-stream'}
            )
        elif numpy_image is not None:
            height, width, _ = numpy_image.shape
            response = requests.post(
                url='{}/analyze_raw_image?width={}&height={}&{}'.format(url, width, height, query),
                data=numpy_image.tobytes(),
                headers={'Content-Type': 'application/octet-stream'},
                timeout=timeout
            )
        else:
            return {}

        if response_type in ['heatmap', 'annotated_image']:
            if self.context_in_body:
                image_len_str = response.headers.get('ImageLen')
                if not image_len_str:
                    return response.json()
                image_len = int(image_len_str)
                np_arr = np.frombuffer(response.content[:image_len], np.uint8)
                context_json = response.content[image_len:].decode('utf-8')
            else:
                np_arr = np.frombuffer(response.content, np.uint8)
                context_base64 = response.headers.get('ContextBase64utf')
                if context_base64 is None:
                    return response.json()
                context_json = base64.b64decode(context_base64)
            try:
                import cv2
                return cv2.imdecode(np_arr, 1), json.loads(context_json)
            except ImportError:
                raise OpenCVImportError()
        else:
            return response.json()

    def __get_dist_path(self) -> Path:
        if self.dist_path:
            if self.dist_path.exists():
                return self.dist_path
            else:
                raise DistNotExists()
        elif platform.system() == "Windows":
            program_files_path = Path(os.environ['systemdrive']) / "Program Files"
            for p in reversed(sorted(program_files_path.glob("PEKAT VISION *"))):
                return program_files_path / p  # Path to the newest version of PEKAT VISION in Program Files

        raise DistNotFound()

    @staticmethod
    def __find_free_ports():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('localhost', 0))
        _, port = s.getsockname()
        s.close()
        return port

    def __random_string(self, string_length: int) -> str:
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for _ in range(string_length))

    def __check_project(self) -> bool:
        assert self.project_path is not None
        return (self.project_path / "pekat_package.json").exists()

    def __start_instance(self):
        assert self.project_path is not None
        if not self.__check_project():
            raise ProjectNotFound(self.project_path)

        dist_path = self.__get_dist_path()
        server_path = dist_path / "pekat_vision" / "pekat_vision"
        self.stop_key = self.__random_string(10)

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
        if self.api_key:
            params += ["-api_key", self.api_key]
        if self.password:
            params += ["-password", self.password]
        if self.disable_code:
            params += ["-disable_code", self.disable_code]
        if self.tutorial_only:
            params += ["-tutorial_only", self.tutorial_only]

        self.process = subprocess.Popen(
            params,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        stop_init_model = not self.wait_for_init_model
        server_running = False

        # wait for start
        while True:
            next_line = self.process.stdout.readline().decode()  # type: ignore
            if next_line == '' and self.process.poll() is not None:
                break
            sys.stdout.flush()

            if next_line.find("__SERVER_RUNNING__") != -1:
                server_running = True
            if next_line.find("STOP_INIT_MODEL") != -1:
                stop_init_model = True
            if server_running and stop_init_model:
                return

            if next_line.find("OSError: [Errno 48] Address already in use") != -1:

                if self.port_is_defined:
                    raise PortIsAllocated()
                else:
                    self.port = self.__find_free_ports()
                    return self.__start_instance()
        raise PekatNotStarted()

    def stop(self, timeout: float = 5):
        """
        Stop running instance
        :param timeout: Timeout to kill process
        :type timeout: float
        """
        # only own subprocess (PEKAT) can be stopped
        if not self.process or self.__stopping:
            return

        self.__stopping = True

        requests.get(
            url='http://{}:{}/stop?key={}'.format(self.host, self.port, self.stop_key),
            timeout=timeout
        )

    def ping(self, timeout: float = 5):
        """
        Ping Pekat server.
        :param timeout: Timeout to ping
        :type timeout: float
        :return: ping response
        :rtype: requests.Response
        """
        try:
            return requests.get(
                url='http://{}:{}/ping'.format(self.host, self.port),
                timeout=timeout
            )
        except requests.exceptions.Timeout:
            raise NoConnection()
        except Exception as e:
            raise e
