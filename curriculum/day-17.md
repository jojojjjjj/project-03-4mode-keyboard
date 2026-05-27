# Day 17: USB HID与无线通信固件 | USB HID & Wireless Communication Firmware

> **今日目标 Today's Goals:**
> - 理解 USB HID 报告描述符和数据格式
> - 集成 TinyUSB 实现 USB 有线键盘
> - 实现 BLE HID 蓝牙键盘
> - 实现 WiFi 键盘和 ESP-NOW 2.4GHz 模式
>
> **产出 Deliverable:** 4 种无线模式全部工作

---

## 时间安排 | Schedule

| 时间 Time | 活动类型 Type | 内容 Content |
|---|---|---|
| 09:00–09:15 | 晨会 | 回顾 Day 16 键盘扫描，答疑 |
| 09:15–10:30 | 讲解 | USB HID 协议 + TinyUSB 集成 |
| 10:30–10:45 | 休息 | — |
| 10:45–12:00 | 实验 | USB HID 键盘实现 |
| 12:00–13:30 | 午休 | — |
| 13:30–15:00 | 实验 | BLE HID 实现 |
| 15:00–15:15 | 休息 | — |
| 15:15–16:30 | 实验 | WiFi 键盘 + ESP-NOW 模式 |
| 16:30–17:00 | 总结 | 日终回顾 + 明日预告 |

---

## 上午：USB HID 有线模式 | Morning: USB HID Wired Mode

### 为什么要学这个? | Why Learn This?

USB HID（Human Interface Device）是键盘、鼠标等输入设备的标准协议。当你按下键盘上的 "A" 键，键盘通过 USB 向电脑发送一个 8 字节的 HID 报告，操作系统据此显示字母 "A"。理解 HID 协议意味着你能设计任何自定义输入设备——键盘、游戏手柄、MIDI 控制器、甚至飞行摇杆。

USB HID is the standard protocol for input devices like keyboards and mice. Understanding HID means you can design any custom input device — keyboards, game controllers, MIDI controllers, even flight sticks.

本项目支持 4 种连接模式，USB 有线是最基础、延迟最低的模式。

---

### 任务 17.1: USB HID 协议详解 (40 分钟)

**HID 报告格式 HID Report Format:**

```
标准键盘 HID 报告 (8 字节):

  Byte 0: 修饰键 Modifier Keys (位图 bitmap)
    bit 0: Left Ctrl
    bit 1: Left Shift
    bit 2: Left Alt
    bit 3: Left GUI (Win/Cmd)
    bit 4: Right Ctrl
    bit 5: Right Shift
    bit 6: Right Alt
    bit 7: Right GUI

  Byte 1: 保留 Reserved (0x00)

  Byte 2-7: 按键码 Key Codes (最多同时6键)
    0x00 = 无键 No key
    0x04 = a/A
    0x05 = b/B
    0x06 = c/C
    ...
    0x27 = 0/)
    0x28 = Enter
    0x29 = Escape
    0x2C = Space
    0x3A = F1
    ...
    0x4F = Right Arrow
    0x50 = Left Arrow
    0x52 = Up Arrow
    0x53 = Down Arrow

示例 Example:
  按下 "A" 键:     [0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00]
  按下 Shift+A:    [0x02, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00]
  按下 Ctrl+C:     [0x01, 0x00, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00]
  全部松开:        [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
```

---

### 任务 17.2: TinyUSB 集成 (35 分钟)

**TinyUSB 简介 TinyUSB Introduction:**

```
TinyUSB 是一个开源的 USB 设备栈:
  - 支持 ESP32-S3 内置 USB OTG
  - 提供 HID / CDC / MSC / Audio 等类别
  - 已集成到 ESP-IDF 组件中

ESP-IDF 中使用 TinyUSB:
  1. 在 sdkconfig 中启用:
     CONFIG_TINYUSB=y
     CONFIG_TINYUSB_HID=y

  2. 或者通过组件管理器添加:
     idf.py add-dependency tinyusb
```

**USB HID 初始化代码 USB HID Init:**

```c
// usb_hid.c — USB HID 键盘

#include "tinyusb.h"
#include "tusb_cdc_acm.h"
#include "class/hid/hid.h"

// HID 报告描述符 Report Descriptor
static uint8_t const hid_report_descriptor[] = {
    TUD_HID_REPORT_DESC_KEYBOARD(HID_REPORT_ID(1))
};

// 发送键盘报告 Send keyboard report
void usb_hid_send_report(uint8_t modifier, uint8_t *keycodes, int count) {
    if (!tud_mounted()) return;

    uint8_t report[8] = {0};
    report[0] = modifier;  // 修饰键
    // report[1] = 0;      // 保留

    for (int i = 0; i < count && i < 6; i++) {
        report[2 + i] = keycodes[i];
    }

    tud_hid_report(1, report, sizeof(report));
}
```

---

### 任务 17.3: 实现 USB 有线键盘 (60 分钟)

**按键映射表 Key Mapping Table:**

```c
// keymap.c — 按键映射
// 将硬件按键索引 (0-79) 映射为 HID 键码

#include "usbhid_keys.h"  // HID key code definitions

// 示例: 80键布局映射
static const uint8_t keymap[KEY_COUNT] = {
    // Row 0 (Keys 0-9)
    HID_KEY_ESCAPE, HID_KEY_1, HID_KEY_2, HID_KEY_3, HID_KEY_4,
    HID_KEY_5, HID_KEY_6, HID_KEY_7, HID_KEY_8, HID_KEY_9,
    // Row 1 (Keys 10-19)
    HID_KEY_TAB, HID_KEY_Q, HID_KEY_W, HID_KEY_E, HID_KEY_R,
    HID_KEY_T, HID_KEY_Y, HID_KEY_U, HID_KEY_I, HID_KEY_O,
    // ... 更多行
    // 最后一键: 旋钮按下
    HID_KEY_MUTE,
};

// 从按键事件生成 HID 报告
void process_key_event(key_event_t *evt) {
    static uint8_t active_keys[6] = {0};
    static uint8_t active_count = 0;
    static uint8_t modifier = 0;

    uint8_t hid_key = keymap[evt->key_index];

    if (evt->pressed) {
        // 添加到活跃按键列表
        if (active_count < 6) {
            active_keys[active_count++] = hid_key;
        }
    } else {
        // 从活跃按键列表移除
        for (int i = 0; i < active_count; i++) {
            if (active_keys[i] == hid_key) {
                active_keys[i] = active_keys[--active_count];
                active_keys[active_count] = 0;
                break;
            }
        }
    }

    usb_hid_send_report(modifier, active_keys, active_count);
}
```

---

## 下午：无线模式实现 | Afternoon: Wireless Modes

### 任务 17.4: BLE HID 蓝牙键盘 (60 分钟)

**BLE HID 概述 BLE HID Overview:**

```
BLE HID 工作流程:
  1. GAP 初始化 (广播、可被发现)
  2. 设备配对 (Pairing)
  3. 建立 GATT 连接
  4. 通过 HID Service 发送按键报告

GATT 服务结构:
  Service: HID (0x1812)
    ├── Report Map (0x2A4B) — HID 描述符
    ├── Report (0x2A4D) — 键盘数据
    ├── Report Reference (0x2908)
    ├── Protocol Mode (0x2A4E)
    └── Control Point (0x2A4C)
```

**BLE HID 关键代码 BLE HID Key Code:**

```c
// ble_hid.c — BLE HID 键盘

#include "esp_bt.h"
#include "esp_bt_main.h"
#include "esp_gap_ble_api.h"
#include "esp_hidd.h"

static esp_hidd_dev_t *hid_dev = NULL;

void ble_hid_init(void) {
    // 初始化蓝牙控制器和 Bluedroid 协议栈
    ESP_ERROR_CHECK(esp_bt_controller_mem_release(ESP_BT_MODE_CLASSIC_BT));

    esp_bt_controller_config_t bt_cfg = BT_CONTROLLER_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_bt_controller_init(&bt_cfg));
    ESP_ERROR_CHECK(esp_bt_controller_enable(ESP_BT_MODE_BLE));
    ESP_ERROR_CHECK(esp_bluedroid_init());
    ESP_ERROR_CHECK(esp_bluedroid_enable());

    // 初始化 BLE HID 设备
    esp_hidd_profile_init(hid_event_handler);
}

void ble_hid_send_report(uint8_t modifier, uint8_t *keys, int count) {
    if (hid_dev == NULL) return;

    uint8_t report[8] = {modifier, 0, 0, 0, 0, 0, 0, 0};
    for (int i = 0; i < count && i < 6; i++) {
        report[2 + i] = keys[i];
    }

    esp_hidd_send_report(hid_dev, HID_REPORT_TYPE_INPUT, 1,
                          sizeof(report), report);
}
```

---

### 任务 17.5: WiFi 键盘 + ESP-NOW (75 分钟)

**WiFi 键盘原理 WiFi Keyboard Principle:**

```
WiFi 键盘模式:
  键盘 (ESP32-S3, WiFi STA) ──TCP/UDP──→ 电脑端接收程序

  1. 键盘连接到同一 WiFi 网络
  2. 键盘发送按键事件到电脑上的接收程序 (Python)
  3. 接收程序调用 pyautogui / keyboard 库模拟按键

  优点: 范围大（室内30m+），可穿透墙壁
  缺点: 延迟较高（10-50ms），需要运行接收端软件
```

**ESP-NOW 2.4GHz 模式:**

```
ESP-NOW 模式:
  键盘 (ESP-NOW 发送方) ──2.4GHz 直连──→ 接收器 (ESP-NOW 接收方 → USB HID)

  1. 键盘和接收器预先配对（交换 MAC 地址）
  2. 键盘发送精简按键数据包
  3. 接收器通过 USB HID 转发给电脑

  优点: 低延迟（< 5ms），无需 WiFi 网络，无需软件
  缺点: 范围较短（室内约10-20m）

  ESP-NOW 数据包格式:
  ┌──────┬──────┬───────┬──────┐
  │ MODE │  LEN │ EVENTS│ CRC  │
  │ 1B   │ 1B   │ N*3B  │ 1B   │
  └──────┴──────┴───────┴──────┘

  每个 EVENT: [key_index(1B), pressed(1B), modifier(1B)]
```

**无线模式管理器 Wireless Mode Manager:**

```c
// wireless_manager.c — 4模式切换

typedef enum {
    MODE_USB = 0,     // USB 有线
    MODE_BLE,         // 蓝牙 BLE
    MODE_WIFI,        // WiFi
    MODE_ESP_NOW,     // 2.4GHz ESP-NOW
    MODE_COUNT
} wireless_mode_t;

static wireless_mode_t current_mode = MODE_USB;

void wireless_mode_switch(wireless_mode_t mode) {
    // 先关闭当前模式
    switch (current_mode) {
        case MODE_USB:     usb_hid_deinit();     break;
        case MODE_BLE:     ble_hid_deinit();     break;
        case MODE_WIFI:    wifi_kb_deinit();     break;
        case MODE_ESP_NOW: esp_now_deinit();     break;
    }

    current_mode = mode;

    // 初始化新模式
    switch (mode) {
        case MODE_USB:     usb_hid_init();       break;
        case MODE_BLE:     ble_hid_init();       break;
        case MODE_WIFI:    wifi_kb_init();       break;
        case MODE_ESP_NOW: esp_now_tx_init();    break;
    }
}

// 统一发送接口
void wireless_send_report(uint8_t modifier, uint8_t *keys, int count) {
    switch (current_mode) {
        case MODE_USB:     usb_hid_send_report(modifier, keys, count);      break;
        case MODE_BLE:     ble_hid_send_report(modifier, keys, count);      break;
        case MODE_WIFI:    wifi_kb_send_report(modifier, keys, count);      break;
        case MODE_ESP_NOW: esp_now_send_report(modifier, keys, count);      break;
    }
}
```

---

## 日终总结 | Daily Wrap-up (16:30-17:00)

**今日关键词 Key Takeaways:**
1. USB HID 报告固定 8 字节：1 字节修饰键 + 1 保留 + 6 键码
2. TinyUSB 是跨平台 USB 设备栈，ESP-IDF 已集成
3. BLE HID 通过 GATT 服务发送按键，需要配对过程
4. ESP-NOW 是乐鑫专有协议，低延迟点对点通信，最适合 2.4GHz 模式

---

## 今日作业 | Homework

1. **完成 4 种模式测试**：USB 有线 + BLE + WiFi + ESP-NOW 各成功发送至少一个按键
2. **截图提交**：4 种模式的串口日志或接收端截图
3. **回答思考题**：
   - USB HID 为什么最多同时报 6 个键？如何实现全键无冲（NKRO）？
   - BLE 和 WiFi 都使用 2.4GHz 射频，为什么 BLE 延迟更低？
   - ESP-NOW 为什么不需要 WiFi 网络也能通信？

---

## 明日预告 | Tomorrow's Preview

明天是系统集成日——我们将音频管道（ES7210 录音 + ES8311 播放）、LVGL 旋钮界面、SimpleFOC 电机控制、RGB 灯效等全部模块整合到主固件中，并协调 FreeRTOS 任务优先级。

Tomorrow is system integration — combining audio pipeline (ES7210 capture + ES8311 playback), LVGL knob UI, SimpleFOC motor control, RGB effects into the main firmware, coordinating FreeRTOS task priorities.

---

## 参考资源 | References

- TinyUSB 官方文档：https://docs.tinyusb.org/
- ESP-IDF BLE HID 示例：https://github.com/espressif/esp-idf/tree/master/examples/bluetooth/bluedroid/ble/bluedroid_ble_hid_device_demo
- ESP-NOW 官方文档：https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/network/esp_now.html
- USB HID 规范：https://www.usb.org/hid
- B 站搜索 "ESP32 BLE HID 键盘"
- B 站搜索 "ESP-NOW 通信 教程"

---

*最后更新 | Last updated: 2026-05-27*
