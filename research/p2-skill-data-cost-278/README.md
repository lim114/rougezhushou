#278缓存准备：技能费用的逐次数据修饰与更新

主API skill_data_cost_reference(payload)严格绑定原32方法3145独立指令4034fresh byte spans及manifest。仅成本5kind进入此次草案；四槽初始化原件保留为后继，不冒称已实现。

CSkillCdMul/Add的名称不是实际回复率计算：源中改变的是spCost，按每个独立decoded读点先Int32转Single，再mul/add、half-even round、编码及20byte写。root当前游戏RC/FTZ/DAZ/exception masks未证，草案仅exact Single安全域给数字。10×0x3d4ccccd以及16777217转换例保留unknown。25×0.5→12、23×0.5→12、−23×0.5→−12；没有夹成零。

SpScale为独立Int32 m_scale的low32乘法，MIN32×−1仍MIN32，并在正常写之后独立owner/data2读取，再调用UpdateSpData(onlycost=true)。replacement先编码后firstSpData-null检查；modifySpType=true会写type并使onlycost=false；三个data、两个owner快照不能复用。

public.independent_next_decode声明101，该读点不会继承前一步编码入参12。所有写入只保留opaque20byte payload和编码入参，不输出修改后实际decoded费用。当前SP、真实完整技能周期和时钟一律unknown；void update没有虚构Boolean返回。

普通分支、对象存在、读点normal和值分别资格。unknown未来called=null，只有源支路证明不调用才false。null deferred owner仍先执行后续data getter，不提前漏掉前缀。原始准备错误标签与修证并存；原件、独立审计和当前草案不互相覆盖。

CPU Single/RC原证：[Intel SDM Volume1 December2024](https://cdrdv2-public.intel.com/843827/253665-sdm-vol-1-dec-24.pdf)。它证明指令资格，不证明游戏当前环境。raw round helper地址0x18059e290的metadata身份未闭合；不得称为另一码表地址上的Mathf.RoundToInt。
