# Day 13: 外设原理图与多层板概念 | Peripheral Schematics & Multi-layer PCB Concepts

> **今日目标 Today's Goals:**
> - 绘制音频子系统原理图（ES7210 ADC + ES8311 DAC + NS4150B 功放，全配档参考）
> - 理解 I2S 数字音频接口的接线方式
> - 绘制 WS2812B RGB LED 链和磁吸扩展接口
> - 掌握双层 PCB 结构与铺地概念（主线只做双层板）
>
> **产出 Deliverable:** 音频板 + LED 板原理图 + 双层板铺地笔记

---

## 时间安排 | Schedule

| 时间 Time | 活动类型 Type | 内容 Content |
|---|---|---|
| 09:00–09:15 | 晨会 | 回顾 Day 12 主控板原理图，答疑 |
| 09:15–10:30 | 讲解 | 音频子系统架构 + I2S 协议 |
| 10:30–10:45 | 休息 | — |
| 10:45–12:00 | 实验 | 绘制音频电路 + WS2812B 链 |
| 12:00–13:30 | 午休 | — |
| 13:30–15:00 | 实验 | 扩展接口电路 + 子板原理图 |
| 15:00–15:15 | 休息 | — |
| 15:15–16:30 | 实验 | 4 层板概念学习 + 层叠设计笔记 |
| 16:30–17:00 | 总结 | 日终回顾 + 明日预告 |

---

## 上午：音频子系统原理图 | Morning: Audio Subsystem Schematic

### 为什么要学这个? | Why Learn This?

本项目的一大特色是支持语音交互——这需要麦克风阵列采集声音、扬声器播放声音。音频子系统涉及 I2S（数字音频接口）、ADC（模数转换）、DAC（数模转换）和功放（功率放大），是嵌入式系统中非常典型的外设集成案例。

A key feature of this project is voice interaction — requiring microphone arrays for capture and speakers for playback. The audio subsystem involves I2S digital audio, ADC, DAC, and power amplification — a typical embedded peripheral integration case.

---

### 任务 13.1: 音频子系统架构 (40 分钟)

**音频信号链 Audio Signal Chain:**

```
麦克风输入路径 Microphone Input Path:

  麦克风 x2 ──→ ES7210 (ADC) ──→ I2S ──→ ESP32-S3
  (模拟信号)    (模拟→数字)     (数字)    (处理/传输)

  ES7210: 4通道 24bit ADC
  - 2个I2S数据输出通道
  - 可配置采样率: 8kHz ~ 96kHz
  - 内置PGA（可编程增益放大器）
  - I2C 控制接口（地址: 0x40）


扬声器输出路径 Speaker Output Path:

  ESP32-S3 ──→ I2S ──→ ES8311 (DAC) ──→ NS4150B (功放) ──→ 扬声器
  (数字)     (数字)   (数字→模拟)     (模拟放大)      (声音)

  ES8311: 单通道 24bit DAC
  - I2S数据输入通道
  - 内置耳机放大器
  - I2C 控制接口（地址: 0x18）

  NS4150B: 3W D类音频功放
  - 单声道输出
  - 差分输入，桥接推挽输出（BTL）
  - EN 引脚控制开关（节省功耗）
```

---

### 任务 13.2: I2S 接口接线详解 (35 分钟)

**I2S (Inter-IC Sound) 协议 I2S Protocol:**

```
I2S 信号线 I2S Signal Lines:

  BCLK (Bit Clock)     ─┬─→ ES7210 BCLK
                         └─→ ES8311 BCLK
  WS (Word Select)    ──┬─→ ES7210 WS
                        └─→ ES8311 WS
  DOUT (Data Out)     ───→ ES8311 SDIN    (ESP32→DAC)
  DIN (Data In)       ←─── ES7210 SDOUT   (ADC→ESP32)

时序关系 Timing:
        ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐
  BCLK  │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
     ───┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─
        ┌───────────────┐ ┌───────────────┐
  WS    │    左声道 L    │ │    右声道 R    │
     ───┘               └─┘               └──
        ┌─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┐
  DATA  │MSB             LSB│MSB             LSB│
     ───┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┘

  BCLK频率 = 采样率 x 位深度 x 声道数
  例: 16kHz x 16bit x 2 = 512kHz = 0.512MHz
```

**原理图要点 Schematic Notes:**
- ES7210 和 ES8311 共享 BCLK 和 WS 信号线
- 两个编解码器通过不同的 I2C 地址区分（0x40 和 0x18）
- ES7210 的 MIC 输入需要偏置电路（电阻分压提供 Vmic_bias）
- NS4150B 的输出需要 LC 滤波器减少 EMI 辐射

---

### 任务 13.3: 绘制音频电路 (60 分钟)

**步骤 Steps:**
1. 放置 ES7210 符号，连接 I2S、I2C、MIC 输入
2. 放置 ES8311 符号，连接 I2S、I2C、模拟输出
3. 放置 NS4150B 功放，连接 ES8311 输出和扬声器接口
4. 添加麦克风偏置电路（2.2kΩ + 10uF）
5. 添加 NS4150B LC 滤波器（10uH + 1uF）
6. 放置扬声器连接器（JST PH 2.0 或焊盘）

**ES7210 外围元件清单 ES7210 BOM:**
- 1uF 输入耦合电容 x 4（MIC 输入）
- 100nF 去耦电容 x 2
- 10uF VREF 电容 x 1
- 2.2kΩ MIC 偏置电阻 x 2

---

### 任务 13.4: WS2812B RGB LED 链 (15 分钟)

```
WS2812B 级联电路 Cascade Circuit:

  ESP32-S3 ──→ DIN ──→ [WS2812B #1] ──→ DOUT ──→ DIN ──→ [WS2812B #2] ──→ DOUT ──→ ...

  每个 WS2812B:
    VDD ── 5V_STABLE
    GND ── GND
    DIN ── 前一级 DOUT 或 ESP32 数据线
    DOUT ── 下一级 DIN

  在 DIN 信号线上串联一个 330-470Ω 电阻（靠近第一个 LED）
  在 VDD 和 GND 之间并联一个 100nF 去耦电容（每个 LED 一个）
```

---

## 下午：扩展接口与 4 层板概念 | Afternoon: Expansion Ports & 4-Layer Concepts

### 任务 13.5: 磁吸扩展接口电路 (60 分钟)

```
磁吸连接器引脚定义 Magnetic Connector Pinout:

  主板端 (6-pin Pogo Pin):
  ┌─────────────────────────┐
  │ Pin 1: VBUS (5V)         │  电源输出
  │ Pin 2: GND               │  地
  │ Pin 3: I2C_SDA           │  I2C 数据
  │ Pin 4: I2C_SCL           │  I2C 时钟
  │ Pin 5: UART_TX           │  串口发送
  │ Pin 6: UART_RX           │  串口接收
  └─────────────────────────┘

  子板端 (6-pin Pogo Pad):
  ┌─────────────────────────┐
  │ Pin 1: VBUS (5V)         │  电源输入
  │ Pin 2: GND               │  地
  │ Pin 3: I2C_SDA           │  I2C 数据
  │ Pin 4: I2C_SCL           │  I2C 时钟
  │ Pin 5: UART_RX           │  串口接收
  │ Pin 6: UART_TX           │  串口发送
  └─────────────────────────┘

  注意：子板端的 TX/RX 与主板端交叉连接
```

**扩展子板列表 Expansion Board List:**

| 子板 Board | 功能 Function | 通信接口 Interface |
|---|---|---|
| 旋钮主板 Knob Main | FOC 电机 + AS5047P + GC9A01 | SPI + I2C |
| 方向键板 Arrow Key | 4键方向键盘 | GPIO (通过 I2C IO 扩展) |
| LED 灯板 LED Board | 额外 WS2812B 灯珠 | 单线数据 |
| 音频板 Audio Board | 麦克风 + 扬声器 | I2S + I2C |
| 接收器板 Receiver | ESP-NOW 接收器（2.4G 模式） | USB HID |

---

### 任务 13.6: 双层 PCB 结构与铺地概念 (90 分钟)

> **夏令营体验档**：本课程主线只设计 1 块双层主控板，不要求四层板阻抗控制。下面讲双层板够不够用、什么时候才需要上四层。

**双层板 vs 四层板 2-Layer vs 4-Layer:**

| 特性 Feature | 2 层板 2-Layer（本课程主线）| 4 层板 4-Layer（全配档参考）|
|---|---|---|
| 信号完整性 | 一般，走线要绕，底层铺地铜可改善 | 优秀，有完整参考平面 |
| EMI 辐射 | 较大，靠铺地铜缓解 | 内层吸收，辐射小 |
| 电源分配 | 走线供电，压降大 | 完整电源平面，压降小 |
| 成本 | 低（嘉立创约 50 元/5片） | 略高（嘉立创约 100 元/5片） |
| 适用场景 | 简单低速电路（纯键盘主线）| USB Hub/高速信号/射频（全配档）|

**本课程双层板方案 Our 2-Layer Plan:**

```
双层板结构 2-Layer Stackup:

  Top (L1):    元件焊盘 + 信号走线（SPI、I2C、GPIO、USB D+/D-）
  Bottom (L2): 大面积地铜铺铜 + 少量辅助走线 + 电源走线

  板厚: 1.6mm
  铜厚: 1oz (35um)
  阻焊: 绿色/黑色
  表面处理: 无铅喷锡 HASL（学生手焊友好）
```

**铺地铜与电源走线 Ground Pour & Power Routing:**

```
双层板关键做法:
  1. 底层大面积铺地铜 —— 给信号提供回流路径，减少 EMI
  2. 电源走线加粗（0.5mm/20mil 以上）—— 减小压降
  3. 去耦电容贴芯片引脚 1-2mm —— 就近提供瞬时电流
  4. USB D+/D- 等长紧耦合走线 —— 即使双层板也要尽量做

  为什么双层板够用？
  纯键盘主线（按键扫描 + USB HID + 一种无线）信号速度不高、走线不密，
  底层铺地铜 + 粗电源线就能满足。四层板的全配档才有 USB Hub + I2S 音频
  + 多无线同时跑，那时才需要完整地/电源平面和阻抗控制。
```

---

### 任务 13.7: 主线 PCB 进度（精简档）| Main-line PCB Progress (simplified tier)

> 本课程主线只做 1 块双层主控板。下表为全配档的 12 块板参考（主线不要求）。

**主线进度 Main-line Progress:**

| # | 板名 Board | 状态 Status | 层数 Layers |
|---|---|---|---|
| 1 | 主控板 Mainboard（主线必做）| [ ] Day 12 原理图 / Day 14 布局 | 2 |
| — | 其余子板（全配档参考，主线不做）| 选做 | 2-4 |

---

## 日终总结 | Daily Wrap-up (16:30-17:00)

**今日关键词 Key Takeaways:**
1. 音频子系统 = ADC（录音）+ DAC（播放）+ 功放（驱动扬声器）
2. I2S 是数字音频传输标准，BCLK/WS/DATA 三线制
3. WS2812B 级联只需一根数据线，每个 LED 独立寻址
4. 双层板靠底层铺地铜 + 粗电源线就能满足纯键盘主线；四层板留给全配档

---

## 今日作业 | Homework

1. **完成音频板 + LED 板原理图**（全配档参考，主线可只看不做）：ES7210 + ES8311 + NS4150B + WS2812B 链
2. **完成双层板铺地笔记**：记录双层板结构、铺地铜做法、电源走线宽度
3. **回答思考题**：
   - 为什么 ES7210 和 ES8311 可以共享 BCLK 和 WS，但不能共享 DATA 线？
   - WS2812B 数据线上的 330Ω 电阻起什么作用？
   - 本课程主线为什么选双层板而不是四层板？什么情况才值得上四层板？

---

## 明日预告 | Tomorrow's Preview

明天是 PCB 布局布线日——我们将把主控板原理图导入 PCB 编辑器，进行元件放置和走线，重点学习键盘布局的 19.05mm 间距规则、USB 差分对走线和 DRC 检查。

Tomorrow is PCB layout day — importing the mainboard schematic into the PCB editor, placing components, routing traces, with emphasis on 19.05mm key spacing, USB differential pair routing, and DRC checks.

---

## 参考资源 | References

- ES7210 数据手册：搜索 "ES7210 ADC datasheet"
- ES8311 数据手册：搜索 "ES8311 DAC datasheet"
- NS4150B 数据手册：搜索 "NS4150B class-D amplifier datasheet"
- WS2812B 数据手册：https://www.worldsemi.com/
- I2S 协议介绍：https://www.sparkfun.com/datasheets/BreakoutBoards/I2S.pdf
- 嘉立创 4 层板设计教程：搜索 "嘉立创 4层板 阻抗控制 教程"
- Saturn PCB Toolkit（阻抗计算工具）：https://saturnpcb.com/pcb_toolkit/

---

*最后更新 | Last updated: 2026-05-27*
