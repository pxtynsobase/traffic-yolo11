# Model setup

This project requires a custom Ultralytics YOLO object detection model named `best-4.pt`. Model weights, training data, installed libraries, and runtime files are excluded from Git.

By default, the app loads `C:\ai\yolo_11\best-4.pt` on Windows. To use another location, set the `YOLO_MODEL_PATH` environment variable to the full path of the model before starting the app.

The supplied model has one class named `class_0`. The interface selects a single-class model automatically. For models with multiple classes, select the vehicle classes in Analysis settings.

Run `start.bat`, then visit http://127.0.0.1:8050. The first run downloads dependencies; later runs reuse the local installation. The tested CPU dependency versions are in `requirements-lock.txt`.

For an existing Python environment:

```sh
python -m pip install -r requirements-lock.txt
python app.py
```

Run the API tests with `python -m unittest test_app.py`. These tests use mock detection results; real inference requires your model weights.

The green-time estimate is calculated for a single approach. This application does not operate physical traffic signals.
