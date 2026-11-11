"""Local preprocessing adapter for the project's pinned RapidOCR 1.4.4."""
import cv2
import numpy as np
import platform
import sys


def create_engine(*, backend=None):
    from rapidocr_onnxruntime import RapidOCR

    if backend is None:
        backend = 'openvino' if sys.platform == 'win32' and platform.machine() == 'AMD64' else 'onnx'
    if backend not in ('onnx', 'openvino'):
        raise ValueError('Unknown OCR inference backend: ' + str(backend))
    engine = RapidOCR(intra_op_num_threads=4, inter_op_num_threads=2)
    if backend == 'openvino':
        from .ocr_cpu_inference import use_cpu_inference
        use_cpu_inference(engine)
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
