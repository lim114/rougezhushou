"""CPU FP32 execution of the pinned OCR models, with one request per thread."""
from threading import local


class CPUInference:
    def __init__(self, core, model_path):
        self.model = core.compile_model(str(model_path), 'CPU', {
            'INFERENCE_PRECISION_HINT': 'f32',
            'PERFORMANCE_HINT': 'LATENCY',
            'NUM_STREAMS': 1,
            'INFERENCE_NUM_THREADS': 4,
        })
        self.requests = local()

    def __call__(self, tensor):
        if not hasattr(self.requests, 'request'):
            self.requests.request = self.model.create_infer_request()
        # Full-page reading and the busy HUD preview share model weights.
        # They must own separate requests and returned output arrays.
        outputs = self.requests.request.infer(tensor, share_inputs=True, share_outputs=False)
        return [outputs[port] for port in self.model.outputs]


def use_cpu_inference(engine):
    from openvino import Core
    from rapidocr_onnxruntime.main import DEFAULT_CFG_PATH
    from rapidocr_onnxruntime.utils import read_yaml, update_model_path

    config = update_model_path(read_yaml(DEFAULT_CFG_PATH))
    core = Core()
    # RapidOCR has already loaded its character dictionary from ONNX metadata.
    # Keep its preprocessing, classifier, decoder and thresholds unchanged.
    engine.text_det.infer = CPUInference(core, config['Det']['model_path'])
    engine.text_cls.infer = CPUInference(core, config['Cls']['model_path'])
    engine.text_rec.session = CPUInference(core, config['Rec']['model_path'])
