# 第102节确认标记消费资格候选（只准备Source）

本目录未应用、未运行，不计完成小节。Root实际原实现七组JSON读取
证明：`inventory_verified='false'`和`[1]`、count0会输出completeTrue；
None输出None、整数1/0保留旧短路行为，原盘字节未变、tmp不存在。
完整真实凭据已原字节复制为root-actual-original-flag-proof.json。

当前RunState三个直接生产位置只写bool；归档公开JSON扫描61个匹配
文件/122个直接字段均为bool。这不能推定私人保存记录、全部历史版本
或游戏native schema。详见source-facts.json和历史扫描JSON。

候选只增加一helper并改三个确认资格消费者，不修改loader、原始flag、
count/删除算式/时间戳/已持有记录/未知字段/原save语义。文字、列表和
字典不能通过truthiness声称已核对；native bool/int/float/None仍进入
原短路表达式，保留None/int0原生输出，整数1仍需原count匹配。
其它numeric边界仅保留旧兼容行为，不宣称已有生产证据。

坏标记读取本身不会触发清洗、迁移、拒绝整份记录或自动保存。原flag和
原盘raw保留；随后合法当前完整读图或明确0可经原producer产生True，
这需要真实证据，不把字符串false解析成布尔值或假设新读取成功。

run_state.baseline.py绑定Root当前Source SHA；candidate/patch只在
仓库外。test_inventory_confirmation_102.py有15个拟议真实RunState API
方法：临时独占JSON、type/float bits、无写盘查询、重启、部分/过时/跨局
读取、正记录/旧确认区分、合法全读与0升级、旧删除和手动reset。
它们只被AST解析，没有执行。CONTRACT.md给完整兼容和实际验证要求。
Root应在实际完成101后重新核对Source guard，再做真实unit/相关回归、
真实MainWindow旧新完整math/3texts/磁盘/caller对照及PNG核验。

原数值缺陷不得为测试通过而随意改游戏机制。本方案不解决其他确认
字段、全部cache schema、实际任务解锁或任何native时钟问题。
项目导入/项目测试/helper/Wine/Git/私有路径读取/tracked修改均为0。
