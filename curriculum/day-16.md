# Day 16: ESP-IDF固件架构 | ESP-IDF Firmware Architecture

> **今日目标 Today's Goals:**
> - 理解 ESP-IDF 项目结构和构建系统
> - 掌握 FreeRTOS 任务模型和任务间通信
> - 创建键盘固件项目框架
> - 实现键盘扫描任务（74HC165 SPI 读取 + 消抖算法）
>
> **产出 Deliverable:** 工作的键盘扫描器（串口打印按键事件）

---

## 时间安排 | Schedule

| 时间 Time | 活动类型 Type | 内容 Content |
|---|---|---|
| 09:00–09:15 | 晨会 | 第四阶段介绍，固件开发目标 |
| 09:15–10:30 | 讲解 | ESP-IDF 项目结构 + FreeRTOS 基础 |
| 10:30–10:45 | 休息 | — |
| 10:45–12:00 | 实验 | 创建项目 + 配置 SPI 外设 |
| 12:00–13:30 | 午休 | — |
| 13:30–15:00 | 实验 | 实现 74HC165 扫描任务 |
| 15:00–15:15 | 休息 | — |
| 15:15–16:30 | 实验 | 消抖算法 + 按键事件队列 |
| 16:30–17:00 | 总结 | 日终回顾 + 明日预告 |

---

## 上午：ESP-IDF 与 FreeRTOS | Morning: ESP-IDF & FreeRTOS

### 为什么要学这个? | Why Learn This?

前面 5 天我们完成了硬件设计（原理图 + PCB），接下来 3 天我们转向固件开发。ESP-IDF 是乐鑫官方的 ESP32 开发框架，基于 FreeRTOS 实时操作系统。与 Day 8-9 的 QMK 固件不同，ESP-IDF 使用 C 语言直接操作硬件，更适合复杂的多任务系统（同时处理键盘扫描、无线通信、音频、LED）。

The past 5 days completed hardware design. The next 3 days cover firmware development. ESP-IDF is Espressif's official framework, built on FreeRTOS. Unlike QMK, ESP-IDF uses C to directly control hardware, better suited for complex multi-task systems (key scanning, wireless, audio, LED simultaneously).

---

### 任务 16.1: ESP-IDF 项目结构 (40 分钟)

**ESP-IDF 项目目录结构 Project Directory:**

```
4mode-keyboard/
├── CMakeLists.txt          # 顶层构建配置 Top-level build config
├── main/
│   ├── CMakeLists.txt      # 主组件构建 Main component build
│   ├── main.c              # 程序入口 Program entry point
│   ├── key_scanner.c       # 键盘扫描模块 Key scanner module
│   ├── key_scanner.h       # 键盘扫描头文件 Key scanner header
│   ├── debounce.c          # 消抖算法 Debounce algorithm
│   ├── debounce.h
│   ├── usb_hid.c           # USB HID 模块
│   ├── ble_hid.c           # BLE HID 模块
│   ├── wifi_kb.c           # WiFi 键盘模块
│   ├── esp_now_rx.c        # ESP-NOW 接收模块
│   ├── audio_pipeline.c    # 音频管道
│   ├── rgb_controller.c    # RGB LED 控制
│   └── knob_ctrl.c         # 旋钮控制
├── components/
│   ├── matrix/             # 矩阵扫描组件 Matrix component
│   ├── wireless/           # 无线通信组件 Wireless component
│   └── drivers/            # 硬件驱动 Hardware drivers
├── sdkconfig               # ESP-IDF 配置 ESP-IDF menuconfig output
└── partitions.csv          # 分区表 Partition table
```

**创建项目 Creating the Project:**

```bash
# 方法1: 使用 ESP-IDF 模板
. $HOME/esp/v5.x/esp-idf/export.sh
idf.py create-project 4mode-keyboard
cd 4mode-keyboard

# 方法2: 从模板仓库克隆
git clone https://github.com/espressif/esp-idf-template.git 4mode-keyboard
cd 4mode-keyboard

# 设置目标芯片
idf.py set-target esp32s3

# 配置项目（可选）
idf.py menuconfig

# 编译
idf.py build

# 烧录
idf.py -p COMx flash monitor
```

---

### 任务 16.2: FreeRTOS 任务模型 (35 分钟)

**FreeRTOS 核心概念 FreeRTOS Core Concepts:**

```
FreeRTOS 任务状态机 Task State Machine:

              ┌──────────────┐
              │   Running    │ ← 同一时刻只有一个任务在运行
              │  (正在执行)   │
              └──┬───────┬───┘
         被抢占  │       │  阻塞 (等待信号量/队列/延时)
        (更高优) │       │
              ┌─▼───┐  ┌▼──────────┐
              │Ready │  │ Blocked   │
              │(就绪) │  │ (阻塞等待) │
              └──┬───┘  └─────┬─────┘
                 │           │ (等待条件满足)
                 │     ┌─────▼─────┐
                 └────→│   Ready   │
                       │ (条件满足  │
                       │  变为就绪) │
                       └───────────┘

本项目的任务规划:
  Task 1: Key Scanner (优先级: 高)  —— 1ms 周期扫描
  Task 2: USB HID Report (优先级: 高) —— 发送按键报告
  Task 3: RGB Controller (优先级: 中)  —— 灯效更新
  Task 4: Audio Pipeline (优先级: 中)  —— 音频录制/播放
  Task 5: Wireless Manager (优先级: 低) —— 无线模式切换
  Task 6: Knob Controller (优先级: 中)  —— 旋钮力反馈
```

**任务间通信 IPC:**

```
FreeRTOS 提供多种任务间通信方式:

1. 队列 Queue (最常用):
   Key Scanner ──→ [Queue: Key Events] ──→ USB HID Task
                   容量: 32 个事件
                   数据: struct key_event_t

2. 信号量 Semaphore:
   适合"事件通知"场景 (一键一信号)

3. 互斥锁 Mutex:
   保护共享资源 (如 I2C 总线)

4. 事件组 Event Group:
   适合"多条件等待"场景 (如等待所有模块初始化完成)
```

---

### 任务 16.3: 配置 ESP32-S3 SPI 外设 (75 分钟)

**SPI 配置代码 SPI Configuration:**

```c
// spi_config.h — SPI 引脚定义
// SPI Pin Definitions for 74HC165 chain

#define SPI_CLK_PIN    GPIO_NUM_36
#define SPI_MISO_PIN   GPIO_NUM_37
#define SPI_PL_PIN     GPIO_NUM_38
#define SPI_DMA_CH     SPI_DMA_CH_AUTO

// 74HC165 数量 (10 级菊花链 = 80 键)
#define HC165_COUNT    10
#define KEY_COUNT      (HC165_COUNT * 8)  // 80 keys

// spi_74hc165.c — SPI 初始化和读取
#include "driver/spi_master.h"
#include "spi_config.h"

static spi_device_handle_t spi_dev;

esp_err_t spi_74hc165_init(void) {
    spi_bus_config_t buscfg = {
        .sclk_io_num   = SPI_CLK_PIN,
        .mosi_io_num   = -1,          // 不需要 MOSI（只读）
        .miso_io_num   = SPI_MISO_PIN,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        .max_transfer_sz = HC165_COUNT,
    };

    spi_device_interface_config_t devcfg = {
        .clock_speed_hz = 1 * 1000 * 1000,  // 1 MHz
        .mode           = 3,                  // CPOL=1, CPHA=1
        .spics_io_num   = -1,                 // 不用硬件 CS
        .queue_size     = 1,
    };

    ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST, &buscfg, SPI_DMA_CH));
    ESP_ERROR_CHECK(spi_bus_add_device(SPI2_HOST, &devcfg, &spi_dev));
    return ESP_OK;
}
```

---

## 下午：键盘扫描与消抖 | Afternoon: Key Scanning & Debounce

### 任务 16.4: 74HC165 扫描任务实现 (90 分钟)

**扫描流程 Scan Flow:**

```c
// key_scanner.c — 键盘扫描核心任务

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "driver/gpio.h"
#include "driver/spi_master.h"

// 按键事件结构体 Key event structure
typedef struct {
    uint8_t key_index;    // 按键编号 0-79
    bool    pressed;      // true=按下, false=松开
    int64_t timestamp;    // 时间戳 (us)
} key_event_t;

#define SCAN_PERIOD_MS  1     // 扫描周期 1ms
#define DEBOUNCE_COUNT  5     // 消抖计数 5次 = 5ms

static uint8_t prev_state[KEY_COUNT];         // 上一次稳定状态
static uint8_t debounce_counter[KEY_COUNT];   // 消抖计数器
static QueueHandle_t key_event_queue;

// 并行加载脉冲 (PL)
static void pulse_pl(void) {
    gpio_set_level(SPI_PL_PIN, 0);  // PL=0: 锁存并行输入
    esp_rom_delay_us(1);            // 保持 1us
    gpio_set_level(SPI_PL_PIN, 1);  // PL=1: 切换到移位模式
}

// 读取所有 74HC165 状态
static void read_all_keys(uint8_t *buf) {
    pulse_pl();  // 先锁存

    spi_transaction_t trans = {
        .rx_buffer = buf,
        .length    = HC165_COUNT * 8,  // 80 bits
    };
    spi_device_polling_transmit(spi_dev, &trans);
}

// 键盘扫描任务
void key_scanner_task(void *arg) {
    uint8_t raw_buf[HC165_COUNT];

    while (1) {
        read_all_keys(raw_buf);

        // 逐位解析，消抖判断
        for (int i = 0; i < KEY_COUNT; i++) {
            int byte_idx = i / 8;
            int bit_idx  = i % 8;
            bool current = (raw_buf[byte_idx] >> bit_idx) & 0x01;

            if (current != prev_state[i]) {
                debounce_counter[i]++;
                if (debounce_counter[i] >= DEBOUNCE_COUNT) {
                    prev_state[i] = current;
                    debounce_counter[i] = 0;

                    // 发送按键事件
                    key_event_t evt = {
                        .key_index = i,
                        .pressed   = current,
                        .timestamp = esp_timer_get_time(),
                    };
                    xQueueSend(key_event_queue, &evt, 0);
                }
            } else {
                debounce_counter[i] = 0;
            }
        }

        vTaskDelay(pdMS_TO_TICKS(SCAN_PERIOD_MS));
    }
}

// 初始化键盘扫描器
void key_scanner_init(void) {
    // 配置 PL 引脚为输出
    gpio_config_t pl_conf = {
        .pin_bit_mask = (1ULL << SPI_PL_PIN),
        .mode         = GPIO_MODE_OUTPUT,
    };
    gpio_config(&pl_conf);

    // 初始化 SPI
    spi_74hc165_init();

    // 创建事件队列
    key_event_queue = xQueueCreate(32, sizeof(key_event_t));

    // 创建扫描任务
    xTaskCreate(key_scanner_task, "key_scan", 4096, NULL, 5, NULL);
}
```

---

### 任务 16.5: 测试 — 串口打印按键事件 (75 分钟)

**main.c — 测试入口 Test Entry:**

```c
// main.c — 键盘扫描测试

#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "key_scanner.h"

void app_main(void) {
    printf("4-Mode Keyboard - Key Scanner Test\n");
    printf("Waiting for key events...\n");

    key_scanner_init();

    // 获取事件队列引用 (需要暴露接口)
    extern QueueHandle_t key_event_queue;

    key_event_t evt;
    while (1) {
        if (xQueueReceive(key_event_queue, &evt, portMAX_DELAY)) {
            printf("Key %2d %s at %lld us\n",
                   evt.key_index,
                   evt.pressed ? "PRESSED " : "RELEASED",
                   evt.timestamp);
        }
    }
}
```

**预期输出 Expected Output:**
```
4-Mode Keyboard - Key Scanner Test
Waiting for key events...
Key  0 PRESSED  at 1234567 us
Key  0 RELEASED at 1234800 us
Key  5 PRESSED  at 1235100 us
Key  5 RELEASED at 1235350 us
```

---

## 日终总结 | Daily Wrap-up (16:30-17:00)

**今日关键词 Key Takeaways:**
1. ESP-IDF 是 ESP32 官方开发框架，基于 CMake 构建系统和 FreeRTOS
2. FreeRTOS 使用任务（Task）、队列（Queue）、信号量（Semaphore）管理并发
3. 74HC165 通过 SPI 菊花链读取 80 个按键状态
4. 消抖算法：连续 N 次读取一致才确认状态变化

---

## 今日作业 | Homework

1. **完成键盘扫描器**：串口能正确打印所有按键事件
2. **截图提交**：串口输出截图（至少 5 个不同按键事件）
3. **回答思考题**：
   - 为什么扫描任务优先级要比 RGB 任务高？
   - 如果消抖计数 DEBOUNCE_COUNT 设为 1 会怎样？设为 50 会怎样？
   - 为什么用 xQueueSend 而不是全局变量传递按键事件？

---

## 明日预告 | Tomorrow's Preview

明天我们将实现 4 种无线模式：USB HID（有线）、BLE HID（蓝牙）、WiFi 键盘、ESP-NOW（2.4GHz），让键盘以四种不同方式连接电脑。

Tomorrow we implement all 4 wireless modes: USB HID (wired), BLE HID (Bluetooth), WiFi keyboard, and ESP-NOW (2.4GHz), connecting the keyboard to a computer in four different ways.

---

## 参考资源 | References

- ESP-IDF 官方文档：https://docs.espressif.com/projects/esp-idf/
- ESP-IDF SPI 主机驱动：https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/peripherals/spi_master.html
- FreeRTOS 官方文档：https://www.freertos.org/
- ESP32-S3 技术参考手册：https://www.espressif.com/
- 74HC165 数据手册：https://www.ti.com/lit/ds/symlink/sn74hc165.pdf
- B 站搜索 "ESP-IDF 入门教程 FreeRTOS"

---

*最后更新 | Last updated: 2026-05-27*
