# 物料清单 | Bill of Materials (BOM)

## 四模机械键盘 — 承载我所有幻想的键盘
## 4-Mode Mechanical Keyboard — The Keyboard of All My Fantasies

> 基于 Oshwhub 开源项目改编 | Based on [Oshwhub open-source project](https://oshwhub.com/ran-pang/multifunctional-keyboard)
> 支持 USB / 蓝牙 / WiFi / 2.4G 接收器 四模连接，磁吸 FOC 旋钮屏，语音交互
> Supports 4-mode connectivity (USB / Bluetooth / WiFi / 2.4G receiver), detachable FOC knob display, voice interaction

---

## 项目总预算 | Project Total Budget

| 类别 Category | 子系统 Subsystem | 金额 Amount (CNY) |
|---|---|---|
| 主控与有源器件 | Main ICs & Active Components | 88.50 |
| 旋钮模块元器件 | Knob Module Components | 82.50 |
| 接收器元器件 | Receiver Components | 16.00 |
| LED 与光电器件 | LEDs & Optoelectronics | 25.00 |
| 连接器与线缆 | Connectors & Cables | 31.60 |
| 被动元件 | Passive Components | 18.25 |
| 机电元件 | Electromechanical (switches, keycaps, etc.) | 352.00 |
| PCB 制造（12 块板） | PCB Manufacturing (12 boards) | 144.00 |
| SMT 贴片 | SMT Assembly | 125.00 |
| 3D 打印/结构件 | 3D Printing / Structural | 105.00 |
| 线缆与杂项 | Cables & Misc | 28.00 |
| 工具（共用） | Tools (shared) | 12.00 |
| **总计 Grand Total** | | **¥1,027.75** |

> 预算说明：本项目为高集成度客制化键盘，包含 12 块 PCB、FOC 旋钮、音频系统、无线接收器等子系统。
> Budget note: This is a highly integrated custom keyboard with 12 PCBs, FOC knob, audio system, and wireless receiver subsystems.

---

## 完整物料清单 | Full BOM

### 一、主控与有源器件（键盘）| Main ICs & Active Components (Keyboard)

| 编号 No. | 元件 Component | 型号 Specification | 数量 Qty | 单价 Unit (CNY) | 小计 Subtotal | 采购渠道 Source | 备注 Notes |
|---|---|---|---|---|---|---|---|
| 1 | 键盘主控 MCU | ESP32-S3-WROOM-1-N16R8 | 1 | 32.00 | 32.00 | 淘宝/嘉立创 | 16MB Flash + 8MB PSRAM，WiFi+BT+USB |
| 2 | 旋钮主控 MCU | ESP32-S3-WROOM-1-N16R8 | 1 | 32.00 | 32.00 | 淘宝/嘉立创 | FOC 旋钮独立主控 |
| 3 | USB HUB 芯片 | SL2.1A | 1 | 3.50 | 3.50 | 淘宝 | 扩展 USB-A 口 + 模拟 U 盘 |
| 4 | USB 转 TTL | CH342F | 1 | 5.00 | 5.00 | 淘宝 | 双通道，分别下载键盘/旋钮固件 |
| 5 | USB 存储控制 | GL823K | 1 | 4.50 | 4.50 | 淘宝 | 模拟 U 盘功能（存储配置文件） |
| 6 | 音频 DAC | ES8311 | 1 | 3.80 | 3.80 | 淘宝/嘉立创 | I2S 接口，参考 ESP-BOX 设计 |
| 7 | 音频 ADC | ES7210 | 1 | 5.50 | 5.50 | 淘宝/嘉立创 | 4 通道 I2S ADC，录音用 |
| 8 | 音频功放 | NS4150B | 2 | 1.20 | 2.40 | 淘宝 | D 类功放，驱动扬声器 |
| 9 | 移位寄存器 | 74HC165 (SOP-16) | 10 | 0.60 | 6.00 | 嘉立创商城 | 按键矩阵扫描，参考瀚文键盘 |
| 10 | LDO 稳压器 | ME6217C33M5G (SOT-23-5) | 2 | 0.80 | 1.60 | 嘉立创商城 | 3.3V / 500mA 低功耗 LDO |
| 11 | DC-DC 升压 | HX3608 | 1 | 1.50 | 1.50 | 淘宝 | 锂电池升压至 5V |
| 12 | 锂电充电 IC | TP4056 (SOP-8) | 1 | 0.80 | 0.80 | 嘉立创商城 | 单节锂电池充电 |
| 13 | 电池保护 | DW01 + FS8205A | 1 set | 0.80 | 0.80 | 嘉立创商城 | 过充/过放/过流保护 |
| **小计 Subtotal** | | | | | **88.50** | | |

> **说明 Notes:**
> - ESP32-S3 自带 WiFi、蓝牙 5.0、USB OTG、I2S 音频接口，一颗芯片覆盖四模通信。
> - 74HC165 用于按键矩阵行扫描（参考稚辉君瀚文键盘方案），10 片级联覆盖 75 键。
> - ES8311 + ES7210 + NS4150B 音频方案参考乐鑫 ESP-BOX 官方设计。

---

### 二、旋钮模块元器件 | Knob Module Components

| 编号 No. | 元件 Component | 型号 Specification | 数量 Qty | 单价 Unit (CNY) | 小计 Subtotal | 采购渠道 Source | 备注 Notes |
|---|---|---|---|---|---|---|---|
| 14 | 圆形 LCD 屏幕 | GC9A01 1.28" 240x240 圆形 TFT | 1 | 18.00 | 18.00 | 淘宝 | SPI 接口，用于旋钮 UI 显示 |
| 15 | BLDC 电机驱动 | TMC6300 (QFN-20) | 1 | 12.00 | 12.00 | 淘宝 | 三相无刷电机驱动，FOC 控制 |
| 16 | 磁编码器 | AS5047P (TSSOP-14) | 1 | 22.00 | 22.00 | 淘宝 | 14-bit SPI，闭环 FOC 反馈 |
| 17 | 称重 ADC | HX711 (SOP-16) | 1 | 2.00 | 2.00 | 淘宝 | 24-bit ADC，读取应变计 |
| 18 | 升压驱动 | SY7200AABC (SOT-23-6) | 1 | 1.50 | 1.50 | 淘宝 | 为电机提供高压驱动 |
| 19 | BLDC 云台电机 | 2204 云台无刷电机 | 1 | 15.00 | 15.00 | 淘宝 | 低速大扭矩，力反馈旋钮 |
| 20 | 应变计 | 应变片 x4 (350 ohm) | 1 set | 12.00 | 12.00 | 淘宝 | 按压力检测（推/拉/左/右） |
| **小计 Subtotal** | | | | | **82.50** | | |

> **说明 Notes:**
> - 旋钮模块为独立子系统，自带 ESP32-S3 主控（表第 2 项），通过磁吸 pogo pin 与键盘连接。
> - TMC6300 + AS507P + 云台电机实现 FOC 力反馈，结合 LVGL 显示 UI（类似 SmartKnob）。
> - 应变计配合 HX711 检测旋钮按压方向与力度。

---

### 三、接收器元器件 | Receiver Components

| 编号 No. | 元件 Component | 型号 Specification | 数量 Qty | 单价 Unit (CNY) | 小计 Subtotal | 采购渠道 Source | 备注 Notes |
|---|---|---|---|---|---|---|---|
| 21 | 接收器主控 | ESP32-S3-WROOM-1-N8 | 1 | 16.00 | 16.00 | 淘宝/嘉立创 | 8MB Flash，2.4G 接收器 |
| **小计 Subtotal** | | | | | **16.00** | | |

> **说明 Notes:**
> - 接收器使用 ESP-NOW 协议与键盘通信（2.4G 模式），板载天线，无需外接天线。
> - Receiver uses ESP-NOW protocol for 2.4G mode communication, onboard antenna.

---

### 四、LED 与光电器件 | LEDs & Optoelectronics

| 编号 No. | 元件 Component | 型号 Specification | 数量 Qty | 单价 Unit (CNY) | 小计 Subtotal | 采购渠道 Source | 备注 Notes |
|---|---|---|---|---|---|---|---|
| 22 | RGB LED 灯珠 | WS2812B 5050 (PLCC-4) | 100 | 0.25 | 25.00 | 淘宝/嘉立创 | 每键一颗，预留备用 |
| **小计 Subtotal** | | | | | **25.00** | | |

> **说明 Notes:**
> - 75 键 + 若干格栅灯 = 约 85-100 颗 WS2812B。
> - WS2812B 采用单线级联协议，所有灯珠串联仅需 1 根数据线。

---

### 五、连接器与线缆 | Connectors & Cables

| 编号 No. | 元件 Component | 型号 Specification | 数量 Qty | 单价 Unit (CNY) | 小计 Subtotal | 采购渠道 Source | 备注 Notes |
|---|---|---|---|---|---|---|---|
| 23 | USB Type-C 母座 | 16P 全针脚 | 2 | 1.00 | 2.00 | 淘宝/嘉立创 | 键盘主 USB + 旋钮充电口 |
| 24 | USB Type-A 母座 | 标准直立式 | 1 | 0.60 | 0.60 | 淘宝/嘉立创 | 外接鼠标/USB 设备 |
| 25 | 磁吸弹簧针连接器 | Pogo Pin 磁吸座 | 2 pairs | 8.00 | 16.00 | 淘宝 | 键盘-旋钮磁吸连接 |
| 26 | FPC 连接器 | 0.5mm 间距 翻盖式 | 10 | 0.80 | 8.00 | 嘉立创商城 | 各子板间 FPC 排线连接 |
| 27 | 其他连接器 | 排针/排母/PH2.0 等 | 1 lot | — | 5.00 | 嘉立创商城 | 批量采购 |
| **小计 Subtotal** | | | | | **31.60** | | |

---

### 六、被动元件 | Passive Components

| 类别 Category | 说明 Description | 预估金额 Est. (CNY) |
|---|---|---|
| 电阻 (0402/0603/0805) | 上拉、分压、限流、I2C 上拉等 | 5.00 |
| 电容 (0402/0603/0805) | 旁路、滤波、耦合（100pF~100uF） | 5.00 |
| 电感 | DC-DC 功率电感、滤波电感 | 3.00 |
| 二极管/TVS | 静电保护、ESD 防护 | 2.00 |
| 晶振 | 40MHz（ESP32-S3）、32.768kHz | 1.25 |
| MOSFET | 模拟开关、电源切换 | 2.00 |
| **小计 Subtotal** | | **¥18.25** |

> **说明 Notes:**
> - 被动元件数量大但单价极低，建议在嘉立创商城按 BOM 一次性采购。
> - 主控板和旋钮板的被动元件请严格参照原理图/BOM，其他小板以附件 BOM 为准。

---

### 七、机电元件 | Electromechanical Components

| 编号 No. | 元件 Component | 型号 Specification | 数量 Qty | 单价 Unit (CNY) | 小计 Subtotal | 采购渠道 Source | 备注 Notes |
|---|---|---|---|---|---|---|---|
| 28 | 机械轴体 | Gateron G Pro 3.0 (佳达隆) | 75 | 2.00 | 150.00 | 淘宝客制化店 | 可选红/青/茶/黄轴 |
| 29 | 热插拔轴座 | Kailh (凯华) 热插拔插座 | 75 | 0.80 | 60.00 | 淘宝 | MX 兼容，支持免焊接换轴 |
| 30 | PBT 键帽套装 | 热升华 75% 配列 | 1 set | 65.00 | 65.00 | 淘宝 | 含所有配列键帽 |
| 31 | 模拟摇杆 | 双轴模拟摇杆模块 | 1 | 5.00 | 5.00 | 淘宝 | ADC 接口，多功能扩展 |
| 32 | 扬声器 | 8 ohm 20mm 动圈 | 2 | 2.50 | 5.00 | 淘宝 | 音频播放输出 |
| 33 | MEMS 麦克风 | SPH0645 或等效 | 2 | 3.00 | 6.00 | 淘宝 | 语音交互/录音 |
| 34 | 锂电池 | 3000mAh 103040 聚合物 | 1 | 25.00 | 25.00 | 淘宝 | 键盘主电池 |
| 35 | 锂电池（旋钮） | 500mAh 802025 聚合物 | 1 | 10.00 | 10.00 | 淘宝 | 旋钮模块电池 |
| 36 | 钕磁铁 | N35 圆形 5x2mm | 10 | 0.30 | 3.00 | 淘宝 | 磁吸定位与固定 |
| 37 | 轻触开关/按钮 | 6x6mm 贴片 | 3 | 1.00 | 3.00 | 嘉立创商城 | 复位/Boot/功能按钮 |
| 38 | 卫星轴 | PCB 卫星轴套装 | 1 set | 15.00 | 15.00 | 淘宝 | 空格/Shift/Enter 等大键 |
| **小计 Subtotal** | | | | | **352.00** | | |

> **说明 Notes:**
> - Gateron G Pro 3.0 为出厂润滑轴体，手感优秀且价格适中。
> - 锂电池请注意运输限制，建议国内采购，不可空运。

---

### 八、PCB 制造（12 块板）| PCB Manufacturing (12 Boards)

| 编号 No. | 板名 Board Name | 层数 Layers | 板厚 Thickness | 表面处理 Surface Finish | 数量 Qty | 预估单价 Est. Unit | 小计 Subtotal |
|---|---|---|---|---|---|---|---|
| 39 | 键盘-主控板 V4 | 4 层 | 1.2mm | 无铅喷锡 HASL | 5 pcs | 25.00 | 25.00 |
| 40 | 键盘-音频板 V2 | 4 层 | 1.0mm | 无铅喷锡 HASL | 5 pcs | 20.00 | 20.00 |
| 41 | 旋钮-主控板 V4 | 4 层 | 1.0mm | **沉金 ENIG**（手焊推荐） | 5 pcs | 22.00 | 22.00 |
| 42 | 接收器 | 4 层 | 1.0mm | **沉金 ENIG**（手焊推荐） | 5 pcs | 15.00 | 15.00 |
| 43 | 键盘-方向键小板 | 2 层 | 1.2mm | 无铅喷锡 HASL | 5 pcs | 5.00 | 5.00 |
| 44 | 键盘-指示灯板 | 2 层 | 1.0mm | 无铅喷锡 HASL | 5 pcs | 5.00 | 5.00 |
| 45 | 键盘-磁吸接口板 | 2 层 | 1.6mm | 无铅喷锡 HASL | 5 pcs | 6.00 | 6.00 |
| 46 | 键盘-旋钮磁吸转接板 | 2 层 | 1.0mm | 无铅喷锡 HASL | 5 pcs | 5.00 | 5.00 |
| 47 | 键盘-圆灯板 | 2 层 | 1.0mm | 无铅喷锡 HASL | 5 pcs | 5.00 | 5.00 |
| 48 | 键盘-USB 板 | 2 层 | 1.0mm | 无铅喷锡 HASL | 5 pcs | 5.00 | 5.00 |
| 49 | 旋钮-电池灯光板 | 2 层 | 1.0mm | 无铅喷锡 HASL | 5 pcs | 5.00 | 5.00 |
| 50 | 旋钮-屏幕排线转接板 | 2 层 | 1.0mm | 无铅喷锡 HASL | 5 pcs | 5.00 | 5.00 |
| | **PCB 制造小计** | | | | | | **¥128.00** |
| | **加运费 (约 2 批)** | | | | | | **¥16.00** |
| | **PCB 合计** | | | | | | **¥144.00** |

> **制板说明 PCB Notes:**
> - 四层板层压结构推荐 JLC04121H-3313（嘉立创免费选项），阻抗管控 +/-20%。
> - 旋钮主控板和接收器建议沉金处理（ENIG），QFN 等小焊盘手焊更容易。
> - 每种板嘉立创最低 5 片起订，实际每种只需 1-2 片，可组团分摊。

---

### 九、SMT 贴片 | SMT Assembly

| 项目 Item | 说明 Description | 金额 Amount (CNY) |
|---|---|---|
| SMT 贴片费 | 键盘主控板 + 旋钮主控板 + 接收器 + 音频板 | 100.00 |
| 钢网费 | 激光钢网 | 25.00 |
| **SMT 合计** | | **¥125.00** |

> **说明 Notes:**
> - 建议键盘主控板和旋钮主控板由嘉立创 SMT 贴片（QFN、BGA 等封装手工焊接难度大）。
> - 其他简单双层板（方向键小板、灯板等）可手工焊接。

---

### 十、3D 打印 / 结构件 | 3D Printing / Structural

| 编号 No. | 部件 Part | 材料 Material | 数量 Qty | 预估费用 Est. (CNY) | 备注 Notes |
|---|---|---|---|---|---|
| 51 | 键盘底壳 | PLA/PETG | 1 | 45.00 | FDM 打印，参考开源结构文件 |
| 52 | 键盘定位板 | PLA/铝板 | 1 | 20.00 | 或使用铝板 CNC 切割 |
| 53 | 旋钮外壳（上下盖）| PLA/树脂 | 1 set | 25.00 | 树脂打印精度更高 |
| 54 | 其他结构件 | PLA | 1 lot | 15.00 | 垫片、支架等 |
| **小计 Subtotal** | | | | **¥105.00** | |

---

### 十一、线缆与杂项 | Cables & Misc

| 项目 Item | 说明 Description | 金额 Amount (CNY) |
|---|---|---|
| FPC 柔性排线 | 各子板间连接用 | 10.00 |
| 硅胶线 | 电源线、电池线 | 5.00 |
| 导热硅胶垫 | MCU 散热 | 3.00 |
| 螺丝/铜柱 | M2/M3 各规格 | 5.00 |
| 硅胶减震垫 | 底壳防滑 | 5.00 |
| **小计 Subtotal** | | **¥28.00** |

---

### 十二、工具（教室共用）| Tools (Shared / Classroom-provided)

| 工具 Tool | 用途 Purpose | 是否必须 Required | 价格参考 Ref. Price |
|---|---|---|---|
| 烙铁 + 焊台（温控） | 焊接 0402~QFN 元件 | 必须（教室提供） | — |
| 焊锡丝 0.6mm | 含松香芯，精细焊接 | 必须（教室提供） | — |
| 热风枪 | QFN/芯片焊接与返修 | 必须 | ~80 元 |
| 万用表 | 电压/电流/通断测量 | 必须（教室提供） | — |
| 助焊剂 | 辅助焊接 | 建议 | ~5 元 |
| 吸锡带/吸锡器 | 去除多余焊锡 | 建议 | ~3 元 |
| ESD 防静电镊子 | 放置小元件 | 建议 | ~5 元 |
| 放大镜/显微镜 | 检查焊点质量 | 建议 | ~20 元 |
| **工具小计** | | | **~¥12.00** (消耗品) |

---

## 采购建议 | Purchasing Tips

### 分渠道采购清单 | One-stop Shopping by Channel

**嘉立创商城** (https://www.szlcsc.com/)：
- 所有被动元件（电阻、电容、电感、二极管）
- 74HC165、ME6217C33M5G、TP4056、DW01、FS8205A
- FPC 连接器、Type-C 母座、Type-A 母座
- NS4150B、ES8311、ES7210

**嘉立创 PCB** (https://www.jlc.com/)：
- 12 种 PCB 打样（4 层 x4 + 2 层 x8）
- SMT 贴片服务（主控板、旋钮板、接收器、音频板）

**淘宝**：
- ESP32-S3-WROOM-1 模块 (x3)
- SL2.1A、CH342F、GL823K
- GC9A01 圆形 LCD、AS5047P、TMC6300、HX711
- Gateron G Pro 3.0 轴体 (75 颗)
- Kailh 热插拔轴座 (75 个)
- PBT 键帽套装
- 锂电池 (3000mAh + 500mAh)
- 云台电机、应变计、扬声器、MEMS 麦克风
- 钕磁铁、卫星轴、摇杆
- 3D 打印服务（底壳、定位板、旋钮外壳）

### 预计采购时间线 | Estimated Timeline

| 时间 When | 采购内容 What | 说明 Notes |
|---|---|---|
| 开课前 3 周 | 下单所有 PCB 打样 | 4 层板约 5-7 天，2 层板约 3-5 天 |
| 开课前 3 周 | 下单 SMT 贴片 | 需等 PCB 到齐后贴片，再 3-5 天 |
| 开课前 2 周 | 下单 3D 打印 | 约 5-10 天到货 |
| 开课前 2 周 | 采购所有电子元器件 | 淘宝 3-7 天到货 |
| 开课前 1 周 | 采购轴体、键帽、轴座 | 淘宝现货通常 3 天 |
| 开课前 1 周 | 采购锂电池 | 注意物流时效，不可空运 |
| 开课前 3 天 | 检查到货清单 | 确认所有物料齐全，补漏 |

---

## 替代方案 | Alternative Parts

| 标准方案 Standard | 替代方案 Alternative | 价格差异 Price Diff | 说明 Notes |
|---|---|---|---|
| ESP32-S3-WROOM-1-N16R8 | ESP32-S3-WROOM-1-N8R8 | -8 元 | 8MB Flash 够用可省 |
| Gateron G Pro 3.0 | Kailh Box Cream / 佳达隆 CJ | 相近 | 手感偏好不同 |
| GC9A01 1.28" LCD | GC9A01A (新版) | 相近 | 兼容，色彩更好 |
| AS5047P | AS5600 (I2C 版) | -12 元 | 12-bit 精度较低，但便宜很多 |
| TMC6300 | DRV8313 | +3 元 | 三相驱动替代方案 |
| 75 键配列 | 65 键/60% 配列 | -30~-60 元 | 减少轴体和轴座数量 |
| SMT 贴片服务 | 全手工焊接 | -125 元 | QFN 封装焊接难度大，不推荐新手 |
| PBT 热升华键帽 | ABS 二色成型键帽 | -20 元 | ABS 易打油但价格更低 |

---

## 项目特色功能成本拆解 | Feature Cost Breakdown

| 功能模块 Feature Module | 额外成本 Added Cost | 说明 Notes |
|---|---|---|
| FOC 旋钮屏 | ~¥160 | 含独立 MCU、电机、编码器、屏幕 |
| 音频系统（语音交互） | ~¥30 | DAC + ADC + 功放 + 麦克风 + 扬声器 |
| 2.4G 接收器 | ~¥20 | 独立 ESP32-S3 接收器 PCB |
| USB HUB + 模拟 U 盘 | ~¥10 | SL2.1A + GL823K |
| 75 键 RGB 灯光 | ~¥25 | 100 颗 WS2812B |
| 磁吸扩展接口 | ~¥20 | Pogo pin + 保护电路 |
| 无线（WiFi/BT/ESP-NOW） | ¥0 | ESP32-S3 内置 |

---

*最后更新 | Last updated: 2026-05-27*
