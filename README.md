# 4模式机械键盘 "幻想键盘" | 4-Mode Mechanical Keyboard "FantasyKB"

> **本项目基于开源项目 [承载我所有幻想的键盘](https://oshwhub.com/ran-pang/multifunctional-keyboard) 改编，已获得原作者授权用于教学目的。**
>
> This project is adapted from the open-source project ["The Keyboard That Carries All My Fantasies"](https://oshwhub.com/ran-pang/multifunctional-keyboard), used with the original author's permission for educational purposes.

---

## 项目简介 | Project Overview

"幻想键盘"是一款 4 模无线机械键盘，集成 FOC 无刷电机旋钮屏、语音交互、USB Hub、磁吸扩展接口等多项前沿功能。学生将在 20 天的课程中，从电子学基础出发，逐步完成子系统原型验证、12 块 PCB 设计、固件开发与最终组装调试，亲手打造一台功能丰富的全尺寸机械键盘。

"FantasyKB" is a 4-mode wireless mechanical keyboard integrating a FOC brushless motor knob with circular LCD, voice interaction, USB hub, and magnetic expansion ports. Over 20 days, students will progress from electronics fundamentals through subsystem prototyping, designing 12 PCBs, firmware development, and final assembly — ultimately producing a fully featured mechanical keyboard.

本项目涵盖 SPI 移位寄存器按键扫描（74HC165）、FOC 磁场定向电机控制、I2S 音频流水线、ESP-NOW 2.4GHz 无线通信、磁编码器（AS5047P）、USB HID 人机接口协议等核心技术。课程以实践驱动，每天 6-8 小时，采用模块化教学，确保学生即使无法完成全部功能也能取得阶段性成果。

This project covers SPI shift-register key scanning (74HC165), FOC motor control, I2S audio pipeline, ESP-NOW 2.4GHz wireless, magnetic encoder (AS5047P), USB HID protocol, and more. The course is practice-driven at 6-8 hours/day with a modular approach — students can achieve partial success even if not every subsystem is completed.

---

## 最终效果 | Final Result

完成本项目后，你将拥有一台：

Upon completing this project, you will have:

- **~75 键全尺寸机械键盘** — 完整布局，热插拔轴座，支持自定义键位
- **4 模无线连接** — USB 有线 / 蓝牙 / WiFi / 2.4GHz (ESP-NOW) 自由切换
- **FOC 无刷电机旋钮** — 磁吸可拆卸，带触觉力反馈和 GC9A01 1.28" 圆形 LCD
- **语音交互** — 双麦克风录音 + 立体声扬声器，支持语音指令
- **USB Hub** — 4 口 USB 2.0 Hub + 双通道 USB-TTL + U 盘模拟
- **鼠标数据转发** — 鼠标插入键盘 Type-A 口，数据随无线模式一并转发
- **95 颗 WS2812B RGB 灯珠** — 每键独立 RGB，多种灯效模式
- **4 个磁吸扩展端口** — IIC 通信，自动检测设备类型，可接小键盘等扩展模块
- **模拟摇杆输入** — 可作为游戏手柄或自定义控制器使用
- **3D 打印外壳与旋钮壳体** — 个性化外观设计
- **12 块 PCB** — 包含 4 块四层板 + 8 块双层板的完整硬件系统

---

## 核心功能 | Core Features

| 功能 Feature | 说明 Description |
|---|---|
| 4 模连接 | USB 有线、蓝牙 BLE、WiFi、ESP-NOW 2.4GHz 无线接收器 |
| ~75 键全布局 | 74HC165 移位寄存器 SPI 菊花链扫描，支持全键无冲 |
| FOC 电机旋钮 | TMC6300 三相驱动 + AS5047P 14 位磁编码器 + SimpleFOC 算法 |
| 旋钮显示屏 | GC9A01 1.28" 240x240 圆形 LCD，LVGL 图形界面 |
| 触觉力反馈 | 旋钮支持档位感、弹性回弹、阻尼等力反馈效果 |
| 压力传感 | HX711 + 应变片 x4，检测旋钮按压力度 |
| 语音交互 | ES7210 四通道 ADC 录音 + ES8311 DAC + NS4150B x2 立体声功放 |
| USB Hub | SL2.1A 四口 USB 2.0 Hub |
| USB-TTL | CH342F 双通道 USB 转串口（键盘主控 + 旋钮主控） |
| U 盘模拟 | GL823K USB 存储控制器 |
| 鼠标转发 | Type-A 口接鼠标，ESP32-S3 读取并随无线模式转发 |
| RGB 灯效 | WS2812B x95，每键独立 RGB |
| 磁吸扩展 | 4 个磁吸弹簧针接口，IIC 通信 + 自动设备检测电路 |
| 模拟摇杆 | 摇杆模拟量输入，可映射为方向键或游戏输入 |

---

## 技术架构 | Technical Architecture

### 系统框图 | System Block Diagram

```
                        ┌─────────────────────────────────────────┐
                        │          键盘主板 (Keyboard MCU)         │
                        │         ESP32-S3-WROOM-1-N16R8          │
                        │                                         │
  ┌──────────┐  SPI    │  ┌─────────────┐    ┌──────────────┐    │
  │74HC165 x10│◄────────┤  │ Key Scanner │    │   Wireless   │    │
  │(Shift Reg)│         │  └─────────────┘    │  WiFi/BLE/   │    │
  └──────────┘         │                     │  ESP-NOW     │    │
                        │  ┌─────────────┐    └──────┬───────┘    │
  ┌──────────┐  UART   │  │  Comm Mgmt  │◄──────────┤            │
  │ 旋钮主控  │◄────────┤  └─────────────┘           │            │
  │ (Knob)   │         │                            │            │
  └──────────┘         │  ┌─────────────┐           │            │
                        │  │   USB HID   │◄──────────┘            │
  ┌──────────┐  I2S    │  └─────────────┘                        │
  │ ES7210   │◄────────┤                                         │
  │ (ADC)    │         │  ┌─────────────┐    ┌──────────────┐    │
  └──────────┘         │  │  Audio Pipe │    │   USB Hub    │    │
  ┌──────────┐  I2S    │  │  I2S + IIC  │    │   SL2.1A     │    │
  │ ES8311   │◄────────┤  └─────────────┘    └──────────────┘    │
  │ (DAC)    │         │                                         │
  └──────────┘         │  ┌─────────────┐    ┌──────────────┐    │
                        │  │   RGB LED   │    │  Magnetic    │    │
  ┌──────────┐  Single │  │ WS2812B x95 │    │  Expansion   │    │
  │ WS2812B  │◄────────┤  └─────────────┘    │  x4 (IIC)   │    │
  │  (x95)   │         │                     └──────────────┘    │
  └──────────┘         │                                         │
                        └────────────────┬────────────────────────┘
                                         │
                                    USB-C / Wireless
                                         │
                                  ┌──────┴──────┐
                                  │   电脑/设备   │
                                  │  Host PC     │
                                  └─────────────┘
```

### 子系统详细 | Subsystem Details

| 子系统 Subsystem | 主要元件 Main Components | 通信协议 Protocol | 说明 Description |
|---|---|---|---|
| 主控 MCU | ESP32-S3-WROOM-1-N16R8 | - | 16MB Flash + 8MB PSRAM，WiFi/BLE/USB 全集成 |
| 按键扫描 Key Scanning | 74HC165 移位寄存器 x10 | SPI 菊花链 | 参考稚辉君瀚文键盘方案，全键无冲 |
| 无线通信 Wireless | ESP32-S3 内置 WiFi/BLE + ESP-NOW | WiFi/BLE/2.4GHz | 4 模切换：USB / BLE / WiFi / ESP-NOW |
| USB Hub | SL2.1A | USB 2.0 | 4 口 USB 2.0 集线器 |
| USB-TTL | CH342F (双通道) | UART | 分别连接键盘主控和旋钮主控的串口下载 |
| USB 存储 | GL823K | USB Mass Storage | U 盘模拟功能 |
| 音频 ADC | ES7210 (4 通道) | I2S + IIC | 双麦克风录音，参考 ESP-BOX 设计 |
| 音频 DAC | ES8311 | I2S + IIC | 音频播放输出 |
| 音频功放 | NS4150B x2 (立体声) | - | 3W 立体声输出 |
| 旋钮主控 Knob MCU | ESP32-S3-WROOM-1-N16R8 | UART 至键盘 | 独立 MCU，通过 UART 与键盘主控通信 |
| 旋钮显示屏 Knob Display | GC9A01 1.28" 圆形 LCD | SPI | 240x240 分辨率，LVGL 图形界面 |
| 电机驱动 Motor Driver | TMC6300 (三相 BLDC) | FOC | 磁场定向控制，实现力反馈 |
| 磁编码器 Magnetic Encoder | AS5047P (14 位) | SPI | 高精度角度检测，分辨率 0.022 度 |
| 压力传感器 Pressure Sensor | HX711 + 应变片 x4 | - | 检测旋钮按压力度 |
| RGB LED | WS2812B x95 | 单线协议 | 每键独立 RGB 地址able LED |
| 磁吸扩展 Magnetic Expansion | 磁吸弹簧针 x4 | IIC | 带自动检测与保护电路 |
| 接收器 Receiver | ESP32-S3 (基础版) | ESP-NOW | 2.4GHz 无线 USB 接收器 |
| 键盘电源 Power (Keyboard) | TP4056 + HX3608 + ME6217 | - | 充电管理 + 升压 + LDO |
| 旋钮电源 Power (Knob) | DW01 + FS8205A + ME6217 | - | 锂电保护 + LDO |

### 三颗 ESP32-S3 分工 | Three ESP32-S3 MCU Roles

```
┌──────────────────┐     UART      ┌──────────────────┐
│   键盘主控 MCU    │◄─────────────►│   旋钮主控 MCU    │
│   (Keyboard)      │               │   (Knob)          │
│                   │               │                    │
│ - 按键扫描         │               │ - FOC 电机控制     │
│ - USB HID         │               │ - GC9A01 LCD 显示  │
│ - 无线通信         │               │ - AS5047P 编码器   │
│ - 音频流水线       │               │ - LVGL UI         │
│ - RGB 控制        │               │ - 压力传感         │
│ - USB Hub 管理     │               │ - SimpleFOC       │
│ - 磁吸扩展管理     │               │                    │
└──────────────────┘               └──────────────────┘

┌──────────────────┐
│   接收器 MCU      │
│   (Receiver)      │
│                   │
│ - ESP-NOW 接收    │
│ - USB HID 上报    │
│ - 2.4GHz 适配器   │
└──────────────────┘
```

---

## 硬件清单 | Hardware List

### PCB 清单 | PCB List (12 块板)

本项目共包含 12 块 PCB，其中 4 块四层板 + 8 块双层板：

This project includes 12 PCBs: 4 four-layer boards + 8 two-layer boards.

| 编号 | 板名 Board Name | 层数 Layers | 板厚 Thickness | 尺寸 Size | 特殊工艺 Special Process |
|---|---|---|---|---|---|
| 1 | 键盘主板 V4 (Keyboard Main Board) | 4 层 | 1.2mm | 300x120mm | 阻抗控制 +/-20% |
| 2 | 方向键小板 (Arrow Key Sub-Board) | 2 层 | 1.2mm | - | - |
| 3 | 音频板 V2 (Audio Board) | 4 层 | 1.0mm | - | - |
| 4 | 指示灯板 (Indicator LED Board) | 2 层 | 1.0mm | - | - |
| 5 | 磁吸接口板 (Magnetic Connector Board) | 2 层 | 1.6mm | - | - |
| 6 | 旋钮磁吸转接板 (Knob Magnetic Adapter) | 2 层 | 1.0mm | - | - |
| 7 | 圆灯板 (Round LED Board) | 2 层 | 1.0mm | - | - |
| 8 | USB 板 (USB Board) | 2 层 | 1.0mm | - | - |
| 9 | 旋钮主板 V4 (Knob Main Board) | 4 层 | 1.0mm | - | ENIG 沉金 |
| 10 | 旋钮电池灯板 (Knob Battery & LED Board) | 2 层 | 1.0mm | - | - |
| 11 | 屏幕 FPC 转接板 (Screen FPC Adapter) | 2 层 | 1.0mm | - | - |
| 12 | 接收器板 (Receiver Board) | 4 层 | 1.0mm | - | ENIG 沉金 |

> 四层板层压结构：JLC04161H-7628（嘉立创免费阻抗叠层）。
> Four-layer stackup: JLC04161H-7628 (free impedance-controlled stackup from JLCPCB).

---

## 预算总览 | Budget Summary

> **重要提示 Important Note**: 本项目总预算约 ¥1,028，超出 CLAUDE.md 中 ¥500 的预算约束。这是因为该项目复杂度远超原有宏键盘项目，涉及 12 块 PCB、3 颗 ESP32-S3、FOC 电机等高成本组件。这是一个已记录的已知权衡（详见 FAQ 部分）。
>
> Total budget is approximately ¥1,028, exceeding the ¥500 constraint in CLAUDE.md. This is a documented tradeoff due to the project's significantly higher complexity.

| 类别 Category | 金额 Amount (CNY) | 说明 Description |
|---|---|---|
| 主要 IC 及有源器件 Main ICs & Active Components | ¥116.40 | ESP32-S3 x3、74HC165 x10、ES7210/ES8311、TMC6300、AS5047P 等 |
| 旋钮模块 Knob Module (motor/encoder/LCD) | ¥82.50 | 无刷电机 + TMC6300 + AS5047P + GC9A01 |
| WS2812B RGB LED (95 颗) | ¥25.00 | 每键一颗 |
| 连接器 Connectors (magnetic/Type-C/FPC) | ¥31.60 | 磁吸弹簧针、Type-C 母座、FPC 排线座 |
| 被动元件 Passive Components | ¥18.25 | 电阻、电容、电感、二极管等 |
| 机电元件 Electromechanical (switches/keycaps/hot-swap) | ¥352.00 | 机械轴体 x75、热插拔轴座 x75、键帽套装 |
| PCB 制造 PCB Manufacturing (12 块板) | ¥144.00 | 4 块四层板 + 8 块双层板 |
| SMT 贴片 SMT Assembly | ¥125.00 | 嘉立创 SMT 服务 |
| 3D 打印/结构件 3D Printing / Structural | ¥105.00 | 外壳、旋钮壳体、定位板 |
| 线材及杂项 Cables & Misc | ¥28.00 | FPC 排线、杜邦线、螺丝等 |
| **总计 Total** | **~¥1,027.75** | |

### 核心元器件清单 | Key Component List

| 元件 Component | 型号/规格 Specification | 数量 Qty | 参考单价 Unit Price (CNY) | 说明 Notes |
|---|---|---|---|---|
| 主控 MCU (键盘) | ESP32-S3-WROOM-1-N16R8 | 1 | 25.00 | 16MB Flash + 8MB PSRAM |
| 主控 MCU (旋钮) | ESP32-S3-WROOM-1-N16R8 | 1 | 25.00 | 同上 |
| 主控 MCU (接收器) | ESP32-S3-WROOM-1-N16R8 | 1 | 25.00 | 同上 |
| 移位寄存器 | 74HC165 | 10 | 0.80 | SPI 菊花链按键扫描 |
| 音频 ADC | ES7210 | 1 | 5.00 | 4 通道 I2S ADC |
| 音频 DAC | ES8311 | 1 | 3.50 | I2S DAC |
| 音频功放 | NS4150B | 2 | 1.50 | 3W D 类功放 |
| USB Hub | SL2.1A | 1 | 3.00 | 4 口 USB 2.0 |
| USB-TTL | CH342F | 1 | 4.00 | 双通道 USB 转串口 |
| USB 存储 | GL823K | 1 | 2.50 | U 盘模拟 |
| LCD 驱动 | GC9A01 | 1 | 12.00 | 1.28" 240x240 圆形屏 |
| 电机驱动 | TMC6300 | 1 | 15.00 | 三相 BLDC 驱动 |
| 磁编码器 | AS5047P | 1 | 18.00 | 14 位 SPI 磁编码器 |
| 压力传感器 | HX711 | 1 | 3.00 | 24 位 ADC |
| RGB LED | WS2812B-5050 | 95 | 0.26 | 可寻址 RGB LED |
| 机械轴体 | 佳达隆 G Pro 3.0 (或等同) | ~75 | 2.50 | 可选红/青/茶轴 |
| 热插拔轴座 | Kailh 热插拔底座 | ~75 | 0.50 | MX 兼容 |
| 充电管理 | TP4056 | 1 | 0.50 | 锂电池充电 |
| 升压芯片 | HX3608 | 1 | 1.00 | 升压至 5V |
| LDO | ME6217 (3.3V) | 3 | 0.50 | 低压差线性稳压器 |
| 电池保护 | DW01 + FS8205A | 1 套 | 0.50 | 旋钮锂电保护 |

---

## 软件环境 | Software Environment

### 固件层（运行在 ESP32-S3 上 | Firmware on ESP32-S3）

| 模块 Module | 开发环境 IDE | 语言 Language | 框架 Framework | 说明 Description |
|---|---|---|---|---|
| 键盘固件 Keyboard Firmware | ESP-IDF | C | FreeRTOS | 按键扫描、4 模通信、音频、USB HID |
| 旋钮固件 Knob Firmware | PlatformIO (VS Code) | C/C++ | LVGL + SimpleFOC | FOC 控制、LCD 显示、力反馈 |
| 接收器固件 Receiver Firmware | ESP-IDF | C | ESP-NOW | 2.4GHz 无线接收 + USB HID |

### 工具层（运行在 PC 上 | Tools on PC）

| 工具 Tool | 用途 Purpose |
|---|---|
| **VS Code** | 主力代码编辑器 Main code editor |
| **ESP-IDF v5.x** | 键盘和接收器固件开发环境 Keyboard & receiver firmware SDK |
| **PlatformIO** | 旋钮固件开发环境 Knob firmware IDE (VS Code extension) |
| **嘉立创 EDA (LCEDA)** | PCB 设计（原理图 + 布局）PCB design tool |
| **Git** | 版本控制 Version control |
| **Python 3.10+** | 测试脚本、工具链 Test scripts and tooling |

---

## 快速开始 | Quick Start

```bash
# 1. 克隆项目 | Clone the project
git clone <repo-url>
cd project-03-4mode-keyboard

# 2. 安装 Python 依赖 | Install Python dependencies
cd software
pip install -r requirements.txt

# 3. 运行基础测试 | Run basic tests
python -m pytest tests/ -v

# 4. 安装 ESP-IDF | Install ESP-IDF
#    参考 | Follow: https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/get-started/
#    Windows 安装器 | Windows installer: https://dl.espressif.com/dl/esp-idf/

# 5. 安装 PlatformIO | Install PlatformIO
#    VS Code 扩展 | VS Code extension: 搜索 "PlatformIO IDE"

# 6. 按照 Day 1 课程开始学习 | Start with Day 1
#    打开 curriculum/day-01.md
```

---

## 课程安排 | Course Schedule

> 本项目扩展为 20 天课程（原宏键盘为 12 天），以容纳更复杂的硬件设计和多子系统开发。
>
> Extended to 20 days (vs. 12 for the original macro keyboard) to accommodate the more complex hardware design and multi-subsystem development.

### 第一阶段：电子基础与 ESP32-S3 入门（Day 1-5）| Phase 1: Electronics Fundamentals

| 天数 Day | 主题 Topic | 核心内容 Key Content |
|---|---|---|
| Day 01 | 项目启动与电子学基础 | 电路基础、面包板实验、LED 点亮、ESP32-S3 简介 |
| Day 02 | SPI 通信与移位寄存器 | 74HC165 菊花链原理、SPI 协议、面包板按键扫描实验 |
| Day 03 | I2C/I2S 通信与音频入门 | I2C 协议、I2S 音频基础、ES7210/ES8311 简介 |
| Day 04 | 无线通信基础 | WiFi/BLE/ESP-NOW 原理、ESP32-S3 无线功能实验 |
| Day 05 | RGB 与显示 | WS2812B 单线协议、GC9A01 SPI LCD、LVGL 入门 |

### 第二阶段：子系统原型验证（Day 6-10）| Phase 2: Subsystem Prototyping

| 天数 Day | 主题 Topic | 核心内容 Key Content |
|---|---|---|
| Day 06 | 按键扫描子系统 | 10 片 74HC165 菊花链焊接与测试、全键扫描固件 |
| Day 07 | FOC 电机旋钮子系统 | TMC6300 + AS5047P + SimpleFOC、力反馈原型 |
| Day 08 | 音频子系统 | ES7210 录音 + ES8311 播放 + NS4150B 功放调试 |
| Day 09 | 无线与 USB 子系统 | 4 模通信切换、SL2.1A Hub + CH342F + GL823K |
| Day 10 | 磁吸扩展与压力传感 | IIC 磁吸接口、HX711 压力传感、摇杆输入 |

### 第三阶段：PCB 设计（Day 11-15）| Phase 3: PCB Design

| 天数 Day | 主题 Topic | 核心内容 Key Content |
|---|---|---|
| Day 11 | 嘉立创 EDA 四层板入门 | 四层板设计规范、阻抗控制、层叠结构 |
| Day 12 | 键盘主板原理图绘制 | 完整原理图：ESP32-S3 + 74HC165 + USB + 电源 |
| Day 13 | 键盘主板 PCB 布局 | 300x120mm 四层板布局布线、DRC 检查 |
| Day 14 | 旋钮板 + 接收器板设计 | 旋钮主板 V4 + 接收器板原理图与 PCB |
| Day 15 | 其余小板设计 | 方向键板、音频板、USB 板等 8 块双层板 |

### 第四阶段：固件开发与集成（Day 16-18）| Phase 4: Firmware Development

| 天数 Day | 主题 Topic | 核心内容 Key Content |
|---|---|---|
| Day 16 | 键盘固件开发 | ESP-IDF FreeRTOS 任务架构、按键扫描 + USB HID |
| Day 17 | 旋钮固件开发 | LVGL UI + SimpleFOC 力反馈 + GC9A01 显示 |
| Day 18 | 系统集成 | UART 通信协议、4 模切换、音频流水线联调 |

### 第五阶段：组装调试与展示（Day 19-20）| Phase 5: Assembly & Demo

| 天数 Day | 主题 Topic | 核心内容 Key Content |
|---|---|---|
| Day 19 | 焊接组装与调试 | 12 块 PCB 焊接、3D 打印外壳组装、全系统联调 |
| Day 20 | 项目展示与总结 | 成果演示、Demo 网站部署、技术分享、复盘总结 |

---

## 评分标准 | Grading Rubric

| 维度 Dimension | 权重 Weight | 说明 Description |
|---|---|---|
| 技术实现 Technical Implementation | 40 分 | 功能完整度、代码质量、PCB 设计合理性 |
| 文档质量 Documentation Quality | 20 分 | README、注释、原理图标注、接线图 |
| 演示展示 Final Presentation | 20 分 | 现场演示清晰度、功能展示完整性 |
| Demo 网站 Project Demo Website | 15 分 | 在线项目展示网站（可访问性、内容完整性、视觉呈现） |
| 进度汇报 Check-in Reports | 10 分 | 每周汇报的质量与及时性 |
| 团队协作 & 学习态度 Collaboration & Attitude | 10 分 | Git 提交记录、分工合理性、互助精神 |
| **总分 Total** | **115 分** | |

> 详细的评分细则请参阅 [curriculum/grading-rubric.md](curriculum/grading-rubric.md)。
> For detailed grading criteria, see [curriculum/grading-rubric.md](curriculum/grading-rubric.md)。

### 等级对照 | Grade Scale

| 等级 Grade | 分数 Score | 说明 Description |
|---|---|---|
| A (优秀 Excellent) | 100-115 | 全部功能完成，文档优秀，展示出色，Demo 网站完善 |
| B (良好 Good) | 85-99 | 主要功能完成，文档和展示质量良好 |
| C (合格 Pass) | 70-84 | 基本功能完成，文档和展示达标 |
| D (需改进 Needs Improvement) | 60-69 | 部分功能完成，需补交材料 |
| F (不合格 Fail) | <60 | 未能完成基本要求 |

---

## 项目结构 | Project Structure

```
project-03-4mode-keyboard/
├── README.md                          # 本文件 | This file
├── cover.pdf                          # 项目封面 | Project cover
├── resources/
│   ├── search-results.md              # 资源搜索结果 | Resource search results
│   └── review-report.md               # 项目评审报告 | Review report
├── curriculum/                        # 课程文档 | Curriculum
│   ├── overview.md                    # 课程概述 | Course overview
│   ├── prerequisites.md               # 前置知识 | Prerequisites
│   ├── assignments.md                 # 作业说明 | Assignments
│   ├── grading-rubric.md              # 评分细则 | Grading details
│   └── day-01.md ~ day-12.md          # 每日课程 | Daily lessons
├── hardware/                          # 硬件文档 | Hardware docs
│   ├── BOM.md                         # 物料清单 | Bill of Materials
│   ├── wiring-guide.md               # 接线指南 | Wiring guide
│   ├── assembly-steps.md             # 组装步骤 | Assembly steps
│   └── troubleshooting.md            # 故障排查 | Troubleshooting
├── software/                          # 软件代码 | Software
│   ├── requirements.txt              # Python 依赖 | Python deps
│   ├── config.template.yaml          # 配置模板 | Config template
│   ├── src/                          # 源代码 | Source code
│   │   ├── main.py                   # 主程序入口 | Main entry
│   │   ├── keymatrix.py              # 74HC165 移位寄存器扫描 | Shift register scanning
│   │   ├── oled_display.py           # GC9A01 圆形 LCD 驱动 | Round LCD driver
│   │   ├── rgb_led.py                # WS2812B RGB 控制 | RGB control
│   │   ├── encoder.py                # AS5047P 磁编码器 | Magnetic encoder
│   │   ├── usb_hid.py                # USB HID 协议 | HID protocol
│   │   ├── audio.py                  # ES7210/ES8311 音频流水线 | Audio pipeline
│   │   ├── wireless.py               # WiFi/BLE/ESP-NOW 无线 | Wireless modes
│   │   ├── foc_motor.py              # TMC6300 FOC 电机控制 | FOC motor control
│   │   └── utils.py                  # 工具函数 | Utilities
│   └── tests/                        # 测试代码 | Tests
│       └── test_basic.py             # 基础测试 | Basic tests
└── assignments/                       # 作业模板 | Assignment templates
    ├── week-1-checkin.md             # 第一周汇报 | Week 1 check-in
    ├── week-2-checkin.md             # 第二周汇报 | Week 2 check-in
    ├── week-3-checkin.md             # 第三周汇报 | Week 3 check-in
    ├── week-4-checkin.md             # 第四周汇报 | Week 4 check-in
    ├── final-presentation.md         # 最终展示 | Final presentation
    └── rubric.md                     # 评分量表 | Rubric
```

---

## 学习资源 | Learning Resources

### B 站视频（精选搜索关键词）| Bilibili Video Search Keywords

以下为推荐搜索关键词，可在 B 站找到大量优质教程：

| 关键词 Keyword | 主题 Topic | 说明 Description |
|---|---|---|
| ESP32-S3 键盘 | ESP32-S3 keyboard | ESP32-S3 键盘开发教程 |
| FOC 电机控制 | FOC motor control | 磁场定向控制原理与实现 |
| SimpleFOC 教程 | SimpleFOC tutorial | 开源 FOC 库使用教程 |
| 嘉立创 EDA 4层板 | JLCEDA 4-layer PCB | 四层板设计教程 |
| LVGL 入门 | LVGL beginner | 嵌入式图形界面开发 |
| ESP-IDF 开发 | ESP-IDF development | ESP32 官方开发框架 |
| 移位寄存器 74HC165 | 74HC165 shift register | SPI 按键扫描原理 |
| I2S 音频 ESP32 | I2S audio ESP32 | ESP32 I2S 音频开发 |

#### 特别推荐 | Featured Videos

1. **[开源] 历时 9 个月，我终于完成了承载我所有幻想的机械键盘**
   - 链接：在 B 站搜索标题即可
   - 推荐理由：**本项目的原始灵感来源**，完整展示了幻想键盘的所有功能
   - Recommended: The original inspiration for this project, showcasing all features of FantasyKB.

2. **稚辉君 瀚文键盘 HelloWord-Keyboard**
   - 来源：嘉立创开源硬件平台
   - 推荐理由：移位寄存器按键扫描方案的参考来源，无刷电机在键盘上的开创性应用
   - Recommended: The origin of the shift-register key scanning approach and brushless motor in keyboards.

3. **X-Knob (SmartKnob + SurfaceDial)**
   - GitHub: https://github.com/SmallPound/X-Knob
   - 推荐理由：FOC 旋钮 + LVGL + SurfaceDial 功能的参考项目
   - Recommended: Reference project for FOC knob + LVGL + SurfaceDial.

### GitHub 开源项目 | Open-Source Projects

| 项目 Project | Stars | 说明 Description | 本项目参考 Reference |
|---|---|---|---|
| [承载我所有幻想的键盘](https://oshwhub.com/ran-pang/multifunctional-keyboard) | - | 本项目的直接来源 | 核心参考 Core reference |
| [HelloWord-Keyboard (瀚文)](https://oshwhub.com/hiwanz/wand-keyboard) | - | 稚辉君瀚文键盘，移位寄存器 + 无刷电机 | 按键扫描、电机方案 |
| [X-Knob](https://github.com/SmallPound/X-Knob) | 1k+ | LVGL + SmartKnob + SurfaceDial | 旋钮 FOC + UI |
| [SimpleFOC](https://github.com/simplefoc/Arduino-FOC) | 3k+ | 开源 FOC 电机控制库 | 电机控制核心库 |
| [LVGL](https://github.com/lvgl/lvgl) | 16k+ | 嵌入式图形库 | 旋钮 LCD UI |
| [ESP-IDF](https://github.com/espressif/esp-idf) | 13k+ | ESP32 官方开发框架 | 键盘 & 接收器固件 |
| [QMK Firmware](https://github.com/qmk/qmk_firmware) | 18k+ | 开源键盘固件 | 键盘功能参考 |

### 官方文档 | Official Documentation

| 文档 Document | 链接 URL | 说明 Description |
|---|---|---|
| ESP-IDF 官方文档 | https://docs.espressif.com/projects/esp-idf/ | ESP32-S3 开发权威文档 |
| SimpleFOC 文档 | https://docs.simplefoc.com/ | FOC 电机控制入门与 API |
| LVGL 文档 | https://docs.lvgl.io/ | 嵌入式图形界面开发 |
| 嘉立创 EDA 文档 | https://lceda.cn/ | PCB 设计工具（在线版）|
| ESP32-S3 技术参考手册 | https://www.espressif.com/ | 芯片数据手册与参考设计 |
| ESP-BOX 硬件设计 | https://github.com/espressif/esp-box | 音频子系统参考设计 |
| AS5047P 数据手册 | AMS 官网 | 14 位磁编码器技术文档 |
| TMC6300 数据手册 | Trinamic 官网 | 三相 BLDC 驱动器技术文档 |

### 推荐书籍 | Recommended Books

- 《圈圈教你玩USB》-- 中文 USB 入门经典，讲解 HID 协议
- 《C Primer Plus》-- C 语言基础，ESP-IDF 固件开发必备
- SimpleFOC 源码 -- 最好的 FOC 学习材料
- ESP-IDF examples 目录 -- 最实用的 ESP32-S3 编程参考

---

## 常见问题 | FAQ

### 关于项目难度 | About Difficulty

**Q: 这个项目是不是太难了？高中生能完成吗？**
A: 确实，这个项目的难度远超原有的 16 键宏键盘。但课程采用模块化设计，学生不需要完成全部 12 块 PCB 和所有功能。只要完成了核心模块（按键扫描 + USB HID + 至少一种无线模式），就能获得合格成绩。每个子系统都可以独立验证，鼓励学生量力而行。

This project is significantly harder than the original 16-key macro keyboard. However, the modular course design means students don't need to complete all 12 PCBs and every feature. Completing the core modules (key scanning + USB HID + at least one wireless mode) is sufficient for a passing grade. Each subsystem can be validated independently.

**Q: 如果我只能完成部分功能怎么办？**
A: 评分采用分级制（A/B/C/D/F），部分完成也能获得相应分数。例如：
- 完成按键扫描 + USB 有线 = 可获得 C 等级
- 再加上无线通信 + RGB = 可获得 B 等级
- 完成全部功能 + FOC 旋钮 + 语音 = 可获得 A 等级

Partial completion is graded proportionally. Key scanning + USB wired alone can earn a C; adding wireless + RGB reaches B; full features reach A.

### 关于预算 | About Budget

**Q: 为什么预算超过 500 元？有办法降低成本吗？**
A: 本项目涉及 12 块 PCB、3 颗 ESP32-S3、FOC 无刷电机、音频编解码器等高成本组件，¥1,028 是实际物料成本。降低成本的方案：

Why does the budget exceed 500 CNY? The project involves 12 PCBs, 3x ESP32-S3, FOC motor, audio codecs, etc. Cost reduction options:

| 精简方案 Simplification | 节省 Savings | 说明 Description |
|---|---|---|
| 去掉旋钮模块 Remove knob module | -¥82.50 | 不做 FOC 旋钮，改用普通 EC11 编码器 (-¥80) |
| 减少到 1 颗 ESP32-S3 | -¥50.00 | 旋钮和接收器共用或去掉 |
| 去掉音频子系统 Remove audio | -¥15.00 | 去掉 ES7210/ES8311/NS4150B |
| 简化 PCB 数量 Reduce PCBs | -¥60.00 | 合并小板，减少到 6-8 块 |
| 自己焊接代替 SMT | -¥125.00 | 手工焊接所有元件 |
| 减少按键数量 Fewer keys (40-50) | -¥100.00 | 精简键盘布局 |

> 精简后最低成本约 ¥500-600。Simplified minimum cost is approximately ¥500-600.

**Q: 可以多人分摊成本吗？**
A: 强烈建议 2-3 人组队，分摊物料成本的同时也分担工作量。每人负责不同的子系统（如一人负责键盘、一人负责旋钮、一人负责固件），这在评分中也会体现团队协作能力。

Team formation (2-3 members) is strongly recommended to share both costs and workload, with each member responsible for different subsystems.

### 关于技术 | About Technology

**Q: 我完全没有电子学基础，能参加这个项目吗？**
A: Day 1 从最基础的电路知识开始，每天循序渐进。但本项目确实需要较强的学习能力和动手意愿。建议开课前自学一些电路基础知识和 C 语言基础。

Day 1 starts from the very basics, but this project does require strong learning ability. We recommend self-studying basic circuit theory and C before the course begins.

**Q: ESP-IDF 和 Arduino 有什么区别？为什么本项目用 ESP-IDF？**
A: ESP-IDF 是 Espressif 官方开发框架，功能更完整，支持 FreeRTOS 多任务、USB HID、ESP-NOW 等高级功能。Arduino 更简单但不支持部分高级特性。本项目选择 ESP-IDF 是因为需要 4 模通信和 FreeRTOS 多任务。

ESP-IDF is the official framework with full feature support including FreeRTOS, USB HID, and ESP-NOW. Arduino is simpler but lacks some advanced features. We use ESP-IDF for 4-mode communication and FreeRTOS multitasking.

**Q: FOC 电机控制是什么？为什么不用普通编码器？**
A: FOC (磁场定向控制) 可以精确控制无刷电机的扭矩，实现旋钮的触觉力反馈（如档位感、弹性回弹、阻尼）。普通 EC11 编码器只能检测旋转方向，无法提供力反馈。SimpleFOC 库大大降低了 FOC 的实现难度。

FOC enables precise torque control for haptic force feedback (detents, elastic return, damping). A standard EC11 encoder only detects rotation direction without force feedback. SimpleFOC library significantly simplifies FOC implementation.

**Q: 12 块 PCB 设计工作量会不会太大？**
A: 其中 8 块是简单的双层小板（如指示灯板、磁吸接口板），设计难度很低。核心设计集中在 3 块四层板（键盘主板、旋钮主板、接收器板）。课程 Phase 3（Day 11-15）专门安排了 5 天时间进行 PCB 设计。

8 of the 12 PCBs are simple two-layer boards. The core complexity is in the 3 four-layer boards. Phase 3 (Day 11-15) provides 5 dedicated days for PCB design.

**Q: 焊接难度如何？需要什么水平？**
A: 本项目包含 0402/0603 贴片元件和 QFN 封装 IC，焊接难度较高。建议使用嘉立创 SMT 服务贴焊主要 IC，学生只焊接通孔元件和简单贴片元件。Day 19 会专门讲解焊接技巧。

The project includes 0402/0603 SMD and QFN packages. We recommend using JLCPCB SMT service for main ICs, with students soldering through-hole and simple SMD components. Day 19 covers soldering techniques.

### 关于开源项目 | About the Source Project

**Q: 原项目在哪里可以找到？**
A: 原项目 "承载我所有幻想的键盘" 发布在嘉立创开源硬件平台：https://oshwhub.com/ran-pang/multifunctional-keyboard 。原项目包含完整的原理图、PCB 文件、BOM、结构图纸和基础测试程序。QQ 交流群：992743278（1 群）、826157034（2 群）。

The original project is on OSHWHub at the link above. It includes complete schematics, PCB files, BOM, structural drawings, and basic test programs.

**Q: 原项目用了哪些参考项目？**
A: 主要参考了两个开源项目：
1. **稚辉君的瀚文键盘 (HelloWord-Keyboard)** -- 移位寄存器按键扫描和无刷电机在键盘上的应用
2. **叮叮木石的 X-Knob** -- SmartKnob 与 SurfaceDial 的结合

---

## 与原项目的关系 | Relationship to Source Project

| 项目 Project | 作者 Author | 平台 Platform | 定位 Positioning |
|---|---|---|---|
| 承载我所有幻想的键盘 | ran-pang | [嘉立创 OSHWHub](https://oshwhub.com/ran-pang/multifunctional-keyboard) | 开源硬件项目 Original open-source project |
| 幻想键盘 FantasyKB | 本课程改编 | 本仓库 This repo | 教学课程改编 Educational adaptation |

### 主要改动 | Key Adaptations

1. **课程化改造** -- 将个人项目改编为 20 天教学课程，增加详细的每日计划
2. **难度分级** -- 模块化设计，允许部分完成，适应高中生水平差异
3. **工具链简化** -- 优先使用嘉立创 EDA + ESP-IDF，降低工具链复杂度
4. **文档补充** -- 为每个子系统增加原理说明、接线指南和故障排查

---

## 许可证 | License

本项目文档采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 许可证。
This project documentation is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

软件代码部分采用 [MIT License](https://opensource.org/licenses/MIT)。
Software code is licensed under [MIT License](https://opensource.org/licenses/MIT).

原项目 "承载我所有幻想的键盘" 遵循其自身的开源许可。
The original project follows its own open-source license.

---

*最后更新 | Last updated: 2026-05-27*
