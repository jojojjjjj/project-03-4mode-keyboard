# 第四周进度汇报 | Week 4 Check-in Report

**提交截止 | Deadline:** Day 18 结束前 | Before end of Day 18

## 基本信息 | Basic Information

| 项目 Item | 填写 Fill In |
|---|---|
| 学号 Student ID | |
| 姓名 Name | |
| 日期 Date | |
| 小组 Team | |

---

## 一、第四周学习总结 | Weekly Learning Summary

> 请用 500 字以上总结第四周（Day 16-18）的固件开发过程。
> Summarize your firmware development experience this week (Day 16-18) in 500+ words.

### 1.1 ESP-IDF + FreeRTOS 架构理解 | ESP-IDF & FreeRTOS

（你对 FreeRTOS 任务模型的理解，如何协调多个并发任务）

### 1.2 键盘扫描实现 | Key Scanner Implementation

（分享你实现 74HC165 SPI 键盘扫描和消抖算法的过程）

### 1.3 4 种无线模式 | 4 Wireless Modes

（分享 USB/BLE/WiFi/ESP-NOW 四种模式的实现心得）

### 1.4 系统集成体验 | System Integration

（将音频、LVGL、SimpleFOC、RGB 整合到一起的体验）

---

## 二、固件开发总结 | Firmware Development Summary

### 2.1 ESP-IDF 项目结构理解 | Project Structure

（用自己的话解释 main.c、CMakeLists.txt、sdkconfig、components 各自的作用）

### 2.2 FreeRTOS 任务架构 | Task Architecture

| 任务 Task | 优先级 Priority | 功能 Function | 状态 Status |
|---|---|---|---|
| key_scanner | | 74HC165 SPI 扫描 | [ ] 完成 |
| usb_hid | | USB 键盘报告 | [ ] 完成 |
| ble_hid | | BLE 键盘 | [ ] 完成 |
| wifi_kb | | WiFi 键盘 | [ ] 完成 |
| esp_now | | 2.4GHz 通信 | [ ] 完成 |
| audio | | I2S 音频 | [ ] 完成 |
| rgb_ctrl | | WS2812B 灯效 | [ ] 完成 |
| knob_ctrl | | 旋钮控制 | [ ] 完成 |

### 2.3 编译结果 | Build Result

| 项目 Item | 状态 Status |
|---|---|
| 固件编译是否成功 | [ ] 是 [ ] 否 |
| 固件文件大小 | KB |
| 编译警告数量 | 个 |
| 烧录是否成功 | [ ] 是 [ ] 否 |
| 串口日志是否正常 | [ ] 是 [ ] 否 |

---

## 三、4 种无线模式测试 | Wireless Mode Testing

### 3.1 USB 有线模式 | USB Wired Mode

| 测试项 Test | 结果 Result |
|---|---|
| 电脑识别为键盘 | [ ] 通过 |
| 单键输入正确 | [ ] 通过 |
| 组合键工作 | [ ] 通过 |
| 80 键全部响应 | [ ] 通过 |

### 3.2 BLE 蓝牙模式 | BLE Mode

| 测试项 Test | 结果 Result |
|---|---|
| 广播可被发现 | [ ] 通过 |
| 配对成功 | [ ] 通过 |
| 按键发送正确 | [ ] 通过 |
| 延迟测试 | ms |

### 3.3 WiFi 模式 | WiFi Mode

| 测试项 Test | 结果 Result |
|---|---|
| WiFi 连接成功 | [ ] 通过 |
| 接收端收到数据 | [ ] 通过 |
| 按键模拟正确 | [ ] 通过 |

### 3.4 ESP-NOW 2.4GHz | ESP-NOW Mode

| 测试项 Test | 结果 Result |
|---|---|
| 接收器配对成功 | [ ] 通过 |
| 数据传输正常 | [ ] 通过 |
| 延迟测试 | ms |

---

## 四、遇到的挑战与突破 | Challenges & Breakthroughs

### 挑战 1 | Challenge 1

- **问题描述 | Problem:**
- **尝试的方法 | Attempts:**
- **最终解决方案 | Solution:**

### 挑战 2 | Challenge 2

- **问题描述 | Problem:**
- **尝试的方法 | Attempts:**
- **最终解决方案 | Solution:**

---

## 五、展示计划 | Presentation Plan

> 说明你在 Day 20 展示中计划展示哪些内容。
> Describe what you plan to show on Day 20.

### 5.1 计划展示的功能 | Planned Features to Demo

- [ ] USB 有线键盘打字
- [ ] BLE 蓝牙键盘
- [ ] WiFi 键盘
- [ ] ESP-NOW 2.4GHz 模式
- [ ] 模式切换（Fn+1/2/3/4）
- [ ] RGB 灯效（模式指示颜色）
- [ ] FOC 旋钮（旋转+按压）
- [ ] 旋钮 LCD 显示
- [ ] 麦克风录音
- [ ] 扬声器播放
- [ ] 电池充电与电量显示
- [ ] 磁吸扩展模块
- [ ] 其他：_________

### 5.2 展示大纲 | Presentation Outline

1. 开场（1 分钟）：
2. 项目概述（2 分钟）：
3. 技术讲解（5 分钟）：
4. 实物演示（5 分钟）：
5. 总结反思（2 分钟）：

### 5.3 演示备份方案 | Backup Plan

（如果现场演示失败，准备什么替代方案？）

---

## 六、自我评分 | Self Assessment

| 维度 Dimension | 1-10 分 Score | 说明 Notes |
|---|---|---|
| 固件开发能力 | | |
| 4 种无线模式 | | |
| 系统集成能力 | | |
| 代码质量 | | |
| 整体进度 | | |
| **总分 Total** | **/50** | |

---

*最后更新 | Last updated: 2026-05-27*
