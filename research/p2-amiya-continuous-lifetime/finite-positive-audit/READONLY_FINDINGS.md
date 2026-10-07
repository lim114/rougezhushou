# 连续敌方有限正生命周期：只读审计

冻结基线 `ab1a2f49332e9dbb577eb3ffa1a497c0bb969fa6`，生产分支 `codex/p2-development`。仅本持久目录有审计文件；未编辑 tracked 文件，未访问私人状态、游戏或聊天。

主反例只有两类，均调用公开 `calculate_damage`，使用术师阿米娅 S1、base_attack=1000、continuous、window_seconds=10；其它培养字段沿用公开默认值。

| 反例 | 输入 | 当前结果与报告 |
| --- | --- | --- |
| 有限正敌生命周期 | `timing.target_disappears_seconds=.1`；独立复核 `1` 同样 | 窗口11击/11000，单次技能35000，充能14、周期44/43000；与持续供靶控制完全相同 |
| 有限正供靶范围 | `timing.target_windows=[[0,1]]` | 同样11击/11000、单次35000、充能14、周期44/43000；没有把声明范围用于生成这些 continuous 参考事件 |

两者 `estimate.complete=True`；报告写“支持范围内估算”“观察窗口总伤：11,000”“单次技能总伤：35,000”“预计回转：44.00秒”，情景范围仍称单个持续命中目标。报告尾部说明连续供靶/未模拟前后摇，但没有明确说明这些已填写的有限约束未用于当前数值。问题是按当前输入展示为支持估算；本审计不把报告说成明确声称原生时钟已验证。

另列同一范围反例的数学空源诊断：`target_windows=[]` 在该 continuous 分支仍11000/充能14；已有 life0 控制正确为窗口0/自然充能参数30，初动仍7。不能把“life0已修复”概括成该分支所有空范围已修复。这个诊断不是第三类机制反例。

源事实已复用并逐项核验固定 commit `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add` 两表哈希：S1的真实映射为 `character_table.char_002_amiya.skills[0].skillId = skcom_magic_rage[3]`；`skill_table.skcom_magic_rage[3].levels[9]` 只有攻速+90、30秒持续、SP cost30/init15/自然1。`character_table.char_002_amiya.talents[0].candidates[1]` 明确攻击敌人额外回2SP、消灭敌人回8SP；该场景未推断击倒回技力。原间隔参数1.6秒。它们支持条件攻击数值、SP量和持续参数，不能证明第一击相位、实际获取/释放/命中时刻或目标消失/离范围后的动作与回SP顺序。

已有 `research/p2-empty-enemy-scope/NOTE.md` 明确说明有限正生命周期及非空范围 continuous 是未改变的旧参数参考，真实时钟仍未知；同 receipt 的 timing contract 明写 continuous floor duration 不 consult selectable_lifetime，而且施放后生命周期不会覆盖独立 initial 条件。`p2-phase-guards` 和 `p2-environment-and-lifecycle` 原生绑定验证为false。不是缺少资料后重新猜测机制。

`AttackTimeline.attacks` continuous 的 `.8421…9.2631` 来自 `ready+(i+1)*interval`；即使有 `times_seconds` 字段，也只有人为间隔算例的时间来源。不能拿它直接按 min(life,window) 或均匀比例切成“真实伤害”，也不能据第一个人工时间晚于.1秒就声称实际0。

建议第52先做很窄的护栏：只针对术师阿米娅S1的 continuous 敌向周期来源，在声明有限正生命周期或限制范围会影响当前单次/窗口/后续充能来源时，将对应实际伤害、依赖攻击回SP的实际回转/周期输出保持unknown，并关闭 `estimate.complete`。旧11击、35000、14/44/43000等存入明确的条件参数参考，不作为当前受限情景已建模实际小计；每击1000、攻速/间隔、自然SP rate1、cost30等参数继续显示。空范围单独按数学无攻击来源处理，不能与正范围相位unknown混在一起。

保留施放前初动7的既有独立参考，不以施放后life/range自动取消precast攻击回SP。可保留 cost/rate=30 的无攻击回SP自然充能算术参考，但不要将它当作“实际30秒”：当前敌人消失不证明游戏里没有其它攻击目标或其它来源。受限情景的实际后续回转仍unknown。时序 metadata应表明整段phase未绑定、伤害与资源没有已证实的共享实际时钟；不会建立新的SP事件或更改原自然回复参数。

事件来源要分开：有独立资料明确绑定的事件时刻才按其来源及目标生命周期约束检查；单凭 `times_seconds` 不算绑定。明确即时来源、既有frames动作预览、独立友方治疗及其它技能不应被这个窄guard一并遮蔽。既有frames里的reference_binding/exact_binding字段也不代表原生实测；其当前参考裁剪路径保持。未来扩大范围时，需先记录每个来源属于敌向周期、独立即时、友方，或依赖实际伤害的派生事件。

恢复条件：取得匹配版本的 `skcom_attack_speed_up` 与阿米娅普通攻击获取/释放/命中模板，以及情绪吸收回SP回调和目标消失/离范围顺序的独立证据；再绑定实际事件、闭合充能起点与后续目标来源。原技能黑板、普通动画资源或人工interval算例本身不满足恢复条件。

`audit.py` 只读运行6个公开调用（持续供靶控制、生命周期.1/1、正范围、life0、空范围），确认上述现状及输入不变。`public-reproduction.json`保存完整输入、返回和报告；`source-receipt.json`保存固定资料与来源边界。没有实现草稿或新测试，本审计不声称做过原生/Wine或UI验证。

```bash
cd /workspace/.continuation/p2-after-050/finite-positive-audit
/workspace/rougezhushou/.venv/bin/python audit.py
```
