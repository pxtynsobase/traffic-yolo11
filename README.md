# Traffic Flow

A local web application that counts vehicles with a custom YOLO11 model and estimates the green-light duration for a single traffic approach.

## Features

- English interface with image uploads, video playback, and live camera input.
- Vehicle detection with bounding boxes and counts for the latest analyzed frame.
- Configurable confidence threshold and vehicle classes.
- Adjustable discharge time, minimum and maximum green time, and number of lanes.
- Local processing without saving uploaded images.

## Requirements

- Windows with Python 3.11 or 3.12 and Python Launcher, or the bundled Codex Python runtime used by the launcher.
- Internet access for the first dependency installation.
- Your custom `best-4.pt` detection model. Model weights and training data are not included in this repository.

## Quick start on Windows

1. Clone or download this repository.
2. Place your model at `C:\ai\yolo_11\best-4.pt`, or set `YOLO_MODEL_PATH` to its full path before starting the app.
3. Double-click `start.bat`. The first run installs the tested CPU dependencies into `.packages`; later runs reuse them.
4. Open **http://127.0.0.1:8050**.
5. Select the vehicle classes, upload an image or video, or open your camera. Review the detected count and recommended green time.

Use **Stop** to stop video or camera analysis. Close the server window to shut down the application.

### Run in an existing Python environment

```sh
python -m pip install -r requirements-lock.txt
python app.py
```

`requirements-lock.txt` records the tested dependency versions, including CPU builds of PyTorch and torchvision. `requirements.txt` provides broader dependency ranges.

To change the model path in PowerShell:

```powershell
$env:YOLO_MODEL_PATH = "C:\path\to\best-4.pt"
python app.py
```

The default port is 8050. Set the `PORT` environment variable to use a different port. See [MODEL_SETUP.md](MODEL_SETUP.md) for additional model details.

## Green-time calculation

```text
raw time = ceil(vehicle count × seconds per vehicle ÷ simultaneous lanes)
green time = min(maximum green, max(minimum green, raw time))
```

When no vehicles are detected, the recommendation is **0 seconds**.

Defaults: **2 seconds per vehicle**, **10-second minimum**, **90-second maximum**, and **1 lane**. For example, 12 vehicles produce 24 seconds; 3 vehicles produce the 10-second minimum.

## Counting behavior and limitations

Counts represent vehicles visible in the latest analyzed frame. They are not cumulative traffic totals or unique vehicle counts. Video and camera frames are processed sequentially after the previous detection finishes.

The application reads class labels from the model instead of assuming COCO class IDs. The supplied model has a single class named `class_0`, which is selected automatically. For models with multiple classes, select the classes that represent vehicles.

There is no queue region of interest or tracking across frames. Use footage focused on the approach you want to analyze. Green time is an estimate, not a countdown or a command to physical traffic signal equipment. Pedestrian phases, yellow time, intersection clearance, and coordination between approaches are not implemented.

The server listens only on the local machine. Images are limited to 12 MB and 20 million pixels and are resized before inference. Camera use requires browser permission; video formats must be supported by the browser.

## Project structure

| File | Purpose |
| --- | --- |
| `app.py` | Flask server, model inference, and timing calculation |
| `static/index.html` | English interface |
| `static/app.js` | Image, video, camera, and result handling |
| `start.bat` | Windows launcher and dependency setup |
| `requirements-lock.txt` | Tested dependency versions |
| `requirements.txt` | General dependency requirements |
| `test_app.py` | API validation tests using mock detection results |
| `MODEL_SETUP.md` | Model configuration instructions |
| `VALIDATION.md` | Validation notes and real-model test results |

## Validation

```sh
python -m unittest test_app.py
```

Six API tests cover the page, missing models, invalid settings, invalid files, class selection, and result handling. These use mock inference results.

A separate test with the actual `best-4.pt` model detected **15 vehicles**, producing a **30-second** green-time recommendation. A blank image returned **0 vehicles** and **0 seconds**. Live video and camera operation have not yet been tested end to end.

Model API reference: [Ultralytics prediction documentation](https://docs.ultralytics.com/modes/predict/).
