# Day 14: PCB布局布线 — 主控板 | PCB Layout & Routing — Mainboard

> **今日目标 Today's Goals:**
> - 掌握 PCB 元件放置策略和键盘布局的 19.05mm 间距规则
> - 完成键盘主控板的元件布局（4 层板）
> - 学习电源平面分割、信号走线和 USB 差分对布线
> - 通过 DRC（设计规则检查）
>
> **产出 Deliverable:** 主控板 PCB 布局布线完成 + DRC 通过

---

## 时间安排 | Schedule

| 时间 Time | 活动类型 Type | 内容 Content |
|---|---|---|
| 09:00–09:15 | 晨会 | 回顾 Day 13 子板原理图，答疑 |
| 09:15–10:30 | 讲解 | 元件放置策略 + 键盘布局规则 |
| 10:30–10:45 | 休息 | — |
| 10:45–12:00 | 实验 | 主控板元件放置 |
| 12:00–13:30 | 午休 | — |
| 13:30–15:00 | 实验 | 电源平面 + 信号走线 + USB 差分对 |
| 15:00–15:15 | 休息 | — |
| 15:15–16:30 | 实验 | DRC 检查 + 布线优化 |
| 16:30–17:00 | 总结 | 日终回顾 + 明日预告 |

---

## 上午：元件放置与键盘布局 | Morning: Component Placement & Keyboard Layout

### 为什么要学这个? | Why Learn This?

PCB 布局（Placement）决定了元件的物理位置，直接影响走线难度、信号质量和组装便利性。一个好的布局可以让走线轻松、走线短、干扰小；一个差的布局则会导致走线困难、信号干扰严重、甚至无法完成布线。

PCB placement determines component physical positions, directly impacting routing difficulty, signal quality, and assembly convenience. Good placement makes routing easy, traces short, and interference minimal; poor placement leads to routing nightmares.

---

### 任务 14.1: 元件放置策略 (40 分钟)

**放置原则 Placement Principles:**

```
1. 先大后小 Place Large Components First:
   - 连接器（USB Type-C、磁吸接口）先定位（它们有固定的板边位置）
   - 主控芯片（ESP32-S3 模块）放在中心
   - 电源芯片（TP4056、HX3608、ME6217）放在一起
   - 74HC165 靠近各自负责的按键区域

2. 功能分区 Functional Zoning:
   ┌─────────────────────────────────────────┐
   │  ┌──────┐                    ┌──────┐   │
   │  │USB-C │    74HC165 链       │ 磁吸  │   │
   │  │ 接口  │   (键盘扫描区)      │ 接口  │   │
   │  └──┬───┘                    └──────┘   │
   │     │                                    │
   │  ┌──┴──────────────────────────────┐    │
   │  │  SL2.1A    CH342F   GL823K      │    │
   │  │  (USB Hub 区)                    │    │
   │  └─────────────────────────────────┘    │
   │                                          │
   │         ┌─────────────────┐              │
   │         │   ESP32-S3      │              │
   │         │   (中心区域)     │              │
   │         └────────┬────────┘              │
   │                  │                        │
   │  ┌───────────────┴──────────────┐        │
   │  │ TP4056 → HX3608 → ME6217    │        │
   │  │ (电源区，靠近板边)            │        │
   │  └──────────────────────────────┘        │
   └─────────────────────────────────────────┘

3. 去耦电容紧贴 IC Pin:
   每个 100nF 去耦电容放在 IC 电源引脚旁边（< 3mm）
```

---

### 任务 14.2: 键盘布局 — 19.05mm 间距 (35 分钟)

**19.05mm 规则 The 19.05mm Rule:**

```
机械键盘标准键距 = 0.75 inch = 19.05mm

  ┌────┐  ┌────┐  ┌────┐  ┌────┐
  │ K0 │  │ K1 │  │ K2 │  │ K3 │
  └────┘  └────┘  └────┘  └────┘
  |←19.05→|←19.05→|←19.05→|
     mm      mm      mm

  在嘉立创 EDA 中:
  - 设置网格 Grid = 0.05mm
  - 轴座焊盘中心间距 = 19.05mm (水平) 和 19.05mm (垂直)
  - 建议使用阵列放置工具 (Array Place)
  - 第一个轴座放在原点 (0,0)

  轴座焊盘位置计算:
  Row_i, Col_j 中心坐标:
    X = j × 19.05
    Y = i × 19.05
```

**轴座方向 Orientation:**

```
热插拔轴座焊接面 (Bottom View):

  ┌──────────┐
  │  ○    ○  │  两个焊盘
  │          │
  │          │
  └──────────┘

  重要：所有轴座方向必须一致！
  不然按键手感会不统一
```

---

### 任务 14.3: 主控板元件放置 (75 分钟)

**步骤 Steps:**
1. 设置板框尺寸（参考开源项目的尺寸）
2. 放置 USB Type-C 母座（板边居中）
3. 放置磁吸连接器（板边，与 USB 对侧或同侧）
4. 放置 ESP32-S3 模块（中心区域）
5. 按阵列放置键盘轴座焊盘（19.05mm 间距）
6. 放置 74HC165 芯片（均匀分布在轴座区域旁）
7. 放置电源芯片组（靠近 USB 接口）
8. 放置 USB Hub 芯片组
9. 放置去耦电容、二极管等被动元件

---

## 下午：走线策略与 DRC | Afternoon: Routing Strategy & DRC

### 任务 14.4: 电源平面与信号走线 (60 分钟)

**走线优先级 Routing Priority:**

```
优先级从高到低 Priority (High to Low):

1. USB 差分对 (D+/D-) —— 必须等长、紧耦合、阻抗匹配
2. 电源走线 —— 足够宽，承载电流
3. SPI 信号线 (CLK/MISO/PL) —— 尽量短，避免交叉
4. I2S 信号线 —— 类似 SPI
5. I2C 信号线 —— 速度低，宽容度高
6. GPIO / LED 数据线 —— 最低优先级
```

**电源平面分割 Power Plane Split:**

```
Inner2 (L3): 电源平面

  ┌──────────────────────────────┐
  │ 3V3 区域    │   5V 区域      │
  │ (ME6217 输出)│ (HX3608 输出) │
  │              │               │
  │  覆盖 ESP32  │ 覆盖 WS2812B  │
  │  74HC165     │ USB 外设      │
  │  音频编解码器 │               │
  │              │               │
  └──────────────────────────────┘
       ↑ 分割线尽量窄
       避免信号线跨越分割区！
```

**走线宽度设置 Trace Width Settings:**

| 网络 Net | 线宽 Width | 说明 |
|---|---|---|
| VBUS (5V) | 0.5mm (20mil) | USB 电源 |
| 3V3 | 0.5mm (20mil) | 主电源 |
| GND | 铜皮铺满 | 地平面 |
| USB D+/D- | 0.15mm (6mil) | 差分对 |
| SPI/I2S/I2C | 0.15mm (6mil) | 一般信号 |
| WS2812B DIN | 0.15mm (6mil) | LED 数据 |

---

### 任务 14.5: USB 差分对走线 (30 分钟)

**USB 差分对规则 USB Differential Pair Rules:**

```
规则:
1. D+ 和 D- 必须等长（误差 < 5mil / 0.127mm）
2. D+ 和 D- 必须平行且紧耦合（间距 = 4-6mil）
3. 差分阻抗 = 90Ω ±10%
4. 过孔数量尽量少（每个过孔引入阻抗不连续）
5. 不要在差分对下方走其他信号
6. 差分对下方必须有完整地平面（L2 GND）

  ┌──────┐                    ┌──────┐
  │USB-C │════════════════════│SL2.1A│
  │ D+   │  ──────────────    │ D+1  │
  │ D-   │  ──────────────    │ D-1  │
  └──────┘                    └──────┘
    等长、紧耦合、参考地平面完整

  嘉立创 EDA 差分对设置:
  - Design → Differential Pair Manager
  - 设置 + 和 - 网络的对应关系
  - 设置线宽 6mil，间距 4mil
  - 使用自动等长调节 (Serpentine Tuning)
```

---

### 任务 14.6: DRC 检查与修复 (60 分钟)

**DRC 常见错误 Common DRC Errors:**

| 错误 Error | 含义 Meaning | 修复 Fix |
|---|---|---|
| Clearance violation | 走线/焊盘间距不足 | 调整走线或修改规则 |
| Width violation | 走线宽度不符合规则 | 修改线宽 |
| Unrouted net | 有网络未完成走线 | 补完走线 |
| Silk over pad | 丝印覆盖焊盘 | 移动丝印 |
| Unconnected pad | 焊盘未连接 | 检查网络分配 |

**DRC 规则设置建议 Recommended DRC Rules:**

| 参数 Parameter | 值 Value | 说明 Notes |
|---|---|---|
| 最小线宽 Min Trace Width | 0.15mm (6mil) | 一般信号 |
| 最小间距 Min Clearance | 0.15mm (6mil) | 走线之间 |
| 过孔内径 Via Drill | 0.3mm | 最小钻孔 |
| 过孔外径 Via Diameter | 0.6mm | 含焊环 |
| 阻焊扩展 Solder Mask Expansion | 0.1mm | — |
| 丝印字高 Min Silkscreen Text | 0.8mm | — |

---

## 日终总结 | Daily Wrap-up (16:30-17:00)

**今日关键词 Key Takeaways:**
1. 元件放置遵循"先大后小、功能分区、去耦紧贴"三大原则
2. 键盘轴座间距严格 19.05mm，用阵列放置保证精度
3. USB 差分对必须等长、紧耦合、阻抗匹配 90Ω
4. DRC 检查是交付前的最后一道关卡，0 错误才能下单

---

## 今日作业 | Homework

1. **完成主控板 PCB 布局**：所有元件放置完成，走线完成，DRC 通过
2. **截图提交**：PCB 正面 + 背面 + 3D 预览 + DRC 报告
3. **回答思考题**：
   - 为什么去耦电容必须尽量靠近 IC 的电源引脚？
   - 如果 USB 差分对的 D+ 和 D- 长度差了 2mm，会有什么影响？
   - 为什么信号线不应该跨越电源平面的分割区？

---

## 明日预告 | Tomorrow's Preview

明天我们将完成所有子板的 PCB 布局——旋钮主板（4 层 ENIG）、音频板、接收器板等，并导出全部 12 块 PCB 的 Gerber 文件提交嘉立创打样。

Tomorrow we complete all sub-board PCB layouts — knob mainboard (4-layer ENIG), audio board, receiver board, etc., and export all 12 Gerber files for JLCPCB fabrication.

---

## 参考资源 | References

- 嘉立创设计规则：https://www.jlc.com/portal/vFaq.html
- USB 2.0 走线指南：搜索 "USB 2.0 PCB layout guidelines"
- Saturn PCB Toolkit（阻抗计算）：https://saturnpcb.com/pcb_toolkit/
- B 站搜索 "PCB布局 走线 差分对 教程"
- [不专业教学] 零基础绘制机械键盘 PCB（浚达良）：https://www.bilibili.com/video/BV1vz4y127qL/
- 嘉立创开源硬件平台（参考项目）：https://oshwhub.com/ran-pang/multifunctional-keyboard

---

*最后更新 | Last updated: 2026-05-27*
