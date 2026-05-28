# 前置知识 | Prerequisites

## 知识要求 | Knowledge Requirements

### 必须具备 | Required

| 领域 Area | 具体要求 Specifics | 说明 Notes |
|---|---|---|
| **数学基础** | 初中数学水平，理解电阻并联/串联计算 | 欧姆定律 V = I x R |
| **英语能力** | 能阅读简单的英文技术文档 | ESP-IDF 文档和代码为英文 |
| **计算机操作** | 熟练使用 Windows 系统，会安装软件 | 需要安装开发环境 |
| **打字能力** | 能使用键盘输入代码 | 编程练习需要 |

### 建议具备 | Recommended (Not Required)

| 领域 Area | 具体建议 Suggestions |
|---|---|
| **编程经验** | 有任何编程语言基础（Python/C/Scratch 均可），Day 16-18 固件使用 C 语言 |
| **电子学接触** | 玩过 Arduino、搭过简单电路（LED + 电阻） |
| **焊接经验** | 见过或尝试过焊接（非必须，Day 19 会教 SMD 焊接） |
| **Linux 基础** | 了解基本命令行操作（ESP-IDF 构建使用命令行） |

---

## 核心技术预备 | Technical Prerequisites

### 1. SPI 通信协议 | SPI Protocol

本项目中 SPI 用于：
- 74HC165 移位寄存器菊花链（80 键扫描）
- AS5047P 磁编码器（旋钮位置反馈）
- GC9A01 圆形 LCD（旋钮显示屏）

**课前建议了解 What to Know Before:**

```
SPI (Serial Peripheral Interface) 四线制:
  - SCLK: 时钟信号 Clock
  - MOSI: 主机输出 Master Out
  - MISO: 主机输入 Master In
  - CS: 片选 Chip Select

本项目主要用 SPI 读取数据 (MISO)，MOSI 很少使用
```

**学习资源 Resources:**
- B 站搜索 "SPI 通信协议 入门"
- ESP-IDF SPI 文档：https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/peripherals/spi_master.html

### 2. I2C 通信协议 | I2C Protocol

本项目中 I2C 用于：
- ES7210 ADC（音频编解码器控制）
- ES8311 DAC（音频编解码器控制）
- OLED 显示屏（如果使用 I2C OLED）

**课前建议了解 What to Know Before:**

```
I2C (Inter-Integrated Circuit) 两线制:
  - SDA: 数据线 Data
  - SCL: 时钟线 Clock
  - 每个 I2C 设备有唯一地址（7-bit）
  - 速率：标准 100kHz / 快速 400kHz
```

**学习资源 Resources:**
- B 站搜索 "I2C 通信协议 入门"

### 3. I2S 数字音频接口 | I2S Digital Audio

本项目中 I2S 用于：
- ES7210 麦克风阵列音频采集
- ES8311 扬声器音频播放

**课前建议了解 What to Know Before:**

```
I2S (Inter-IC Sound) 三线制:
  - BCLK: 位时钟 Bit Clock
  - WS: 字选择 (左/右声道) Word Select
  - SDIN/SDOUT: 串行数据 Serial Data
```

**学习资源 Resources:**
- B 站搜索 "I2S 音频接口 原理"
- ESP-IDF I2S 文档

### 4. FreeRTOS 实时操作系统概念 | FreeRTOS Concepts

本项目的固件基于 FreeRTOS 多任务系统，Day 16 会详细讲解。

**课前建议了解 What to Know Before:**

```
FreeRTOS 核心概念:
  - 任务 (Task): 独立的执行线程
  - 优先级 (Priority): 数字越大优先级越高
  - 队列 (Queue): 任务间传递数据的管道
  - 信号量 (Semaphore): 任务间同步信号
  - 互斥锁 (Mutex): 保护共享资源
```

**学习资源 Resources:**
- FreeRTOS 官方中文文档：https://www.freertos.org/zh-cn-cmn-s/
- B 站搜索 "FreeRTOS 入门 教程"

### 5. 4 层 PCB 概念 | 4-Layer PCB Concepts

本项目的主控板、旋钮板和接收器板使用 4 层 PCB，Day 13-14 会详细讲解。

**课前建议了解 What to Know Before:**

```
4 层板典型层叠 (信号-地-电源-信号):
  Layer 1 (Top):    信号层 (元件、走线)
  Layer 2 (Inner1): 地平面 (完整 GND)
  Layer 3 (Inner2): 电源平面 (3V3/5V)
  Layer 4 (Bottom): 信号层 (辅助走线)
```

---

## 工具准备 | Tool Preparation

### 学生自备 | Students Bring

| 工具 Tool | 用途 Purpose | 是否必须 Required |
|---|---|---|
| 笔记本电脑（Windows 10/11） | 编程、EDA 设计、固件编译 | 必须 |
| U 盘（>= 8GB） | 文件备份与传输 | 建议 |
| 笔记本 + 笔 | 记录课堂笔记和电路图 | 建议 |

### 电脑软件预装 | Pre-install Software

请在开课前完成以下软件的安装（Day 1 会检查）：

Please install the following before Day 1:

| 软件 Software | 下载地址 Download | 版本 Version | 用途 |
|---|---|---|---|
| **VS Code** | https://code.visualstudio.com/ | 最新稳定版 | 代码编辑 |
| **Git** | https://git-scm.com/download/win | 最新版 | 版本控制 |
| **Python 3.10+** | https://www.python.org/downloads/ | 3.10 或更高 | 测试脚本 |
| **ESP-IDF v5.x** | https://docs.espressif.com/projects/esp-idf/ | v5.3+ | 固件开发 |
| **嘉立创 EDA 专业版** | https://pro.lceda.cn/ | 在线版或客户端 | PCB 设计 |
| **PlatformIO** | VS Code 插件 | 最新版 | 旋钮开发 |

> **提示**：ESP-IDF 安装较复杂，建议使用 ESP-IDF Tools Installer 一键安装。Day 2 会确认环境。嘉立创 EDA 为网页版，使用 Chrome 或 Edge 浏览器即可。

---

## 课前自学建议 | Pre-course Self-study

如果你是完全零基础，建议在开课前花 3-5 天完成以下自学：

If you have no background, spend 3-5 days on these before the course:

### 第 1 天：电路基础 (2-3 小时)
- 观看 B 站搜索 "欧姆定律 入门讲解"
- 了解电压(V)、电流(A)、电阻(ohm) 的概念
- 学会使用万用表测量电压和通断
- 动手：用面包板点亮一个 LED

### 第 2 天：初识 ESP32 (2-3 小时)
- 观看 B 站搜索 "ESP32 入门 第一课"
- 了解什么是微控制器（MCU）
- 安装 ESP-IDF，尝试编译 Hello World
- 了解 GPIO 输入/输出的概念

### 第 3 天：通信协议基础 (2-3 小时)
- 观看 B 站搜索 "SPI I2C 通信协议 对比 入门"
- 了解 SPI 和 I2C 的基本工作方式
- 不需要完全理解，有概念即可

### 第 4 天：键盘原理 (1-2 小时)
- 观看 B 站搜索 "机械键盘原理 矩阵扫描"
- 了解键盘是如何检测按键的
- 了解 USB HID 是什么

### 第 5 天：PCB 基础概念 (1-2 小时)
- 观看 B 站搜索 "PCB 印刷电路板 入门"
- 了解 PCB 的基本结构（铜层、阻焊、丝印）
- 注册嘉立创 EDA 账号

---

## 知识检查 | Knowledge Check

开课第一天（Day 1）会进行简单的知识检查，确保大家具备基础能力：

A brief knowledge check on Day 1:

1. **电路计算**：LED 工作电压 2V，电流 20mA，5V 电源供电，需要多大限流电阻？
2. **二进制**：将十进制数 13 转换为二进制。
3. **十六进制**：将十进制数 255 转换为十六进制。
4. **逻辑门**：AND 门的两个输入都是 1，输出是什么？
5. **通信协议**：SPI 和 I2C 各需要几根信号线？
6. **FreeRTOS**：什么是任务（Task）的优先级？

> 答案会在 Day 1 课程中揭晓，不用担心答错。
> Answers will be revealed in Day 1. Don't worry about getting them wrong.

---

## 常见顾虑 | Common Concerns

**"我只会 Scratch，能学吗？"**
可以。课程中的代码会一行一行讲解，不会跳步。Day 16-18 的 C 语言固件也会从最基础的 ESP-IDF 模板开始。

**"我怕焊接烫到手"**
这是正常的担心。Day 19 会详细讲解 SMD 焊接安全规范，并有老师全程指导。本项目使用锡膏+回流焊方法，烙铁使用时间很少。

**"英语不好怎么办？"**
ESP-IDF 文档虽然是英文的，但课程会提供中文讲解。遇到不理解的术语，随时问老师。

**"12 块 PCB 会不会太多了？"**
Day 11-15 有充足的时间，并且很多子板非常简单（方向键板只有 4 个按键）。主控板是最复杂的，会花最多时间。

---

*最后更新 | Last updated: 2026-05-27*
