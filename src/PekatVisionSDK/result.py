"""Module with the Result class."""

from typing import Any, NamedTuple, cast

import numpy as np
from numpy.typing import NDArray

from .context import Context
from .errors import OpenCVImportError


class _BaseResult(NamedTuple):
    image_bytes: bytes | None
    context: dict[str, Any]


class Result(_BaseResult):
    """Class representing the result of [`Instance.analyze`][PekatVisionSDK.Instance.analyze].

    Attributes:
        image_bytes: Encoded PNG image, to get the decoded image, use [`get_decoded_image`][PekatVisionSDK.Result.get_decoded_image].
        context: Context dictionary.
    """

    def get_decoded_image(self) -> NDArray[np.uint8]:
        """Get the decoded image.

        Raises:
            ValueError: If image is `None`, usually when `response_type` is `"context"`.
            OpenCVImportError: If image is not `None` and OpenCV is not installed.
        """
        if self.image_bytes is None:
            msg = "Image is None, call `analyze` with a different `response_type`"
            raise ValueError(msg)
        try:
            import cv2
        except ImportError as e:
            raise OpenCVImportError from e

        return cv2.imdecode(np.frombuffer(self.image_bytes, np.uint8), cv2.IMREAD_COLOR)

    def typed(self) -> "TypedResult":
        """Get the typed version of the result.

        This has no effect on runtime, but allows for better type checking and autocompletion in IDEs.
        """
        return cast("TypedResult", self)


class TypedResult(Result):
    """Typed variant of [`Result`][PekatVisionSDK.Result] with a refined `context` type."""

    context: Context  # pyright: ignore[reportIncompatibleVariableOverride]
