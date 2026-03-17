"""Module with utility functions for working with context."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict, cast

from .errors import OpenCVImportError

if TYPE_CHECKING:
    import numpy as np
    from numpy.typing import NDArray

    from PekatVisionSDK import context


class FilterParams(TypedDict, total=False):
    """Parameters for filtering rectangles."""

    min_x: int
    max_x: int
    min_y: int
    max_y: int
    min_width: int
    max_width: int
    min_height: int
    max_height: int
    min_area: int
    max_area: int
    min_confidence: float
    max_confidence: float


def filter_rectangles(
    provided_context: context.Context,
    filters: FilterParams | None = None,
    modules: list[context.ModuleType] | set[context.ModuleType] | None = None,
    labels: list[context.ClassName] | set[context.ClassName] | None = None,
) -> list[context.DetectedRectangle]:
    """Filter detected rectangles in context based on provided parameters.

    The function returns empty list if it's not a full context.

    Arguments:
        provided_context: Context from Instance.analyze to be filtered.
        filters: Filter parameters.
        modules: List or set of modules to filter by.
        labels: List of labels to filter by.

    Returns:
        lict[context.DetectedRectangle]: Filtered list of detected rectangles.
    """
    if not provided_context["processing"]:
        return []

    if filters is None:
        filters = {}

    provided_context = cast("context.FullContext", provided_context)
    return [
        rectangle
        for rectangle in provided_context["detectedRectangles"]
        if filter_function(rectangle, filters, modules, labels)
    ]


def filter_function(
    rectangle: context.DetectedRectangle,
    filters: FilterParams,
    modules: list[context.ModuleType] | set[context.ModuleType] | None = None,
    labels: list[context.ClassName] | set[context.ClassName] | None = None,
) -> bool:
    """Filter function for rectangles.

    Arguments:
        rectangle: Rectangle to be filtered.
        filters: Filter parameters.
        modules: List or set of modules to filter by.
        labels: List or set of labels to filter by.

    Returns:
        bool: True if rectangle passes the filter, False otherwise.
    """
    return (
        _check_bounds(rectangle["x"], filters.get("min_x"), filters.get("max_x"))
        and _check_bounds(rectangle["y"], filters.get("min_y"), filters.get("max_y"))
        and _check_bounds(
            rectangle["width"],
            filters.get("min_width"),
            filters.get("max_width"),
        )
        and _check_bounds(
            rectangle["height"],
            filters.get("min_height"),
            filters.get("max_height"),
        )
        and _check_bounds(
            rectangle["height"] * rectangle["width"],
            filters.get("min_area"),
            filters.get("max_area"),
        )
        and _check_bounds(
            rectangle["confidence"],
            filters.get("min_confidence"),
            filters.get("max_confidence"),
        )
        and _check_module(rectangle["source"]["type"], modules)
        and _check_label(rectangle["classNames"], labels)
    )


def _check_bounds(
    value: float,
    min_value: float | None,
    max_value: float | None,
) -> bool:
    return (min_value is None or value >= min_value) and (
        max_value is None or value <= max_value
    )


def _check_module(
    value: context.ModuleType,
    modules: list[context.ModuleType] | set[context.ModuleType] | None,
) -> bool:
    return modules is None or value in modules


def _check_label(
    class_names: list[context.ClassName],
    labels: list[context.ClassName] | set[context.ClassName] | None,
) -> bool:
    return labels is None or len(class_names) == 0 or class_names[0]["label"] in labels


def draw_rectangles(
    image: NDArray[np.uint8],
    provided_context: context.Context,
    color: tuple[int, int, int] = (0, 0, 255),
    thickness: int = 2,
) -> NDArray[np.uint8]:
    """Draw rectangles on image based on provided context.

    Arguments:
        image: Image to draw rectangles on.
        provided_context: Context from Instance.analyze to be drawn.
        color: Color of the rectangles. Defaults to (0, 0, 255).
        thickness: Thickness of the rectangles. Defaults to 2.

    Raises:
        OpenCVImportError: If OpenCV is not installed.

    Returns:
        NDArray[np.uint8]: Image with drawn rectangles.
    """
    try:
        import cv2  # noqa: PLC0415
    except ImportError as e:
        raise OpenCVImportError from e

    res_image = image.copy()

    if provided_context["processing"] is False:
        return res_image

    provided_context = cast("context.FullContext", provided_context)
    for rectangle in provided_context["detectedRectangles"]:
        cv2.rectangle(
            res_image,
            (round(rectangle["x"]), round(rectangle["y"])),
            (
                round(rectangle["x"] + rectangle["width"]),
                round(rectangle["y"] + rectangle["height"]),
            ),
            color,
            thickness,
        )
    return res_image
