"""Local preprocessing adapter for the project's pinned RapidOCR 1.4.4."""
import cv2
import numpy as np
import platform
import sys
from types import MethodType


def _crop_text_rows(engine, image, boxes):
    """An integral, axis-aligned RapidOCR box maps each output pixel to itself."""
    from rapidocr_onnxruntime import RapidOCR
    points = np.asarray(boxes)
    if (image.dtype != np.uint8 or image.ndim != 3 or image.shape[2] != 3
            or points.dtype != np.float32 or points.ndim != 3 or points.shape[1:] != (4, 2)):
        return RapidOCR.get_crop_img_list(engine, image, boxes)
    left, top = points[:, 0].T
    right, bottom = points[:, 2].T
    upright = ((left >= 0) & (top >= 0) & (right <= image.shape[1]) & (bottom <= image.shape[0])
               & (left < right) & (top < bottom)
               & (points[:, 1, 0] == right) & (points[:, 1, 1] == top)
               & (points[:, 3, 0] == left) & (points[:, 3, 1] == bottom)
               & (points == np.trunc(points)).all(axis=(1, 2)))
    remaining = iter(RapidOCR.get_crop_img_list(engine, image, points[~upright]))
    crops = []
    for i, direct in enumerate(upright):
        if direct:
            crop = image[int(top[i]):int(bottom[i]), int(left[i]):int(right[i])].copy()
            crops.append(np.rot90(crop) if crop.shape[0] >= 1.5 * crop.shape[1] else crop)
        else:
            crops.append(next(remaining))
    return crops


def default_backend():
    return 'openvino' if sys.platform == 'win32' and platform.machine() == 'AMD64' else 'onnx'


def create_engine(*, backend=None):
    from rapidocr_onnxruntime import RapidOCR
    if backend is None:
        backend = default_backend()
    if backend not in ('onnx', 'openvino', 'openvino-gpu'):
        raise ValueError('Unknown OCR inference backend: ' + str(backend))
    engine = RapidOCR(intra_op_num_threads=4, inter_op_num_threads=2)
    engine.get_crop_img_list = MethodType(_crop_text_rows, engine)
    if backend in ('openvino', 'openvino-gpu'):
        from .ocr_cpu_inference import use_cpu_inference
        use_cpu_inference(engine, accelerate_gpu=backend == 'openvino-gpu')
    engine.inference_backend = backend
    original_factory = engine.text_det.get_preprocess
    levels = np.repeat(np.arange(256, dtype=np.uint8)[:, None, None], 3, axis=2)

    def get_preprocess(max_side):
        original = original_factory(max_side)
        # Compute all possible channel values with this detector's own arithmetic.
        table = original.normalize(levels).astype(np.float32)

        def preprocess(image):
            if image.dtype != np.uint8:
                return original(image)
            resized = original.resize(image)
            if resized is None:
                return None
            normalized = cv2.LUT(resized, table)
            return np.ascontiguousarray(original.permute(normalized)[None])

        return preprocess

    engine.text_det.get_preprocess = get_preprocess
    return engine
