"""OpenVINO FP32 execution of the pinned OCR models, with one request per thread."""
from pathlib import Path
from threading import local


class InferenceSession:
    def __init__(self, model):
        self.model = model
        self.requests = local()

    def __call__(self, tensor):
        if not hasattr(self.requests, 'request'):
            self.requests.request = self.model.create_infer_request()
        # Full-page reading and the busy HUD preview share model weights.
        # They must own separate requests and returned output arrays.
        outputs = self.requests.request.infer(tensor, share_inputs=True, share_outputs=False)
        return [outputs[port] for port in self.model.outputs]


class CPUInference(InferenceSession):
    def __init__(self, core, model_path):
        super().__init__(core.compile_model(str(model_path), 'CPU', {
            'INFERENCE_PRECISION_HINT': 'f32', 'PERFORMANCE_HINT': 'LATENCY',
            'NUM_STREAMS': 1, 'INFERENCE_NUM_THREADS': 4,
        }))


class FixedShapeGPU(InferenceSession):
    def __init__(self, core, path, shape, cpu, cache):
        graph = core.read_model(str(path))
        graph.reshape(shape)
        super().__init__(core.compile_model(graph, 'GPU', {
            'INFERENCE_PRECISION_HINT': 'f32', 'CACHE_DIR': str(cache),
        }))
        self.shape = tuple(shape)
        self.cpu = cpu

    def __call__(self, tensor):
        # Match model input dimensions exactly, preserving original pixels and batch padding.
        if tensor.shape == self.shape:
            return super().__call__(tensor)
        # Recognition rows are independent images. Fill spare batch slots
        # without changing a real line's width, pixels or decoder input.
        if tensor.shape[1:] == self.shape[1:] and 1 < len(tensor) < self.shape[0]:
            import numpy as np
            batch = np.zeros(self.shape, dtype=tensor.dtype)
            batch[:len(tensor)] = tensor
            return [output[:len(tensor)] for output in super().__call__(batch)]
        return self.cpu(tensor)


def use_cpu_inference(engine, *, accelerate_gpu=False):
    from concurrent.futures import ThreadPoolExecutor
    from openvino import Core
    from rapidocr_onnxruntime.main import DEFAULT_CFG_PATH
    from rapidocr_onnxruntime.utils import read_yaml, update_model_path

    config = update_model_path(read_yaml(DEFAULT_CFG_PATH))
    core = Core()
    gpu_shapes = {}
    if accelerate_gpu:
        # One measured full-page detector size and the recognizer's normal full batch.
        # Dynamic GPU shapes incur compilation stalls during sampling.
        rec = engine.text_rec
        gpu_shapes = {'Det': (1, 3, 1088, 1984), 'Rec': (rec.rec_batch_num, *rec.rec_image_shape)}
        cache = Path(__file__).resolve().parents[1] / '.local' / 'ocr-model-cache'
        cache.mkdir(parents=True, exist_ok=True)
    # RapidOCR has already loaded its character dictionary from ONNX metadata.
    # Keep its preprocessing, classifier, decoder and thresholds unchanged.
    # The three models have independent graphs. Join all three before installing
    # their sessions; the temporary workers are gone before the first read.
    def compile_role(role):
        path = config[role]['model_path']
        cpu = CPUInference(core, path)
        if role in gpu_shapes:
            return FixedShapeGPU(core, path, gpu_shapes[role], cpu, cache)
        return cpu

    with ThreadPoolExecutor(max_workers=3, thread_name_prefix='rouge-ocr-init') as pool:
        engine.text_det.infer, engine.text_cls.infer, engine.text_rec.session = pool.map(
            compile_role, ('Det', 'Cls', 'Rec'))
