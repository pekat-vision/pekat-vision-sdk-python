# ruff: noqa: N815


"""Module holding utility functions for working with Context."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


class Position(BaseModel):
    """Class representing the position of a detected object."""

    x: int | float
    y: int | float


class ImageShape(BaseModel):
    """Class representing the shape of an image."""

    height: int
    width: int


class BareContext(BaseModel):
    """Class representing bare context.

    This class represents context that will be returned when processing
    is set to OFF in the target project.
    """

    model_config = ConfigDict(extra="forbid")

    error: bool
    imageShape: ImageShape
    processing: Literal[False]
    processingTime: float
    save: bool


class ModuleType(StrEnum):
    """Enum representing different module types."""

    UNSUPERVISED = "UNSUPERVISED"
    SUPERVISED = "SUPERVISED"
    CLASSIFIER = "CLASSIFIER"
    DETECTOR = "DETECTOR"
    CODE = "CODE"


class ClassName(BaseModel):
    """Class representing single className."""

    id: int
    confidence: int
    label: str
    color: Optional[str] = None
    color_bgr: Optional[list[int]] = None


class RectangleSource(BaseModel):
    """Class representing information about source module of a detected rectangle."""

    modelId: int
    moduleId: int
    type: ModuleType


class DetectedRectangle(BaseModel, Position):
    """Class representing single detected rectangle."""

    # Positional info
    width: int | float
    height: int | float
    rotate: float
    area: Optional[float] = None

    # Detection info
    classNames: list[ClassName]
    confidence: float

    # Additional info
    id: int
    source: RectangleSource


class DetectedLine(BaseModel):
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


class FullContext(BareContext):
    """Class representing full context.

    This class represents context that will be returned when processing
    is set to ON in the target project.
    """

    # Change from BareContext
    model_config = ConfigDict(extra="allow")
    processing: Literal[True]

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
