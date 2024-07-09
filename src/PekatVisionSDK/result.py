"""Module with the Result class."""

from typing import NamedTuple, Optional

import numpy as np
from numpy.typing import NDArray

from .errors import OpenCVImportError


class Result(NamedTuple):
    """Class representing the result of [`Instance.analyze`][PekatVisionSDK.Instance.analyze].

    Attributes:
        image_bytes: Encoded PNG image, to get the decoded image, use [`get_decoded_image`][PekatVisionSDK.Result.get_decoded_image].
        context: Context dictionary.
    """

    image_bytes: Optional[bytes]
    context: dict

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
