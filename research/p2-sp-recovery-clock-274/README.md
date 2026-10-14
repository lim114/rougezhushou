# 第274节：自然技力的批量计时器与独立恢复请求

候选本机原件为DLL SHA256 583b04ff4d1b1a4b35eaf09d77d936408c25447c9e345ef0463d814b6a123fc5、metadata SHA256 d3fede171f92740a6f5dc053c58c7013d3c962db764ad1f05cbe977c074fcd1f。source-proof.json完整保留50方法、2252条唯一可达指令、9731指令字节和3518个原字节span。本节对13份准备来源、两原件完整SHA和每段原字节独立重读；没有执行DLL或读取进程内存。准备束内cache路径是原始来源索引，产品只依赖manifest绑定的公开原件。Reset/UpdateSpData等上层代码只作研究保留，不因此宣称其真实生命周期已实现。

SpController.m_spRecoverTimer声明类型为PrecisePeriodicTimer。普通OnTick依次检查spType bit1、timer存在与有效、owner存在及首次spStopped、独立isFull。未开启、旧周期不严格大于EPS=42950、暂停或满技力时不减剩余。isFull的普通实现是独立SP与Int32(maxSP)*ONE的直接signed比较，不套EPS；本节接收独立getter结果及正常资格，未由后续恢复SP读点代用这个布尔值。

UpdateMultiple先写wrap(R-delta)。新R严格小于EPS时，原生UnaryNegation(R)作为分子除以P，再FloorToInt，max(0,floor)+1以signed32 inc回绕。UnaryNegation对MIN64返回FP.MaxValue=9223372036854775806，不能简单wrap(-MIN64)。Floor是遮去低32位，AsInt是算术右移32后eax返回，不走float/CVTT。INT_MAX取整后加1会得到INT_MIN；OnTick count<=0时不Next、不恢复，但已经写出的R保留。

一般除法仅核准abs(A)*ONE <= abs(B)*FP.MaxValue的无溢出子域，B!=0；原额外一位商与最终加1再右移，按绝对值half-up得qraw，符号独立恢复。B=0的原码返回-ONE。域外数值或未读数值保持未知，不虚构饱和结果或异常。此子域比272仅ONE/非微小率的保守范围更广，不能以EPS过滤所有微小率。P=2*ONE、R=0、delta=2*ONE-1时qraw由ONE-0.5舍入到ONE，count=2，Next后的R=2*ONE+1；采用float或直接对实数floor会少算一批。

正count先NextMultiple：独立ready检查通过后写wrap(R+FPmul(P,Int32ToFP(count)))。OnTick不依据该函数返回bool作分支。在已声明无其它timer变化与Precise身份下，两次ready见同一个R。随后_RecoverMp(force=false)重新读取spStopped；若停，timer已经推进但没有SP请求。否则一次独立get_sp，再请求set_sp(wrap(SP+count*ONE))，不模拟count次逐点getter。显式force恢复跳过第二暂停读取，但仍访问独立SP及setter；零和负量不强行改成正量。写入参数不当作实际SP或下一次SP读值。

UpdateSpRecoveryPerSec(newValue,oldValue)普通码使用独立newValue，未使用oldValue。旧timer有效时先OnTick(0)，正常后再独立canRecoverSp；后者读取属性14×30并严格比较rate>EPS。资格false才MarkInvalid(-ONE,-ONE)，true用ONE/newValue与ResetButKeepPastTime：past=wrap(oldP-currentR)，newR=max(0,wrap(newP-past))。旧timer无效时直接Reset(ONE/newValue,true)，P/R都为新周期，不读取canRecoverSp，也不复用其率替代传入参数。未脏或真实缓存取得14/30不在本节推导。

typed暂停、force、读取正常或对象存在资格的未知值分别按原生两支求值，只有各支相同的参考值合流。确定未调用为false，条件可能调用为null；owner为空在get_sp调用之前进入异常，不能称getter已经被call。正常资格在两个分支都true时可以闭合，但请求次数仍可能0/1，此时完整请求数未知。改速drain未知正常仍可能继续重置，最终P/R未知；已发生的Next与R作为drain前缀保留。未知hotfix普通路径不展开成假想逻辑，最终值保持未知。

公共输入示例P=ONE/4、R=ONE/8、delta=7*ONE/8，得到count4和Next后R=ONE/4，独立SP=5*ONE的setter参数9*ONE。第二次delta=ONE/4后重新暂停，无SP访问，但R仍ONE/4。显式force负2*ONE，另一个独立SP=9*ONE得到参数7*ONE；两个写入请求不证明最终SP=7。原准备束的SP9→13是另一独立算例，原字节保留不改写。

实际属性、时钟、SP接受、完整回复、技能初动/回转与周期保持未知。本节只做局外独立声明参考，不采集/操作游戏或发聊天。源审查原8组探针、原代码、追加资格反例、首轮产品失败及后续测试预期错误均另存verification/sections/274-*；来源归档首次offset字符串处理失败的控制台原全文未保存，原生成代码和随后同源失败复现日志分别保留，不冒称首次原日志。
