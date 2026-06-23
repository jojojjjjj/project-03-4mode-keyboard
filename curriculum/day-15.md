# Day 15: PCB布局收尾与 Gerber 导出 | PCB Layout Wrap-up & Gerber Export

> **夏令营体验档**：主线只做 1 块双层主控板——今天导出它的 Gerber 并下单嘉立创。旋钮板/接收器板/音频板等子板布局列为全配档参考，主线可只看不做。
>
> **Experiential bar**: the main line makes only 1 double-layer mainboard — today you export its Gerber and order from JLCPCB. Knob/receiver/audio sub-board layouts are full-tier reference; the main line can just read without doing.

> **今日目标 Today's Goals:**
> - 完成主控板 PCB 收尾，导出双层板 Gerber
> - 提交嘉立创打样订单（主线 1 块双层板）
> - 了解全配档子板（旋钮板/接收器板/音频板）的布局要点（参考）
>
> **产出 Deliverable:** 主控板 Gerber 文件 + 嘉立创打样订单截图

---

## 时间安排 | Schedule

| 时间 Time | 活动类型 Type | 内容 Content |
|---|---|---|
| 09:00–09:15 | 晨会 | 回顾 Day 14 主控板，答疑 |
| 09:15–10:30 | 讲解 | 旋钮板布局要点 + ENIG 工艺 |
| 10:30–10:45 | 休息 | — |
| 10:45–12:00 | 实验 | 旋钮主板 + 接收器板布局 |
| 12:00–13:30 | 午休 | — |
| 13:30–15:00 | 实验 | 音频板 + 其余子板布局 |
| 15:00–15:15 | 休息 | — |
| 15:15–16:30 | 实验 | Gerber 导出 + 嘉立创下单 |
| 16:30–17:00 | 总结 | 日终回顾 + 第三阶段总结 |

---

## 上午：旋钮主板与接收器板 | Morning: Knob Board & Receiver

### 为什么要学这个? | Why Learn This?

主控板是整个系统的大脑，而子板则是它的四肢和感官。旋钮板提供力反馈旋钮（FOC 无刷电机），接收器板让键盘通过 2.4GHz ESP-NOW 连接电脑。每块子板有各自的设计要点：旋钮板需要 ENIG 表面处理保证磁编码器精度，接收器板需要紧凑的 USB HID 设计。

The mainboard is the brain; sub-boards are its limbs and senses. The knob board provides haptic feedback (FOC motor), the receiver enables 2.4GHz ESP-NOW. Each sub-board has unique requirements: ENIG for encoder accuracy, compact USB HID for the receiver.

---

### 任务 15.1: 旋钮主板布局 (75 分钟)

**旋钮板设计要点 Knob Board Design Notes:**

```
旋钮主板元件清单:
  - ESP32-S3 (旋钮专用，独立 MCU)
  - TMC6300 (三相无刷电机驱动)
  - AS5047P (14-bit 磁编码器，SPI 接口)
  - GC9A01 (1.28寸圆形 LCD，SPI 接口)
  - 2204 无刷电机
  - HX711 (压力传感器 ADC)
  - 磁吸连接器 (与主控板对接)
  - 4 层板，ENIG 沉金表面处理

布局注意:
  ┌─────────────────────────────┐
  │         GC9A01 LCD          │  ← 圆形屏幕居中
  │      (圆形开孔区域)          │
  │    ┌──────┐                 │
  │    │ 电机  │  TMC6300        │  ← 电机驱动靠近电机
  │    │ 中心  │                 │
  │    └──────┘                 │
  │  AS5047P                    │  ← 磁编码器在电机正下方
  │  (电机轴心投影位置)           │
  │                             │
  │  ESP32-S3    HX711          │  ← 主控和压力传感
  │  ┌─────────────────────┐    │
  │  │  磁吸连接器 (板边)    │    │  ← 与主板对接
  │  └─────────────────────┘    │
  └─────────────────────────────┘
```

**ENIG 沉金工艺说明 ENIG Process:**

| 特性 Feature | ENIG 沉金 | HASL 喷锡 |
|---|---|---|
| 表面平整度 | 极好（适合细密焊盘） | 一般（有锡珠不平） |
| 可靠性 | 高（金面抗氧化） | 一般（锡面会氧化） |
| 成本 | 较高 | 较低 |
| 适用场景 | BGA/QFN/磁编码器焊盘 | 通用元件 |
| 本项目使用 | 旋钮板（AS5047P 需要） | 其他所有板 |

---

### 任务 15.2: 接收器板布局 (45 分钟)

```
接收器板设计要点:

  功能: 接收 ESP-NOW 2.4GHz 无线信号，通过 USB HID 发送按键给电脑
  主控: ESP32-S3 (独立固件)
  接口: USB Type-A 或 Type-C ( HID 设备)

  ┌──────────────────────┐
  │  USB-A 公头           │  ← 直接插入电脑 USB 口
  │  ┌──┐                 │
  │  │  │ ESP32-S3        │  ← 紧凑布局
  │  └──┘                 │
  │  [按钮] [LED]         │  ← 配对按钮 + 状态指示灯
  │  天线区域 ←─────────── │  ← 远离金属，预留净空区
  └──────────────────────┘

  尺寸: 尽量小（类似无线鼠标接收器）
  天线: 使用 ESP32-S3 内置 PCB 天线，下方禁止铺铜
```

---

## 下午：其余子板与 Gerber 导出 | Afternoon: Remaining Boards & Gerber Export

### 任务 15.3: 音频板布局 (30 分钟)

```
音频板要点:
  - ES7210 (ADC) + ES8311 (DAC) + NS4150B (功放)
  - 模拟地和数字地分开（单点接地）
  - 麦克风位置远离扬声器
  - NS4150B 输出走线短而粗
  - 2 层板即可满足要求
```

### 任务 15.4: 其余子板快速布局 (60 分钟)

| 子板 Board | 要点 Notes | 预计时间 Time |
|---|---|---|
| 方向键板 Arrow Key | 4 个轴座 + 4 个二极管 + 磁吸连接器 | 15 min |
| LED 灯板 LED Board | WS2812B 阵列 + 去耦电容 | 15 min |
| 磁吸连接器板 Mag Connector | Pogo Pin 底座 + 导线焊盘 | 10 min |
| USB 扩展板 USB Expansion | USB-A 母座 + ESD 保护 | 10 min |
| FPC 转接板 FPC Adapter | FPC 连接器 + 直插排针 | 10 min |

---

### 任务 15.5: Gerber 文件导出与打样下单 (75 分钟)

**Gerber 文件说明 Gerber File Explanation:**

```
每块 PCB 的 Gerber 文件包含:

  GTL - Top Copper (顶层铜)
  GBL - Bottom Copper (底层铜)
  GTS - Top Solder Mask (顶层阻焊)
  GBS - Bottom Solder Mask (底层阻焊)
  GTO - Top Silkscreen (顶层丝印)
  GBO - Bottom Silkscreen (底层丝印)
  GKO - Board Outline (板框)
  (4层板还有 G1L/G2L - Inner1/Inner2 Copper)
  (钻孔文件 - Drill File: DRL 或 TXT)
```

**嘉立创下单参数 JLCPCB Order Parameters:**

| 参数 Parameter | 值 Value | 说明 Notes |
|---|---|---|
| 板层数 Layers | 2 层（主线主控板）| 双层板够用 |
| 板厚 Thickness | 1.6mm | 标准 |
| 铜厚 Copper Weight | 1 oz (35um) | 标准 |
| 阻焊颜色 Solder Mask | 绿色 / 黑色 | 按组选择 |
| 丝印颜色 Silkscreen | 白色 | 标准 |
| 表面处理 Surface Finish | 无铅喷锡 HASL（学生手焊友好）| 主线不用 ENIG |
| 数量 Quantity | 5 片 | 嘉立创最低起订 |
| 是否贴片 SMT Assembly | 否（手工焊接）| 主线学生手焊通孔 + 简单贴片 |

**下单步骤 Order Steps:**
1. 登录 https://www.jlc.com/
2. 点击"在线下单"
3. 上传 Gerber 文件压缩包
4. 系统自动识别板子参数，核对并修改
5. 选择加急/普通（建议普通，约 3-5 天到货）
6. 确认价格，提交订单

---

## 日终总结 | Daily Wrap-up (16:30-17:00)

**第三阶段总结 Phase 3 Summary:**

在 Day 11-15 这一周里，你完成了：
1. 学习了 PCB 设计基础概念和嘉立创 EDA 工具
2. 跟教程画了键盘主控板原理图（ESP32-S3 + 电源 + 74HC165 + USB）
3. 了解了音频子系统、WS2812B 链等子板原理图（全配档参考）
4. 学习了双层板结构与铺地铜概念
5. 完成了主控板双层 PCB 的布局布线和 Gerber 导出（主线）
6. 向嘉立创提交了打样订单

---

## 今日作业 | Homework

1. **导出主控板 Gerber 文件**：1 块双层板，一个压缩包
2. **提交嘉立创打样订单**：截图订单确认页面
3. **完成第三周进度汇报**：详见 assignments/week-3-checkin.md
4. **回答思考题**：
   - 双层板为什么底层铺地铜？四层板多了什么？
   - 如果 Gerber 文件中的板框层 (GKO) 缺失会怎样？
   - 12 块 PCB 拼板（V-cut）有什么好处？（全配档参考）

---

## 明日预告 | Tomorrow's Preview

明天进入第四阶段——固件开发！你将搭建 ESP-IDF 项目框架，学习 FreeRTOS 任务模型，实现键盘扫描任务（74HC165 SPI 读取 + 消抖算法），让你的键盘在串口上打印按键。

Tomorrow we enter Phase 4 — firmware development! You'll set up an ESP-IDF project, learn FreeRTOS tasks, and implement key scanning (74HC165 SPI + debounce), printing key events to serial.

---

## 参考资源 | References

- 嘉立创下单教程：https://www.jlc.com/portal/vFaq.html
- 嘉立创 Gerber 导出教程：搜索 "嘉立创 EDA 导出 Gerber"
- ENIG vs HASL 对比：搜索 "PCB表面处理 ENIG HASL 对比"
- B 站搜索 "嘉立创打样 下单 教程"
- 嘉立创开源硬件平台（参考项目）：https://oshwhub.com/ran-pang/multifunctional-keyboard

---

*最后更新 | Last updated: 2026-05-27*
