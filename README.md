# PEKAT VISION SDK - Python

A Python module for communication with [PEKAT VISION](https://www.pekatvision.com/products/software/).

Full SDK documentation available here: <https://pekat-vision.github.io/pekat-vision-sdk-python>

## Installation

Type `pip install "pekat-vision-sdk"` into your terminal.

Installing with `pip install "pekat-vision-sdk[opencv]"` also installs [`opencv`](https://pypi.org/project/opencv-python/).

## Example

### Creating the analyzer

```python
from PekatVisionSDK import Instance

# Start a project locally (host 0.0.0.0 - listen on all interfaces)

p_local = Instance("~/PekatVisionProjects/my_project", port=8100, host="0.0.0.0")

# Connect to an already running project

p_remote = Instance(port=8000, already_running=True)
```

### Sending an image to analyze

```python
import numpy as np

# p = Instance(...)

# Analyze image from disk

result = p.analyze("path_to_image.png", response_type="annotated_image")

# Analyze a numpy image

# image: np.ndarray = ...
result = p.analyze(image)
```

### Accessing the results

```python
# Get the evaluation result (True/False)

flow_result = result.context["result"]

# Decode image bytes and save image on disk

import cv2

if result.image_bytes is not None:
    image = result.get_decoded_image()
    cv2.imwrite("result_with_annotations.png", image)
```

### Stopping a project

```python
# Project must have been started using the SDK
p_local.stop()
```
