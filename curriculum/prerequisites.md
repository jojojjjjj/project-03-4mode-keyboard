# 前置知识 | Prerequisites

## 知识要求 | Knowledge Requirements

### 必须具备 | Required

| 领域 Area | 具体要求 Specifics | 说明 Notes |
|---|---|---|
| **数学基础** | 初中数学水平，理解电阻并联/串联计算 | 欧姆定律 V = I x R |
| **英语能力** | 能阅读简单的英文技术文档 | QMK 文档和代码为英文 |
| **计算机操作** | 熟练使用 Windows 系统，会安装软件 | 需要安装开发环境 |
| **打字能力** | 能使用键盘输入代码 | 编程练习需要 |

### 建议具备 | Recommended (Not Required)

| 领域 Area | 具体建议 Suggestions |
|---|---|
| **编程经验** | 有任何编程语言基础（Python/C/Scratch 均可） |
| **电子学接触** | 玩过 Arduino、搭过简单电路（LED + 电阻） |
| **焊接经验** | 见过或尝试过焊接（非必须，Day 10 会教） |
| **Linux 基础** | 了解基本命令行操作（QMK 编译环境基于 Linux 工具链） |

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

| 软件 Software | 下载地址 Download | 版本 Version |
|---|---|---|
| **VS Code** | https://code.visualstudio.com/ | 最新稳定版 |
| **Git** | https://git-scm.com/download/win | 最新版 |
| **Python 3.10+** | https://www.python.org/downloads/ | 3.10 或更高 |
| **嘉立创 EDA**（可选） | https://lceda.cn/ | 在线版，无需安装 |
| **QMK MSYS** | https://msys.qmk.fm/ | 开课后安装（Day 8） |
| **QMK Toolbox** | https://github.com/qmk/qmk_toolbox/releases | 开课后安装（Day 9） |

> **提示**：嘉立创 EDA 为网页版，使用 Chrome 或 Edge 浏览器即可。QMK 相关工具在 Day 8 前安装即可。
> Note: JLCEDA is web-based — use Chrome or Edge. QMK tools can be installed by Day 8.

---

## 课前自学建议 | Pre-course Self-study

如果你是完全零基础，建议在开课前花 2-3 天完成以下自学：

If you have no background, spend 2-3 days on these before the course:

### 第 1 天：电路基础 (2-3 小时)
- 观看 B 站搜索 "欧姆定律 入门讲解"
- 了解电压(V)、电流(A)、电阻(ohm) 的概念
- 学会使用万用表测量电压和通断
- 动手：用面包板点亮一个 LED（需要 LED + 220ohm 电阻 + 电池）

### 第 2 天：初识 Arduino (2-3 小时)
- 观看 B 站搜索 "Arduino 入门 第一课"
- 了解什么是微控制器（MCU）
- 安装 Arduino IDE，上传第一个 Blink 程序
- 了解数字输入/输出（HIGH/LOW）的概念

### 第 3 天：初识键盘原理 (1-2 小时)
- 观看 B 站搜索 "机械键盘原理 矩阵扫描"
- 了解键盘是如何检测按键的
- 思考：16 个按键最少需要几根线？

---

## 知识检查 | Knowledge Check

开课第一天（Day 1）会进行简单的知识检查，确保大家具备基础能力：

A brief knowledge check on Day 1:

1. **电路计算**：一个 LED 的工作电压是 2V，工作电流是 20mA，用 5V 电源供电，需要串联多大的限流电阻？
2. **二进制**：将十进制数 13 转换为二进制。
3. **十六进制**：将十进制数 255 转换为十六进制。
4. **逻辑门**：AND 门的两个输入都是 1，输出是什么？
5. **命令行**：在 Windows 上如何打开命令提示符（CMD）？

> 答案会在 Day 1 课程中揭晓，不用担心答错。
> Answers will be revealed in Day 1. Don't worry about getting them wrong.

---

## 常见顾虑 | Common Concerns

**"我只会 Scratch，能学吗？"**
可以。课程中的代码会一行一行讲解，不会跳步。Scratch 的逻辑思维能力对编程很有帮助。

**"我怕焊接烫到手"**
这是正常的担心。课程中会详细讲解安全规范，使用合适的温度（约 320 度），并有老师全程指导。焊锡的熔点只有约 183 度，烙铁头接触焊锡的时间很短。

**"英语不好怎么办？"**
QMK 文档虽然是英文的，但课程会提供中文讲解。遇到不理解的术语，随时问老师。

---

*最后更新 | Last updated: 2026-05-26*
