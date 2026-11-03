# RapidOCR文字行复用接入说明

依赖版本：`rapidocr-onnxruntime==1.4.4`，作者SWHL；包元数据许可证为Apache-2.0。继续使用已安装的原模型、检测、文字裁切、归一化、推理及解码接口，没有另行分发模型或安装新依赖。

- 上游项目：https://github.com/RapidAI/RapidOCR
- 固定版本接口文档：https://rapidai.github.io/RapidOCRDocs/v1.4.4/install_usage/api/RapidOCR/
- 原文字识别实现：该版本包的`rapidocr_onnxruntime/ch_ppocr_rec/text_recognize.py`。
- 原文件署名：Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
- 原许可证：https://www.apache.org/licenses/LICENSE-2.0

本项目的`PageOCR`沿用该版本的宽高排序、归一化填充与解码比例，在其接口上增加精确模型输入的有界逐行缓存；缺失行按相同宽度填充后推理，其它行复用。完整当前文字检测、方向分类、置信过滤和原坐标转换保留。本机对比记录见`verification/maintenance/text-row-sync-20261103/replay/summary.json`。其它版本尚未接入；现有版本检查仍有效。
