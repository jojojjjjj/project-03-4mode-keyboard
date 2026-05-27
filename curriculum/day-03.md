# Day 03: SPI协议与移位寄存器 | SPI Protocol & Shift Registers

## 今日目标 | Today's Goals
- 理解三种常见通信协议（SPI/I2C/UART）的区别与应用场景
- 深入掌握 SPI 协议的工作原理（时钟极性/相位、主从模式）
- 学会使用 74HC165 并转串移位寄存器
- 在面包板上实现用 SPI 读取 8 个按键

## 知识讲解 | Knowledge Lecture (09:15-10:30)

### 通信协议概览 | Communication Protocol Overview

微控制器需要与各种外设芯片通信。为什么不能像LED那样直接用GPIO控制？因为按键太多了——FantasyKB有80多个按键，ESP32-S3没有那么多的GPIO引脚。通信协议就是用少量引脚传输大量数据的方法。

```
FantasyKB 按键检测方案：
80+ 个按键 ──> 10个74HC165移位寄存器（链式连接）──> SPI总线（4根线）──> ESP32-S3
                 并行输入，串行输出                           只需4个GPIO！
```

#### 三种协议对比

| 特性 | SPI | I2C | UART |
|---|---|---|---|
| 全称 | Serial Peripheral Interface | Inter-Integrated Circuit | Universal Async Receiver/Transmitter |
| 线数 | 4根（SCLK/MOSI/MISO/CS） | 2根（SCL/SDA） | 2根（TX/RX） |
| 速率 | 高（可达80MHz） | 中（100k-3.4MHz） | 低（通常115200 baud） |
| 全双工 | 是 | 否（半双工） | 是 |
| 多设备 | 每个设备需要独立CS线 | 地址寻址（7/10位） | 点对点 |
| 应用 | 移位寄存器、显示屏、SD卡 | 传感器、EEPROM、音频编解码器 | 串口调试、GPS模块 |

---

### SPI协议深入讲解 | SPI Protocol Deep Dive

#### SPI 四根线的功能

```
Master (ESP32-S3)              Slave (74HC165)
    SCLK ──────────────────> CLK      时钟线（Master驱动）
    MOSI ──────────────────> SER      主输出从输入（数据输出）
    MISO <────────────────── Q7       主输入从输出（数据输入）
    CS   ──────────────────> PL       片选（低有效，锁存控制）
```

| 信号 | 方向 | 功能 |
|---|---|---|
| **SCLK** | Master -> Slave | 时钟信号，每个边沿传输一位数据 |
| **MOSI** | Master -> Slave | 主设备发送的数据 |
| **MISO** | Slave -> Master | 从设备返回的数据 |
| **CS** | Master -> Slave | 片选，拉低表示开始通信 |

#### SPI 通信时序

```
CS:   ‾‾‾‾‾\___________________________/‾‾‾‾‾‾
            |  通信开始                    通信结束
SCLK: ______|_‾|_|‾|_|‾|_|‾|_|‾|_|‾|_|‾|_|‾|______
           C0  C1  C2  C3  C4  C5  C6  C7

MISO: ----< D7  D6  D5  D4  D3  D2  D1  D0 >------
      (高位先发)
```

#### SPI 在 FantasyKB 中的应用

FantasyKB 的按键检测参考了稚辉君的瀚文键盘，使用 **74HC165 移位寄存器**：
- 每个 74HC165 有 8 个并行输入（D0-D7），可以连接 8 个按键
- 10 个 74HC165 菊花链（daisy-chain）连接，可以检测 80 个按键
- ESP32-S3 只需 4 个 GPIO（SCLK/MISO/CS + 一个锁存控制）就能读取全部按键

---

## 动手实验 | Hands-on Lab (10:45-12:00)

### 任务 3.1: 单个 74HC165 连接与测试

**所需材料 Materials:**
- ESP32-S3 开发板 x 1
- 74HC165 芯片 x 1
- 按键开关 x 8（或用杜邦线模拟）
- 面包板 + 杜邦线

**74HC165 引脚功能：**

| 引脚 | 名称 | 功能 |
|---|---|---|
| 1 | PL (PL) | 并行加载（低有效）：拉低时锁存8个输入到内部寄存器 |
| 2 | CP (CLK) | 时钟输入 |
| 3-6, 11-14 | D0-D7 | 8个并行数据输入 |
| 7 | Q7 | 串行输出（连接到ESP32-S3的MISO） |
| 9 | Q7' | 级联输出（连接到下一个74HC165的SER） |
| 10 | SER | 串行输入（级联时连接上一个的Q7'） |
| 15 | CE | 时钟使能（低有效） |
| 16 | VCC | 电源（3.3V或5V） |
| 8 | GND | 地 |

**接线方案 Wiring:**

```
ESP32-S3              74HC165
GPIO4 (CS)   ------>  PL (pin 1)     锁存控制
GPIO5 (SCLK) ------>  CP (pin 2)     时钟
GPIO6 (MISO) <------  Q7 (pin 7)     数据输出
                     SER (pin 10) --> VCC (无级联时接高)
                     CE  (pin 15) --> GND (始终使能)
                     VCC (pin 16) --> 3.3V
                     GND (pin 8)  --> GND

D0-D7 (pins 3-6, 11-14) 各通过一个按键接地
按键未按下 = 高电平（需10k上拉电阻或使用内部上拉）
按键按下   = 低电平（接地）
```

**代码 Code:**

```c
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"

// 引脚定义
#define PIN_PL   4   // 锁存控制 (CS)
#define PIN_CLK  5   // 时钟
#define PIN_DATA 6   // 数据输入 (MISO)

/**
 * 从74HC165读取8位并行输入
 * Read 8-bit parallel input from 74HC165
 */
uint8_t read_74hc165(void)
{
    uint8_t data = 0;

    // 步骤1: 拉低PL，锁存并行输入
    gpio_set_level(PIN_PL, 0);
    // 短暂延时确保锁存完成
    ets_delay_us(5);
    gpio_set_level(PIN_PL, 1);
    ets_delay_us(5);

    // 步骤2: 读取8位数据（高位先出）
    for (int i = 7; i >= 0; i--) {
        // 读取当前数据位
        int bit = gpio_get_level(PIN_DATA);
        if (bit) {
            data |= (1 << i);  // 设置对应位
        }
        // 产生时钟上升沿，移出下一位
        gpio_set_level(PIN_CLK, 0);
        ets_delay_us(2);
        gpio_set_level(PIN_CLK, 1);
        ets_delay_us(2);
    }

    return data;
}

void app_main(void)
{
    // 初始化GPIO
    gpio_reset_pin(PIN_PL);
    gpio_set_direction(PIN_PL, GPIO_MODE_OUTPUT);
    gpio_set_level(PIN_PL, 1);

    gpio_reset_pin(PIN_CLK);
    gpio_set_direction(PIN_CLK, GPIO_MODE_OUTPUT);
    gpio_set_level(PIN_CLK, 1);

    gpio_reset_pin(PIN_DATA);
    gpio_set_direction(PIN_DATA, GPIO_MODE_INPUT);

    printf("FantasyKB - 74HC165 Shift Register Test\n");

    while (1) {
        uint8_t keys = read_74hc165();
        printf("Keys: 0x%02X (", keys);
        for (int i = 7; i >= 0; i--) {
            printf("%d", (keys >> i) & 1);
        }
        printf(")\n");

        // 检测哪个按键被按下（低电平=按下）
        for (int i = 0; i < 8; i++) {
            if (!(keys & (1 << i))) {
                printf("  -> Key %d pressed!\n", i);
            }
        }

        vTaskDelay(100 / portTICK_PERIOD_MS);
    }
}
```

**预期结果 Expected Result:**
- 串口输出8位二进制值，如 `Keys: 0xFF (11111111)` 表示无按键按下
- 按下某个按键后，对应位变为0，如 `Keys: 0xFB (11111011)` 表示第2个按键被按下

---

## 项目实践 | Project Work (13:30-16:30)

### 任务 3.2: 菊花链多个 74HC165

**为什么需要菊花链?**
FantasyKB 有 80+ 个按键，需要 10 个 74HC165 芯片。菊花链连接让多个芯片共享同一组SPI线。

**菊花链连接方式：**

```
ESP32-S3
  |
  PL ----+----------+----------+----------+
  CLK ---+----------+----------+----------+
  DATA <-- Q7       |          |          |
          74HC165#1 |          |          |
          Q7' ----> SER       |          |
                    74HC165#2 |          |
                    Q7' ----> SER       |
                              74HC165#3 |
                              Q7' ----> SER
                                        74HC165#N...
```

**级联规则：**
- 所有芯片的 PL 和 CLK 并联
- 第1个芯片的 Q7 连接到 ESP32-S3 的 MISO
- 前一个芯片的 Q7' 连接到下一个芯片的 SER
- 读取时，先读到的数据来自第1个芯片，后读到的来自后面的芯片

**读取N个芯片的代码：**

```c
#define NUM_REGISTERS 2  // 先用2个芯片测试

/**
 * 从N个菊花链连接的74HC165读取数据
 * Read data from N daisy-chained 74HC165s
 */
void read_all_keys(uint8_t *buffer, int count)
{
    // 锁存所有芯片的并行输入
    gpio_set_level(PIN_PL, 0);
    ets_delay_us(5);
    gpio_set_level(PIN_PL, 1);
    ets_delay_us(5);

    // 逐位读取
    for (int chip = 0; chip < count; chip++) {
        buffer[chip] = 0;
        for (int bit = 7; bit >= 0; bit--) {
            int val = gpio_get_level(PIN_DATA);
            if (val) buffer[chip] |= (1 << bit);

            gpio_set_level(PIN_CLK, 0);
            ets_delay_us(2);
            gpio_set_level(PIN_CLK, 1);
            ets_delay_us(2);
        }
    }
}

void app_main(void)
{
    // ... GPIO初始化同上 ...

    uint8_t key_data[NUM_REGISTERS];

    while (1) {
        read_all_keys(key_data, NUM_REGISTERS);

        printf("Keys: ");
        for (int i = 0; i < NUM_REGISTERS; i++) {
            printf("Chip%d=0x%02X ", i, key_data[i]);
        }
        printf("\n");

        vTaskDelay(100 / portTICK_PERIOD_MS);
    }
}
```

---

### 任务 3.3: 按键消抖与事件检测

**消抖原理：**
机械按键在按下/松开的5-20ms内会快速弹跳。FantasyKB 使用软件消抖——连续N次扫描结果一致才确认状态变化。

```c
#define DEBOUNCE_COUNT 5

uint8_t last_state[NUM_REGISTERS] = {0};
uint8_t stable_state[NUM_REGISTERS] = {0};
uint8_t debounce[NUM_REGISTERS][8] = {0};

void scan_with_debounce(void)
{
    uint8_t current[NUM_REGISTERS];
    read_all_keys(current, NUM_REGISTERS);

    for (int chip = 0; chip < NUM_REGISTERS; chip++) {
        for (int bit = 0; bit < 8; bit++) {
            bool now_pressed = !(current[chip] & (1 << bit));
            bool was_pressed = !(stable_state[chip] & (1 << bit));

            if (now_pressed != was_pressed) {
                debounce[chip][bit]++;
                if (debounce[chip][bit] >= DEBOUNCE_COUNT) {
                    // 状态确认变化
                    if (now_pressed) {
                        stable_state[chip] &= ~(1 << bit);
                        printf("Key[%d][%d] PRESSED\n", chip, bit);
                    } else {
                        stable_state[chip] |= (1 << bit);
                        printf("Key[%d][%d] RELEASED\n", chip, bit);
                    }
                    debounce[chip][bit] = 0;
                }
            } else {
                debounce[chip][bit] = 0;
            }
        }
    }
}
```

---

## 日终总结 | Daily Wrap-up (16:30-17:00)

**今日关键要点：**
1. **SPI** 是高速全双工协议，适合移位寄存器、显示屏等需要快速数据传输的场景
2. **74HC165** 将8个并行输入转为1根串行线输出，是FantasyKB按键检测的核心芯片
3. **菊花链** 连接让多个74HC165共享SPI总线，用4根GPIO读取80+个按键
4. **消抖** 是按键检测中不可省略的步骤

**明日预告：**
明天学习 I2C 协议和音频子系统——ES7210 ADC（录音）+ ES8311 DAC（播放），你将在面包板上实现录音和播放功能！

---

## 今日作业 | Homework

1. **完成实验报告**：74HC165接线照片 + 串口输出截图
2. **扩展任务**：连接2个以上的74HC165，读取16+个按键并打印每个按键的编号
3. **思考题**：
   - 如果需要读取 80 个按键，需要多少个 74HC165？读取一次需要多少个时钟周期？
   - SPI 的时钟频率为 1MHz 时，读取 80 个按键需要多少微秒？
   - 74HC165 的 PL 引脚在什么时刻应该拉低？如果在读取过程中一直拉低会怎样？
4. **预习 Day 4**：搜索 "I2C 协议 原理" 和 "I2S 数字音频接口"

---

## 常见问题 | FAQ

**Q: 74HC165 读取的数据全是 0xFF 或全是 0x00 怎么办？**
A: 全0xFF说明没有按键按下（输入悬空为高）。全0x00检查：(1) VCC/GND是否接好 (2) CE引脚是否接GND (3) PL时序是否正确。用万用表逐个检查引脚电压。

**Q: 菊花链连接后后面的芯片数据不对？**
A: 检查Q7'到SER的连接是否正确，确认方向是从前一个芯片的Q7'到下一个的SER。读取顺序是先读第1个芯片，所以数组索引0对应的是物理上离ESP32最近的芯片。

**Q: 按键按下但检测不到？**
A: 确认按键的一端连接到74HC165的D0-D7，另一端连接到GND。未按下时输入应为高电平（需要上拉电阻）。有些74HC165模块已内置上拉电阻。

---

## 参考资源 | References

- 74HC165 数据手册（搜索 "74HC165 datasheet PDF"）
- 瀚文键盘项目（移位寄存器方案参考）：https://oshwhub.com/
- ESP-IDF SPI 驱动文档：https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/peripherals/spi_master.html
- B 站搜索 "74HC165 移位寄存器 教程"
- B 站搜索 "SPI 协议 详解"

---

*最后更新 | Last updated: 2026-05-27*
