# 作业说明 | Assignments Overview

## 作业体系 | Assignment System

本课程的作业分为四类：每日实验、每周进度汇报、最终展示和项目展示网站。

Assignments fall into four categories: daily labs, weekly check-in reports, final presentation, and project demo website.

---

## 一、每日实验 | Daily Labs

每天课程结束前，需要完成当天的实验任务并提交。

Each day's lab must be completed and submitted before end of day.

### 阶段一：电子基础 (Day 1-5) Phase 1: Electronics Fundamentals

| 天数 Day | 实验内容 Lab Content | 提交方式 Submission |
|---|---|---|
| Day 1 | 面包板电路 + LED 点亮 | 拍照 + 代码截图 |
| Day 2 | ESP32-S3 GPIO + 按键检测 | 代码文件 + 串口输出截图 |
| Day 3 | SPI 移位寄存器 (74HC165) 按键扫描 | 代码文件 + 串口输出 |
| Day 4 | I2C OLED + I2S 音频播放 | 拍照 + 代码文件 |
| Day 5 | USB HID 协议分析 + 电源预算计算 | 计算报告 + 代码截图 |

### 阶段二：子系统验证 (Day 6-10) Phase 2: Subsystem Verification

| 天数 Day | 实验内容 Lab Content | 提交方式 Submission |
|---|---|---|
| Day 6 | BLE 蓝牙键盘配对 | 配对截图 + 串口日志 |
| Day 7 | WiFi 键盘 + ESP-NOW 通信 | 串口日志 + 接收端截图 |
| Day 8 | WS2812B RGB 灯效编程 | 拍照/视频 + 代码文件 |
| Day 9 | FOC 无刷电机 + AS5047P 位置控制 | 代码文件 + 串口日志 |
| Day 10 | LVGL 旋钮界面显示 | 拍照/视频 + 代码文件 |

### 阶段三：PCB 设计 (Day 11-15) Phase 3: PCB Design

| 天数 Day | 实验内容 Lab Content | 提交方式 Submission |
|---|---|---|
| Day 11 | 嘉立创 EDA 封装 + 练习原理图 | EDA 文件 + ERC 截图 |
| Day 12 | 主控板完整原理图 (ESP32-S3+电源+SPI+USB) | EDA 文件 + ERC 截图 |
| Day 13 | 音频板 + LED 板原理图 + 4层板笔记 | EDA 文件 + 笔记 |
| Day 14 | 主控板 PCB 布局布线 + DRC | PCB 文件 + DRC 报告 |
| Day 15 | 全部 12 块 PCB Gerber + 嘉立创下单 | Gerber 文件 + 订单截图 |

### 阶段四：固件开发 (Day 16-18) Phase 4: Firmware Development

| 天数 Day | 实验内容 Lab Content | 提交方式 Submission |
|---|---|---|
| Day 16 | ESP-IDF 键盘扫描器 (SPI+消抖) | 代码文件 + 串口输出截图 |
| Day 17 | 4 种无线模式 (USB/BLE/WiFi/ESP-NOW) | 4 种模式串口日志 |
| Day 18 | 系统集成固件 (音频+LVGL+FOC+RGB) | 代码文件 + 运行日志 |

### 阶段五：组装展示 (Day 19-20) Phase 5: Assembly & Presentation

| 天数 Day | 实验内容 Lab Content | 提交方式 Submission |
|---|---|---|
| Day 19 | 焊接完成 + 键盘组装 | 拍照（正面+反面+组装后） |
| Day 20 | 最终展示 + 项目文档 | PPT + 视频 + Git 仓库 |

---

## 二、每周进度汇报 | Weekly Check-in Reports

### Week 1 汇报（Day 5 结束前提交）

详见 [week-1-checkin.md](../assignments/week-1-checkin.md)

内容要求：
1. **本周学习总结**（500 字以上）：电子基础、ESP32-S3、通信协议
2. **遇到的问题与解决方案**：至少记录 2 个问题及解决过程
3. **关键代码片段**：本周最满意的代码
4. **下周计划**：准备如何推进无线通信和旋钮开发
5. **自我评分**（1-10 分）：对本周学习效果的自我评价

### Week 2 汇报（Day 10 结束前提交）

详见 [week-2-checkin.md](../assignments/week-2-checkin.md)

内容要求：
1. **第二周学习总结**（500 字以上）
2. **无线通信与电机控制心得**
3. **PCB 设计准备思路**
4. **遇到的挑战与突破**
5. **PCB 设计计划**

### Week 3 汇报（Day 15 结束前提交）

详见 [week-3-checkin.md](../assignments/week-3-checkin.md)

内容要求：
1. **第三周学习总结**（500 字以上）：PCB 设计过程回顾
2. **12 块 PCB 设计总结**：原理图和布局的设计思路
3. **嘉立创 EDA 使用心得**
4. **Gerber 导出与打样经验**
5. **固件开发计划**

### Week 4 汇报（Day 18 结束前提交）

详见 [week-4-checkin.md](../assignments/week-4-checkin.md)

内容要求：
1. **第四周学习总结**（500 字以上）：固件开发过程
2. **ESP-IDF + FreeRTOS 架构理解**
3. **4 种无线模式实现心得**
4. **系统集成中的挑战**
5. **展示计划**

---

## 三、最终展示 | Final Presentation

详见 [final-presentation.md](../assignments/final-presentation.md)

### 展示要求 Presentation Requirements

- **时间**：每组 15 分钟展示 + 5 分钟问答
- **形式**：PPT + 实物演示
- **评分维度**：
  - 功能完整度（4 种无线模式 + 外设）
  - 技术深度（对 ESP-IDF/FreeRTOS/PCB/音频等原理的理解）
  - 工程质量（PCB 设计、焊接、代码质量）
  - 表达能力（展示是否清晰有条理）
  - 回答问题（对提问的回应质量）

### 展示大纲 Presentation Outline

1. **开场**（1 分钟）：项目名称、团队介绍
2. **项目概述**（2 分钟）：4 模式键盘功能展示
3. **技术讲解**（5 分钟）：主控架构、无线模式、音频、PCB 设计、固件架构
4. **实物演示**（5 分钟）：4 种模式切换、旋钮、RGB、语音
5. **总结与反思**（2 分钟）：学到了什么、不足与改进
6. **问答**（5 分钟）

---

## 四、项目展示网站 | Project Demo Website

### 要求 | Requirements

1. **部署平台** — 使用 GitHub Pages / Vercel / Netlify 等免费平台
2. **必须包含**：
   - [ ] 项目介绍（4 模式键盘名称、目标、核心功能）
   - [ ] 硬件展示（BOM 清单、12 块 PCB 截图、接线图）
   - [ ] 软件架构（ESP-IDF 固件架构、FreeRTOS 任务图、4 种无线模式）
   - [ ] 演示视频或 GIF（展示 4 种连接模式）
   - [ ] 20 天学习心得与总结
   - [ ] 参考资源链接列表

---

## 五、提交规范 | Submission Guidelines

### 文件命名规范
```
Day01_实验报告_学号_姓名.md
Week1_进度汇报_学号_姓名.md
Final_展示PPT_学号_姓名.pptx
```

### Git 提交规范
```
feat: 添加 Day 16 键盘扫描器代码
fix: 修复 BLE HID 配对失败的问题
hw: 完成主控板原理图绘制
fw: 实现 ESP-NOW 2.4GHz 发送模式
docs: 完成 Week 3 进度汇报
```

### 提交方式
- 代码文件：通过 Git 仓库提交（GitHub / Gitee）
- 文档文件：提交到仓库的 assignments/ 目录下
- 拍照/视频：上传到指定网盘链接

### 提交时间
- 每天作业当天 23:59 前提交
- 每周汇报在指定 Day 结束前提交
- 最终材料 Day 20 展示前提交
- 延迟提交扣 10% 分数/天

---

## 六、评分标准 | Grading Criteria

| 项 Item | 权重 Weight |
|---|---|
| 技术实现 Technical Implementation | 40% |
| 文档质量 Documentation Quality | 20% |
| 演示展示 Final Presentation | 20% |
| Demo 网站 Project Demo Website | 15% |
| 进度汇报 Check-in Reports | 10% |
| 团队协作 & 学习态度 Collaboration & Attitude | 10% |

详见 [grading-rubric.md](grading-rubric.md) 和 [assignments/rubric.md](../assignments/rubric.md)

---

*最后更新 | Last updated: 2026-05-27*
