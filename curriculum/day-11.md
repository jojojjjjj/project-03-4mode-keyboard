# Day 11: PCB设计入门 — 嘉立创EDA | PCB Design Fundamentals — JLCEDA

> **今日目标 Today's Goals:**
> - 理解 PCB 的基本结构：铜层、过孔、走线、焊盘、丝印
> - 熟悉嘉立创 EDA 专业版界面和基本操作
> - 学会创建元件封装（Footprint）和原理图符号
> - 完成一个简单的 2 层练习板设计
>
> **产出 Deliverable:** 自定义元件封装 + 2 层 breakout board 原理图

---

## 时间安排 | Schedule

| 时间 Time | 活动类型 Type | 内容 Content |
|---|---|---|
| 09:00–09:15 | 晨会 | 第三阶段介绍，PCB 设计的意义 |
| 09:15–10:30 | 讲解 | PCB 基础概念 + 嘉立创 EDA 界面导览 |
| 10:30–10:45 | 休息 | — |
| 10:45–12:00 | 实验 | 创建元件封装 + 简单 2 层 breakout 板 |
| 12:00–13:30 | 午休 | — |
| 13:30–15:00 | 实验 | 原理图符号 + 网络标签 + ERC 检查 |
| 15:00–15:15 | 休息 | — |
| 15:15–16:30 | 实验 | 完成练习原理图 + DRC 基础 |
| 16:30–17:00 | 总结 | 日终回顾 + 明日预告 |

---

## 上午：PCB 基础概念与 EDA 导览 | Morning: PCB Basics & EDA Tour

### 为什么要学这个? | Why Learn This?

前面 10 天我们在面包板上搭建原型，用 ESP-IDF 编写固件。但面包板电路松散、接触不稳定、无法携带。PCB（Printed Circuit Board，印刷电路板）将电路永久固化在板子上——可靠、紧凑、专业。本项目共有 12 块不同的 PCB，从今天开始你将逐一学会设计它们。

The previous 10 days used breadboard prototypes and ESP-IDF firmware. But breadboard circuits are loose, unreliable, and not portable. A PCB permanently fixes the circuit — reliable, compact, professional. This project has 12 different PCBs, and starting today you will learn to design them all.

---

### 任务 11.1: PCB 基础概念 (40 分钟)

**PCB 结构 PCB Structure:**

```
横截面 Cross-section (4-layer board):

  ┌──────────────────────────────┐
  │  丝印层 Silkscreen (文字标识)   │
  ├──────────────────────────────┤
  │  阻焊层 Solder Mask (绿色/黑色)  │
  ├──────────────────────────────┤
  │  顶层铜 Top Copper (信号走线)    │  ← Layer 1 (Signal)
  ├──────────────────────────────┤
  │  介质层 Prepreg (绝缘材料)       │
  ├──────────────────────────────┤
  │  内层1 Inner 1 (GND 地平面)     │  ← Layer 2 (Ground)
  ├──────────────────────────────┤
  │  介质层 Core (绝缘材料)          │
  ├──────────────────────────────┤
  │  内层2 Inner 2 (电源平面)       │  ← Layer 3 (Power)
  ├──────────────────────────────┤
  │  介质层 Prepreg (绝缘材料)       │
  ├──────────────────────────────┤
  │  底层铜 Bottom Copper (信号)    │  ← Layer 4 (Signal)
  ├──────────────────────────────┤
  │  阻焊层 Solder Mask            │
  ├──────────────────────────────┤
  │  丝印层 Silkscreen             │
  └──────────────────────────────┘

  过孔 Via: 连接不同铜层的导电孔
  ┌──┐        ┌──┐
  │●│ ──>    │ │ │ ──> 通孔过孔 (Through-hole Via)
  └──┘        │ │ │              盲孔 (Blind Via)
              │ ● │              埋孔 (Buried Via)
              └───┘
```

**核心术语 Key Terms:**

| 术语 Term | 英文 | 说明 |
|---|---|---|
| 铜层 | Copper Layer | 承载电气连接的铜箔层 |
| 走线 | Trace / Track | 铜层上的导电路径 |
| 焊盘 | Pad | 用于焊接元件的铜区域 |
| 过孔 | Via | 连接不同铜层的镀铜孔 |
| 丝印 | Silkscreen | 板上的文字和图形标识 |
| 阻焊 | Solder Mask | 保护铜层，防止焊接短路（绿色/黑色/蓝色） |
| 封装 | Footprint | 元件在 PCB 上的焊盘图案 |

**线宽与电流关系 Trace Width vs Current:**

| 线宽 Width | 承载电流 Current (1oz铜) | 典型用途 Application |
|---|---|---|
| 0.15mm (6mil) | ~0.3A | 细密信号线 |
| 0.25mm (10mil) | ~0.5A | 一般信号线 |
| 0.5mm (20mil) | ~1.0A | 电源线（小功率） |
| 1.0mm (40mil) | ~2.0A | 电源线（大功率） |
| 2.0mm (80mil) | ~4.0A | 电池/主电源 |

---

### 任务 11.2: 嘉立创 EDA 专业版导览 (35 分钟)

**注册与登录 Registration:**
1. 访问 https://pro.lceda.cn/ 或打开已安装的嘉立创 EDA 专业版
2. 使用手机号注册/登录
3. 创建新工程：`4mode-keyboard`

**界面布局 Interface Layout:**

```
┌───────────────────────────────────────────────────┐
│  菜单栏 Menu: 文件/编辑/视图/放置/工具/...           │
├────────┬──────────────────────────────┬────────────┤
│        │                              │            │
│ 元件库  │     主绘图区                   │   属性面板   │
│ Library│     Canvas                    │  Properties│
│ 面板    │                              │            │
│        │                              │            │
│ - 原理图 │                              │  - 元件属性  │
│ - PCB   │                              │  - 网络属性  │
│ - 元件   │                              │  - 约束规则  │
│        │                              │            │
├────────┼──────────────────────────────┼────────────┤
│ 设计树  │     坐标/网格/单位/层切换         │   DRC 面板   │
│ Design │     Status Bar                │            │
│ Tree   │                              │            │
└────────┴──────────────────────────────┴────────────┘
```

**快捷键速查 Essential Shortcuts:**

| 快捷键 | 功能 |
|---|---|
| W | 放置导线 Wire |
| L | 放置网络标签 Net Label |
| P | 放置元件 Component |
| Ctrl+Z | 撤销 |
| Ctrl+S | 保存 |
| Space | 切换走线角度 |
| Tab | 切换到 PCB 编辑器 |
| V | 放置过孔 Via |

---

### 任务 11.3: 创建第一个元件封装 (75 分钟)

**封装设计步骤 Footprint Design Steps:**

我们以 WS2812B RGB LED 为例，设计其封装。

1. **查找数据手册尺寸** Find datasheet dimensions:
   - WS2812B-2020 封装：2.0mm x 2.0mm
   - 焊盘尺寸：0.6mm x 0.7mm
   - 焊盘间距：0.5mm

2. **创建封装 Create Footprint:**
   - 在工程中新建 PCB 封装库
   - 放置 4 个焊盘（SMD 类型）
   - 设置焊盘尺寸和位置
   - 添加丝印轮廓
   - 添加 1 脚标识（极性标记）

3. **保存并关联符号 Save & Link:**
   - 创建对应的原理图符号
   - 将符号与封装关联

```
WS2812B-2020 封装俯视图:

         ┌─────────┐
    DOUT ●1       4● VDD
         │         │
         │  WS2812B │
         │  2020    │
         │         │
    GND  ●2       3● DIN
         └─────────┘

焊盘排列 (bottom view):
  ┌─────────┐
  │ ●     ● │  ← Pad 1 (DOUT), Pad 4 (VDD)
  │         │
  │ ●     ● │  ← Pad 2 (GND), Pad 3 (DIN)
  └─────────┘
```

---

## 下午：原理图符号与 ERC 检查 | Afternoon: Schematic Symbols & ERC

### 任务 11.4: 原理图绘制练习 (90 分钟)

**练习：绘制 ESP32-S3 最小系统外围电路**

```
ESP32-S3 最小系统所需外围:

1. 电源去耦电容（每对 VDD/GND 一个 100nF）
2. 晶振电路（40MHz 晶振 + 2x 10pF 电容，如果使用外部晶振）
3. BOOT 模式选择（GPIO0 / GPIO46 上拉/下拉电阻）
4. EN 复位电路（EN 引脚上拉 + 按键）
5. USB 连接（D+/D- 直连或通过 ESD 保护）
```

**步骤 Steps:**
1. 在原理图中放置 ESP32-S3 符号
2. 添加电源符号（VDD_3V3、GND）
3. 连接去耦电容
4. 添加网络标签（ESP_TX、ESP_RX、SPI_CLK 等）
5. 运行 ERC（Electrical Rules Check）

---

### 任务 11.5: ERC 检查与错误修复 (75 分钟)

**常见 ERC 错误 Common ERC Errors:**

| 错误类型 Error | 含义 Meaning | 修复方法 Fix |
|---|---|---|
| 单端网络 Single-pin net | 一个网络只连了一个引脚 | 检查是否漏连或需要添加 No ERC 标记 |
| 电源引脚未驱动 Power pin not driven | 电源网络没有电源输入 | 添加电源符号或 PWR_FLAG |
| 输入引脚悬空 Input pin floating | 输入引脚未连接 | 添加上拉/下拉电阻或接地 |
| 重复网络名 Duplicate net name | 两个不同网络有相同名称 | 修改网络标签 |
| 未连接引脚 Unconnected pin | 引脚未连接 | 检查是否需要连接或标记 NC |

---

## 日终总结 | Daily Wrap-up (16:30-17:00)

**今日关键词 Key Takeaways:**
1. PCB 由多层铜箔和绝缘介质叠加而成，走线、焊盘、过孔是三大核心要素
2. 线宽决定电流承载能力——电源线要粗，信号线可以细
3. 嘉立创 EDA 是国产免费工具，直接对接嘉立创打样服务
4. ERC 是原理图层面的电气规则检查，必须在进入 PCB 前通过

---

## 今日作业 | Homework

1. **完成练习原理图**：ESP32-S3 最小系统外围 + 至少 3 个自定义封装
2. **截图提交**：原理图全貌 + ERC 检查通过截图
3. **回答思考题**：
   - 4 层板相比 2 层板有什么优势？为什么本项目需要 4 层板？
   - 过孔有哪些类型？各适用于什么场景？
   - 为什么去耦电容要尽量靠近 IC 的电源引脚？

---

## 明日预告 | Tomorrow's Preview

明天我们将正式绘制键盘主控板的完整原理图，包括 ESP32-S3 最小系统、电源树（TP4056 + HX3608 + ME6217）、74HC165 移位寄存器链、以及 USB 子系统。

Tomorrow we draw the complete keyboard mainboard schematic, including the ESP32-S3 minimum system, power tree (TP4056 + HX3608 + ME6217), 74HC165 shift register chain, and USB subsystem.

---

## 参考资源 | References

- 嘉立创 EDA 专业版：https://pro.lceda.cn/
- 嘉立创 EDA 教程：https://pro.lceda.cn/editor_doc
- WS2812B 数据手册：https://www.worldsemi.com/
- B 站搜索 "嘉立创 EDA 入门教程"
- [不专业教学] 零基础绘制机械键盘 PCB（浚达良）：https://www.bilibili.com/video/BV1vz4y127qL/
- 嘉立创开源硬件平台：https://oshwhub.com/ran-pang/multifunctional-keyboard

---

*最后更新 | Last updated: 2026-05-27*
