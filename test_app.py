"""API validation tests; inference requires the actual model and Ultralytics."""
import io
import unittest
from unittest.mock import patch
from PIL import Image
import app


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()

    def test_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Traffic Intelligence', response.get_data(as_text=True))
        response.close()

    def test_model_unavailable_is_explicit(self):
        with patch.object(app, 'get_model', side_effect=FileNotFoundError('missing model')):
            response = self.client.get('/api/status')
            self.assertEqual(response.status_code, 503)
            self.assertFalse(response.json['ready'])

    def test_health_does_not_load_model(self):
        with patch.object(app, 'get_model') as loader:
            response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['service'], 'traffic-flow')
        self.assertTrue(response.json['healthy'])
        loader.assert_not_called()

    def test_invalid_settings_rejected(self):
        response = self.client.post('/api/detect', data={'minimum': '90', 'maximum': '10'})
        self.assertEqual(response.status_code, 400)

    def test_non_image_rejected(self):
        response = self.client.post('/api/detect', data={
            'classes': '0', 'image': (io.BytesIO(b'not an image'), 'bad.jpg')})
        self.assertEqual(response.status_code, 400)

    def test_empty_selection_rejected(self):
        response = self.client.post('/api/detect', data={'classes': ''})
        self.assertEqual(response.status_code, 400)

    def test_detection_passes_custom_classes_and_counts_boxes(self):
        import numpy as np
        from types import SimpleNamespace
        class Scalar:
            def item(self):
                return 0
        fake_result = SimpleNamespace(boxes=[SimpleNamespace(cls=Scalar())] * 12,
                                      plot=lambda: np.zeros((64, 64, 3), dtype=np.uint8))
        from unittest.mock import Mock
        fake = SimpleNamespace(names={0: 'Car'}, predict=Mock(return_value=[fake_result]))
        image = io.BytesIO()
        Image.new('RGB', (64, 64)).save(image, 'JPEG')
        image.seek(0)
        with patch.object(app, 'get_model', return_value=fake):
            response = self.client.post('/api/detect', data={
                'classes': '0', 'image': (image, 'road.jpg')})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['count'], 12)
        self.assertEqual(response.json['green'], 24)
        self.assertEqual(fake.predict.call_args.kwargs['classes'], [0])
        self.assertTrue(response.json['image'].startswith('data:image/jpeg;base64,'))


if __name__ == '__main__':
    unittest.main()
