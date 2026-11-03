# 第380节历史图审格式的严格兼容候选

只读诊断：355条历史复用链，24条旧格式叶记录和2条同文档引用被旧封存器格式前提误拒；各证明原件SHA和整PNG字节保持一致。诊断原件逐条保留在 original-row-diagnosis.json。

本目录只准备源代码，不执行封存，不重新运行测试或窗口，不新增图片查看，不写summary.json，也不修改原registry、visual、执行档案、freeze或任何旧工具。

execution-summary380-original.py逐字节保留实际失败的原封存器。historical_schema_compat.py只允许6份精确proof SHA下的24个准确row指针，并保留各原字段真正表达的旧直看复用；327的唯一同文档row6→row5边还核对准确原文、原行指纹及/root直看原点。其余条目继续走原守卫。

execution-summary380-revision2.py嵌入该模块，避免新增运行时.cache依赖。只在verify_registry_chain两个局部条件处增加上述准确分支；原跨proof require、统一叶require原AST都原样保留，其他函数AST不变。完整逆替换能恢复原文件全部文本和AST。它仍检查actor、无环、全PNG整字节、原proof摘要以及原100组件/原30/独立29/typed/完整scope，绝不把旧复用改称新直看。

root审阅并决定使用后，可将这个新candidate复制到新的公开verification/full-380/execution-summary380-revision2.py，或运行generate_revision2.py --out <该新文件绝对路径>。生成器只允许新revision2文件且核对原sealer与模块精确SHA、每个唯一锚点、候选SHA和逆文本/AST；绝不执行它。必须保留原实际exit1及来源，随后由root明确实际执行新的独立后处理版本；生成候选不等于封存成功。

所有scope/未通过/本局状态边界保持。任何额外schema、proof、row、原文或字节差异仍应拒绝，不能借本候选接受未知证据。
