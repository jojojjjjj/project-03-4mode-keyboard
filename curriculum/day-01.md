# Day 01: 项目启动与电子学基础 | Project Kickoff & Electronics Fundamentals

## 今日目标 | Today's Goals
- 了解项目全貌，明确20天学习目标和最终成果
- 掌握基本电路理论：电压、电流、电阻、欧姆定律
- 学会使用面包板和万用表
- 完成第一个电路：LED点亮与闪烁

## 知识讲解 | Knowledge Lecture (09:15-10:30)

### 为什么要学电子学? | Why Learn Electronics?

电子学是所有硬件项目的基础。你即将构建的4模式机械键盘内部包含ESP32-S3微控制器、移位寄存器、音频编解码器、无线模块、电机驱动等数十种芯片，它们全部通过电路连接协同工作。不理解基本的电路理论，后续的键盘扫描、SPI通信、电源设计都无法真正理解。

Electronics is the foundation of all hardware projects. Your 4-mode keyboard contains an ESP32-S3 MCU, shift registers, audio codecs, wireless modules, motor drivers, and dozens of other chips connected by circuits. Without basic circuit theory, you cannot truly grasp keyboard scanning, SPI communication, or power design.

---

### 任务 1.1: 项目概述与团队组建 (30 分钟)

**步骤 Steps:**

1. **观看项目演示视频** — 展示最终成品：4模式无线键盘 + FOC旋钮 + 语音交互
2. **了解项目架构** — 浏览开源项目 https://oshwhub.com/ran-pang/multifunctional-keyboard
3. **分组** — 每 2-3 人一组，选出组长
4. **环境检查** — 确认电脑已安装 VS Code、Python、Git

**FantasyKB 核心功能一览:**

| 功能 Function | 技术实现 Implementation |
|---|---|
| USB有线模式 | USB HID 协议，SL2.1A Hub扩展 |
| 蓝牙BLE模式 | ESP32-S3 内置BLE 5.0 |
| WiFi模式 | ESP32-S3 WiFi STA/AP |
| 2.4GHz接收器模式 | ESP-NOW 对等通信 |
| FOC旋钮 | TMC6300驱动 + AS5047P编码器 + GC9A01圆形屏 |
| 语音交互 | ES7210 ADC + ES8311 DAC + 扬声器 + 双麦克风 |
| RGB灯效 | WS2812B 级联LED |
| 磁吸扩展 | I2C接口 + 身份识别电路 |

---

### 任务 1.2: 电路基础理论 (45 分钟)

#### 1. 电压 (Voltage, V)
- 类比：水压 —— 推动电子流动的"压力"
- 单位：伏特 (V)
- 常见电压：USB 5V，锂电池 3.7V，ESP32-S3 IO 为 3.3V

#### 2. 电流 (Current, I)
- 类比：水流 —— 单位时间内流过导体的电子数量
- 单位：安培 (A)，常用毫安 (mA)
- 1A = 1000mA

#### 3. 电阻 (Resistance, R)
- 类比：水管粗细 —— 阻碍电流流动的能力
- 单位：欧姆 (ohm)，常用千欧 (kohm)

#### 4. 欧姆定律 (Ohm's Law)
```
V = I x R
电压 = 电流 x 电阻

变形公式：
I = V / R    （已知电压和电阻，求电流）
R = V / I    （已知电压和电流，求电阻）
```

**实例计算 Example:**
- LED 工作电压 2V，工作电流 20mA，电源 3.3V
- 需要的限流电阻 = (3.3V - 2V) / 0.02A = 65 ohm
- 实际选用 100 ohm（标准阻值，偏安全）

#### 5. 串联与并联 (Series & Parallel)
- 串联：电阻相加，R_total = R1 + R2；电流相同，电压分配
- 并联：1/R_total = 1/R1 + 1/R2；电压相同，电流分配

#### 6. 基尔霍夫定律简介 (Kirchhoff's Laws)
- **KCL（电流定律）**：流进一个节点的电流之和 = 流出的电流之和
- **KVL（电压定律）**：闭合回路中电压的代数和 = 0
- 应用：电源预算计算、分压电路设计

**课堂练习 Classroom Exercise:**
1. 一个 100 ohm 的电阻接在 3.3V 电源上，流过的电流是多少？（答案：33mA）
2. 两个 1kohm 电阻并联，总电阻是多少？（答案：500 ohm）
3. ESP32-S3 工作电流约 200mA，WS2812B 每颗最大 60mA，10颗LED全亮时总功耗是多少？3.7V锂电池能供电多久？（1000mAh电池）

---

## 动手实验 | Hands-on Lab (10:45-12:00)

### 任务 1.3: 万用表使用与面包板基础

**万用表三种基本测量：**

| 测量模式 | 用途 | 注意事项 |
|---|---|---|
| 电压档 (V) | 测量两点间电压 | 并联在被测电路两端 |
| 电流档 (A) | 测量流过电路的电流 | 串联在电路中（必须断开原电路） |
| 通断档 (蜂鸣) | 检查导线/焊点是否连通 | 断电测量，蜂鸣声表示导通 |

**面包板结构 Breadboard Layout:**
```
      电源轨           元件区
    +   -    a  b  c  d  e   f  g  h  i  j
    |   |    |  |  |  |  |   |  |  |  |  |
 ===|===|====|==|==|==|==|===|==|==|==|==|===  (上半部分)
    |   |    |  |  |  |  |   |  |  |  |  |
 ---|---|----|--|--|--|--|---|--|--|--|--|---  (中间隔离)
    |   |    |  |  |  |  |   |  |  |  |  |
 ===|===|====|==|==|==|==|===|==|==|==|==|===  (下半部分)
    |   |    |  |  |  |  |   |  |  |  |  |
```
- 每列的 a-e 和 f-j 内部连通
- 上下两半通过中间隔离条分开
- 电源轨（+/-）纵向贯通

**练习步骤：**
1. 用万用表测量USB口输出电压（应为5V）
2. 用通断档验证面包板的内部连通关系
3. 测量一个100 ohm电阻的实际阻值

---

### 任务 1.4: 面包板LED点亮实验

**所需材料 Materials:**
- 面包板 x 1
- LED（红色）x 3
- 100 ohm / 220 ohm 电阻 x 3
- 杜邦线 x 若干
- ESP32-S3 开发板 x 1

**步骤 Steps:**

1. **单颗LED点亮**：
   - ESP32-S3 开发板的 3.3V 连到面包板电源轨
   - 100 ohm 电阻从电源轨 + 连到元件区
   - LED 长脚（+）接电阻另一端，短脚（-）接 GND
   - 通电，LED 应亮起

2. **串联LED实验**：
   - 两颗LED串联（长脚接短脚），再串联一个电阻
   - 观察亮度变化——两颗LED分压，可能都不亮（3.3V不够两颗LED的压降）

3. **并联LED实验**：
   - 两颗LED并联（长脚都接电阻，短脚都接GND）
   - 观察亮度——两颗都正常亮

**电路图 Circuit Diagram:**
```
ESP32-S3 3.3V ──── 100 ohm ──── LED(+) ──── LED(-) ──── GND
                   限流电阻       长脚(阳极)      短脚(阴极)
```

**常见问题 Common Issues:**

| 问题 Problem | 可能原因 Cause | 解决方法 Solution |
|---|---|---|
| LED 不亮 | 极性接反 | 长脚接正极，短脚接负极 |
| LED 不亮 | 面包板接触不良 | 重新插紧杜邦线 |
| LED 很暗 | 电阻太大 | 换用较小电阻 |
| LED 烧了 | 没接限流电阻 | 一定先接电阻再通电！ |

---

## 项目实践 | Project Work (13:30-16:30)

### 任务 1.5: 电压分压电路与电流测量

**电压分压器 Voltage Divider:**
```
VCC (3.3V)
  |
 [R1 = 10k]
  |---- Vout = 3.3 x R2/(R1+R2)
 [R2 = 10k]
  |
 GND
```

当 R1 = R2 = 10kohm 时，Vout = 3.3 x 10/(10+10) = 1.65V

**实践步骤：**
1. 在面包板上搭建分压电路
2. 用万用表测量 Vout，验证计算结果
3. 更换不同电阻值，观察输出变化

**为什么学这个？** FantasyKB 的磁吸扩展接口正是使用电阻分压来识别不同类型的扩展模块——通过检测FPC第6脚的电压判断连接的是供电模块还是小键盘模块。

---

### 任务 1.6: ESP32-S3 开发环境安装

**安装步骤 Installation Steps:**

1. **安装 VS Code**（如已安装则跳过）
2. **安装 ESP-IDF 插件**：
   - 打开 VS Code 扩展商店
   - 搜索 "ESP-IDF" 并安装 Espressif IDF 插件
   - 按照向导下载 ESP-IDF v5.x（约 2-3 GB，需要良好网络）
3. **验证安装**：
   - 创建新的 ESP-IDF 项目
   - 选择芯片 ESP32-S3
   - 编译示例 "hello_world"
   - 确认编译成功

> **网络提示**：ESP-IDF 下载可能较慢，建议提前配置镜像源。如网络受限，可使用离线安装包。
> **Network Note**: ESP-IDF download is large. Pre-configure mirror sources or use offline installer if needed.

---

## 日终总结 | Daily Wrap-up (16:30-17:00)

**今日关键要点 Key Takeaways:**

1. **欧姆定律** V = IR 是电子学的基石，所有电路分析都从这里出发
2. **串联分压、并联分流** — 理解这两种基本连接方式是分析复杂电路的前提
3. **万用表**是你最常用的调试工具——学会它、信任它
4. **ESP32-S3**是本项目的核心大脑，内置WiFi/BLE/USB，一颗芯片实现4种通信模式

**明日预告 Tomorrow's Preview:**
明天将正式接触 ESP32-S3 微控制器，学习数字电路基础，点亮你的第一个由程序控制的LED！

---

## 今日作业 | Homework

1. **完成面包板实验报告**：拍照记录电路，写下电压/电流测量值
2. **思考题**：
   - 如果把 LED 的极性反过来接，会发生什么？
   - FantasyKB 键盘有约 80 颗 WS2812B LED，全白全亮时总电流是多少？USB 5V/500mA 能否直接驱动？
   - 电压分压器中，如果 R1 开路（断开），Vout 是多少？如果 R2 短路呢？
3. **预习 Day 2**：搜索 "ESP32-S3 入门教程"，了解什么是微控制器

---

## 常见问题 | FAQ

**Q: ESP-IDF 安装失败怎么办？**
A: 最常见的原因是网络问题。可以尝试：使用手机热点、配置国内镜像源（如乐鑫官方镜像）、或下载离线安装包。具体方法见 ESP-IDF 官方文档的 "Offline Installation" 章节。

**Q: 面包板上的LED为什么不亮？**
A: 按以下顺序排查：(1) LED极性是否正确（长脚接+）(2) 电阻是否太大（试试100ohm）(3) 面包板接触是否良好（拔插一下杜邦线）(4) 电源是否接通（用万用表量3.3V输出）。

**Q: 我之前没有用过命令行，会影响后续学习吗？**
A: 不会。课程中会手把手教授所需的命令行操作。ESP-IDF 插件已经将大部分操作集成到 VS Code 的图形界面中，命令行使用频率不高。

---

## 参考资源 | References

- 嘉立创开源项目（本项目参考）：https://oshwhub.com/ran-pang/multifunctional-keyboard
- ESP-IDF 官方快速入门：https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/get-started/
- B 站搜索 "欧姆定律 入门讲解"
- B 站搜索 "面包板使用教程 入门"
- B 站搜索 "ESP32-S3 入门教程"

---

*最后更新 | Last updated: 2026-05-27*
