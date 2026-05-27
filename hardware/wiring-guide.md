# 接线指南 | Wiring Guide

## 四模机械键盘 — 承载我所有幻想的键盘
## 4-Mode Mechanical Keyboard — The Keyboard of All My Fantasies

> 本文档提供完整接线指南，覆盖键盘主板、旋钮模块、接收器三大子系统。
> This document provides the complete wiring guide covering three subsystems: keyboard mainboard, knob module, and receiver.

---

## 一、ESP32-S3 引脚分配 | ESP32-S3 Pin Assignment (Keyboard Main Board)

### 主控引脚总览 | MCU Pin Overview

ESP32-S3-WROOM-1 共有 45 个可用 GPIO（GPIO0~GPIO48），部分引脚有特殊用途或限制。

```
                      ESP32-S3-WROOM-1-N16R8
                    ┌────────────────────────────┐
                    │                            │
         (USB-DM) ──│ GPIO20          GPIO19 │── (USB-DP)
         (STRAP)  ──│ GPIO0           GPIO1  │── (STRAP)
         (STRAP)  ──│ GPIO3           GPIO2  │── (STRAP)
         (JTAG)   ──│ GPIO39          GPIO40 │── (JTAG)
         (JTAG)   ──│ GPIO42          GPIO41 │── (JTAG)
         (SPICLK) ──│ GPIO7           GPIO8  │── (SPIQ/MISO)
         (SPID/MOSI)─│ GPIO11          GPIO9  │── (SPIHD)
         (SPICS)  ──│ GPIO10          GPIO12  │
         (UART RX)──│ GPIO44          GPIO43 │── (UART TX)
                    │  (USB_D-)       (USB_D+)│
                    │   [内置 USB PHY]        │
                    └────────────────────────────┘

        左侧: GPIO 0-3 (启动配置), 4-6 (可用),
              7-12 (SPI), 13-18 (可用),
              19-20 (USB PHY), 21 (可用)
              26-32 (可用), 33-34 (仅输出)
              35-42 (JTAG/SPI), 43-44 (UART),
              45-48 (可用)
```

### 功能引脚分配表 | Function Pin Assignment Table

| ESP32-S3 GPIO | 功能 Function | 方向 Direction | 连接目标 Target | 备注 Notes |
|---|---|---|---|---|
| GPIO0 | STRAP (Boot) | — | Boot 按钮 | 启动时必须为高电平 |
| GPIO3 | STRAP (JTAG) | — | 预留 | 启动时必须为高电平 |
| GPIO4 | I2S_MCLK | Output | ES7210 MCLK / ES8311 MCLK | 音频主时钟 |
| GPIO5 | I2S_BCLK | Output | ES7210 BCLK / ES8311 BCLK | I2S 位时钟 |
| GPIO6 | I2S_WS (LRCK) | Output | ES7210 WS / ES8311 WS | I2S 字选择 |
| GPIO7 | SPI_CLK | Output | 74HC165 SCLK (级联时钟) | 移位寄存器 SPI 时钟 |
| GPIO8 | SPI_MISO (Q) | Input | 74HC165 Q7 (串行输出) | 读取移位寄存器数据 |
| GPIO9 | SPI_HD | — | 预留 | |
| GPIO10 | SPI_CS | Output | 74HC165 CE (芯片使能) | 低有效 |
| GPIO11 | SPI_MOSI (D) | Output | 74HC165 SER (串行输入) | 加载模式控制 |
| GPIO12 | PL (Parallel Load) | Output | 74HC165 PL (并行加载) | 低有效，锁存按键状态 |
| GPIO13 | I2S_DOUT (数据入) | Input | ES7210 SDOUT | I2S ADC 数据输入 (录音) |
| GPIO14 | I2S_DIN (数据出) | Output | ES8311 DIN | I2S DAC 数据输出 (播放) |
| GPIO15 | I2C_SDA | Bidirectional | ES7210 SDA / ES8311 SDA / OLED SDA | I2C 数据线，需 4.7k 上拉 |
| GPIO16 | I2C_SCL | Output | ES7210 SCL / ES8311 SCL / OLED SCL | I2C 时钟线，需 4.7k 上拉 |
| GPIO17 | WS2812B DIN | Output | WS2812B #1 DIN | RGB 灯珠数据线 |
| GPIO18 | USB_SEL | Output | 模拟开关 U6/U7 (控制信号) | USB 路径切换 |
| GPIO19 | USB_DP (内置) | Bidirectional | SL2.1A HUB 上行口 | ESP32-S3 内置 USB PHY |
| GPIO20 | USB_DM (内置) | Bidirectional | SL2.1A HUB 上行口 | ESP32-S3 内置 USB PHY |
| GPIO21 | DETECT_MAGNETIC | Input | 磁吸接口检测脚 | 检测旋钮是否连接 |
| GPIO26 | UART0_TX | Output | CH342F CH1 RX | 固件下载 / 调试串口 |
| GPIO27 | UART0_RX | Input | CH342F CH1 TX | 固件下载 / 调试串口 |
| GPIO28 | KNOB_UART_TX | Output | CH342F CH2 RX | 旋钮主控下载口 |
| GPIO29 | KNOB_UART_RX | Input | CH342F CH2 TX | 旋钮主控下载口 |
| GPIO33 | EXP_IIC_SDA | Bidirectional | 扩展接口 I2C SDA | 磁吸扩展 I2C (经保护电路) |
| GPIO34 | EXP_IIC_SCL | Output | 扩展接口 I2C SCL | 磁吸扩展 I2C (经保护电路) |
| GPIO35 | GPIO_EXT | Bidirectional | 扩展接口 GPIO | 磁吸扩展通用 IO |
| GPIO36 | HUB_RESET | Output | SL2.1A RESET | USB HUB 复位 |
| GPIO37 | LED_BAR_CLK | Output | 横流 LED 灯条 (格栅灯) | 后灯板控制 |
| GPIO38 | LED_BAR_DAT | Output | 横流 LED 灯条 (格栅灯) | 后灯板控制 |
| GPIO43 | UART_TX (默认) | Output | 预留调试 | USB-CDC 或 UART |
| GPIO44 | UART_RX (默认) | Input | 预留调试 | USB-CDC 或 UART |
| GPIO45 | STRAP | — | 预留 | 启动配置 |
| GPIO46 | STRAP | — | 预留 | 启动配置 |
| GPIO47 | JOY_X | Input (ADC) | 模拟摇杆 X 轴 | ADC 模拟输入 |
| GPIO48 | JOY_Y | Input (ADC) | 模拟摇杆 Y 轴 | ADC 模拟输入 |

> **重要 Notes:**
> - GPIO0, 3, 45, 46 为 STRAP 引脚，上电时决定启动模式，不可随意上拉/下拉。
> - GPIO19/20 连接 ESP32-S3 内置 USB PHY，无需外部晶振。
> - GPIO33-34 为仅输出引脚，不可用作中断输入。

---

## 二、74HC165 移位寄存器级联接线 | Shift Register Daisy-Chain Wiring

### 原理说明 | Principle

75 键使用 10 片 74HC165 级联。每片 74HC165 提供 8 个并行输入，10 片 = 80 个输入（75 键 + 5 个预留）。所有芯片共享时钟和数据线，串行数据首尾相连。

75 keys use 10x 74HC165 daisy-chained. Each chip provides 8 parallel inputs: 10 chips = 80 inputs (75 keys + 5 reserved). All chips share clock and data lines; serial data is chained end-to-end.

### 级联接线图 | Daisy-Chain Diagram

```
                    ESP32-S3
                        │
    ┌───────────────────┼───────────────────────────────┐
    │                   │                               │
    │  GPIO7 (SCLK) ────┤──── SCLK ── 所有 74HC165 CLK  │
    │  GPIO10 (CS)  ────┤──── CE   ── 所有 74HC165 CE   │
    │  GPIO12 (PL)  ────┤──── PL   ── 所有 74HC165 PL   │
    │                   │                               │
    │  GPIO11 (SER) ────┤── SER ← 74HC165 #10 D7        │
    │                   │    (加载模式时数据入口)          │
    │  GPIO8  (Q7)  ←───┤── Q7  ← 74HC165 #1  Q7_OUT   │
    │                   │                               │
    └───────────────────┼───────────────────────────────┘
                        │
    数据流向 Data Flow:

    GPIO8 ←── [HC165 #1].Q7_OUT ←── [HC165 #2].Q7_OUT ←── ... ←── [HC165 #10].Q7_OUT
                (按键 0-7)              (按键 8-15)              (按键 72-79)
```

### 单片 74HC165 接线表 | Single 74HC165 Pin Wiring

| 74HC165 引脚 | 名称 Name | 连接目标 Connection | 说明 Notes |
|---|---|---|---|
| Pin 1 (PL) | 并行加载 | GPIO12 (所有芯片共用) | 低电平时锁存并行输入 |
| Pin 2 (CP) | 时钟 | GPIO7 (所有芯片共用) | 上升沿移位 |
| Pin 6 (D4) | 并行输入 4 | 按键开关 → GND | 经热插拔轴座 |
| Pin 7 (Q7) | 串行输出 | 下一级 SER (或 ESP32 GPIO8) | 级联数据输出 |
| Pin 8 (GND) | 地 | GND | |
| Pin 9 (Q7) | 互补输出 | 不接 (NC) | |
| Pin 10 (DS) | 串行输入 | 上一级 Q7 (第一片接 GPIO11) | 级联数据输入 |
| Pin 11 (D6) | 并行输入 6 | 按键开关 → GND | |
| Pin 12-15 | D5,D3,D2,D1 | 按键开关 → GND | |
| Pin 15 (CE) | 芯片使能 | GPIO10 (所有芯片共用) | 低有效 |
| Pin 16 (VCC) | 电源 | 3.3V | |

### 按键扫描时序 | Key Scanning Timing

```
步骤1: PL = LOW  (锁存所有并行输入)
        ↓
步骤2: PL = HIGH (结束锁存)
        ↓
步骤3: CS = LOW  (使能输出)
        ↓
步骤4: 发送 80 个 SCLK 脉冲，每个上升沿读取 GPIO8 状态
        → 第 1 个脉冲后读到 HC165 #1 的 D0
        → 第 2 个脉冲后读到 HC165 #1 的 D1
        → ...
        → 第 8 个脉冲后读到 HC165 #1 的 D7
        → 第 9 个脉冲后读到 HC165 #2 的 D0
        → ... 共 80 位
        ↓
步骤5: CS = HIGH (禁用输出)
```

---

## 三、I2C 总线接线 | I2C Bus Wiring

### 总线拓扑 | Bus Topology

```
ESP32-S3 (Master)
    │
    ├── GPIO15 (SDA) ────+──── 4.7k 上拉到 3.3V
    │                     │
    │                     ├── ES7210 (ADC) ──── I2C Address: 0x40
    │                     │
    │                     ├── ES8311 (DAC) ──── I2C Address: 0x18
    │                     │
    │                     └── SSD1306 OLED ─── I2C Address: 0x3C
    │
    ├── GPIO16 (SCL) ────+──── 4.7k 上拉到 3.3V
                          │
                          └── (所有设备共用 SCL)
```

### 接线表 | Wiring Table

| ESP32-S3 GPIO | 信号 Signal | 连接目标 Devices | 上拉电阻 Pull-up | 说明 Notes |
|---|---|---|---|---|
| GPIO15 | I2C_SDA | ES7210 SDA, ES8311 SDA, OLED SDA | 4.7k 到 3.3V | 双向数据线 |
| GPIO16 | I2C_SCL | ES7210 SCL, ES8311 SCL, OLED SCL | 4.7k 到 3.3V | 时钟线 |
| 3.3V | VCC | 所有 I2C 设备 VCC | — | |
| GND | GND | 所有 I2C 设备 GND | — | |

> **说明 Notes:**
> - I2C 总线为共享总线，3 个设备并联在同一组 SDA/SCL 上，靠不同地址区分。
> - 上拉电阻必须靠近主控端放置。
> - ES7210 和 ES8311 同时用于 I2C 控制（配置寄存器）和 I2S 数据传输。

---

## 四、I2S 音频总线接线 | I2S Audio Bus Wiring

### 音频信号链 | Audio Signal Chain

```
录音路径 Recording Path:

MEMS 麦克风 x2 ──(模拟音频)──→ ES7210 (ADC)
                                     │
                                     │ I2S 数字音频 (4 线)
                                     ↓
                                  ESP32-S3 (I2S 控制器)
                                     │
                                     │ 数字处理 (降噪/编码)
                                     ↓
                                  WiFi/BT/ESP-NOW 发送

播放路径 Playback Path:

ESP32-S3 ←── WiFi/BT/ESP-NOW 接收
    │
    │ I2S 数字音频
    ↓
ES8311 (DAC) ──(模拟音频)──→ NS4150B #1 (功放) ──→ 扬声器 L
                          ──→ NS4150B #2 (功放) ──→ 扬声器 R
```

### I2S 接线表 | I2S Wiring Table

| ESP32-S3 GPIO | I2S 信号 Signal | 方向 Direction | 连接目标 Target | 说明 Notes |
|---|---|---|---|---|
| GPIO4 | I2S_MCLK | Output | ES7210 MCLK, ES8311 MCLK | 音频主时钟 (256×fs) |
| GPIO5 | I2S_BCLK | Output | ES7210 BCLK, ES8311 BCLK | 位时钟 |
| GPIO6 | I2S_WS (LRCK) | Output | ES7210 WS, ES8311 WS | 左右声道选择 |
| GPIO13 | I2S_DIN (数据入) | Input | ES7210 DOUT | ADC 录音数据 |
| GPIO14 | I2S_DOUT (数据出) | Output | ES8311 DIN | DAC 播放数据 |

### ES7210 (ADC) 外围接线 | ES7210 Peripheral Wiring

```
                    ES7210
              ┌───────────────┐
  MIC1+  ────│ MIC1P         │
  MIC1-  ────│ MIC1N         │
  MIC2+  ────│ MIC2P    SDA │──── GPIO15 (I2C)
  MIC2-  ────│ MIC2N    SCL │──── GPIO16 (I2C)
              │          MCLK│──── GPIO4  (I2S_MCLK)
              │          BCLK│──── GPIO5  (I2S_BCLK)
              │            WS│──── GPIO6  (I2S_WS)
              │        DOUT │──── GPIO13 (I2S_DIN)
              │               │
              │          VCC │──── 3.3V
              │          GND │──── GND
              └───────────────┘

  MEMS 麦克风 → 耦合电容 (1uF) → ES7210 MIC 输入
```

### ES8311 (DAC) + NS4150B (功放) 接线 | ES8311 + NS4150B Wiring

```
                    ES8311
              ┌───────────────┐
              │          SDA │──── GPIO15 (I2C)
              │          SCL │──── GPIO16 (I2C)
              │          MCLK│──── GPIO4  (I2S_MCLK)
              │          BCLK│──── GPIO5  (I2S_BCLK)
              │            WS│──── GPIO6  (I2S_WS)
              │           DIN│──── GPIO14 (I2S_DOUT)
              │               │
              │        DOUTL │──┐
              │        DOUTR │──┤
              └───────────────┘  │
                                 │ 模拟音频 (RC 滤波)
                                 ↓
              ┌───────────────┐
              │  NS4150B #1  │──→ 扬声器 L (8 ohm)
              │  NS4150B #2  │──→ 扬声器 R (8 ohm)
              └───────────────┘
              所有 NS4150B:
              VCC ← 5V (USB 或电池升压)
              GND ← GND
              IN  ← ES8311 输出 (经 RC 低通滤波)
```

> **说明 Notes:**
> - I2S_MCLK 为可选信号，ESP32-S3 可通过 APB_CLK 分频产生。ES7210 和 ES8311 需要精确的 MCLK 以保证采样率精度。
> - NS4150B 为 D 类功放，输出需加 LC 滤波器避免 EMI 干扰。

---

## 五、USB 子系统接线 | USB Subsystem Wiring

### USB 拓扑结构 | USB Topology

```
                          USB Type-C (连接电脑)
                                │
                         ┌──────┴──────┐
                         │   SL2.1A    │
                         │  USB HUB    │
                         └──┬───┬───┬──┘
                            │   │   │
                   Port 1   │   │   │  Port 3
                            │   │   │
                     ┌──────┘   │   └──────┐
                     ↓          │          ↓
              ┌────────────┐    │    ┌────────────┐
              │  GL823K    │    │    │ USB Type-A │ ← 外接鼠标/U盘
              │ (模拟U盘)  │    │    └────────────┘
              └────────────┘    │
                                │  Port 2
                                │
                     ┌──────────┘
                     │
                     │  模拟开关 U6/U7 (USB_SEL 由 GPIO18 控制)
                     │
                     ├── USB_SEL = 0 (无线模式): USB ←→ ESP32-S3 内置 USB
                     │       ESP32-S3 通过 USB 读取鼠标数据并转发
                     │
                     └── USB_SEL = 1 (USB 有线模式): USB ←→ Type-A 口
                             Type-A 直连电脑 (透传所有 USB 设备)
```

### USB 信号接线表 | USB Signal Wiring Table

| 信号 Signal | ESP32-S3 GPIO | 连接目标 Target | 说明 Notes |
|---|---|---|---|
| USB_DP (内置) | GPIO19 | SL2.1A Port 2 D+ / 模拟开关 | ESP32-S3 内置 USB PHY |
| USB_DM (内置) | GPIO20 | SL2.1A Port 2 D- / 模拟开关 | ESP32-S3 内置 USB PHY |
| USB_SEL | GPIO18 | 模拟开关 U6/U7 控制脚 | USB 路径选择 |

### CH342F 下载电路接线 | CH342F Download Circuit Wiring

```
                    CH342F (双通道 USB-TTL)
              ┌─────────────────────────────┐
  USB ←──────│ USB DP/DM                    │
              │                              │
              │  Channel 1 (键盘主控):        │
              │    TX1 ──── GPIO27 (ESP32 RX) │
              │    RX1 ──── GPIO26 (ESP32 TX) │
              │                              │
              │  Channel 2 (旋钮主控):        │
              │    TX2 ──── 旋钮 ESP32 RX     │
              │    RX2 ──── 旋钮 ESP32 TX     │
              │                              │
              │  VCC ← 3.3V                  │
              │  GND ← GND                   │
              └─────────────────────────────┘
```

> **说明 Notes:**
> - CH342F 提供双通道 USB 转 TTL，一个通道用于键盘 ESP32-S3，另一个用于旋钮 ESP32-S3。
> - ESP32-S3 进入下载模式: GPIO0 拉低 → 复位 → 通过 UART 烧录。

---

## 六、WS2812B 级联接线 | WS2812B Daisy-Chain Wiring

### 级联拓扑 | Daisy-Chain Topology

```
GPIO17 (WS2812B DIN) ──[330R 保护电阻]──→ LED #1 DIN
                                            │
                                          DOUT → LED #2 DIN
                                                     │
                                                   DOUT → LED #3 DIN
                                                              │
                                                            ... (串联 75~100 颗)
                                                              │
                                                            DOUT → LED #N (最后一颗)

电源注入 Power Injection:
  5V ────┬─── LED #1 VCC
         ├─── LED #20 VCC  (每 20 颗注入一次)
         ├─── LED #40 VCC
         ├─── LED #60 VCC
         └─── LED #80 VCC

  GND ───┬─── LED #1 GND
         ├─── LED #20 GND
         ├─── LED #40 GND
         ├─── LED #60 GND
         └─── LED #80 GND
```

### WS2812B 单颗接线 | Single WS2812B Wiring

| WS2812B 引脚 | 连接目标 Connection | 说明 Notes |
|---|---|---|
| VCC (4V~5.5V) | 5V 电源 | 每 20 颗注入一次 5V 和 GND |
| DIN | 上一颗 DOUT (首颗接 GPIO17) | 数据输入 |
| DOUT | 下一颗 DIN (末颗悬空) | 数据输出 |
| GND | 公共地 | |

### 电源注入建议 | Power Injection Guidelines

```
  每颗 WS2812B 全亮白光时功耗约 60mA。
  75 颗全亮 = 75 × 60mA = 4.5A — 远超 ESP32-S3 供电能力!

  建议:
  1. 每 20 颗灯珠从 5V 电源轨单独注入供电
  2. 在每段供电点并联 100uF 电解电容 + 100nF 陶瓷电容
  3. USB 模式: 由电脑 USB 供电 (最大 500mA，控制亮度)
  4. 无线模式: 由电池经 HX3608 升压 5V 供电
  5. 软件限制最大亮度为 30-50%，避免过流
```

> **警告 Warning:**
> WS2812B 全白光电流极大。务必在软件中限制亮度，并确保 5V 电源轨能提供足够电流。

---

## 七、电源分配系统 | Power Distribution System

### 电源拓扑 | Power Topology

```
                        USB Type-C (5V VBUS)
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    │  直供 5V 负载:     │
                    │  ├── SL2.1A HUB   │
                    │  ├── NS4150B x2   │
                    │  └── WS2812B      │
                    │                   │
                    ↓                   │
              ┌─────────────┐          │
              │   TP4056    │          │
              │  锂电充电 IC │←────────┘ (充电电源)
              └──────┬──────┘
                     │
                     ↓
              ┌─────────────┐
              │  DW01 +     │
              │  FS8205A    │
              │  电池保护    │
              └──────┬──────┘
                     │
                锂电池 3000mAh (3.7V nominal)
                     │
                     ↓
              ┌─────────────┐
              │   HX3608    │
              │  DC-DC 升压  │
              │  3.7V → 5V  │
              └──────┬──────┘
                     │
                5V 系统电源轨 (无线模式)
                     │
              ┌──────┴──────┐
              │   ME6217    │
              │  LDO 3.3V   │
              │  5V → 3.3V  │
              └──────┬──────┘
                     │
                3.3V 系统电源轨
                ├── ESP32-S3 VDD (3.3V)
                ├── 74HC165 VCC
                ├── ES7210 VCC
                ├── ES8311 VCC
                ├── I2C 上拉电源
                └── OLED VCC
```

### 电源轨规格 | Power Rail Specifications

| 电源轨 Rail | 电压 Voltage | 来源 Source | 最大电流 Max Current | 负载 Loads |
|---|---|---|---|---|
| 5V_USB | 5.0V | USB VBUS (有线模式) | 500mA | HUB, 充电, 外设 |
| 5V_BAT | 5.0V | HX3608 升压 (无线模式) | 2A | 全系统 |
| 3V3 | 3.3V | ME6217C33M5G LDO | 500mA | MCU, ICs, 逻辑 |
| VBAT | 3.7V | 锂电池直出 | — | HX3608 输入 |
| VCHARGE | 4.2V | TP4056 输出 | 1A | 电池充电 |

### 关键电源接线表 | Key Power Wiring Table

| IC | 输入 Input | 输出 Output | 外围元件 Peripheral | 说明 Notes |
|---|---|---|---|---|
| TP4056 | 5V_USB | VCHARGE → 电池+ | R_PROG = 1.2k (充电电流 1A) | 充电状态 LED |
| DW01 | 电池+ | — | + FS8205A 双 MOSFET | 保护电路 |
| HX3608 | VBAT (3.0~4.2V) | 5V | 电感 4.7uH, 肖特基二极管 | 升压转换 |
| ME6217 | 5V | 3.3V | 输入 10uF, 输出 10uF | LDO 稳压 |

---

## 八、磁吸扩展接口引脚定义 | Magnetic Expansion Port Pinout

### 磁吸 Pogo Pin 引脚定义 | Magnetic Pogo Pin Pinout

```
          键盘侧 (母座)              旋钮/扩展模块 (公头)
        ┌──────────────┐          ┌──────────────┐
        │  ●  ●  ●  ●  │ ←→→→→→ │  ●  ●  ●  ●  │
        │  1  2  3  4  │          │  1  2  3  4  │
        │              │          │              │
        │  ●  ●        │ ←→→→→→ │  ●  ●        │
        │  5  6        │          │  5  6        │
        └──────────────┘          └──────────────┘

Pin 1: VCC (5V) — 电源 (双向，可充电或供电)
Pin 2: GND — 地
Pin 3: IIC_SDA — I2C 数据 (经保护电路)
Pin 4: IIC_SCL — I2C 时钟 (经保护电路)
Pin 5: DETECT — 设备检测 (GPIO21)
Pin 6: ID — 身份识别 (电阻分压，20K = 扩展模块)
```

### 扩展接口保护电路 | Expansion Port Protection Circuit

```
             内部 I2C 总线
                 │
            ┌────┴────┐
            │  保护    │ ←── 异或逻辑芯片 U132 控制
            │  开关    │     (基于 ID 脚电压判断设备类型)
            └────┬────┘
                 │
            Pogo Pin 3/4 (I2C)
            连接外部设备

    ID 脚逻辑:
    ├── ID 脚接 20K → GND: 电压 ≈ 3.3V → U132 输出 HIGH
    │   → 关闭充电、开启对外供电、开启 I2C (扩展设备模式)
    │
    └── ID 脚悬空或其它电阻: 电压 ≠ 3.3V → U132 输出 LOW
        → 开启充电、关闭对外供电、关闭 I2C (充电底座模式)
```

### 接线表 | Wiring Table

| Pogo Pin | 信号 Signal | ESP32-S3 GPIO | 说明 Notes |
|---|---|---|---|
| Pin 1 | VCC (5V) | 经电源开关电路 | 双向电源 |
| Pin 2 | GND | GND | 公共地 |
| Pin 3 | IIC_SDA | GPIO33 (经保护) | 扩展 I2C 数据 |
| Pin 4 | IIC_SCL | GPIO34 (经保护) | 扩展 I2C 时钟 |
| Pin 5 | DETECT | GPIO21 | 磁吸连接检测 (高低电平) |
| Pin 6 | ID | 电压监控芯片 U35/U37 | 设备类型识别 |

---

## 九、旋钮模块接线 | Knob Module Wiring

### 旋钮系统总框图 | Knob System Block Diagram

```
      旋钮 ESP32-S3 (独立主控)
             │
    ┌────────┼──────────────────────────┐
    │        │                          │
    │  SPI   │  I2C          PWM        │
    │        │              │           │
    ↓        ↓              ↓           ↓
 GC9A01   AS5047P      TMC6300       HX711
 (屏幕)   (磁编码)    (电机驱动)    (压力ADC)
    │        │              │           │
    │        │              ↓           │
    │        │         云台电机         │
    │        │        (BLDC)           │
    │        │                         ↓
    │        │                      应变计 x4
    │        │
    │        └──→ FOC 闭环控制 (SimpleFOC)
    │
    └──→ 磁吸 Pogo Pin ←→ 键盘主板 (电源 + I2C 通信)
```

### SPI 屏幕 (GC9A01) 接线 | SPI Display Wiring

| 旋钮 ESP32-S3 GPIO | 信号 Signal | GC9A01 引脚 | 说明 Notes |
|---|---|---|---|
| GPIO7 | SPI_CLK | SCL | SPI 时钟 |
| GPIO11 | SPI_MOSI | SDA (DIN) | SPI 数据 |
| GPIO10 | SPI_CS | CS | 片选 (低有效) |
| GPIO12 | DC (数据/命令) | DC | 0=命令, 1=数据 |
| GPIO13 | RESET | RST | 硬件复位 (低有效) |
| 3.3V | VCC | VCC | 3.3V 供电 |
| GND | GND | GND | 公共地 |

> **说明 Notes:**
> - GC9A01 为 240x240 圆形 TFT，SPI 接口驱动，配合 LVGL 图形库显示旋钮 UI。
> - 背光控制 (BL) 可接 GPIO 或直连 3.3V。

### TMC6300 电机驱动接线 | TMC6300 Motor Driver Wiring

| 旋钮 ESP32-S3 GPIO | 信号 Signal | TMC6300 引脚 | 说明 Notes |
|---|---|---|---|
| GPIO5 | PWM_UH | UH | U 相高边 MOSFET |
| GPIO6 | PWM_UL | UL | U 相低边 MOSFET |
| GPIO7 | PWM_VH | VH | V 相高边 MOSFET |
| GPIO8 | PWM_VL | VL | V 相低边 MOSFET |
| GPIO9 | PWM_WH | WH | W 相高边 MOSFET |
| GPIO10 | PWM_WL | WL | W 相低边 MOSFET |
| GPIO14 | EN | EN | 使能 (高有效) |
| GPIO15 | DIAG | DIAG | 故障诊断输出 |
| 5V | VCC | VCC | 逻辑电源 5V |
| GND | GND | GND | 公共地 |
| VM (电机电源) | 5-8V | VM | SY7200AABC 升压输出 |

```
          TMC6300 → 云台电机 (BLDC)
          ┌──────────────────┐
          │  UH ──┐          │
          │  UL ──┤ U 相 ────│─── 电机红线
          │  VH ──┤ V 相 ────│─── 电机蓝线
          │  VL ──┤          │
          │  WH ──┤ W 相 ────│─── 电机黄线
          │  WL ──┘          │
          └──────────────────┘
```

### AS5047P 磁编码器接线 | AS5047P Magnetic Encoder Wiring

| 旋钮 ESP32-S3 GPIO | 信号 Signal | AS5047P 引脚 | 说明 Notes |
|---|---|---|---|
| GPIO1 | SPI_CLK | CLK | SPI 时钟 (最大 10MHz) |
| GPIO2 | SPI_MISO | DO | SPI 数据输出 |
| GPIO3 | SPI_MOSI | DI | SPI 数据输入 |
| GPIO4 | SPI_CS | CSn | 片选 (低有效) |
| 3.3V | VCC | VDD | 3.3V 供电 |
| GND | GND | GND | 公共地 |

> **说明 Notes:**
> - AS5047P 提供 14-bit 分辨率 (16384 步/圈)，用于 FOC 闭环控制的角度反馈。
> - 磁铁安装在电机轴末端，编码器 PCB 对准磁铁中心。

### HX711 压力传感器接线 | HX711 Pressure Sensor Wiring

| 旋钮 ESP32-S3 GPIO | 信号 Signal | HX711 引脚 | 说明 Notes |
|---|---|---|---|
| GPIO16 | PD_SCK | PD_SCK | 时钟/电源控制 |
| GPIO17 | DOUT | DOUT | 24-bit 数据输出 |
| 3.3V | VCC | VCC | 供电 |
| GND | GND | GND | 公共地 |

```
HX711 外围:
  ┌─────────────┐
  │   HX711     │
  │             │
  │  E+  ──── 应变计组 1 (推/拉) ──→ 2 片应变计组成半桥
  │  E-  ──── 应变计组 2 (左/右) ──→ 2 片应变计组成半桥
  │  A+  ←─── 半桥输出 +
  │  A-  ←─── 半桥输出 -
  │             │
  └─────────────┘

  应变计安装: 均匀分布在旋钮底座 4 个方向
  用于检测: 推、拉、左倾、右倾 四个方向的按压力
```

### 旋钮供电 | Knob Power

```
  锂电池 500mAh (旋钮内置)
      │
      ├──→ ME6217C33 (3.3V) → ESP32-S3, AS5047P, GC9A01
      │
      └──→ SY7200AABC (升压 5~8V) → TMC6300 VM (电机电源)

  充电: 通过磁吸 Pogo Pin VCC → TP4056 → 电池
```

---

## 十、接收器接线 | Receiver Wiring

### 接收器系统框图 | Receiver System Diagram

```
          接收器 ESP32-S3-WROOM-1-N8
          ┌───────────────────────┐
          │                       │
  USB ────│ GPIO19 (USB_DP)      │
  Type-C──│ GPIO20 (USB_DM)      │
          │                       │
          │  ESP-NOW 接收 (2.4G) │ ← 板载天线
          │                       │
          │  HID 报告 ──→ USB     │ → 电脑识别为 USB 键盘
          │                       │
          │  VCC ← 5V (USB)       │
          │  VDD ← 3.3V (LDO)    │
          │  GND ← GND            │
          └───────────────────────┘
```

### 接收器接线表 | Receiver Wiring Table

| ESP32-S3 GPIO | 功能 Function | 连接目标 Target | 说明 Notes |
|---|---|---|---|
| GPIO19 | USB_DP | USB Type-C D+ | 内置 USB PHY，枚举为 HID 键盘 |
| GPIO20 | USB_DM | USB Type-C D- | |
| GPIO43 | UART_TX | 预留调试口 | 固件下载 |
| GPIO44 | UART_RX | 预留调试口 | |
| GPIO0 | BOOT | Boot 按钮 | |
| GPIO46 | LED | 状态指示 LED | 连接/配对指示 |
| VCC (5V) | 电源 | USB VBUS | |
| 3V3 (内部 LDO) | 逻辑电源 | — | ESP32-S3 模块内置 LDO |

> **说明 Notes:**
> - 接收器为最简设计: ESP32-S3 + USB Type-C + 天线。
> - 通过 ESP-NOW 协议接收键盘数据，转为 USB HID 报告发送给电脑。
> - ESP-NOW 为乐鑫专有 2.4G 协议，延迟低于蓝牙，无需配对。

---

## 附录 A：总线速查表 | Appendix A: Bus Quick Reference

| 总线 Bus | GPIO 引脚 Pins | 速率 Speed | 设备 Devices | 协议 Protocol |
|---|---|---|---|---|
| I2C #0 | GPIO15(SDA), GPIO16(SCL) | 400 kHz | ES7210, ES8311, OLED | I2C |
| I2C #1 (扩展) | GPIO33(SDA), GPIO34(SCL) | 400 kHz | 磁吸扩展设备 | I2C (经保护) |
| I2S #0 | GPIO4(MCLK), GPIO5(BCLK), GPIO6(WS), GPIO13(DIN), GPIO14(DOUT) | 取决于采样率 | ES7210, ES8311 | I2S (TDM) |
| SPI #0 (按键) | GPIO7(CLK), GPIO8(MISO), GPIO11(MOSI), GPIO10(CS), GPIO12(PL) | 1 MHz | 74HC165 x10 | 同步串行 |
| SPI #1 (旋钮屏幕) | 旋钮 GPIO7/11/10/12/13 | 20 MHz | GC9A01 | SPI |
| SPI #2 (旋钮编码) | 旋钮 GPIO1/2/3/4 | 10 MHz | AS5047P | SPI |
| USB | GPIO19(DP), GPIO20(DM) | Full Speed (12Mbps) | SL2.1A HUB | USB 2.0 |
| UART #0 | GPIO26(TX), GPIO27(RX) | 460800 bps | CH342F CH1 | 8N1 |
| UART #1 | GPIO28(TX), GPIO29(RX) | 460800 bps | CH342F CH2 | 8N1 |
| WS2812B | GPIO17 | 800 kHz | LED x75~100 | 单线 NZR |

---

## 附录 B：关键走线注意事项 | Appendix B: Critical Routing Notes

| 信号 Signal | 注意事项 Notes |
|---|---|
| USB D+/D- | 差分对，90 ohm 阻抗匹配，等长，远离数字信号 |
| I2S (BCLK/WS/DATA) | 时钟和数据线等长匹配，远离电源开关噪声 |
| I2C (SDA/SCL) | 上拉电阻靠近主控，走线尽量短 |
| WS2812B DIN | 串联 330R 电阻靠近 GPIO 端，减少反射 |
| SPI (74HC165) | SCLK 走线尽量短，避免串扰，PL 信号加去耦 |
| 电源 (5V/3.3V) | 5V 走线宽 >= 0.5mm，3.3V 走线宽 >= 0.3mm |
| GND | 四层板内层完整地平面，双层板大面积铺铜 |
| 天线区 | ESP32-S3 模块天线正下方禁止铺铜和走线 |
| 音频模拟 | ES7210/ES8311 模拟信号远离数字信号，独立模拟地 |

---

*最后更新 | Last updated: 2026-05-27*
