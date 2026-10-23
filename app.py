import base64
import io
import math
import os
import threading
import sys
import importlib
from pathlib import Path

LOCAL_PACKAGES = Path(__file__).resolve().parent / '.packages'
sys.path.insert(0, str(LOCAL_PACKAGES))
os.environ.setdefault('YOLO_CONFIG_DIR', str(Path(__file__).resolve().parent / '.runtime' / 'yolo'))
os.environ.setdefault('MPLCONFIGDIR', str(Path(__file__).resolve().parent / '.runtime' / 'matplotlib'))
Path(os.environ['YOLO_CONFIG_DIR']).mkdir(parents=True, exist_ok=True)
Path(os.environ['MPLCONFIGDIR']).mkdir(parents=True, exist_ok=True)

from flask import Flask, jsonify, request, send_from_directory
from PIL import Image, UnidentifiedImageError

app = Flask(__name__, static_folder='static')
app.config['MAX_CONTENT_LENGTH'] = 12 * 1024 * 1024
DEFAULT_MODEL = r'C:\ai\yolo_11\best-4.pt' if os.name == 'nt' else str(Path(__file__).resolve().parent / 'models' / 'best-4.pt')
MODEL_PATH = Path(os.environ.get('YOLO_MODEL_PATH', DEFAULT_MODEL))
model = None
lock = threading.Lock()


def get_model():
    global model
    if model is None:
        if not MODEL_PATH.is_file():
            raise FileNotFoundError(f'Model not found: {MODEL_PATH}')
        importlib.invalidate_caches()
        from ultralytics import YOLO
        model = YOLO(str(MODEL_PATH))
        if model.task != 'detect':
            model = None
            raise ValueError('This app requires an object detection model.')
        if (LOCAL_PACKAGES / 'flask').is_dir():
            (LOCAL_PACKAGES / 'setup.ok').touch()
    return model


def timing(count, seconds, minimum, maximum, lanes):
    if not (0.1 <= seconds <= 30 and 1 <= minimum <= maximum <= 300 and 1 <= lanes <= 8):
        raise ValueError('Invalid timing or lane settings.')
    return 0 if count == 0 else min(maximum, max(minimum, math.ceil(count * seconds / lanes)))


@app.get('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.get('/api/status')
def status():
    try:
        with lock:
            m = get_model()
            return jsonify(ready=True, model=MODEL_PATH.name, classes=m.names)
    except Exception as exc:
        return jsonify(ready=False, error=str(exc)), 503


@app.get('/api/health')
def health():
    return jsonify(service='traffic-flow', healthy=True, model_present=MODEL_PATH.is_file())


@app.post('/api/detect')
def detect():
    try:
        confidence = float(request.form.get('confidence', '.5'))
        seconds = float(request.form.get('seconds', '2'))
        minimum = int(request.form.get('minimum', '10'))
        maximum = int(request.form.get('maximum', '90'))
        lanes = int(request.form.get('lanes', '1'))
        timing(0, seconds, minimum, maximum, lanes)
        if not .1 <= confidence <= .95:
            raise ValueError('Confidence must be between 0.1 and 0.95.')
        selected = [int(c) for c in request.form.get('classes', '').split(',') if c.strip()]
        if not selected:
            raise ValueError('Select at least one vehicle class.')
        if 'image' not in request.files:
            raise ValueError('Please provide an image.')
        source = Image.open(request.files['image'].stream)
        if source.width * source.height > 20_000_000:
            raise ValueError('Image dimensions are too large.')
        source = source.convert('RGB')
        source.thumbnail((1280, 1280))
        with lock:
            m = get_model()
            if any(c not in m.names for c in selected):
                raise ValueError('Selected classes do not match the model.')
            result = m.predict(source, conf=confidence, classes=selected, verbose=False)[0]
            counts = {str(m.names[c]): 0 for c in selected}
            for box in result.boxes:
                counts[str(m.names[int(box.cls.item())])] += 1
            annotated = Image.fromarray(result.plot()[:, :, ::-1])
        output = io.BytesIO()
        annotated.save(output, format='JPEG', quality=85)
        count = sum(counts.values())
        return jsonify(count=count, counts=counts, green=timing(count, seconds, minimum, maximum, lanes),
                       image='data:image/jpeg;base64,' + base64.b64encode(output.getvalue()).decode())
    except (ValueError, UnidentifiedImageError) as exc:
        return jsonify(error=str(exc)), 400
    except Exception as exc:
        return jsonify(error=f'Detection failed: {exc}'), 503


@app.errorhandler(413)
def too_large(_):
    return jsonify(error='Image files must not exceed 12 MB.'), 413


if __name__ == '__main__':
    app.run(host=os.environ.get('HOST', '127.0.0.1'), port=int(os.environ.get('PORT', '8050')), debug=False)
