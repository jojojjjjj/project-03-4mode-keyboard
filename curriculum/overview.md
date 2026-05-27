# 课程概述 | Course Overview

## 项目名称 | Project Name
**4模式机械键盘 "幻想键盘"** | **4-Mode Mechanical Keyboard "FantasyKB"**

> 支持WIFI的4模机械键盘（USB、蓝牙BLE、WiFi、2.4GHz ESP-NOW），搭载可拆卸FOC无刷电机旋钮屏（支持SurfaceDial），支持多功能磁吸扩展（例如小键盘等），支持语音交互。
>
> A 4-mode mechanical keyboard supporting USB, Bluetooth BLE, WiFi, and 2.4GHz ESP-NOW, with a detachable FOC knob display (SurfaceDial compatible), magnetic expansion modules (e.g., numpad), and voice interaction.

**开源参考项目 | Open-Source Reference:** https://oshwhub.com/ran-pang/multifunctional-keyboard

---

## 项目目标 | Project Goals

通过 20 天的集中学习，学生将完成一台功能完整的4模式机械键盘，掌握以下核心能力：

Over 20 intensive days, students will build a fully functional 4-mode mechanical keyboard, gaining these core competencies:

1. **电子电路基础** — 理解电压、电流、电阻，能独立在面包板上搭建电路，使用万用表测量参数
2. **微控制器开发** — 掌握 ESP32-S3 开发流程，理解 GPIO、定时器、中断等基本概念
3. **通信协议** — 深入理解 SPI、I2C、I2S、UART 四种主流通信协议及其应用场景
4. **无线通信系统** — 掌握蓝牙BLE（GAP/GATT）、WiFi STA/AP、ESP-NOW三种无线模式的工作原理
5. **USB子系统** — 理解USB HID协议、USB Hub拓扑、USB-TTL桥接器工作原理
6. **电源管理** — 掌握锂电池充电（TP4056）、DC-DC升压（HX3608）、LDO稳压（ME6217）等电源架构
7. **音频子系统** — 理解I2S数字音频接口、ADC/DAC编解码器（ES7210/ES8311）、麦克风阵列基础
8. **PCB设计** — 使用嘉立创EDA完成12块PCB的原理图绘制与PCB布局（4层板设计）
9. **电机控制与力反馈** — 理解FOC无刷电机控制（TMC6300）、磁编码器（AS5047P）、压力传感（HX711）
10. **嵌入式GUI开发** — 使用LVGL在圆形LCD（GC9A01）上开发现代化用户界面

---

## 课程结构 | Course Structure

```
阶段一 (Day 1-5)               阶段二 (Day 6-10)             阶段三 (Day 11-15)
电子基础与ESP32-S3入门          子系统原型验证                 PCB设计（12块板）
┌───────────────────┐          ┌───────────────────┐         ┌───────────────────┐
│ Day 1: 电子学基础   │          │ Day 6:  蓝牙BLE    │         │ Day 11: EDA工具    │
│ Day 2: ESP32-S3    │  ──>    │ Day 7:  WiFi/ESP-NOW│  ──>   │ Day 12: 主控板原理图│
│ Day 3: SPI与移位寄存│          │ Day 8:  WS2812B RGB │         │ Day 13: 子板原理图  │
│ Day 4: I2C与音频    │          │ Day 9:  FOC旋钮硬件 │         │ Day 14: PCB布局布线 │
│ Day 5: USB与电源    │          │ Day 10: FOC旋钮显示 │         │ Day 15: DRC与打样   │
└───────────────────┘          └───────────────────┘         └───────────────────┘
     面包板原型                     无线+外设验证                   12块PCB设计

                                          │
                                          v

                         阶段四 (Day 16-18)             阶段五 (Day 19-20)
                         固件开发与系统集成              组装调试与展示
                         ┌───────────────────┐         ┌───────────────────┐
                         │ Day 16: 键盘固件    │         │ Day 19: 组装调试   │
                 ──>     │ Day 17: 无线固件    │  ──>   │ Day 20: 最终展示   │
                         │ Day 18: 系统集成    │         │                   │
                         └───────────────────┘         └───────────────────┘
                              完整固件                     成品键盘
```

---

## 每日时间安排 | Daily Schedule

| 时间 Time | 活动 Activity | 时长 Duration |
|---|---|---|
| 09:00–09:15 | 晨会：回顾与计划 Morning Standup | 15 min |
| 09:15–10:30 | 知识讲解 Knowledge Lecture | 75 min |
| 10:30–10:45 | 休息 Break | 15 min |
| 10:45–12:00 | 动手实验 Hands-on Lab | 75 min |
| 12:00–13:30 | 午餐与休息 Lunch & Rest | 90 min |
| 13:30–15:00 | 项目实践 Project Work | 90 min |
| 15:00–15:15 | 休息 Break | 15 min |
| 15:15–16:30 | 项目实践（续）Project Work (cont.) | 75 min |
| 16:30–17:00 | 日终总结 Daily Wrap-up | 30 min |

> 每天约 6.5 小时有效学习时间。Approximately 6.5 hours of productive learning per day.

---

## 学习成果 | Learning Outcomes

### 知识维度 Knowledge

| 知识点 Topic | 对应课程 Day(s) | 评估方式 Assessment |
|---|---|---|
| 基本电路理论（欧姆定律、基尔霍夫定律） | Day 1 | 面包板实验 |
| 数字逻辑与二进制/十六进制 | Day 2 | 编程练习 |
| SPI通信协议与移位寄存器74HC165 | Day 3 | 按键扫描实验 |
| I2C协议与I2S数字音频 | Day 4 | 音频播放/录音实验 |
| USB协议与电源管理架构 | Day 5 | 电源预算计算 |
| 蓝牙BLE协议栈（GAP/GATT） | Day 6 | BLE键盘配对 |
| WiFi与ESP-NOW对等通信 | Day 7 | 四模切换测试 |
| WS2812B RGB灯效与功耗管理 | Day 8 | 自定义灯效编程 |
| FOC无刷电机控制与磁编码器 | Day 9 | 位置控制实验 |
| 嵌入式GUI（LVGL）与力反馈 | Day 10 | 旋钮界面演示 |
| PCB设计流程（原理图→Gerber） | Day 11-15 | 12块PCB设计文件 |
| ESP-IDF固件架构与键盘扫描 | Day 16-18 | 编译成功的固件 |

### 技能维度 Skills

- 使用万用表测量电压、电流、通断
- 在面包板上搭建和调试复杂电路
- 使用逻辑分析仪或示波器观察SPI/I2C/I2S信号
- 使用嘉立创EDA绘制原理图和多层PCB（含4层板阻抗控制）
- 编写ESP-IDF固件（C语言），实现键盘扫描与多模式通信
- 配置和使用I2S音频编解码器（ES7210/ES8311）
- 使用SimpleFOC库控制无刷电机，实现力反馈旋钮
- 使用LVGL开发嵌入式GUI界面
- 系统级调试和问题定位（硬件+软件联合排查）

### 素养维度 Competencies

- 工程思维：从需求分析到产品交付的完整流程
- 文档能力：撰写技术文档、引脚分配表、电源预算报告
- 团队协作：分工合作、代码版本管理、设计评审
- 问题解决：面对复杂系统故障的系统化排查能力

---

## 教学资源 | Teaching Resources

### 硬件工具 | Hardware Tools（教室配备 Classroom Equipment）

- 万用表（每组 1 个）
- 烙铁 + 焊台（每组 1 套）
- 面包板 + 杜邦线（每组 1 套）
- 逻辑分析仪（共用 2-3 台）
- ESP32-S3-DEVKITC-1 开发板（每组 1 块）
- 74HC165 移位寄存器模块（每组 10 个）
- ES8311 + ES7210 音频编解码模块（每组 1 套）
- WS2812B 灯带（每组 1 条）
- TMC6300 电机驱动模块 + 2204 无刷电机（每组 1 套）
- AS5047P 磁编码器模块（每组 1 个）
- GC9A01 圆形LCD显示屏（每组 1 个）
- TP4056 充电模块 + 3.7V 锂电池（每组 1 套）

### 软件工具 | Software Tools

- **ESP-IDF v5.x** — ESP32官方开发框架（含编译工具链）
- **VS Code + ESP-IDF插件** — 代码编辑与烧录
- **PlatformIO**（旋钮部分） — SimpleFOC/LVGL开发
- **嘉立创 EDA 专业版** — PCB设计（在线版）
- **Git** — 版本控制
- **Python 3.10+** — 测试脚本与辅助工具

### 在线资源 | Online Resources

- ESP-IDF 官方文档：https://docs.espressif.com/projects/esp-idf/
- ESP32-S3 技术参考手册：https://www.espressif.com/
- 嘉立创 EDA：https://lceda.cn/
- 嘉立创开源硬件平台（参考项目）：https://oshwhub.com/ran-pang/multifunctional-keyboard
- SimpleFOC 文档：https://docs.simplefoc.com/
- LVGL 文档：https://docs.lvgl.io/
- B 站教学视频（详见各Day课程中的参考资源部分）

---

## 评估体系 | Assessment System

| 评估项 Assessment Item | 满分 Points | 截止时间 Deadline |
|---|---|---|
| 技术实现 Technical Implementation | 40 分 | Day 20 |
| 文档质量 Documentation Quality | 20 分 | Day 20 |
| 演示展示 Final Presentation | 20 分 | Day 20 |
| Demo 网站 Project Demo Website | 15 分 | Day 20 |
| 进度汇报 Check-in Reports | 10 分 | Day 5 / Day 10 / Day 15 |
| 团队协作 & 学习态度 Collaboration & Attitude | 10 分 | Day 20 |
| **总分 Total** | **115 分** | |

---

## 先修要求 | Prerequisites

详见 [prerequisites.md](prerequisites.md)

---

*最后更新 | Last updated: 2026-05-27*
