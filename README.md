# PEKAT VISION SDK - Python

A Python module for communication with [PEKAT VISION](https://www.pekatvision.com/products/software/).

## Installation

Type `pip install "pekat-vision-sdk[opencv]"` into your terminal.

## Example

```python
import cv2
from PekatVisionSDK import Instance

# Connect to an already running project
p = Instance(port=8000, already_running=True)

# Send an image to analyze
result = p.analyze("path_to_image.png", response_type="annotated_image")

# Access the result
flow_result = result.context["result"]

# Decode image bytes
image = result.get_decoded_image()

# Save annotated image on disk
cv2.imwrite("result_with_annotations.png", image)
```
