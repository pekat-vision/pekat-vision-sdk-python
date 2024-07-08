# PEKAT VISION SDK - Python

A Python module for communication with [PEKAT VISION](https://www.pekatvision.com/products/software/).

## Installation

- `pip install pekat-vision-sdk[opencv]` - recommended
- `pip install pekat-vision-sdk` - wihout `opencv`, click [here](#without-opencv) for more

## Usage

Using this SDK involves 3 basic steps:

- [Instance creation](#creation)
- [Image analysis](#analysis)
- [Result processing](#processing)

### Creation

Create an [Instance] to start a project or connect to an already running project:

=== "Start a project"

    ```py3
    from pathlib import Path

    from PekatVisionSDK import Instance

    # Start a project on port 8000
    p = Instance(Path.home() / "PekatVisionProjects/myProject", port=8000)
    ```

=== "Connect to a running project"

    ```py3
    from PekatVisionSDK import Instance

    # Connect to a project running on port 8000
    p = Instance(port=8000, already_running=True)
    ```

### Analysis

Call the [analyze] method and supply it with the image, either as a numpy array, bytes or a path on disk:

=== "Analyze numpy"

    ```py3
    import cv2

    # Load an image as a numpy array
    image = cv2.imread("path_to_image.png")

    result = p.analyze(image)
    ```

=== "Analyze bytes"

    ```py3
    from pathlib import Path

    # Load a png
    image_bytes = Path("path_to_image.png").read_bytes()

    result = p.analyze(image_bytes)
    ```

=== "Analyze from disk"

    ```py3
    # Instance will load the image as bytes
    result = p.analyze("path_to_image.png")
    ```

Depending on the response type, the image may or may not be present in the result, see [analyze] for more.

### Processing

The result contains an encoded image and the [context] dictionary.

In case response type was other than the default `"context"`, we can also get the resulting image.

=== "Context only"

    ```py3
    # Getting the context
    context = result.context

    # Getting the result of evaluation
    evaluation_result = context["result"]
    ```

=== "Image"

    ```py3
    # Getting the numpy image
    image = result.get_decoded_image()

    # In case we need just PNG bytes
    image_bytes = result.image_bytes
    ```

## Without OpenCV

You can install this module without [OpenCV](https://opencv.org/) if you

- only want to use `response_type="context"`
- don't need to use `Result.get_decoded_image()`

[Instance]: documentation/instance.md
[analyze]: documentation/instance.md/#PekatVisionSDK.Instance.analyze
[context]: https://pekatvision.atlassian.net/wiki/spaces/KB3/pages/698058893/Context
