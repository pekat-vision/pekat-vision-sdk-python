# PEKAT VISION SDK

A Python module for communication with PEKAT VISION

## Requirements

* numpy
* python-opencv (optional)
* PEKAT VISION 3.10.2 or higher


## Installation
Type `pip install git+https://github.com/pekat-vision/pekat-vision-sdk-python`

## Usage

```python
import cv2
from PekatVisionSDK import Instance

p = Instance('C:\\Users\\Peter\\PekatVisionProjects\\test_project')

# response - only context
context = p.analyze('path_to_image.png')

# response - heatmap and context
img_heatmap, context = p.analyze('path_to_image.png', response_type='heatmap')

# response - annotated image and context
img_annotated, context = p.analyze('path_to_image.png', response_type='annotated_image')

p.stop()
```

You cand send image in numpy array:

```python
import cv2
img_np = cv2.imread('path_to_image.png')

p.analyze(img_np, response_type='annotated_image')
```

Access to already running PEKAT VISION instance
```python
p = Instance(port=8100, host='192.168.10.0', already_running=True)
```

Remote analyzer enables you to connect to a remotely running PEKAT VISION. It is possible to connect from multiple PCs simultaneously. PEKAT VISION behaves as a server automatically.

Multiple cameras
```python
# start projects
p1 = Instance('C:\\Users\\Peter\\PekatVisionProjects\\project_camera_1')
p2 = Instance('C:\\Users\\Peter\\PekatVisionProjects\\project_camera_2')
p3 = Instance('C:\\Users\\Peter\\PekatVisionProjects\\project_camera_3')


# response - only context 
# in loop
context1 = p1.analyze('path_to_image_camera_1.png')
context2 = p2.analyze('path_to_image_camera_2.png')
context3 = p3.analyze('path_to_image_camera_3.png')
```
