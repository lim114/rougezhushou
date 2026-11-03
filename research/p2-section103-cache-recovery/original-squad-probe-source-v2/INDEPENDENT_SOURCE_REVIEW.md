# Squad original probe v2：非作者 Source 审阅

结论：在标明的原743维护源码上未发现探针 Source 阻断项。当前工作仓库已由Root推进新RunState91c8a463，固定原743 probe不能直接运行在当前repo；这是必要基线守护生效，不能忽略或偷偷改pin。没有执行项目、native helper/codec、测试、Qt、Wine、OCR或Git；没有改tracked。没有Runtime PASS。

冻结runner：13206 B /99ec44d08551b90bbbb68ce25814c9f57a6191f3636a5fdf9feabf52b4b873c3；fixture-manifest9445 B /00afcd6e4ea531e818cf1422a0a98331b1d12bccfb117f6c36219709220903a2；trusted native6468 B/f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a。17cases、20public JSON文件实际stdlb parse/hash，all manifest bytes/sha一致。原Source run_config e35262ce、固定run-config data d35b0802均当前实读未变；原RunState53169/1b6f66e7从可信99candidate snapshot实读，不假称当前repo还是原743。

## 验证边界与输入

Source全读ef60b4/0、manifest/native合同与两真实消费者7da1c3/0。2c7fb0/1先完成runner AST/compile及文件pins，再在当前repo RunState hash断言失败；97e05e/0诊断仅当前RunState91c8a463不同，run_config/data/helper仍同。502495/0读取原1b6f99snapshot，比较当前/原recognition_context、reset、save、load所用restore funcs的AST相同；apply config subgroup AST也相同。全部fixtures parse检查mandatory operators/relics对象、已接受guard所需squad.name文字及其它空安全container；public fixed squad6 name矛头、trade19/20同name多边贸易确来自JSON档案。fresh记录实际stringID/name合法、effect_verified是bool，1002晚于start1000/last1001。

原list/dict cached ID与健康real/unknownstr/null/integer、missing/null timestamp、invalid run IDs/wrongname短路分别独立；没有把badID自然生产说成真实OCR能力。四个更强恢复控制包含oldbadID[]/boolTrue→fresh badgeFalse、oldhealthyID/boolTrue→samefreshFalse、oldbadID/boolTrue→freshTrue、healthytrade20/boolTrue→fresh19/boolFalse防降级。全是Source假设观察槽，实际结论必须由Root原运行产生。

## 探针行为

只直接RunState及confirmed_config；没有ScreenReader/OCR/Qt函数。cached/fresh/restart三次reuse都在调用前freeze actual state/context/disks，然后在success或记录实际异常后做native caller/state/run+tmp的守恒比较。freshapply caller before/after实际原生等同；合法apply(True)/save的diskphase分开，未假称授权保存后仍是最初磁盘。constructor/restart异常本身及run-file/tmp bytes均保留，未吞作成功。

native记录编号从1递增，遵守f040的positive-int协议，xb写新文件；没有调用该helper来模拟Source通过。freshout/refuse-existing/public-state仅仓库外公开JSON及预存.tmp哨兵；fixture路径basenames、hash、manifest、helper及源guard743+CORE a75d前后都明确保护。120s daemon超时124；product_pass始终False，observation_complete和primary0只能表示探针完成，不是产品通过。所有原不安全消费异常由观察层记真实Trace；Root实际run若有import/probe错误，不能计产品bug。

## Root下一步

1. 指向已有可信原743完整public tree并匹配原guard，或由作者新版本明确绑定当前真实Sourceguard并保留原v2；不能静默改名为743。
2. Root真实执行并保留primary/log/native/public结果，核五类：accepted cached资格/lookup异常、healthy/unused短路、fresh合法保存、oldqualified True保护、badold True恢复是否被阻断。
3. 第103节产品仍须实际完成102基线再精确运输。resource缺value及101/102未知范围不由本probe认证。
