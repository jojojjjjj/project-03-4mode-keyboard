# 组装步骤 | Assembly Steps

## 概述 | Overview

本项目是一个基于 ESP32-S3 的四模机械键盘（USB / BLE / WiFi / 2.4GHz），由 12 块 PCB 模块组成，外加一个带 FOC 无刷电机旋钮和圆形 LCD 的独立旋钮模块。本文档指导你按正确顺序将所有模块组装为成品。

This project is a 4-mode mechanical keyboard (USB / BLE / WiFi / 2.4GHz) based on ESP32-S3, consisting of 12 PCB modules plus a standalone knob module with a FOC brushless motor and round LCD. This document guides you through assembling all modules into the finished product.

---

## 第零步：组装前检查 | Step 0: Pre-assembly Checklist

在开始任何焊接和组装之前，确认以下所有物料齐全且质量合格：

Before any soldering or assembly, verify all components are present and in good condition:

### 主板组件 | Main Board Components

| 检查项 Item | 规格 Specification | 数量 Qty | 状态 Status |
|---|---|---|---|
| ESP32-S3-WROOM-1 模组 | N16R8 (16MB Flash, 8MB PSRAM) | 1 | [ ] |
| CH342F USB 转串口芯片 | SSOP-20 | 1 | [ ] |
| CH9350 USB HID 芯片 | LQFP-48 | 1 | [ ] |
| GL850G USB HUB 控制器 | LQFP-48 | 1 | [ ] |
| 74HC165 移位寄存器 | DIP-16 / SOIC-16 | 5 | [ ] |
| 74HC138 译码器 | DIP-16 / SOIC-16 | 2 | [ ] |
| AMS1117-3.3 稳压器 | SOT-223 | 2 | [ ] |
| TP4056 锂电池充电 IC | SOP-8 | 1 | [ ] |
| 3.7V 锂电池 | 103040 (1000mAh) | 1 | [ ] |
| USB Type-C 母座 | 16P 全功能 | 2 | [ ] |
| 磁吸连接器 | 5P 磁吸 POGO PIN | 8 组 | [ ] |
| FPC 连接器 | 0.5mm 间距 翻盖式 | 6 | [ ] |

### 子板组件 | Sub-board Components

| 子板 Sub-board | 主要元件 Key Components | 状态 Status |
|---|---|---|
| 音频板 Audio board | ES7210 (ADC) + ES8311 (DAC) + NS4150 (功放) + 麦克风 + 扬声器 | [ ] |
| LED 板 LED boards | WS2812B-2020 (每板若干) | [ ] |
| 磁吸连接器板 Magnetic connector boards | POGO PIN 座 + FPC 座 | [ ] |
| USB 子板 USB sub-board | Type-C 母座 + 保护电路 | [ ] |
| 方向键板 Arrow key board | 热插拔轴座 x 4 + WS2812B | [ ] |

### 旋钮模块组件 | Knob Module Components

| 检查项 Item | 规格 Specification | 数量 Qty | 状态 Status |
|---|---|---|---|
| 旋钮主控板 Knob main PCB | ESP32-S3-MINI-1 | 1 | [ ] |
| 旋钮电池板 Knob battery PCB | 3.7V 602030 锂电池 + TP4056 + DW01A | 1 | [ ] |
| 旋钮屏幕转接板 Screen adapter PCB | GC9A01 圆形 LCD (1.28寸 240x240) 接口 | 1 | [ ] |
| TMC6300 无刷电机驱动 | QFN-20 | 1 | [ ] |
| AS5047P 磁编码器 | TSSOP-14 | 1 | [ ] |
| 应变片传感器 Strain gauge | 350ohm 薄膜式 + HX711 | 2 | [ ] |
| 2204 无刷电机 | 2204 尺寸，内转子 | 1 | [ ] |
| 旋钮外壳 Knob housing | CNC 铝合金 / 3D 打印 | 1 套 | [ ] |

### 接收器组件 | Receiver Components

| 检查项 Item | 规格 Specification | 数量 Qty | 状态 Status |
|---|---|---|---|
| ESP32-S3 接收器板 | ESP32-S3-MINI-1 + CH9350 | 1 | [ ] |
| USB Type-A 公头 | USB 2.0 | 1 | [ ] |

### 通用元件 | Common Components

| 元件 Component | 规格 Specification | 数量 Qty | 状态 Status |
|---|---|---|---|
| 1N4148 二极管 | SOD-123 | 70+ | [ ] |
| 机械轴体 Mechanical switches | 佳达隆 G Pro 3.0 / 适配轴 | 66+ | [ ] |
| 热插拔轴座 Hot-swap sockets | Kailh MX 兼容 | 66+ | [ ] |
| 键帽 Keycaps | 1U / 1.25U / 1.5U / 2U | 66+ 套 | [ ] |
| 0805 电阻电容 | 各常用值 | 若干 | [ ] |

### 工具检查 | Tool Check

| 工具 Tool | 用途 Purpose | 状态 Status |
|---|---|---|
| 烙铁 + 焊台 Soldering iron + station | 焊接所有元件 | [ ] |
| 焊锡丝 Solder wire | 0.8mm 含松香芯 | [ ] |
| 助焊剂 Flux | 辅助焊接贴片元件 | [ ] |
| 万用表 Multimeter | 测量电压/电流/通断 | [ ] |
| 镊子 Tweezers | 放置贴片元件 | [ ] |
| 吸锡带/吸锡器 Desoldering braid/pump | 返工 | [ ] |
| 放大镜/显微镜 Magnifier | 检查焊点质量 | [ ] |
| 热风枪 Hot air station | 返工 QFN/贴片 | [ ] |
| 螺丝刀 Screwdriver set | M2/M2.5/M3 螺丝 | [ ] |
| 杜邦线 Dupont wires | 测试连接 | [ ] |

---

## 第一步：焊接顺序原则 | Step 1: Soldering Order Principles

**核心原则 Core Principle：最低元件先焊，最高元件后焊。**

Solder lowest-profile components first, tallest components last.

```
焊接顺序（从低到高）Soldering Order (low to high):

1. 贴片电阻/电容 (0805)           高度 ~0.5mm
2. 贴片 IC (SOP/SSOP/QFN)         高度 ~1.5mm
3. 贴片二极管 (SOD-123)            高度 ~1.0mm
4. 钽电容 / 电解电容               高度 ~3-5mm
5. 排针 / 排母 / FPC 连接器        高度 ~5-7mm
6. 热插拔轴座                      高度 ~5mm
7. Type-C 母座                     高度 ~3mm
8. 磁吸连接器                      高度 ~5mm
9. ESP32-S3 模组                   高度 ~4mm
10. 机械轴体 (最后安装)            高度 ~12mm
```

**为什么？Why?**
- 低矮元件先焊可以确保 PCB 平稳放置在桌面上
- 先焊高元件会导致 PCB 倾斜，影响后续焊接质量
- QFN 封装（如 TMC6300）需要热风枪，应在其他贴片之后处理

---

## 第二步：键盘主板组装 | Step 2: Keyboard Main Board Assembly

### 2.1 电源子系统 | Power Subsystem

```
焊接顺序 Soldering order:
1. AMS1117-3.3 (x2) — 3.3V 稳压器
2. TP4056 + DW01A — 锂电池充电与保护
3. 电源滤波电容 (100uF 电解 + 100nF 陶瓷)
4. 电源指示 LED + 限流电阻
5. Type-C 母座 (x2) — USB 数据 + 充电

焊接后检查 Post-solder check:
- 万用表蜂鸣档测 VCC 与 GND 是否短路
- 通电测 3.3V 输出是否正常
- Type-C 插入测 VBUS 是否 5V
```

### 2.2 ESP32-S3 主控 | ESP32-S3 MCU

```
焊接顺序 Soldering order:
1. ESP32-S3-WROOM-1 模组（注意方向标记！）
2. 32.768kHz 晶振 + 负载电容 (RTC)
3. Boot 按钮 + EN 复位按钮
4. 自动下载电路 (DTR/RTS 双三极管)
5. Strapping 引脚上拉/下拉电阻

注意 Notes:
- ESP32-S3 模组底部有金属屏蔽罩，不能用手触摸焊盘
- 模组焊好后先不要装天线（如果有外置天线接口）
- Strapping 引脚 (GPIO0, GPIO3, GPIO45, GPIO46) 的上下拉决定启动模式
  - GPIO0 = LOW → USB 下载模式
  - GPIO0 = HIGH → Flash 启动模式
```

### 2.3 USB 子系统 | USB Subsystem

```
焊接顺序 Soldering order:
1. GL850G USB HUB 控制器 — 扩展 USB 端口
2. CH342F USB 转串口 — ESP32-S3 调试/下载
3. CH9350 USB HID — 键盘数据上传到 PC
4. USB 差分对电阻 (22 ohm) + ESD 保护
5. USB HUB 下行端口去耦电容

USB 信号走线注意 USB signal routing notes:
- D+/D- 必须等长等距差分走线
- 差分阻抗 90 ohm
- 远离高速信号 (SPI, I2S)
```

### 2.4 移位寄存器阵列 | Shift Register Array

```
焊接顺序 Soldering order:
1. 74HC165 (x5) — 并行转串行输入，读取按键状态
2. 74HC138 (x2) — 3-8 译码器，选择扫描行/列
3. 去耦电容 (每个 IC 旁 100nF)
4. SPI 总线上拉电阻

链路连接 Daisy-chain connection:
ESP32-S3 SPI → 74HC165 #1 → 74HC165 #2 → ... → 74HC165 #5
                  ↑                                        ↑
               PL (并行加载)                            Q7' (串行输出)

5 片 74HC165 可读取 5 x 8 = 40 个并行输入
2 片 74HC138 可选择最多 16 行/列
```

---

## 第三步：子板组装 | Step 3: Sub-board Assembly

### 3.1 音频板 | Audio Board

```
元件列表 Component list:
- ES7210 (4 通道 ADC, 录音) — TSSOP-24
- ES8311 (2 通道 DAC, 播放) — QFN-20
- NS4150 (D 类功放, 3W) — SOP-8
- MEMS 麦克风 (SPH0645 或 ICS-43434)
- 扬声器 (8ohm 1W, 20mm)
- I2S 滤波电阻电容

焊接顺序 Soldering order:
1. ES7210 + ES8311 (贴片 IC)
2. NS4150 功放
3. MEMS 麦克风
4. 去耦电容和滤波元件
5. FPC 连接器 (连接主板)
6. 扬声器焊接 (最后)

信号流向 Signal flow:
麦克风 → ES7210 (ADC) → I2S → ESP32-S3 → I2S → ES8311 (DAC) → NS4150 → 扬声器
```

### 3.2 LED 板 | LED Boards

```
每块 LED 板的元件:
- WS2812B-2020 灯珠 (小封装)
- 100nF 去耦电容 (每颗灯珠旁)
- FPC 连接器或磁吸连接器

焊接注意 Soldering notes:
- WS2812B-2020 封装极小 (2x2mm)，需要细尖烙铁
- 每颗灯珠方向标记必须一致
- DIN > DOUT 级联方向不能反
- 焊好后逐颗测试颜色是否正常
```

### 3.3 磁吸连接器板 | Magnetic Connector Boards

```
元件:
- 磁吸 POGO PIN 连接器 (5P)
- FPC 连接器 (用于连接其他子板)
- 定位磁铁 (确保极性正确！)

注意事项 Critical notes:
- 磁铁极性必须正确：N 极对 S 极
- POGO PIN 需要一定压缩量（约 0.5-1mm）
- 焊接时不要让助焊剂进入 PIN 孔
```

### 3.4 USB 子板 | USB Sub-board

```
元件:
- USB Type-C 母座 (或 Type-A)
- ESD 保护二极管 (TVS)
- 识别电阻 (CC1/CC2 下拉 5.1k)

注意事项:
- Type-C 母座焊盘易脱落，不要过热
- CC 下拉电阻决定 USB 角色
```

### 3.5 方向键板 | Arrow Key Board

```
元件:
- 4 x 热插拔轴座
- 4 x WS2812B RGB LED
- 4 x 1N4148 二极管
- FPC 连接器

与主板通过 FPC 排线连接
```

---

## 第四步：旋钮模块组装 | Step 4: Knob Module Assembly

### 4.1 旋钮主控板 | Knob Main PCB

```
焊接顺序:
1. ESP32-S3-MINI-1 模组
2. AS5047P 磁编码器 (SPI 接口)
3. TMC6300 无刷电机驱动 (QFN-20，需热风枪)
4. HX711 称重传感器 ADC (读取应变片)
5. SPI Flash (存储 LCD 图像资源)
6. FPC 连接器 (连接屏幕和电池板)

AS5047P 安装注意:
- 安装在电机正下方，中心对准电机轴
- 与磁铁距离 0.5-2mm（参考数据手册）
- SPI 总线需要短且等长

TMC6300 安装注意:
- QFN 封装底部散热焊盘必须焊接
- 输出端连接电机的三根相线 (U/V/W)
- 需要适当的散热设计
```

### 4.2 旋钮电池板 | Knob Battery Board

```
元件:
- TP4056 充电 IC
- DW01A 保护 IC + 8205A MOSFET
- 3.7V 602030 锂电池 (300mAh)
- 磁吸充电触点

焊接注意:
- 电池最后焊接，先焊保护电路
- 电池正负极不能接反！
- 测量保护电路: 过充 4.25V 截止，过放 2.5V 截止
```

### 4.3 屏幕转接板 | Screen Adapter PCB

```
元件:
- GC9A01 圆形 LCD 模组 (1.28寸 240x240)
- FPC 连接器
- 背光驱动电路

安装:
- LCD 模组通过 FPC 连接到转接板
- 转接板通过 FPC 连接到旋钮主控板
- 注意 FPC 方向（金手指朝下/朝上）
```

### 4.4 电机安装 | Motor Installation

```
2204 无刷电机安装步骤:
1. 将电机固定在旋钮外壳底座
2. 电机轴穿过轴承
3. 轴顶端安装径向磁铁 (用于 AS5047P 感应)
4. 轴顶端安装旋钮手柄
5. 三根相线连接到 TMC6300 输出

对齐检查:
- 旋转手柄 360°，确认无摩擦
- AS5047P 读数应为连续的 0-16383
- 应变片安装在旋钮手柄下方，检测按压/侧推力
```

---

## 第五步：接收器组装 | Step 5: Receiver Assembly

```
接收器元件:
- ESP32-S3-MINI-1 (运行 ESP-NOW / 2.4GHz 接收)
- CH9350 USB HID 芯片
- USB Type-A 公头
- 状态指示 LED

焊接顺序:
1. ESP32-S3-MINI-1
2. CH9350
3. USB Type-A 公头
4. LED + 电阻
5. 去耦电容

注意:
- Type-A 公头焊盘较大，需要较多焊锡
- 接收器外壳需要小巧（类似 U 盾大小）
```

---

## 第六步：板间互连 | Step 6: Inter-board Connection

### 6.1 FPC 排线连接 | FPC Cable Connections

```
FPC 排线列表 FPC cable list:

1. 主板 ↔ 音频板 (I2S + I2C 控制)          0.5mm 10P
2. 主板 ↔ LED 板 #1 (WS2812B 数据)          0.5mm 4P
3. 主板 ↔ LED 板 #2                          0.5mm 4P
4. 主板 ↔ 方向键板 (矩阵 + LED)              0.5mm 10P
5. 主板 ↔ USB 子板                            0.5mm 6P
6. 旋钮主控板 ↔ 屏幕转接板 (SPI)             0.5mm 10P

FPC 连接器操作:
1. 翻开连接器锁扣
2. 插入 FPC 排线（金手指面朝接触点）
3. 按下锁扣固定
4. 轻拉排线确认已锁紧
```

### 6.2 磁吸连接器对接 | Magnetic Connector Mating

```
磁吸连接器配对 Magnetic connector pairs:

1. 键盘主板 ←→ 音频板
2. 键盘主板 ←→ LED 板 (左右各一个)
3. 键盘主板 ←→ USB 子板
4. 旋钮模块 ←→ 旋钮充电底座

对接步骤:
1. 确认磁铁极性正确 (会自动吸附)
2. 对准定位柱
3. 轻轻靠近，让磁力引导对齐
4. 检查 POGO PIN 是否全部接触
```

---

## 第七步：轴体和键帽安装 | Step 7: Switch and Keycap Installation

### 7.1 安装轴体 | Install Switches

```
操作步骤:
1. 检查轴体引脚是否弯曲 — 弯曲的引脚用镊子矫正
2. 对准轴座：金属引脚对准轴座的两个金属夹片
3. 定位柱对准轴座中心孔
4. 均匀用力按下，听到"咔嗒"声表示到位
5. 先安装 4-5 个轴体进行测试，确认全部触发后再装全部

安装顺序:
- 先安装 PCB 四角的轴体（对角定位）
- 再安装边缘轴体
- 最后安装中间轴体
```

### 7.2 安装键帽 | Install Keycaps

```
操作步骤:
1. 将键帽对准轴体顶部的十字柱
2. 均匀用力按下
3. 确认高度一致，无倾斜

注意:
- 不同行可能使用不同高度的键帽 (R1-R4 profile)
- 空格键等大键需要平衡杆或卫星轴
```

---

## 第八步：外壳组装 | Step 8: Case Assembly

### 8.1 键盘外壳 | Keyboard Case

```
3D 打印外壳结构:
┌──────────────────────────────────────┐
│  上盖 Top plate (switch plate)        │
│  ┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐...       │
│  │  ││  ││  ││  ││  ││  │          │ ← 轴体开口
│  └──┘└──┘└──┘└──┘└──┘└──┘          │
│                                      │
│  定位板 Positioning plate            │
│  ┌──────────────────────────┐       │
│  │     PCB 组装体            │       │
│  │  [ESP32-S3] [USB Hub]    │       │
│  │  [74HC165] [74HC138]     │       │
│  │  [Audio]   [Power]       │       │
│  └──────────────────────────┘       │
│                                      │
│  底壳 Bottom case                    │
│  ┌──────────────────────────┐       │
│  │  电池仓 / 配重           │       │
│  │  [锂电池]                │       │
│  └──────────────────────────┘       │
└──────────────────────────────────────┘
     ○                      ○          ← 防滑硅胶垫
```

### 8.2 旋钮外壳 | Knob Housing

```
旋钮外壳结构:
┌────────────────┐
│  旋钮手柄        │ ← 铝合金 / ABS
│  ┌──────────┐  │
│  │ 磁铁      │  │ ← AS5047P 感应
│  │ [电机轴]  │  │
│  └────┬─────┘  │
│       │         │
│  ┌────┴─────┐  │
│  │ 2204 电机 │  │ ← 无刷电机
│  └──────────┘  │
│  ┌──────────┐  │
│  │GC9A01 LCD│  │ ← 圆形屏幕
│  └──────────┘  │
│  ┌──────────┐  │
│  │ ESP32-S3 │  │ ← 旋钮主控
│  │ TMC6300  │  │
│  │ AS5047P  │  │
│  └──────────┘  │
│  ┌──────────┐  │
│  │  电池    │  │ ← 锂电池
│  └──────────┘  │
└────────────────┘
     ○     ○       ← 磁吸充电底座触点
```

---

## 第九步：初次通电测试 | Step 9: Initial Power-on Test

### 9.1 测试前准备 | Pre-test Preparation

```
⚠️ 重要：通电前必须完成的检查 Important pre-power checks:

1. 万用表蜂鸣档测量 VCC 与 GND — 必须不短路
2. 目视检查所有 IC 方向是否正确
3. 确认没有焊锡桥连
4. 确认所有 FPC 排线已正确插入
5. 确认电池正负极正确
6. 断开所有子板，先单独测主板
```

### 9.2 分步测试流程 | Step-by-step Test Procedure

```
步骤 1: 主板电源测试
  - USB-C 供电
  - 测量 3.3V 电源轨 → 应为 3.25-3.35V
  - 测量电流 → 待机应 < 100mA
  - LED 指示灯是否亮

步骤 2: ESP32-S3 启动测试
  - 按住 BOOT 键，按 EN 键，松开 BOOT
  - 电脑应识别到 USB 串口设备
  - 使用 esptool.py 或 ESP IDF Flash Tool 验证连接
  - 刷入测试固件

步骤 3: USB HUB 测试
  - 电脑设备管理器应显示 USB HUB
  - HUB 下行端口应可见

步骤 4: 逐个子板连接测试
  - 连接音频板 → 测量 I2C 是否通信
  - 连接 LED 板 → 验证 WS2812B 是否可控
  - 连接方向键板 → 扫描矩阵是否正常
  - 连接 USB 子板 → 验证枚举

步骤 5: 旋钮模块独立测试
  - 旋钮模块单独供电
  - 验证 ESP32-S3 启动
  - 验证 AS5047P 角度读数
  - 验证 LCD 显示
  - 验证电机转动（低电流）
  - 验证应变片响应

步骤 6: 无线连接测试
  - BLE 模式：手机搜索蓝牙设备
  - WiFi 模式：连接路由器
  - 2.4GHz 模式：接收器配对

步骤 7: 整机联调
  - 所有模式切换测试
  - 全键扫描测试
  - RGB 灯效测试
  - 音频输入/输出测试
  - 旋钮力度反馈测试
```

---

## 第十步：常见组装错误与修复 | Step 10: Common Assembly Mistakes and Fixes

| 错误 Mistake | 症状 Symptom | 原因 Cause | 修复 Fix |
|---|---|---|---|
| ESP32-S3 方向焊反 | 无法启动，电流异常 | 模组方向标记没对齐 | 用热风枪拆除重新焊接 |
| 74HC165 链路断开 | 部分按键无响应 | Q7' 到下一片 SER 未连接 | 检查并补焊链路线 |
| FPC 排线插反 | 子板不工作 | 金手指面朝向错误 | 翻转排线重新插入 |
| 磁铁极性装反 | 子板无法吸附对齐 | N-N 或 S-S 同极相斥 | 拆除磁铁，翻转极性 |
| WS2812B 方向反 | LED 不亮或全部颜色错 | DIN/DOUT 接反 | 检查方向标记，必要时补焊 |
| 电池极性反 | 保护电路动作或损坏 | 红线接负极 | 立即断开，检查保护 IC |
| TMC6300 散热不良 | 电机抖动或驱动过热 | 底部焊盘未焊 | 重新加热底部焊盘 |
| Type-C 焊盘脱落 | USB 不工作 | 过热或暴力拔插 | 飞线到附近焊盘 |
| CH9350 不识别 | 键盘数据无法上传 | HID 描述符配置错误 | 检查固件配置 |
| AS5047P 角度跳变 | 旋钮位置读数不稳 | 磁铁距离太远/太近 | 调整磁铁高度到 1-1.5mm |

---

## 组装时间估算 | Assembly Time Estimate

| 步骤 Step | 预计时间 Estimated Time |
|---|---|
| 主板焊接 Main board soldering | 3-4 小时 |
| 子板焊接 Sub-board soldering | 2-3 小时 |
| 旋钮模块焊接 Knob module soldering | 2-3 小时 |
| 接收器焊接 Receiver soldering | 30 分钟 |
| 板间互连 Inter-board connection | 1 小时 |
| 轴体/键帽安装 Switch/keycap install | 1 小时 |
| 外壳组装 Case assembly | 1 小时 |
| 测试与调试 Testing & debugging | 2-4 小时 |
| **总计 Total** | **~12-18 小时** |

---

*最后更新 | Last updated: 2026-05-27*
