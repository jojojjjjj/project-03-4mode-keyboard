# 4模式机械键盘项目资源搜索结果 | Resource Search Results
搜索日期 | Search Date: 2026-05-27

---

## 一、开源项目来源 | Source Project

| 项目 | 链接 | 说明 |
|------|------|------|
| 承载我所有幻想的键盘 | https://oshwhub.com/ran-pang/multifunctional-keyboard | 本项目原版，作者 ran-pang |
| 演示视频 | https://www.bilibili.com/video/BV1Nx4y1t7gE | B站完整演示 |

---

## 二、参考项目 | Reference Projects

| 项目 | 来源 | 说明 |
|------|------|------|
| 汉文键盘 (知乎) | 知乎/开源 | 旋钮+移位寄存器扫描方案参考 |
| X-Knob | GitHub: dingdingmushi | SmartKnob + Surface Dial 蓝牙方案 |
| ESP-BOX | Espressif官方 | 音频子系统参考设计 (ES7210/ES8311) |
| Sofle Keyboard | GitHub: josefadamcik | 分体键盘OLED+旋钮方案 |

---

## 三、核心器件价格调研 | Component Price Research

调研日期：2026-05-27 | 调研渠道：LCSC、淘宝、拼多多

### 确认价格 | Confirmed Prices

| 器件 | 渠道 | 价格 (CNY) | 备注 |
|------|------|------------|------|
| ESP32-S3-WROOM-1-N16R8 | LCSC | ~32.00 | 含8MB PSRAM |
| ESP32-S3-WROOM-1-N8 | LCSC | ~16.00 | 基础版，接收器用 |
| GC9A01 1.28" 圆形LCD | 淘宝 | ~18.00 | SPI接口 |
| TMC6300 BLDC驱动 | LCSC | ~12.00 | QFN-20 |
| AS5047P 磁编码器 | LCSC | ~22.00 | 14位TSSOP-14 |
| 74HC165 移位寄存器 | LCSC | ~0.60 | SOP-16 |
| WS2812B 5050 LED | 淘宝 | ~0.25 | 100颗批量价 |
| 佳达隆 G Pro 3.0 轴体 | 淘宝 | ~2.00 | 单颗价 |
| Kailh 热插拔座 | 淘宝 | ~0.80 | MX兼容 |
| PBT键帽套装 | 淘宝 | ~65.00 | 全键位 |

### 估算价格 | Estimated Prices

| 器件 | 估算价 (CNY) | 依据 |
|------|------------|------|
| SL2.1A USB HUB | ~3.50 | 同类USB HUB IC市场价 |
| CH342F USB-TTL | ~5.00 | 沁恒芯片常规价 |
| GL823K USB存储 | ~4.50 | Genesys Logic兼容芯片价 |
| ES8311 DAC | ~3.80 | Everest半导体常规价 |
| ES7210 ADC | ~5.50 | Everest半导体常规价 |
| NS4150B 功放 | ~1.20 | D类功放常规价 |
| BLDC云台电机 | ~15.00 | 小型云台电机淘宝价 |
| HX711 ADC | ~2.00 | 称重传感器模块常规价 |

---

## 四、PCB打样成本 | PCB Manufacturing Cost

| PCB | 层数 | 嘉立创估价 (5片) |
|-----|------|-----------------|
| 键盘主控板 300x120mm | 4层 | ~¥35 |
| 方向键子板 40x40mm | 2层 | ~¥5 |
| 音频板 50x50mm | 4层 | ~¥12 |
| 指示灯板 60x20mm | 2层 | ~¥5 |
| 磁吸连接器板 30x30mm | 2层 | ~¥5 |
| 旋钮适配板 30x30mm | 2层 | ~¥5 |
| 圆形LED板 40x40mm | 2层 | ~¥5 |
| USB子板 30x20mm | 2层 | ~¥5 |
| 旋钮主控板 50x50mm | 4层 | ~¥15 |
| 旋钮电池LED板 40x40mm | 2层 | ~¥5 |
| FPC转接板 20x20mm | 2层 | ~¥5 |
| 接收器板 30x20mm | 4层 | ~¥12 |
| **12板合计** | | **~¥114** |

---

## 五、完全复刻总成本 | Full Replication Total

| 类别 | 金额 (CNY) |
|------|-----------|
| 主控IC及有源器件 | 116.40 |
| 旋钮模块 | 82.50 |
| RGB LED | 25.00 |
| 连接器 | 31.60 |
| 被动元件 | 18.25 |
| 机械部件 | 352.00 |
| PCB制造 | 144.00 |
| SMT代工 | 125.00 |
| 3D打印/结构 | 105.00 |
| 线材/杂项 | 28.00 |
| **总计** | **¥1,027.75** |

---

*最后更新 | Last updated: 2026-05-27*
