# Day 08: WS2812B RGB灯效 | WS2812B RGB Lighting Effects

## 今日目标 | Today's Goals
- 深入理解 WS2812B 单线通信协议的时序要求
- 使用 ESP32-S3 的 RMT 外设精确驱动 WS2812B
- 实现基础灯效：静态颜色、彩虹、呼吸灯
- 完成RGB灯效的功耗预算与管理策略

## 知识讲解 | Knowledge Lecture (09:15-10:30)

### WS2812B 协议原理 | WS2812B Protocol

FantasyKB 有约80颗 WS2812B LED（键盘按键背光），每颗LED需要24位颜色数据，通过一根数据线级联传输。

#### 数据格式（GRB顺序）

```
一颗 LED 的 24 位数据（注意：GRB 不是 RGB！）：
[GGGGGGGG][RRRRRRRR][BBBBBBBB]
 G7...G0    R7...R0    B7...B0

示例：
纯红色 = 0x00, 0xFF, 0x00  (G=0, R=255, B=0)
纯绿色 = 0xFF, 0x00, 0x00  (G=255, R=0, B=0)
纯白色 = 0xFF, 0xFF, 0xFF  (全部最大)
暖黄色 = 0x60, 0xFF, 0x00  (G=96, R=255, B=0)
```

#### 时序要求（纳秒级精度）

```
数据 "1":          数据 "0":
  +---------+         +--+
  | 0.8us   |         |0.4us|
  |  (高)   |         |(高) |
  +---------+   vs    +---------+
            | 0.45us  |         | 0.85us
            | (低)    |         | (低)

Reset: 低电平 > 50us
```

| 参数 | 典型值 | 容差 |
|---|---|---|
| T0H | 0.4 us | +/-150ns |
| T0L | 0.85 us | +/-150ns |
| T1H | 0.8 us | +/-150ns |
| T1L | 0.45 us | +/-150ns |
| Reset | >50 us | |

#### 为什么用 ESP32-S3 的 RMT？

WS2812B 的纳秒级时序要求用软件延时很难精确实现。ESP32-S3 内置的 **RMT（远程控制）外设** 是专门为此设计的：

- RMT 可以产生精确到时钟周期的脉冲序列
- 不占用CPU——DMA自动发送
- 最多支持8个通道

---

### 功耗预算 | Power Budgeting

FantasyKB 有80颗 WS2812B，这是整个键盘功耗最大的部分：

```
每颗 WS2812B 最大功耗: ~60mA (全白全亮 R=G=B=255)
80颗最大总电流: 80 x 60mA = 4.8A !!!
80颗最大总功率: 5V x 4.8A = 24W !!!

这远超USB和电池的供电能力！
```

**功耗管理策略：**

| 策略 | 实现 | 效果 |
|---|---|---|
| 限制最大亮度 | 代码中上限设为50% (128/255) | 功耗减半 |
| 分时供电 | 快速轮流点亮不同区域 | 视觉上全亮，实际电流减半 |
| 动态亮度 | 根据供电状态自动调节 | USB全亮/电池减亮 |
| 非全白使用 | 避免R=G=B=255 | 单色最大20mA/颗 |

**FantasyKB推荐配置：最大亮度50%，电池模式下降低到30%。**

---

## 动手实验 | Hands-on Lab (10:45-12:00)

### 任务 8.1: 使用 RMT 驱动 WS2812B

**接线：**
```
ESP32-S3 GPIO48 -> 330R电阻 -> WS2812B DIN
5V -> WS2812B VCC
GND -> WS2812B GND
100uF电容并联在VCC和GND之间
```

**ESP-IDF RMT 驱动代码（ESP-IDF v5.x）：**

```c
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/rmt_tx.h"
#include "led_strip.h"

#define LED_NUM     80    // FantasyKB 约80颗LED
#define LED_GPIO    48    // 数据线GPIO

static led_strip_handle_t led_strip;

void led_init(void)
{
    led_strip_config_t strip_config = {
        .strip_gpio_num = LED_GPIO,
        .max_leds = LED_NUM,
        .led_pixel_format = LED_PIXEL_FORMAT_GRBW,
        .led_model = LED_MODEL_WS2812,
        .flags.invert_out = false,
    };

    led_strip_rmt_config_t rmt_config = {
        .clk_src = RMT_CLK_SRC_DEFAULT,
        .resolution_hz = 10 * 1000 * 1000,  // 10MHz
        .flags.with_dma = true,
    };

    led_strip_new_rmt_device(&strip_config, &rmt_config, &led_strip);
    led_strip_clear(led_strip);
}

// 设置单颗LED颜色（含亮度限制）
void set_pixel(uint32_t index, uint8_t r, uint8_t g, uint8_t b)
{
    // 限制最大亮度到50%
    r = (r * 128) / 255;
    g = (g * 128) / 255;
    b = (b * 128) / 255;
    led_strip_set_pixel(led_strip, index, r, g, b);
}

// 刷新显示
void update_leds(void)
{
    led_strip_refresh(led_strip);
}
```

---

### 任务 8.2: 基础灯效——静态颜色与彩虹

```c
#include <math.h>

// 全部设为同一颜色
void set_all_color(uint8_t r, uint8_t g, uint8_t b)
{
    for (int i = 0; i < LED_NUM; i++) {
        set_pixel(i, r, g, b);
    }
    update_leds();
}

// 彩虹效果
void rainbow_effect(uint8_t offset)
{
    for (int i = 0; i < LED_NUM; i++) {
        uint8_t hue = (i * 256 / LED_NUM + offset) & 0xFF;
        uint8_t r, g, b;

        // HSV to RGB 简化版
        uint8_t region = hue / 43;
        uint8_t remainder = (hue - region * 43) * 6;

        switch (region) {
            case 0: r = 255; g = remainder; b = 0; break;
            case 1: r = 255 - remainder; g = 255; b = 0; break;
            case 2: r = 0; g = 255; b = remainder; break;
            case 3: r = 0; g = 255 - remainder; b = 255; break;
            case 4: r = remainder; g = 0; b = 255; break;
            default: r = 255; g = 0; b = 255 - remainder; break;
        }
        set_pixel(i, r, g, b);
    }
    update_leds();
}

// 呼吸灯效果
void breathing_effect(uint8_t phase, uint8_t r, uint8_t g, uint8_t b)
{
    float brightness = (sinf(phase * 2 * M_PI / 256.0f) + 1.0f) / 2.0f;
    set_all_color(r * brightness, g * brightness, b * brightness);
}
```

---

## 项目实践 | Project Work (13:30-16:30)

### 任务 8.3: 高级灯效——按键响应与波浪

**按键响应灯效：按下按键时对应LED亮起**

```c
// 记录每个按键的LED索引
// FantasyKB: 按键按行排列，每行对应一组LED
int key_to_led_index(int row, int col)
{
    return row * 16 + col;  // 根据实际布局调整
}

// 按键按下时的灯效
void on_key_press_led(int key_index)
{
    set_pixel(key_index, 255, 255, 255);  // 按下的键亮白
    update_leds();
}

void on_key_release_led(int key_index, uint8_t bg_r, uint8_t bg_g, uint8_t bg_b)
{
    set_pixel(key_index, bg_r, bg_g, bg_b);  // 松开恢复背景色
    update_leds();
}
```

**彩虹波浪效果：**

```c
void rainbow_wave(uint8_t offset)
{
    for (int i = 0; i < LED_NUM; i++) {
        uint8_t hue = (i * 3 + offset) & 0xFF;
        uint8_t r, g, b;
        uint8_t region = hue / 43;
        uint8_t remainder = (hue - region * 43) * 6;
        switch (region) {
            case 0: r = 255; g = remainder; b = 0; break;
            case 1: r = 255 - remainder; g = 255; b = 0; break;
            case 2: r = 0; g = 255; b = remainder; break;
            case 3: r = 0; g = 255 - remainder; b = 255; break;
            case 4: r = remainder; g = 0; b = 255; break;
            default: r = 255; g = 0; b = 255 - remainder; break;
        }
        set_pixel(i, r, g, b);
    }
    update_leds();
}
```

---

### 任务 8.4: 灯效模式切换器与功耗自适应

```c
typedef enum {
    EFFECT_STATIC = 0,
    EFFECT_RAINBOW,
    EFFECT_RAINBOW_WAVE,
    EFFECT_BREATHING,
    EFFECT_REACTIVE,
    EFFECT_OFF,
    EFFECT_COUNT
} led_effect_t;

static led_effect_t current_effect = EFFECT_RAINBOW_WAVE;

// 根据供电模式调整亮度
uint8_t get_brightness_limit(void)
{
    if (usb_is_connected()) return 128;       // USB: 50%最大亮度
    else if (battery_level() > 50) return 80;  // 电池充足: 31%
    else return 40;                             // 电池低: 16%
}

void led_effect_task(void *arg)
{
    uint8_t frame = 0;
    while (1) {
        switch (current_effect) {
            case EFFECT_STATIC:
                set_all_color(0, 0, 128);
                vTaskDelay(1000 / portTICK_PERIOD_MS);
                break;
            case EFFECT_RAINBOW:
                rainbow_effect(frame++);
                vTaskDelay(20 / portTICK_PERIOD_MS);
                break;
            case EFFECT_RAINBOW_WAVE:
                rainbow_wave(frame++);
                vTaskDelay(30 / portTICK_PERIOD_MS);
                break;
            case EFFECT_BREATHING:
                breathing_effect(frame++, 128, 0, 255);
                vTaskDelay(15 / portTICK_PERIOD_MS);
                break;
            case EFFECT_REACTIVE:
                set_all_color(5, 5, 10);
                update_leds();
                vTaskDelay(50 / portTICK_PERIOD_MS);
                break;
            case EFFECT_OFF:
                led_strip_clear(led_strip);
                vTaskDelay(1000 / portTICK_PERIOD_MS);
                break;
        }
    }
}
```

---

## 日终总结 | Daily Wrap-up (16:30-17:00)

**今日关键要点：**
1. WS2812B 使用纳秒级精度的单线协议，ESP32-S3 使用 **RMT 外设** 精确驱动
2. 数据顺序是 **GRB**（不是RGB！）——最常见的错误
3. 80颗LED全白全亮需要4.8A——必须限制亮度并使用功耗管理策略
4. 灯效应运行在独立的FreeRTOS任务中，不阻塞按键扫描

**明日预告：**
明天进入FantasyKB最酷的部分——FOC无刷电机旋钮！你将学习电机控制理论、磁编码器原理，并实现力反馈效果。

---

## 今日作业 | Homework

1. **完成灯效演示**：至少实现3种灯效，录制演示视频
2. **编程挑战**：创建一个自定义灯效（如流星雨、呼吸彩虹、打字机效果等）
3. **思考题**：
   - 80颗WS2812B发送完整一帧数据需要多少微秒？（提示：每颗24位，每位1.25us + Reset 50us）
   - 如果LED刷新率和按键扫描使用同一个任务，如何避免LED刷新阻塞按键检测？
   - 电池模式下为什么需要降低LED亮度？如果不降低会怎样？
4. **预习 Day 9**：搜索 "FOC 无刷电机控制 SimpleFOC" 和 "AS5047P 磁编码器"

---

## 常见问题 | FAQ

**Q: LED 颜色不对，全红或全绿？**
A: 最常见的原因是GRB顺序搞反。检查代码中的颜色赋值顺序，确保是Green-Red-Blue。如果用的是RGBW版本，还要注意白色通道。

**Q: 前面几颗LED正常，后面的不亮或闪烁？**
A: (1) 供电不足——后面的LED电压过低 (2) 数据线过长导致信号衰减 (3) 级联数量过多需要在中间增加信号放大。

**Q: RMT 初始化失败？**
A: 检查GPIO是否支持RMT输出，确认RMT通道未被其他外设占用。ESP32-S3的RMT通道有限，确保没有冲突。

---

## 参考资源 | References

- WS2812B 数据手册（搜索 "WS2812B datasheet"）
- ESP-IDF LED Strip 组件：https://github.com/espressif/idf-extra-components/tree/master/led_strip
- ESP-IDF RMT 文档：https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/peripherals/rmt.html
- FastLED 库（Arduino平台，参考灯效算法）：https://fastled.io/
- B 站搜索 "WS2812B ESP32 RMT 驱动"

---

*最后更新 | Last updated: 2026-05-27*
