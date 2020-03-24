# PEKAT VISION SDK

A Python module for communication with PEKAT VISION

## Requirements

* numpy
* python-opencv (optional)

## Installation
Type `pip install git+https://github.com/pekat-vision/pekat-vision-sdk-python`

## Usage

```python
import cv2
from PekatVisionSDK import Instance

p = Instance('C:\\Users\\Peter\\PekatVisionProjects\\test_project')

# response - only context
context = p.recognise('path_to_image.png')

# response - heatmap and context
img_heatmap, context = p.recognise('path_to_image.png', response_type='heatmap')

# response - annotated image and context
img_annotated, context = p.recognise('path_to_image.png', response_type='annotated_image')

p.stop()
```

You cand send image in numpy array:

```python
import cv2
img_np = cv2.imread('path_to_image.png')

p.recognise(img_np, response_type='annotated_image')
```

Access to already running PEKAT VISION instance
```python
p = Instance(port=8100, host='192.168.10.0', already_running=True)
```
