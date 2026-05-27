# Day 20: 调试、展示与总结 | Debugging, Presentation & Wrap-up

> **今日目标 Today's Goals:**
> - 系统性地调试集成后的硬件和固件问题
> - 掌握常见故障模式的诊断和修复方法
> - 完成 15 分钟团队展示（含实物演示）
> - 课程总结，颁发结业证书
>
> **产出 Deliverable:** 功能完整的 4 模式键盘 + 最终展示 + 项目文档

---

## 时间安排 | Schedule

| 时间 Time | 活动类型 Type | 内容 Content |
|---|---|---|
| 09:00–09:15 | 晨会 | 最终调试计划，展示时间表 |
| 09:15–10:30 | 实验 | 系统集成调试 |
| 10:30–10:45 | 休息 | — |
| 10:45–12:00 | 实验 | 最终功能验证 + Demo 准备 |
| 12:00–13:30 | 午休 | — |
| 13:30–15:00 | 展示 | 团队展示 (15 min/组 + 5 min Q&A) |
| 15:00–15:15 | 休息 | — |
| 15:15–16:30 | 展示 | 继续展示 / 课程总结 / 颁发证书 |
| 16:30–17:00 | 总结 | 合影留念，课程结束 |

---

## 上午：系统集成调试 | Morning: System Integration Debugging

### 为什么要学这个? | Why Learn This?

调试（Debugging）是工程师最核心的能力之一。硬件项目在首次组装后几乎不可能一次就完美运行——焊接缺陷、设计失误、固件 bug、电源干扰……问题五花八门。系统化的调试方法论比盲目试错高效 100 倍。

Debugging is one of the most core engineering skills. Hardware projects rarely work perfectly on first assembly — soldering defects, design errors, firmware bugs, power noise... A systematic debugging methodology is 100x more efficient than random trial-and-error.

---

### 任务 20.1: 系统化调试方法论 (20 分钟)

**调试四步法 Four-Step Debug Method:**

```
Step 1: 观察 (Observe)
  - 现象是什么？哪些功能正常？哪些不正常？
  - 不要急于动手，先完整记录症状

Step 2: 假设 (Hypothesize)
  - 列出所有可能的原因（从最可能到最不可能排序）
  - 每个假设都应该是可验证的

Step 3: 验证 (Verify)
  - 用最小的实验验证/排除一个假设
  - 一次只改一个变量！

Step 4: 修复 (Fix)
  - 确认根因后修复
  - 修复后验证问题确实解决
  - 记录问题和解决方案
```

**调试工具箱 Debug Toolkit:**

| 工具 Tool | 用途 Purpose |
|---|---|
| 万用表 | 测电压、通断、电阻 |
| USB 电流表 | 检查功耗是否正常 |
| 放大镜/显微镜 | 检查焊点 |
| 串口监视器 | 查看固件日志 |
| 逻辑分析仪 | 观察 SPI/I2C 信号波形 |
| 热成像仪（如果有） | 发现发烫的元件 |

---

### 任务 20.2: 常见故障模式与修复 (40 分钟)

**常见问题排查 Common Failure Modes:**

| 症状 Symptom | 可能原因 Likely Cause | 排查方法 Debug Method | 修复 Fix |
|---|---|---|---|
| 整板不上电 | 电源短路 / USB 线坏 | 万用表测 VCC-GND 阻抗 | 修复短路 / 换线 |
| ESP32 不启动 | EN 引脚悬空 / 供电不足 | 测 3.3V 电压 / 测 EN 电平 | 检查 EN 上拉 / 换电源 |
| 部分按键不响应 | 74HC165 虚焊 / 信号线断 | 串口看哪些键缺失 | 补焊 / 飞线 |
| USB 不识别 | D+/D- 反接 / 差分对问题 | 测 USB 信号线通断 | 修复接线 |
| BLE 无法配对 | 天线问题 / 固件错误 | 检查天线区域 / 看日志 | 清理天线区 / 修改固件 |
| RGB 不亮 | 数据线断 / 第一个 LED 坏 | 测 DIN 信号 / 逐个排查 | 补焊 / 换 LED |
| 音频有杂音 | I2S 接线不稳 / GND 不完整 | 示波器看波形 | 补焊 / 加 GND 连接 |
| 功耗过大 | 某处短路 / 芯片损坏 | 热成像找发热点 | 更换损坏元件 |
| 固件刷入失败 | UART 接线 / BOOT 模式 | 检查 TX/RX / 按 BOOT 键 | 修复接线 / 手动进下载模式 |
| WiFi 连不上 | 天线匹配 / SSID 密码错 | 串口看 WiFi 日志 | 修改配置 / 检查天线 |

---

### 任务 20.3: 最终功能验证 (60 分钟)

**完整功能测试清单 Final Test Checklist:**

| # | 测试项 Test | 方法 Method | 通过 Pass |
|---|---|---|---|
| 1 | USB 有线键盘 | 打开记事本，逐键测试 | [ ] |
| 2 | BLE 蓝牙键盘 | 配对后逐键测试 | [ ] |
| 3 | WiFi 键盘 | 连接后发送按键 | [ ] |
| 4 | ESP-NOW 2.4GHz | 接收器模式下逐键测试 | [ ] |
| 5 | 模式切换 | Fn+1/2/3/4 切换 | [ ] |
| 6 | RGB 灯效 | 每种模式显示对应颜色 | [ ] |
| 7 | 旋钮旋转 | 调节音量/滚动 | [ ] |
| 8 | 旋钮按下 | 静音/确认 | [ ] |
| 9 | 旋钮 LCD 显示 | 显示当前状态 | [ ] |
| 10 | 麦克风录音 | 串口查看音频数据 | [ ] |
| 11 | 扬声器播放 | 播放测试音频 | [ ] |
| 12 | 电池充电 | USB 连接时充电灯亮 | [ ] |
| 13 | 电池续航 | 断开 USB，续航 > 2h | [ ] |
| 14 | 电池电量显示 | OLED/LED 指示 | [ ] |
| 15 | 磁吸扩展 | 连接子板，功能正常 | [ ] |

---

### 任务 20.4: Demo 准备 (45 分钟)

**展示流程模板 Demo Script Template:**

```
1. 开场 Opening (1 min):
   "大家好，我们是 XX 组，今天展示我们设计的 4 模式机械键盘"

2. 项目概述 Overview (2 min):
   "这款键盘支持 USB、蓝牙、WiFi、2.4GHz 四种连接模式，
    还有一个可拆卸的力反馈旋钮，支持语音交互和 RGB 灯效"

3. 技术讲解 Technical Deep-dive (5 min):
   - 主控板架构（ESP32-S3 + 74HC165 链 + 电源树）
   - 4 种无线模式的技术实现
   - 音频子系统（ES7210 + ES8311 + I2S）
   - PCB 设计（4 层板、阻抗控制、12 块子板）
   - 固件架构（FreeRTOS 多任务）

4. 实物演示 Live Demo (5 min):
   - USB 有线打字 (30s)
   - 切换到 BLE 模式 (30s)
   - 切换到 ESP-NOW 2.4GHz (30s)
   - 旋钮演示 (30s)
   - RGB 灯效展示 (30s)
   - 语音交互演示 (1 min)
   - 磁吸扩展模块 (30s)

5. 总结反思 Reflection (2 min):
   - 最大的技术挑战
   - 学到了什么
   - 未来改进方向

6. Q&A 问答 (5 min)
```

---

## 下午：最终展示 | Afternoon: Final Presentations

### 展示规则 Presentation Rules

- 每组 15 分钟展示 + 5 分钟问答
- 必须有实物演示环节
- PPT 建议 10-15 页
- 所有组员必须发言

### 评分维度 Grading Dimensions

| 维度 Dimension | 权重 Weight | 说明 Description |
|---|---|---|
| 功能完整度 | 30% | 4 种模式 + 外设功能是否齐全 |
| 技术深度 | 25% | 对原理的理解和讲解深度 |
| 工程质量 | 20% | PCB 设计、焊接、代码质量 |
| 展示能力 | 15% | PPT 质量、表达清晰度 |
| 团队协作 | 10% | 分工合理性、参与度 |

---

### 课程总结 | Course Summary (16:00-16:30)

**20 天旅程回顾 20-Day Journey:**

```
阶段一 (Day 1-5):  电子基础与 ESP32-S3 入门
  - 电路基础、欧姆定律、面包板实验
  - ESP32-S3 开发环境搭建
  - SPI/I2C/I2S 通信协议
  - USB 协议与电源管理

阶段二 (Day 6-10): 子系统原型验证
  - BLE 蓝牙 / WiFi / ESP-NOW 无线通信
  - WS2812B RGB 灯效
  - FOC 无刷电机旋钮
  - LVGL 嵌入式 GUI

阶段三 (Day 11-15): PCB 设计（12 块板）
  - 嘉立创 EDA 工具
  - 主控板原理图（ESP32-S3 + 电源 + SPI + USB）
  - 子板原理图（音频/旋钮/接收器/LED/扩展）
  - 4 层板布局布线 + Gerber 打样

阶段四 (Day 16-18): 固件开发
  - ESP-IDF + FreeRTOS
  - 74HC165 SPI 键盘扫描
  - 4 种无线模式固件
  - 系统集成（音频/LVGL/SimpleFOC/RGB）

阶段五 (Day 19-20): 组装与展示
  - SMD 焊接与组装
  - 系统调试
  - 最终展示
```

**你们学到的核心能力 Core Competencies Gained:**

| 领域 Area | 技能 Skills |
|---|---|
| 电子电路 | 电路分析、电源设计、信号完整性 |
| PCB 设计 | 原理图绘制、多层板布局、阻抗控制 |
| 固件开发 | ESP-IDF、FreeRTOS、SPI/I2C/I2S 驱动 |
| 无线通信 | BLE、WiFi、ESP-NOW、USB HID |
| 工程实践 | 焊接、调试、文档、团队协作 |

---

## 今日作业 | Homework

1. **提交最终项目文档**：
   - README.md（项目介绍、使用说明、技术架构）
   - 完整原理图截图（所有 12 块 PCB）
   - 固件源代码（通过 Git 仓库提交）
   - 展示 PPT
2. **提交功能演示视频**：3-5 分钟，展示所有功能
3. **提交项目展示网站 URL**（公网可访问）
4. **自我评估表**：填写评分量表，给自己打分

---

## 参考资源 | References

- 所有前 19 天的参考资源均适用
- ESP-IDF 官方文档：https://docs.espressif.com/projects/esp-idf/
- 嘉立创开源硬件平台（参考项目）：https://oshwhub.com/ran-pang/multifunctional-keyboard
- GitHub Pages 部署教程：https://pages.github.com/

---

*恭喜你完成了 20 天的 4 模式机械键盘项目！*
*Congratulations on completing the 20-day 4-mode mechanical keyboard project!*

*最后更新 | Last updated: 2026-05-27*
