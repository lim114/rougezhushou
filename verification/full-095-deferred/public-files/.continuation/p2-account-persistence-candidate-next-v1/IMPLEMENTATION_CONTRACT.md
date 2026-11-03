# 账户缓存持久化可靠性：外部 SOURCE 候选

本稿未接入工程，未运行候选、测试模块、计算 API 或窗口，不计第97节或其它新节。真实 full095 完整验收并保存至 GitHub，以及第96节实际完成，仍是根端集成前置条件；这些当前均保留 null。当前735源码不改。

本组只完善既有账户观察→有效内存→持久化→失败告知的完整流程。游戏机制、培养数值、本局优先、观察时间顺序、记录接受规则和未知附加值保留规则不变。未来精选登记的基线是已冻结但尚未接入的096候选 verify_cloud.py；不能把它说成当前735工程文件。

## 已查明的字符串边界

官方 Python 3.12 系列 JSON 文档与 RFC8259 §8.2 已下载并保留原响应/版本/hash于独立调查包 `p2-after096-account-metadata-source-survey-v1`。查询到的官方页面标明3.12.15；当前执行环境由 pyvenv.cfg、patchlevel.h 和独立根端探针共同证实为3.12.14，二者不混称同一补丁版本。

CPython JSON 接受包含未配对 surrogate 的 ASCII 转义文本，并在 Python 字符串中保留相关码点；RFC语法允许这些位序列，但明确其不能编码有效 Unicode 字符，跨实现行为不可预测。因此本稿只讨论精确保留 CPython 已接受的码点，不声称它们属于可互操作的合法 Unicode。

根端独立 stdlib 探针实际证实：已解码 U+D800 在 ensure_ascii=False 产生的字符串中保留，严格UTF-8临时写入抛 UnicodeEncodeError；原公开夹具不变，新的临时文件存在且为0B，公共内存更新保留。两种转义策略在该已声明的小夹具中精确往返，普通中文/emoji字节不变。这不是工程复现。

本作者另经明确授权运行一次独立 stdlib 控制，实际3.12.14的22个 key/value 行证实4个相邻原生 high→low pair 控制会被连续 JSON 转义后的 decoder 合成为一个码点，其余已声明18行精确往返。该控制未调用项目或候选。不能从已载入JSON的普通emoji，推导任意原生两个surrogate码点都可无损保存。

## 精确改动

- `AccountCache.__init__` 仅新增会话字段 `save_issue=None`。该字段不是账户记录，不写入JSON。
- `save` 保持全映射校核及永久保护门。门后先用原 ensure_ascii=False、indent=2 生成字符串，并扫描序列化文本的真实相邻 high(D800–DBFF)→low(DC00–DFFF) 码点。命中即记录无法无损保存、永久保护并返回False；任何mkdir、临时文件操作和replace均不执行。原生字符串和已接受内存不被改为emoji。
- 不命中时，仅对已完成JSON quoting的字符串做 UTF-8 backslashreplace 再解码。单独或被其它字符隔开的surrogate成为JSON转义；普通Unicode及ASCII字面反斜杠-u文本保持原有字节。仍使用相同UTF-8 `write_text`，保留原平台换行策略和JSON顺序/缩进，不切换成write_bytes。
- `mkdir→临时write_text→replace` 的实际IO顺序保留。只捕获这一组IO的OSError（包括PermissionError/FileExistsError），记录保存未完成并 `_protect()` 无参数，返回False。不复用load_issue，不吞其它异常，不删除/清理/恢复临时文件，不自动重试。
- `observe`、view、校核、原合并、changed保存决定、时间拒绝和所有数值函数完整保持。原有observe在调用save之前赋值，save返回False后仍返回True；有效事实因此可以继续显示。保存保护不单独使有效view不可用。
- `notice` 保留原有本ID issue/load_issue前缀，在保存失败时补充：有效培养记录仍可在当前运行使用，新读取未保存到账号档案，本次不再自动写入或覆盖。坏ID仍说明不可用；不声称所有记录有效，也不声称原文件必然存在。“账号档案”指目标文件，不否认可能保留临时写入证据。无保存失败时旧文本保持。

资格检查移至mkdir之前，以便拒写不创建目录或临时文件；正常IO顺序和普通输出字节保持。未支持的非JSON对象/循环结构/非IO序列化异常不扩展成新可接受输入，也不因泛化catch被误报为已保存。

同一ID的旧顶层extra仍可能被原生产者丢弃，不新增保留语义。可靠的surrogate路线是未知ID记录、另一个未更新ID，或原字段/source/time mapping中未被本次观察替换的叶值；native incoming已接受的opaque叶也可进入该边界。

## 验证合同（均未运行候选）

18个测试方法仅为源码。ASCII原盘控制直接写bytes，避免093原构造器先以严格UTF-8失败。覆盖端点单独surrogate的key/value、合并保留叶、原生低→高/隔开的码点、已解码正常emoji、字面反斜杠-u、普通UTF-8与平台换行字节；相邻native pair安全拒写且不碰既有原盘/tmp或缺失父目录。

IO控制覆盖mkdir/write/replace的OSError族、部分临时写入、完整临时写入后replace失败、原文件缺失、有效内存与notice、同一失败会话的后续changed/unchanged/其它ID及直接save无IO；保留后来发现的坏ID说明、metadata-only的原changed决定、非IO异常和独立新会话。没有重新设计或重复深500层方案。

根端实际集成前须匹配code MF的baseline字节和真实已完成096源码。之后运行新测试与相关093/状态/培养回归及精选；实际项目窗口用独立公开临时档案核对成功保存/重启、拒写、至少可真实构造的IO失败及可见失败信息、有效培养继续计算、完整native/调用方/三文本/原盘与本局隔离。本局优先/数字不应有变化；额外会话字段save_issue是明确的内部状态增量，不可把它宽泛丢弃以掩盖其它差异。

原生Windows、游戏采样、聊天及其它未知机制不由这些SOURCE材料或stdlib探针认证。真实运行结果、失败日志、attempt和归档须由根端fresh执行后记录。
