# Day 02: 数字电路与ESP32-S3入门 | Digital Circuits & ESP32-S3 Introduction

## 今日目标 | Today's Goals
- 理解数字信号基础：HIGH/LOW、二进制、十六进制
- 认识微控制器（MCU）的架构与功能
- 完成 ESP32-S3 开发环境配置
- 编写并烧录第一个程序：LED 闪烁

## 知识讲解 | Knowledge Lecture (09:15-10:30)

### 数字逻辑基础 | Digital Logic Fundamentals

#### 1. 模拟信号 vs 数字信号

```
模拟信号 Analog:          数字信号 Digital:
    ~~~~/----\~~~~          ____|^^^^|____|^^^^|
   /          \             HIGH(3.3V) LOW(0V)
  /            \
```

- **模拟信号**：连续变化的电压值，如温度传感器输出、音频波形
- **数字信号**：只有两个状态——HIGH（高电平，逻辑1）和 LOW（低电平，逻辑0）
- 计算机世界只有 0 和 1 —— 这是所有数字电路的基础

#### 2. 二进制与十六进制

| 十进制 Dec | 二进制 Bin | 十六进制 Hex |
|---|---|---|
| 0 | 0000 0000 | 0x00 |
| 1 | 0000 0001 | 0x01 |
| 10 | 0000 1010 | 0x0A |
| 15 | 0000 1111 | 0x0F |
| 255 | 1111 1111 | 0xFF |
| 1024 | 0100 0000 0000 | 0x400 |

**为什么学十六进制？**
- 一个8位寄存器的值用 `0xFF` 比 `11111111` 更简洁
- I2C地址、寄存器地址、内存地址都用十六进制表示
- 例如 ES8311 的 I2C 地址是 `0x18`，74HC165 锁存引脚是 `PL = 0`

#### 3. 逻辑门简介

| 逻辑门 | 符号 | 真值表 | 应用 |
|---|---|---|---|
| AND | A & B | 全1出1 | 使能控制 |
| OR | A \| B | 有1出1 | 中断标志 |
| NOT | !A | 取反 | 电平转换 |
| XOR | A ^ B | 不同出1 | FantasyKB扩展接口身份识别 |

> FantasyKB的磁吸扩展接口使用异或门（XOR）逻辑来判断扩展模块类型——两个电压监控芯片的输出做异或运算，根据结果决定供电方向和I2C总线开关。

---

### 微控制器（MCU）架构 | Microcontroller Architecture

#### 什么是微控制器?

微控制器 = 处理器(CPU) + 内存(RAM/Flash) + 外设(GPIO/UART/SPI/I2C) 集成在一颗芯片上。

```
+--------------------------------------------------+
|                  ESP32-S3 芯片内部                  |
|                                                    |
|  +----------+   +---------+   +----------------+  |
|  | Xtensa   |   | 512KB   |   | 384KB          |  |
|  | LX7 双核 |-->| SRAM    |   | ROM            |  |
|  | 240MHz   |   +---------+   +----------------+  |
|  +----------+                                       |
|        |                                            |
|  +-----+--------------------------------------+    |
|  | GPIO | SPI | I2C | I2S | UART | USB | WiFi |   |
|  | 45pin| x2  | x2  | x2  | x3   | OTG | BLE  |   |
|  +----------------------------------------------+  |
+--------------------------------------------------+
```

#### ESP32-S3 关键参数

| 参数 Parameter | 值 Value | 说明 |
|---|---|---|
| CPU | Xtensa LX7 双核 240MHz | 性能强劲 |
| SRAM | 512KB | 程序运行内存 |
| Flash | 外部（通常8-16MB） | 存储程序 |
| GPIO | 45 个 | 通用输入输出 |
| WiFi | 802.11 b/g/n | 2.4GHz |
| BLE | Bluetooth 5.0 LE | 低功耗蓝牙 |
| USB | USB OTG 2.0 Full-Speed | 支持HID |
| SPI | 2 组 | 高速通信 |
| I2C | 2 组 | 芯片间通信 |
| I2S | 2 组 | 数字音频 |

**为什么选 ESP32-S3？**
一颗芯片就集成了WiFi、蓝牙、USB——FantasyKB的4种通信模式全部由这颗芯片实现，无需额外的无线模块。

---

## 动手实验 | Hands-on Lab (10:45-12:00)

### 任务 2.1: 第一个程序——LED 闪烁

**接线 Wiring:**
- ESP32-S3 开发板内置LED通常在 GPIO2 或 GPIO38
- 如需外接LED：GPIO2 -> 220ohm电阻 -> LED(+) -> LED(-) -> GND

**代码 Code:**

```c
// hello_led.c — ESP32-S3 LED 闪烁程序
// 使用 ESP-IDF 框架

#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"

#define BLINK_GPIO 2  // 根据开发板调整引脚号

void app_main(void)
{
    // 1. 初始化GPIO
    gpio_reset_pin(BLINK_GPIO);
    gpio_set_direction(BLINK_GPIO, GPIO_MODE_OUTPUT);

    int led_state = 0;

    // 2. 主循环：闪烁LED
    while (1) {
        printf("LED state: %d\n", led_state);
        gpio_set_level(BLINK_GPIO, led_state);
        led_state = !led_state;        // 翻转状态 0 <-> 1
        vTaskDelay(500 / portTICK_PERIOD_MS);  // 延时500ms
    }
}
```

**编译与烧录步骤：**
1. 在 VS Code 中打开 ESP-IDF 项目
2. 点击底部状态栏的 "Build"（锤子图标）编译
3. 用 USB 线连接 ESP32-S3 开发板
4. 点击 "Flash"（闪电图标）烧录
5. 点击 "Monitor"（显示器图标）查看串口输出

**预期结果 Expected Result:**
- LED 以 1Hz 频率闪烁（每500ms切换一次）
- 串口监视器打印 LED 状态信息

---

### 任务 2.2: GPIO 输入——按键读取

**接线 Wiring:**
```
GPIO9 ----[按键开关]---- GND
       |
     [10k 上拉电阻]
       |
     3.3V
```

> ESP32-S3 的 GPIO 可以配置内部上拉电阻，无需外接电阻。

**代码 Code:**

```c
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define BUTTON_GPIO 9
#define LED_GPIO    2

void app_main(void)
{
    // 配置LED输出
    gpio_reset_pin(LED_GPIO);
    gpio_set_direction(LED_GPIO, GPIO_MODE_OUTPUT);

    // 配置按键输入（内部上拉）
    gpio_reset_pin(BUTTON_GPIO);
    gpio_set_direction(BUTTON_GPIO, GPIO_MODE_INPUT);
    gpio_pullup_en(BUTTON_GPIO);       // 启用内部上拉
    gpio_pulldown_dis(BUTTON_GPIO);    // 禁用下拉

    while (1) {
        // 读取按键状态：按下为0（接地），松开为1（上拉）
        int button_state = gpio_get_level(BUTTON_GPIO);

        if (button_state == 0) {
            gpio_set_level(LED_GPIO, 1);  // 按下点亮LED
        } else {
            gpio_set_level(LED_GPIO, 0);  // 松开熄灭LED
        }

        vTaskDelay(10 / portTICK_PERIOD_MS);  // 10ms 轮询
    }
}
```

**预期结果：**
- 按下按键时LED亮起，松开时熄灭
- 注意：此时可能观察到按键抖动（LED偶尔闪烁）

---

## 项目实践 | Project Work (13:30-16:30)

### 任务 2.3: 串口通信基础

**为什么要学串口？**
串口（UART）是嵌入式开发中最常用的调试手段。FantasyKB 项目中，CH342F USB-TTL芯片将键盘主控的串口转为USB，用于固件下载和调试信息输出。

**串口参数：**
| 参数 | 值 | 说明 |
|---|---|---|
| 波特率 | 115200 | 最常用 |
| 数据位 | 8 | |
| 停止位 | 1 | |
| 校验 | None | |

**使用 printf 输出调试信息：**

```c
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

void app_main(void)
{
    int count = 0;
    while (1) {
        printf("FantasyKB Debug: count = %d, tick = %d\n",
               count++, xTaskGetTickCount());
        vTaskDelay(1000 / portTICK_PERIOD_MS);
    }
}
```

---

### 任务 2.4: 修改闪烁模式挑战

**挑战要求：**
修改 LED 闪烁程序，实现以下模式之一：

1. **SOS摩尔斯码**：短闪3次 -> 长闪3次 -> 短闪3次（S = ... O = --- S = ...）
2. **二进制计数器**：用LED的亮灭显示0-15的二进制值（需要4个LED）
3. **呼吸灯效果**：使用PWM让LED亮度渐变（进阶挑战）

**参考代码——SOS模式：**

```c
void sos_blink(void)
{
    // S: 3短闪
    for (int i = 0; i < 3; i++) {
        gpio_set_level(LED_GPIO, 1); vTaskDelay(150 / portTICK_PERIOD_MS);
        gpio_set_level(LED_GPIO, 0); vTaskDelay(150 / portTICK_PERIOD_MS);
    }
    vTaskDelay(300 / portTICK_PERIOD_MS);

    // O: 3长闪
    for (int i = 0; i < 3; i++) {
        gpio_set_level(LED_GPIO, 1); vTaskDelay(400 / portTICK_PERIOD_MS);
        gpio_set_level(LED_GPIO, 0); vTaskDelay(400 / portTICK_PERIOD_MS);
    }
    vTaskDelay(300 / portTICK_PERIOD_MS);

    // S: 3短闪
    for (int i = 0; i < 3; i++) {
        gpio_set_level(LED_GPIO, 1); vTaskDelay(150 / portTICK_PERIOD_MS);
        gpio_set_level(LED_GPIO, 0); vTaskDelay(150 / portTICK_PERIOD_MS);
    }
    vTaskDelay(1000 / portTICK_PERIOD_MS);  // 间隔1秒后重复
}
```

---

## 日终总结 | Daily Wrap-up (16:30-17:00)

**今日关键要点：**
1. 数字电路只有两种状态：HIGH(1) 和 LOW(0)
2. ESP32-S3 是一颗功能强大的微控制器，内置WiFi/BLE/USB
3. GPIO是MCU与外部世界交互的基本方式
4. 串口（UART）是最重要的调试工具

**明日预告：**
明天学习SPI通信协议和74HC165移位寄存器——这是FantasyKB检测80多个按键的核心技术。你将理解如何用3根线读取80个按键的状态！

---

## 今日作业 | Homework

1. **完成实验报告**：LED闪烁代码截图 + 串口输出截图 + 按键实验照片
2. **思考题**：
   - ESP32-S3 的 GPIO 输出高电平是 3.3V，如果需要驱动 5V 的 LED 灯珠，应该怎么办？
   - 按键抖动（bounce）是什么？为什么需要在程序中处理？
   - 将十进制 165 转换为二进制和十六进制。
3. **预习 Day 3**：搜索 "74HC165 移位寄存器 原理"，了解如何用串行方式读取并行输入

---

## 常见问题 | FAQ

**Q: ESP-IDF 编译很慢怎么办？**
A: 首次编译需要编译整个框架（约5-10分钟）。后续增量编译只编译修改的文件，速度快很多。确保电脑有足够的磁盘空间（>10GB）。

**Q: 烧录失败，提示 "无法打开串口" 怎么办？**
A: (1) 检查USB线是否支持数据传输（有些线只能充电）(2) 检查设备管理器中是否识别到COM口 (3) 尝试按住开发板上的BOOT键再烧录。

**Q: 如何知道我的开发板LED在哪个GPIO？**
A: 查看开发板文档或丝印标注。常见ESP32-S3开发板LED在GPIO2。如果不确定，用万用表测量或查看厂商Wiki。

---

## 参考资源 | References

- ESP-IDF GPIO 驱动文档：https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/peripherals/gpio.html
- ESP32-S3 技术规格书：https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf
- B 站搜索 "ESP32-S3 入门教程 LED 闪烁"
- B 站搜索 "ESP-IDF 开发环境搭建"

---

*最后更新 | Last updated: 2026-05-27*
