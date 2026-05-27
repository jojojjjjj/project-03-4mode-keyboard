# Day 04: I2C协议与音频子系统 | I2C Protocol & Audio Subsystem

## 今日目标 | Today's Goals
- 掌握 I2C 协议的工作原理（主从架构、地址寻址、ACK/NACK）
- 学会使用 I2C 总线扫描发现设备
- 理解 I2S 数字音频接口的基本概念
- 驱动 ES8311 DAC 播放音频，驱动 ES7210 ADC 录音

## 知识讲解 | Knowledge Lecture (09:15-10:30)

### I2C 协议原理 | I2C Protocol

I2C（Inter-Integrated Circuit）只需要 2 根线就能让多个芯片互相通信：

```
        VCC
         |
    +---[4.7k]---+---[4.7k]---+
    |             |             |
  SCL线         SDA线          |
    |             |             |
  MASTER      SLAVE1        SLAVE2
  (ESP32-S3)  (ES8311)      (ES7210)
  地址: --     地址: 0x18    地址: 0x40
```

**FantasyKB 中的 I2C 设备：**

| 设备 | I2C 地址 | 功能 |
|---|---|---|
| ES8311 | 0x18 | DAC（数字→模拟），音频播放 |
| ES7210 | 0x40 | ADC（模拟→数字），麦克风录音 |

#### I2C 通信时序

```
起始条件 START: SCL为高时，SDA从高变低
   SCL: ‾‾‾‾‾‾‾
   SDA: ‾‾\____    (下降沿 = START)

数据传输: 每个SCL高电平期间SDA稳定
   SCL: _|‾|_|‾|_|‾|_
   SDA: _D7__D6__D5__

应答 ACK: 第9个时钟周期，从设备拉低SDA
   SCL: _|‾|
   SDA: _\_/    (低 = ACK, 高 = NACK)

停止条件 STOP: SCL为高时，SDA从低变高
   SCL: ‾‾‾‾‾‾‾
   SDA: ___/‾‾‾   (上升沿 = STOP)
```

---

### 音频子系统架构 | Audio Subsystem Architecture

FantasyKB 的音频系统参考 ESP-BOX 硬件设计，包含以下部分：

```
                     I2S 数字音频总线
                    (BCLK / WS / DATA)
                         |
     +-------------------+-------------------+
     |                                       |
  ES7210 (ADC)                          ES8311 (DAC)
  模拟→数字转换                           数字→模拟转换
     |                                       |
  双麦克风输入                            功放 NS4150B
  (I2S RX)                                  |
                                        扬声器输出
```

**I2S 总线（Inter-IC Sound）**

I2S 是专为数字音频设计的接口，与I2C完全不同：

| 信号 | 功能 | 方向 |
|---|---|---|
| BCLK | 位时钟 | Master -> Slave |
| WS | 字选择（左右声道） | Master -> Slave |
| DOUT | 数据输出（ADC->MCU） | Slave -> Master |
| DIN | 数据输入（MCU->DAC） | Master -> Slave |

**为什么用 I2C 和 I2S 两种协议？**
- **I2C**：低速控制通道，用于配置编解码器参数（音量、采样率等）
- **I2S**：高速数据通道，用于实时传输音频数据流

---

## 动手实验 | Hands-on Lab (10:45-12:00)

### 任务 4.1: I2C 总线扫描

**代码——扫描总线上所有设备：**

```c
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/i2c.h"

#define I2C_MASTER_NUM      I2C_NUM_0
#define I2C_MASTER_SDA_IO   8    // GPIO8
#define I2C_MASTER_SCL_IO   9    // GPIO9
#define I2C_MASTER_FREQ_HZ  100000  // 100kHz

void i2c_master_init(void)
{
    i2c_config_t conf = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = I2C_MASTER_SDA_IO,
        .scl_io_num = I2C_MASTER_SCL_IO,
        .sda_pullup_en = GPIO_PULLUP_ENABLE,
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master.clk_speed = I2C_MASTER_FREQ_HZ,
    };
    i2c_param_config(I2C_MASTER_NUM, &conf);
    i2c_driver_install(I2C_MASTER_NUM, conf.mode, 0, 0, 0);
}

void i2c_scan(void)
{
    printf("I2C Bus Scan:\n");
    printf("     0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F\n");

    for (int row = 0; row < 8; row++) {
        printf("%02X: ", row * 16);
        for (int col = 0; col < 16; col++) {
            int addr = row * 16 + col;
            if (addr < 0x03 || addr > 0x77) {
                printf("   ");
                continue;
            }
            i2c_cmd_handle_t cmd = i2c_cmd_link_create();
            i2c_master_start(cmd);
            i2c_master_write_byte(cmd, (addr << 1) | I2C_MASTER_WRITE, true);
            i2c_master_stop(cmd);
            esp_err_t ret = i2c_master_cmd_begin(I2C_MASTER_NUM, cmd,
                                                   50 / portTICK_PERIOD_MS);
            i2c_cmd_link_delete(cmd);
            printf(ret == ESP_OK ? "%02X " : "-- ");
        }
        printf("\n");
    }
}

void app_main(void)
{
    i2c_master_init();
    i2c_scan();
}
```

**预期结果：**
如果 ES8311 模块已连接，应看到地址 `18` 被发现。如果 ES7210 也连接了，地址 `40` 也应该出现。

---

### 任务 4.2: ES8311 DAC 基础——播放正弦波

**ES8311 初始化代码：**

```c
#define ES8311_ADDR 0x18

esp_err_t es8311_write_reg(uint8_t reg, uint8_t val)
{
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (ES8311_ADDR << 1) | I2C_MASTER_WRITE, true);
    i2c_master_write_byte(cmd, reg, true);
    i2c_master_write_byte(cmd, val, true);
    i2c_master_stop(cmd);
    esp_err_t ret = i2c_master_cmd_begin(I2C_MASTER_NUM, cmd, 100 / portTICK_PERIOD_MS);
    i2c_cmd_link_delete(cmd);
    return ret;
}
```

**生成正弦波并通过 I2S 播放：**

```c
#include <math.h>

#define SAMPLE_RATE 16000
#define BUFFER_SIZE 1024

void play_tone_task(void *arg)
{
    // 分配I2S缓冲区
    int16_t *buffer = malloc(BUFFER_SIZE * sizeof(int16_t));

    // 生成440Hz正弦波（A4音符）
    double phase = 0;
    double phase_increment = 2.0 * M_PI * 440.0 / SAMPLE_RATE;

    while (1) {
        for (int i = 0; i < BUFFER_SIZE; i++) {
            buffer[i] = (int16_t)(sin(phase) * 16000);  // 音量约50%
            phase += phase_increment;
            if (phase > 2.0 * M_PI) phase -= 2.0 * M_PI;
        }
        // 写入I2S（此处省略I2S初始化代码，详见ESP-IDF I2S文档）
        size_t bytes_written;
        i2s_write(I2S_NUM_0, buffer, BUFFER_SIZE * 2, &bytes_written, portMAX_DELAY);
    }
    free(buffer);
}
```

> **提示**：如果使用现成的 ES8311 模块，通常已有Arduino/ESP-IDF示例代码可以直接使用。本项目使用面包板验证原理，后续PCB设计阶段会实现完整的音频电路。

---

## 项目实践 | Project Work (13:30-16:30)

### 任务 4.3: ES7210 ADC——麦克风输入

ES7210 是一颗4通道ADC，FantasyKB使用其中2个通道连接双麦克风阵列。

**ES7210 配置要点：**
1. 通过 I2C 写入寄存器配置采样率（16kHz）
2. 配置输入增益（MIC增益）
3. 通过 I2S 接收音频数据

```c
#define ES7210_ADDR 0x40

esp_err_t es7210_write_reg(uint8_t reg, uint8_t val)
{
    // 与ES8311类似，写入I2C寄存器
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (ES7210_ADDR << 1) | I2C_MASTER_WRITE, true);
    i2c_master_write_byte(cmd, reg, true);
    i2c_master_write_byte(cmd, val, true);
    i2c_master_stop(cmd);
    esp_err_t ret = i2c_master_cmd_begin(I2C_MASTER_NUM, cmd, 100 / portTICK_PERIOD_MS);
    i2c_cmd_link_delete(cmd);
    return ret;
}

// 读取麦克风数据
void record_task(void *arg)
{
    int16_t *mic_buffer = malloc(BUFFER_SIZE * 2 * sizeof(int16_t)); // 双声道

    while (1) {
        size_t bytes_read;
        i2s_read(I2S_NUM_1, mic_buffer, BUFFER_SIZE * 4, &bytes_read, portMAX_DELAY);

        // 计算音量（RMS）
        double sum = 0;
        int samples = bytes_read / 2;
        for (int i = 0; i < samples; i++) {
            sum += (double)mic_buffer[i] * mic_buffer[i];
        }
        double rms = sqrt(sum / samples);
        printf("Mic Level: %.0f\n", rms);
    }
}
```

---

### 任务 4.4: 录音与回放

**挑战任务：将麦克风录音通过扬声器实时播放出来（回声/对讲机效果）：**

```c
void loopback_task(void *arg)
{
    int16_t *buffer = malloc(BUFFER_SIZE * 2);
    printf("Audio loopback started!\n");
    printf("Speak into the mic, hear from the speaker.\n");

    while (1) {
        size_t bytes_read, bytes_written;
        // 从ADC（麦克风）读取
        i2s_read(I2S_NUM_1, buffer, BUFFER_SIZE * 2, &bytes_read, portMAX_DELAY);
        // 写入DAC（扬声器）播放
        i2s_write(I2S_NUM_0, buffer, bytes_read, &bytes_written, portMAX_DELAY);
    }
}
```

**实验记录表：**

| 实验项目 | 结果 | 备注 |
|---|---|---|
| I2C总线扫描 | 发现设备地址:___ | |
| 正弦波播放 | 能/不能听到声音 | 频率:___Hz |
| 麦克风音量检测 | RMS值范围:___ | 安静/说话时 |
| 回声测试 | 能/不能听到自己说话 | 延迟感明显吗？ |

---

## 日终总结 | Daily Wrap-up (16:30-17:00)

**今日关键要点：**
1. **I2C** 是低速控制通道（配置芯片参数），**I2S** 是高速数据通道（传输音频流）
2. ES8311 是 DAC（播放），ES7210 是 ADC（录音），两者通过 I2C 配置、通过 I2S 传输数据
3. FantasyKB 的音频系统参考 ESP-BOX 设计，支持语音交互
4. 总线扫描是调试I2C问题的第一步——先确认设备在线

**明日预告：**
明天学习 USB 子系统和电源管理——USB Hub（SL2.1A）、USB-TTL桥接（CH342F）、锂电池充电（TP4056）、DC-DC升压（HX3608）和LDO稳压（ME6217）。

---

## 今日作业 | Homework

1. **完成实验报告**：I2C扫描结果截图 + 音频播放/录音测试记录
2. **扩展任务**：尝试播放不同频率的正弦波（262Hz=C4, 440Hz=A4, 880Hz=A5），描述音高差异
3. **思考题**：
   - I2C 和 I2S 的区别是什么？能否用 I2C 传输音频数据？为什么？
   - 如果 I2C 总线扫描发现不了 ES8311，可能的原因有哪些？
   - FantasyKB 为什么使用双麦克风而不是单麦克风？（提示：搜索"麦克风阵列降噪"）
4. **预习 Day 5**：搜索 "USB HID 协议 原理" 和 "TP4056 锂电池充电"

---

## 常见问题 | FAQ

**Q: I2C 扫描发现不了任何设备怎么办？**
A: 按以下顺序排查：(1) 检查SDA/SCL接线是否正确 (2) 确认上拉电阻（模块通常已内置）(3) 尝试降低频率到10kHz (4) 用万用表测量SDA/SCL线的静态电压（应为3.3V高电平）

**Q: 扬声器没有声音输出？**
A: (1) 确认ES8311已正确初始化 (2) 检查NS4150B功放是否使能 (3) 确认I2S配置的采样率与ES8311一致 (4) 检查扬声器连接和音量设置

**Q: 录音有大量噪音？**
A: 麦克风对电源噪声非常敏感。(1) 确保供电稳定 (2) 麦克风远离ESP32天线 (3) 添加去耦电容 (4) 后续PCB设计时会做专门的音频地隔离

---

## 参考资源 | References

- ES8311 数据手册（搜索 "ES8311 datasheet"）
- ES7210 数据手册（搜索 "ES7210 datasheet"）
- ESP-BOX 音频设计参考：https://github.com/espressif/esp-box
- ESP-IDF I2S 驱动文档：https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/peripherals/i2s.html
- B 站搜索 "I2C 协议 详解 教程"
- B 站搜索 "I2S 数字音频接口 教程"

---

*最后更新 | Last updated: 2026-05-27*
