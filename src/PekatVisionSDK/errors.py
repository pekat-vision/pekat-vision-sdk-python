"""Module with all the custom errors."""

from pathlib import Path


class DistNotFoundError(Exception):
    r"""Raised when no PEKAT VISION was found in the default installation directory.

    * On `Windows`, the search location is `C:\Program Files`.
    * On `Linux`, the search location is `/opt/PEKAT`.

    Location is searched for the `pekat_vision/pekat_vision(.exe)` binary.
    """

    def __str__(self) -> str:
        return "PEKAT VISION not found"


class DistNotExistsError(Exception):
    """Raised when PEKAT VISION does not exist in the specified path."""

    def __init__(self, path: Path, *args: tuple) -> None:
        super().__init__(*args)
        self.path = path

    def __str__(self) -> str:
        return f"PEKAT VISION does not exist at {self.path}"


class PortIsAllocatedError(Exception):
    """Raised when the specified port is already used by another process."""

    def __init__(self, port: int, *args: tuple) -> None:
        super().__init__(*args)
        self.port = port

    def __str__(self) -> str:
        return "Port is allocated"


class InvalidDataTypeError(Exception):
    """Raised when the input data is not a file path, bytes or a [numpy array](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html)."""

    def __init__(self, type_: type, *args: tuple) -> None:
        super().__init__(*args)
        self.type_ = type_

    def __str__(self) -> str:
        return f"Invalid input data type: {self.type_}"


class InvalidResponseTypeError(Exception):
    """Raised when the response type is invalid."""

    def __init__(self, response_type: str, *args: tuple) -> None:
        super().__init__(*args)
        self.response_type = response_type

    def __str__(self) -> str:
        return f"Invalid response type: {self.response_type}"


class ProjectNotFoundError(Exception):
    """Raised when the project was not found in the specified location."""

    def __init__(self, path: Path, *args: tuple) -> None:
        super().__init__(*args)
        self.path = path

    def __str__(self) -> str:
        return f"Project not found at {self.path}"


class PekatNotStartedError(Exception):
    """Raised when [`Instance`][PekatVisionSDK.Instance] couldn't start a project."""

    def __str__(self) -> str:
        return "Pekat not started from unknown reason"


class OpenCVImportError(Exception):
    """Raised when the `response_type` is not `"context"` and OpenCV is not installed: [`cv2`](https://pypi.org/project/opencv-python/)."""

    def __str__(self) -> str:
        return "You need opencv-python installed for this type of response_type"


class NoConnectionError(Exception):
    """Raised when [`ping`][PekatVisionSDK.Instance.ping] times out."""

    def __str__(self) -> str:
        return "Could not establish connection with running instance"
