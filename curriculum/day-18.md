# Day 18: 系统集成固件 | System Integration Firmware

> **今日目标 Today's Goals:**
> - 集成音频管道（ES7210 采集 + ES8311 播放）
> - 集成 LVGL 显示 + SimpleFOC 旋钮控制
> - 协调 FreeRTOS 多任务优先级和资源冲突
> - 实现无线模式切换和 RGB 灯效控制
>
> **产出 Deliverable:** 完整固件集成，所有子系统协同工作

---

## 时间安排 | Schedule

| 时间 Time | 活动类型 Type | 内容 Content |
|---|---|---|
| 09:00–09:15 | 晨会 | 回顾 Day 17 无线模式，答疑 |
| 09:15–10:30 | 讲解 | 音频管道 + LVGL + SimpleFOC 架构 |
| 10:30–10:45 | 休息 | — |
| 10:45–12:00 | 实验 | 音频管道集成 |
| 12:00–13:30 | 午休 | — |
| 13:30–15:00 | 实验 | LVGL 显示 + SimpleFOC 旋钮 |
| 15:00–15:15 | 休息 | — |
| 15:15–16:30 | 实验 | 多任务协调 + 模式切换 + RGB |
| 16:30–17:00 | 总结 | 日终回顾 + 第四阶段总结 |

---

## 上午：音频管道集成 | Morning: Audio Pipeline Integration

### 为什么要学这个? | Why Learn This?

昨天完成了 4 种无线键盘模式，今天把剩余的子系统全部整合进来。音频管道让键盘支持语音交互，LVGL + SimpleFOC 让旋钮有显示和力反馈，RGB 灯效增加视觉效果。真正的工程挑战在于——这些模块同时运行时，如何避免资源冲突和性能问题。

Yesterday completed 4 wireless modes; today we integrate remaining subsystems. The real engineering challenge is running all modules simultaneously without resource conflicts.

---

### 任务 18.1: 音频管道架构 (40 分钟)

**音频数据流 Audio Data Flow:**

```
录音路径 Capture Path:
  麦克风 x2 ──(模拟)──→ ES7210 ──(I2S)──→ ESP32-S3 ──(WiFi/BLE)──→ 语音服务

播放路径 Playback Path:
  语音服务 ──(WiFi/BLE)──→ ESP32-S3 ──(I2S)──→ ES8311 ──(模拟)──→ NS4150B ──→ 扬声器

ESP-IDF 音频管道组件:
  ┌──────────┐    ┌──────────┐    ┌──────────┐
  │ I2S Read │──→ │ Process  │──→ │ I2S Write│
  │ (ES7210) │    │ (Filter) │    │ (ES8311) │
  └──────────┘    └──────────┘    └──────────┘
       ↑                               ↓
  DMA Buffer                      DMA Buffer
  (采集缓冲)                       (播放缓冲)
```

**I2S 配置代码 I2S Configuration:**

```c
// audio_pipeline.c

#include "driver/i2s_std.h"

static i2s_chan_handle_t rx_handle;  // ES7210 录音
static i2s_chan_handle_t tx_handle;  // ES8311 播放

#define SAMPLE_RATE  16000   // 16kHz 语音采样率
#define BIT_DEPTH    16      // 16-bit
#define CHANNELS     2       // 立体声

esp_err_t audio_pipeline_init(void) {
    // I2S 通道配置
    i2s_chan_config_t chan_cfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);

    // 创建 RX 通道 (ES7210 -> ESP32)
    i2s_new_channel(&chan_cfg, NULL, &rx_handle);

    // 创建 TX 通道 (ESP32 -> ES8311)
    i2s_new_channel(&chan_cfg, &tx_handle, NULL);

    // 标准 I2S 模式配置
    i2s_std_config_t std_cfg = {
        .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(SAMPLE_RATE),
        .slot_cfg = I2S_STD_PHILIP_SLOT_DEFAULT_CONFIG(BIT_DEPTH, CHANNELS),
        .gpio_cfg = {
            .mclk = I2S_MCLK,  // 可选
            .bclk = GPIO_NUM_41,
            .ws   = GPIO_NUM_42,
            .dout = GPIO_NUM_39,  // ESP32 -> ES8311
            .din  = GPIO_NUM_40,  // ES7210 -> ESP32
        },
    };

    i2s_channel_init_std_mode(rx_handle, &std_cfg);
    i2s_channel_init_std_mode(tx_handle, &std_cfg);

    i2s_channel_enable(rx_handle);
    i2s_channel_enable(tx_handle);

    return ESP_OK;
}
```

---

### 任务 18.2: ES7210/ES8311 I2C 配置 (35 分钟)

```c
// codec_config.c — 编解码器 I2C 配置

#include "driver/i2c.h"

#define I2C_MASTER_NUM    I2C_NUM_0
#define ES7210_ADDR       0x40
#define ES8311_ADDR       0x18

// ES7210 初始化 (ADC, 4通道, I2S 输出)
esp_err_t es7210_init(void) {
    // 设置时钟管理 Clock Manager
    i2c_write_reg(ES7210_ADDR, 0x00, 0xFF);  // Reset
    vTaskDelay(pdMS_TO_TICKS(10));
    i2c_write_reg(ES7210_ADDR, 0x00, 0x32);  // 时钟使能

    // 设置 I2S 输出格式 (Philips, 16bit)
    i2c_write_reg(ES7210_ADDR, 0x07, 0x00);  // I2S format

    // 使能所有 4 通道
    i2c_write_reg(ES7210_ADDR, 0x01, 0x3F);  // Power up all

    // 设置 PGA 增益 (0dB, 适合近场麦克风)
    i2c_write_reg(ES7210_ADDR, 0x43, 0x1C);
    i2c_write_reg(ES7210_ADDR, 0x44, 0x1C);

    return ESP_OK;
}

// ES8311 初始化 (DAC, I2S 输入, 耳机输出)
esp_err_t es8311_init(void) {
    i2c_write_reg(ES8311_ADDR, 0x00, 0x80);  // Reset
    vTaskDelay(pdMS_TO_TICKS(10));

    // 设置 I2S 格式
    i2c_write_reg(ES8311_ADDR, 0x09, 0x00);  // I2S Philips

    // 设置 DAC 输出音量
    i2c_write_reg(ES8311_ADDR, 0x0D, 0x00);  // 0dB

    // 使能 DAC 和输出
    i2c_write_reg(ES8311_ADDR, 0x0A, 0x00);  // DAC power up

    return ESP_OK;
}
```

---

### 任务 18.3: 集成音频到主固件 (60 分钟)

**音频任务 Audio Task:**

```c
// audio_task.c

#define AUDIO_BUF_SIZE  (SAMPLE_RATE * BIT_DEPTH / 8 * CHANNELS / 100)  // 10ms

void audio_task(void *arg) {
    uint8_t *rx_buf = malloc(AUDIO_BUF_SIZE);
    uint8_t *tx_buf = malloc(AUDIO_BUF_SIZE);

    audio_pipeline_init();
    es7210_init();
    es8311_init();

    while (1) {
        // 从 ES7210 读取音频数据
        size_t bytes_read = 0;
        i2s_channel_read(rx_handle, rx_buf, AUDIO_BUF_SIZE,
                         &bytes_read, portMAX_DELAY);

        // TODO: 这里可以加入音频处理
        // - 降噪 Noise reduction
        // - 回声消除 Echo cancellation
        // - 编码 Encode (opus/PCM)

        // 如果有播放数据，写入 ES8311
        size_t bytes_written = 0;
        i2s_channel_write(tx_handle, tx_buf, AUDIO_BUF_SIZE,
                          &bytes_written, 0);

        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
```

---

## 下午：LVGL + SimpleFOC + 多任务协调 | Afternoon: LVGL + SimpleFOC + Coordination

### 任务 18.4: LVGL 显示 + SimpleFOC 旋钮 (60 分钟)

**旋钮控制器架构 Knob Controller Architecture:**

```
旋钮系统 Knob System:

  ┌─────────────────────────────────────┐
  │  GC9A01 (1.28" 圆形LCD)             │
  │  ┌───────────┐                      │
  │  │  LVGL UI  │ ← 显示当前模式/音量等  │
  │  └───────────┘                      │
  │         ↕ SPI                        │
  │  ESP32-S3 (旋钮独立MCU)              │
  │         ↕ SPI                        │
  │  AS5047P (磁编码器) ──→ 位置反馈     │
  │         ↕ PWM                        │
  │  TMC6300 (电机驱动) ──→ 2204 电机    │
  │         ↕ I2C/SPI                    │
  │  HX711 (压力传感器) ──→ 按压力度     │
  └─────────────────────────────────────┘
```

**SimpleFOC 初始化 (PlatformIO):**

```cpp
// knob_controller.cpp — 简化版旋钮控制

#include <SimpleFOC.h>

BLDCMotor motor = BLDCMotor(7);  // 7极对
BLDCDriver3PWM driver = BLDCDriver3PWM(5, 6, 7);
MagneticSensorSPI sensor = MagneticSensorSPI(AS5047P, 6);

void setup() {
    sensor.init();
    motor.linkSensor(&sensor);

    driver.voltage_power_supply = 5.0;
    driver.init();
    motor.linkDriver(&driver);

    motor.controller = MotionControlType::angle;
    motor.PID_angle.P = 10.0;
    motor.PID_angle.I = 0.0;
    motor.PID_velocity.P = 0.2;

    motor.init();
    motor.initFOC();
}

void loop() {
    motor.loopFOC();
    motor.move(target_angle);
}
```

---

### 任务 18.5: FreeRTOS 多任务协调 (60 分钟)

**完整任务结构 Complete Task Structure:**

```c
// main.c — 系统初始化和任务创建

void app_main(void) {
    printf("4-Mode Keyboard Firmware v1.0\n");

    // 1. 初始化硬件
    spi_74hc165_init();         // SPI 总线
    i2c_master_init();          // I2C 总线
    ws2812b_init();             // RGB LED

    // 2. 创建事件队列
    key_event_queue  = xQueueCreate(32, sizeof(key_event_t));
    mode_event_queue = xQueueCreate(4,  sizeof(wireless_mode_t));

    // 3. 创建任务 (优先级从高到低)
    xTaskCreate(key_scanner_task,    "key_scan",  4096, NULL, 10, NULL);
    xTaskCreate(usb_hid_task,        "usb_hid",   4096, NULL,  8, NULL);
    xTaskCreate(wireless_mode_task,  "wireless",  8192, NULL,  6, NULL);
    xTaskCreate(rgb_controller_task, "rgb_ctrl",  4096, NULL,  4, NULL);
    xTaskCreate(audio_task,          "audio",     8192, NULL,  5, NULL);
    xTaskCreate(knob_ctrl_task,      "knob",      4096, NULL,  5, NULL);
    xTaskCreate(power_monitor_task,  "power",     2048, NULL,  3, NULL);

    printf("All tasks created. System running.\n");
}
```

**优先级设计原理 Priority Design:**

| 任务 Task | 优先级 Priority | 理由 Reason |
|---|---|---|
| Key Scanner | 10 (最高) | 按键延迟必须 < 1ms |
| USB HID | 8 | 按键报告必须及时发送 |
| Audio | 5 | 音频缓冲不能中断（否则有杂音） |
| Knob Control | 5 | FOC 循环需要稳定频率 |
| Wireless Mode | 6 | 模式切换不能阻塞按键 |
| RGB Controller | 4 | 灯效延迟人眼不可感知 |
| Power Monitor | 3 (最低) | 电池电压检测不紧急 |

---

### 任务 18.6: 无线模式切换与 RGB 控制 (剩余时间)

**模式切换触发 Mode Switch Trigger:**

```c
// 绑定物理按键或组合键切换模式
// 例如: Fn + 1 = USB, Fn + 2 = BLE, Fn + 3 = WiFi, Fn + 4 = ESP-NOW

void process_mode_switch(key_event_t *evt) {
    if (evt->pressed && is_fn_active()) {
        switch (evt->key_index) {
            case 76:  // Fn+1 -> USB
                wireless_mode_switch(MODE_USB);
                rgb_set_mode(RGB_MODE_USB);
                break;
            case 77:  // Fn+2 -> BLE
                wireless_mode_switch(MODE_BLE);
                rgb_set_mode(RGB_MODE_BLE);
                break;
            case 78:  // Fn+3 -> WiFi
                wireless_mode_switch(MODE_WIFI);
                rgb_set_mode(RGB_MODE_WIFI);
                break;
            case 79:  // Fn+4 -> ESP-NOW
                wireless_mode_switch(MODE_ESP_NOW);
                rgb_set_mode(RGB_MODE_ESPNOW);
                break;
        }
    }
}
```

**RGB 灯效 RGB Effects:**

```c
// rgb_controller.c

typedef enum {
    RGB_MODE_STATIC = 0,   // 单色常亮
    RGB_MODE_BREATHING,    // 呼吸灯
    RGB_MODE_RAINBOW,      // 彩虹
    RGB_MODE_REACTIVE,     // 按键触发
    RGB_MODE_USB,          // USB 模式指示 (蓝色)
    RGB_MODE_BLE,          // BLE 模式指示 (绿色)
    RGB_MODE_WIFI,         // WiFi 模式指示 (橙色)
    RGB_MODE_ESPNOW,       // ESP-NOW 模式指示 (紫色)
} rgb_mode_t;

void rgb_controller_task(void *arg) {
    ws2812b_init();
    rgb_mode_t mode = RGB_MODE_USB;

    while (1) {
        // 检查模式切换
        xQueueReceive(mode_event_queue, &mode, 0);

        switch (mode) {
            case RGB_MODE_USB:
                rgb_fill_all(0, 0, 255);      // 蓝色 Blue
                break;
            case RGB_MODE_BLE:
                rgb_fill_all(0, 255, 0);      // 绿色 Green
                break;
            case RGB_MODE_WIFI:
                rgb_fill_all(255, 165, 0);    // 橙色 Orange
                break;
            case RGB_MODE_ESPNOW:
                rgb_fill_all(128, 0, 255);    // 紫色 Purple
                break;
            case RGB_MODE_RAINBOW:
                rgb_rainbow_cycle(50);        // 彩虹效果
                break;
            default:
                rgb_fill_all(0, 0, 0);        // 关灯 Off
        }

        rgb_update();
        vTaskDelay(pdMS_TO_TICKS(20));  // 50 FPS
    }
}
```

---

## 日终总结 | Daily Wrap-up (16:30-17:00)

**第四阶段总结 Phase 4 Summary:**

在 Day 16-18 这三天里，你完成了：
1. 搭建了 ESP-IDF 项目框架，理解了 FreeRTOS 任务模型
2. 实现了 74HC165 SPI 键盘扫描（80 键 + 消抖）
3. 实现了 4 种无线模式（USB / BLE / WiFi / ESP-NOW）
4. 集成了音频管道（ES7210 录音 + ES8311 播放）
5. 集成了 LVGL 显示和 SimpleFOC 旋钮控制
6. 完成了多任务优先级协调和 RGB 灯效控制

---

## 今日作业 | Homework

1. **完成固件集成测试**：所有子系统在同一个固件中运行不崩溃
2. **截图提交**：串口日志显示所有任务正常启动 + 按键/音频/RGB 测试
3. **完成第四周进度汇报**：详见 assignments/week-4-checkin.md
4. **回答思考题**：
   - 如果音频任务和键盘扫描任务同时访问 I2C 总线，会怎样？如何解决？
   - 为什么 FOC 电机控制任务的循环频率不能低于 1kHz？
   - 如何检测电池电量低并自动关机？

---

## 明日预告 | Tomorrow's Preview

明天是组装日！你将焊接所有 PCB 上的元件（SMD 贴片 + QFN 芯片），安装机械轴体和键帽，组装外壳。这是从图纸到实物的关键时刻。

Tomorrow is assembly day! You'll solder all components (SMD + QFN), install switches and keycaps, and assemble the case. The moment when drawings become reality.

---

## 参考资源 | References

- ESP-IDF I2S 驱动文档：https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/peripherals/i2s.html
- LVGL 官方文档：https://docs.lvgl.io/
- SimpleFOC 官方文档：https://docs.simplefoc.com/
- ES7210 数据手册：搜索 "ES7210 datasheet"
- ES8311 数据手册：搜索 "ES8311 datasheet"
- B 站搜索 "ESP32 I2S 音频 录音 播放"
- B 站搜索 "SimpleFOC 教程 无刷电机"

---

*最后更新 | Last updated: 2026-05-27*
