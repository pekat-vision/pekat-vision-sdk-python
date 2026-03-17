"""Module holding utility functions for working with Context."""

from __future__ import annotations

from enum import StrEnum
from typing import TypedDict

from typing_extensions import NotRequired


class Context(TypedDict):
    """Abstract class for context from image analysis.

    This class represents context that will be returned when processing
    is set to OFF in the target project.
    """

    error: bool
    imageShape: ImageShape
    processingTime: float
    save: bool
    processing: bool


class Position(TypedDict):
    """Class representing the position of a detected object."""

    x: int | float
    y: int | float


class ImageShape(TypedDict):
    """Class representing the shape of an image."""

    height: int
    width: int


class ModuleType(StrEnum):
    """Enum representing different module types."""

    UNSUPERVISED = "UNSUPERVISED"
    SUPERVISED = "SUPERVISED"
    CLASSIFIER = "CLASSIFIER"
    DETECTOR = "DETECTOR"
    CODE = "CODE"
    OCR = "OCR"


class ClassName(TypedDict):
    """Class representing single className."""

    id: int
    confidence: int
    label: str
    color: NotRequired[str]
    color_bgr: NotRequired[list[int]]


class RectangleSource(TypedDict):
    """Class representing information about source module of a detected rectangle."""

    modelId: int
    moduleId: int
    type: ModuleType


class DetectedRectangle(Position):
    """Class representing single detected rectangle."""

    # Positional info
    width: int | float
    height: int | float
    rotate: float
    area: NotRequired[float]

    # Detection info
    classNames: list[ClassName]
    confidence: float

    # Additional info
    id: int
    source: RectangleSource


class DetectedLine(TypedDict):
    """Class represented line detected using Measure tool."""

    # Positional info
    start: Position
    end: Position
    angle: float
    width: int | float
    length: int | float

    # Additional info
    id: int
    label: str
    method: str
    percent: bool


class FullContext(Context):
    """Class representing full context.

    This class represents context that will be returned when processing
    is set to ON in the target project.
    """

    # Inputs
    data: str

    # Info
    completeTime: float
    errors: list
    stderr: str
    stdout: str
    globalData: dict
    operatorInput: dict
    production_mode: bool
    save: bool
    score: float
    threshold: float
    surfaceClasses: list[ClassName]

    # Detections
    angle: None | float
    detectedRectangles: list[DetectedRectangle]
    lines: list[DetectedLine]

    # Evaluation
    result: bool
