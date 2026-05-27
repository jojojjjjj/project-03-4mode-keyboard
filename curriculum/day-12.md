# Day 12: 键盘主控板原理图绘制 | Keyboard Mainboard Schematic

> **今日目标 Today's Goals:**
> - 绘制 ESP32-S3 最小系统完整原理图（含电源去耦、BOOT 配置、复位电路）
> - 设计电源树：TP4056 充电 + HX3608 升压 + ME6217 稳压
> - 绘制 74HC165 移位寄存器菊花链原理图（SPI 键盘扫描）
> - 完成USB子系统原理图（SL2.1A USB Hub + CH342F USB-TTL + GL823K 读卡器）
>
> **产出 Deliverable:** 键盘主控板完整原理图（Schematic Complete）

---

## 时间安排 | Schedule

| 时间 Time | 活动类型 Type | 内容 Content |
|---|---|---|
| 09:00–09:15 | 晨会 | 回顾 Day 11，答疑 |
| 09:15–10:30 | 讲解 | ESP32-S3 最小系统 + 电源树设计 |
| 10:30–10:45 | 休息 | — |
| 10:45–12:00 | 实验 | 绘制 ESP32-S3 + 电源部分原理图 |
| 12:00–13:30 | 午休 | — |
| 13:30–15:00 | 实验 | 74HC165 菊花链 + USB 子系统 |
| 15:00–15:15 | 休息 | — |
| 15:15–16:30 | 实验 | 完成主控板原理图 + ERC 检查 |
| 16:30–17:00 | 总结 | 日终回顾 + 明日预告 |

---

## 上午：ESP32-S3 与电源树 | Morning: ESP32-S3 & Power Tree

### 为什么要学这个? | Why Learn This?

原理图是电路的"蓝图"——它定义了每个元件的型号、参数以及它们之间的电气连接关系。画对原理图是 PCB 能正常工作的前提。今天你将完成整个键盘最复杂的一块板子——主控板的原理图设计。

The schematic is the "blueprint" of a circuit — it defines every component's model, parameters, and electrical connections. Getting the schematic right is the prerequisite for a working PCB. Today you'll complete the most complex board in the project — the mainboard schematic.

---

### 任务 12.1: ESP32-S3 最小系统原理图 (40 分钟)

**ESP32-S3 最小系统组成 ESP32-S3 Minimum System:**

```
ESP32-S3-WROOM-1 模块已内置:
  - ESP32-S3 芯片
  - 40MHz 晶振
  - Flash (8MB/16MB)
  - 天线 (PCB天线或外接天线)

外部需要添加的外围 External Peripherals Needed:
  ┌────────────────────────────────────┐
  │  3V3 ──┬── 100nF ── GND  (去耦x6) │
  │        ├── 100nF ── GND            │
  │        ├── 10uF  ── GND  (Bulk)    │
  │        └── ME6217 输出              │
  │                                    │
  │  EN  ──┬── 10kΩ ── 3V3  (上拉)    │
  │        └── 按钮 ── GND   (复位)    │
  │                                    │
  │  IO0 ──┬── 10kΩ ── 3V3  (上拉)    │
  │        └── 按钮 ── GND   (BOOT)    │
  │                                    │
  │  IO46 ── 10kΩ ── GND   (下拉)     │
  │        (IO46=0: SPI Boot 模式)     │
  └────────────────────────────────────┘
```

**ESP32-S3 引脚分配规划 Pin Assignment Plan:**

| 功能 Function | 引脚 GPIO | 说明 Notes |
|---|---|---|
| SPI_CLK | IO36 | 74HC165 移位寄存器时钟 |
| SPI_MISO | IO37 | 74HC165 数据输出 (Q7) |
| SPI_PL | IO38 | 74HC165 并行加载 (PL) |
| I2C_SDA | IO8 | I2C 数据（音频编解码器、OLED） |
| I2C_SCL | IO9 | I2C 时钟 |
| I2S_BCLK | IO41 | I2S 位时钟（音频） |
| I2S_WS | IO42 | I2S 字选择（音频） |
| I2S_DOUT | IO39 | I2S 数据输出（DAC） |
| I2S_DIN | IO40 | I2S 数据输入（ADC） |
| UART_TX | IO43 | 调试串口 |
| UART_RX | IO44 | 调试串口 |
| WS2812B_DIN | IO45 | RGB LED 数据线 |
| BATT_ADC | IO4 | 电池电压检测 |
| MOTOR_PWM | IO5 | FOC 电机驱动 |
| KNOB_CS | IO6 | AS5047P 磁编码器 CS |
| USB_D+ | IO20 | USB 2.0 全速 |
| USB_D- | IO19 | USB 2.0 全速 |

---

### 任务 12.2: 电源树设计 (35 分钟)

**电源架构 Power Architecture:**

```
电源树 Power Tree:

  USB 5V ─────────┬─────────────────── TP4056 充电 ──── 锂电池 3.7V
  (VBUS)          │                       │                    │
                  │                       │ (充电电流设置)        │
                  │                    R_prog = 1.2kΩ          │
                  │                    (I_chg = 1000mA)        │
                  │                                            │
                  ├── HX3608 Boost ─── 5V_STABLE              │
                  │   (3.7V → 5V)        │                     │
                  │                      ├── USB 外设供电        │
                  │                      └── WS2812B 供电       │
                  │                                            │
                  ├── ME6217 LDO ──── 3V3                      │
                  │   (5V → 3.3V)      │                       │
                  │                    ├── ESP32-S3             │
                  │                    ├── 74HC165              │
                  │                    ├── 音频编解码器           │
                  │                    └── OLED                  │
                  │                                            │
                  └── 直通 5V (USB 供电时)                       │
```

**电源预算 Power Budget:**

| 负载 Load | 电压 Voltage | 电流 Current | 功率 Power |
|---|---|---|---|
| ESP32-S3 (WiFi active) | 3.3V | ~200mA | 0.66W |
| 74HC165 x 10 | 3.3V | ~10mA | 0.033W |
| WS2812B x 20 (全白) | 5V | ~1.2A | 6.0W |
| ES7210 + ES8311 | 3.3V | ~30mA | 0.1W |
| NS4150B (speaker) | 5V | ~300mA | 1.5W |
| OLED (SSD1306) | 3.3V | ~20mA | 0.066W |
| **总计 Total** | — | — | **~8.4W** |

> **注意**：WS2812B 全白时功耗很大，实际使用中应限制亮度或同时点亮的灯珠数量。

---

### 任务 12.3: 绘制 ESP32-S3 + 电源原理图 (75 分钟)

**步骤 Steps:**
1. 放置 ESP32-S3-WROOM-1 模块符号
2. 连接 6 个 100nF + 1 个 10uF 去耦电容
3. 绘制 EN 复位电路（上拉电阻 + 按钮）
4. 绘制 BOOT 模式选择电路
5. 放置 TP4056 充电电路（含充电状态 LED）
6. 放置 HX3608 升压电路（含电感、二极管、输出电容）
7. 放置 ME6217 LDO 稳压电路（含输入输出电容）
8. 添加电源网络标签（VBUS、VBAT、5V_STABLE、3V3、GND）

---

## 下午：移位寄存器链与 USB 子系统 | Afternoon: Shift Registers & USB

### 任务 12.4: 74HC165 菊花链原理图 (60 分钟)

**74HC165 工作原理 74HC165 Operating Principle:**

```
74HC165: 8位并行转串行移位寄存器
用途：读取键盘矩阵的行状态，通过 SPI 接口传给 ESP32-S3

单级 Single Stage:
  ┌─────────────┐
  │  74HC165     │
  │  D0-D7 ← 行线 │   PL=0: 并行加载（锁存8位输入）
  │  CLK ← SPI_CLK│   PL=1: 移位模式
  │  Q7  → SPI_MISO│  CLK↑: Q7输出一位数据
  │  PL  ← SPI_PL │
  └─────────────┘

菊花链 Daisy Chain (10级):
  ┌──────┐  Q7'  ┌──────┐  Q7'       ┌──────┐
  │ HC165 │──→SER │ HC165 │──→SER ──→ │ HC165 │──→ ESP32 SPI_MISO
  │ #1    │       │ #2   │           │ #10   │
  │D0-D7  │       │D0-D7 │           │D0-D7  │
  │(行0-7)│       │(行8- │           │(行72- │
  └──────┘       │15)   │           │79)    │
                 └──────┘           └──────┘
  所有 74HC165 共享 CLK 和 PL 信号

  总共读取: 10 x 8 = 80 位 = 80 个按键
```

**原理图要点 Schematic Notes:**
- 每个 74HC165 的 VCC 接 3V3，GND 接地
- 每个 IC 的 VCC 旁放一个 100nF 去耦电容
- SER 输入（第 1 级接地，后续级接前级 Q7'）
- CLK INH（时钟禁止）接 GND（始终允许时钟）

---

### 任务 12.5: USB 子系统原理图 (60 分钟)

**USB 子系统组成 USB Subsystem Components:**

```
USB 子系统架构:

  USB Type-C 母座
       │
       ├── SL2.1A USB 2.0 Hub (1上行 → 4下行)
       │     ├── Port 1: ESP32-S3 (USB D+/D- 直连)
       │     ├── Port 2: CH342F (USB → UART，固件调试)
       │     ├── Port 3: GL823K (SD 读卡器，可选)
       │     └── Port 4: 预留扩展
       │
       └── CC1/CC2: 5.1kΩ 下拉电阻 (设备端)
```

**SL2.1A USB Hub Circuit:**
- 上行口 D+/D- 连接 Type-C 母座
- 4 个下行口各通过 100nF 隔离电容连接
- 需要外部 EEPROM（24C02）存储 Hub 描述符（可选）

**CH342F USB-TTL Bridge:**
- 将 USB 转为 UART（TX/RX）
- 用于 ESP32-S3 固件下载和调试串口
- 需要外部晶振（12MHz）

---

### 任务 12.6: 完成主控板原理图 + ERC (60 分钟)

**完整检查清单 Completion Checklist:**

| 模块 Module | 状态 Status | ERC Pass |
|---|---|---|
| ESP32-S3 最小系统 | [ ] 完成 | [ ] |
| TP4056 充电电路 | [ ] 完成 | [ ] |
| HX3608 升压电路 | [ ] 完成 | [ ] |
| ME6217 LDO 电路 | [ ] 完成 | [ ] |
| 74HC165 x 10 菊花链 | [ ] 完成 | [ ] |
| SL2.1A USB Hub | [ ] 完成 | [ ] |
| CH342F USB-TTL | [ ] 完成 | [ ] |
| GL823K SD 读卡器 | [ ] 完成 | [ ] |
| 电源网络完整 | [ ] 完成 | [ ] |
| ERC 检查 | [ ] 0 错误 | [ ] |

---

## 日终总结 | Daily Wrap-up (16:30-17:00)

**今日关键词 Key Takeaways:**
1. ESP32-S3 最小系统需要去耦电容、BOOT 配置和复位电路
2. 电源树设计：电池 -> 升压 -> 稳压，每级转换都有效率损耗
3. 74HC165 菊花链通过 SPI 读取 80 个按键状态
4. USB Hub 拓展了一个 USB 口为多个，方便同时连接调试

---

## 今日作业 | Homework

1. **完成主控板原理图**：确保所有模块连接完成，ERC 检查 0 错误
2. **截图提交**：完整原理图全貌 + ERC 报告
3. **回答思考题**：
   - 为什么电池电压（3.7V）需要先升压到 5V 再降压到 3.3V？直接降压不行吗？
   - 74HC165 菊花链中，如果第 5 级的 SER 断开，会怎样？
   - USB Hub 的下行口能否再接一个 Hub？最多能级联几层？

---

## 明日预告 | Tomorrow's Preview

明天我们将绘制外设原理图：音频子系统（ES7210 + ES8311 + NS4150B）、WS2812B RGB 链、扩展接口，并学习 4 层 PCB 的层叠结构概念。

Tomorrow we draw peripheral schematics: audio subsystem (ES7210 + ES8311 + NS4150B), WS2812B RGB chain, expansion ports, and learn 4-layer PCB stackup concepts.

---

## 参考资源 | References

- ESP32-S3 技术参考手册：https://www.espressif.com/sites/default/files/documentation/esp32-s3_technical_reference_manual_cn.pdf
- TP4056 数据手册：搜索 "TP4056 datasheet"
- HX3608 数据手册：搜索 "HX3608 boost converter datasheet"
- ME6217 数据手册：搜索 "ME6217 LDO datasheet"
- 74HC165 数据手册：https://www.ti.com/lit/ds/symlink/sn74hc165.pdf
- SL2.1A 数据手册：搜索 "SL2.1A USB hub datasheet"
- 嘉立创开源硬件平台（参考项目）：https://oshwhub.com/ran-pang/multifunctional-keyboard

---

*最后更新 | Last updated: 2026-05-27*
