# Day 07: 无线通信——WiFi与ESP-NOW | Wireless Communication — WiFi & ESP-NOW

## 今日目标 | Today's Goals
- 理解 WiFi 的两种模式（STA/AP）及其在键盘中的应用
- 掌握 ESP-NOW 对等通信协议（2.4GHz 无需路由器）
- 实现 WiFi 键盘连接方案
- 完成4种无线模式的自动检测与切换

## 知识讲解 | Knowledge Lecture (09:15-10:30)

### FantasyKB 四种连接模式对比 | 4 Connection Modes Comparison

| 模式 | 协议 | 延迟 | 距离 | 功耗 | 适用场景 |
|---|---|---|---|---|---|
| **USB有线** | USB HID | <1ms | 有线 | 最低 | 桌面固定使用 |
| **蓝牙BLE** | BLE 5.0 | 10-25ms | ~10m | 低 | 连接手机/笔记本 |
| **WiFi** | TCP/UDP | 5-15ms | ~50m | 高 | 远距离、多设备 |
| **2.4GHz接收器** | ESP-NOW | 2-5ms | ~200m | 中 | 游戏低延迟场景 |

```
FantasyKB 自动模式选择逻辑：

     检测USB是否连接？
        |
    Yes +---> USB模式（优先级最高）
    No  |
        +---> 检测ESP-NOW接收器是否在线？
        |         |
        |     Yes +---> ESP-NOW模式（低延迟）
        |     No  |
        |         +---> 检测BLE主机是否连接？
        |               |
        |           Yes +---> BLE模式
        |           No  |
        |                 +---> WiFi模式（连接到配置的AP）
```

---

### WiFi 模式详解 | WiFi Modes

#### STA 模式（Station——客户端）

```
FantasyKB                WiFi路由器               电脑
(STA模式)                (AP)                   (STA)
   |                       |                      |
   +---- 连接路由器 ------->|                      |
                           |<----- 连接路由器 -----+
                           |
   +--- TCP/UDP 发送按键 ->|-- 转发 ------------->|
```

- 键盘作为客户端连接到WiFi路由器
- 电脑也连接到同一个路由器
- 通过TCP/UDP协议发送按键数据

#### AP 模式（Access Point——热点）

```
FantasyKB                电脑/手机
(AP模式)                 (STA)
   |                       |
   +<---- 连接键盘热点 -----+
   |
   +--- 键盘创建WiFi网络 "FantasyKB_Direct"
   +--- 电脑连接后直接通信
```

- 键盘自己变成一个WiFi热点
- 不需要路由器，直连电脑/手机
- 延迟更低，但距离更短

---

### ESP-NOW 协议 | ESP-NOW Protocol

ESP-NOW 是乐鑫开发的专属对等通信协议，非常适合FantasyKB的2.4GHz接收器模式。

#### ESP-NOW 特点

| 特性 | 说明 |
|---|---|
| 无需路由器 | 设备之间直接通信 |
| 无需配对 | 通过MAC地址指定目标 |
| 快速连接 | 毫秒级 |
| 加密支持 | 可选CCMP加密 |
| 最大负载 | 250字节/包 |
| 最大对等设备 | 20个（加密）/ 6个（不加密） |
| 速率 | 1Mbps / 2Mbps |

```
FantasyKB                ESP-NOW接收器
(发送端)                  (USB接收器)
   |                         |
   +--- ESP-NOW 2.4GHz ----->|
                             +--- USB HID ---> 电脑
   
   接收器是一个小型USB dongle
   内含一颗ESP32芯片
   接收ESP-NOW数据后通过USB HID转发给电脑
```

---

## 动手实验 | Hands-on Lab (10:45-12:00)

### 任务 7.1: WiFi STA 模式——连接路由器

```c
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "nvs_flash.h"

#define WIFI_SSID "YourWiFiName"
#define WIFI_PASS "YourWiFiPassword"

void wifi_event_handler(void *arg, esp_event_base_t event_base,
                         int32_t event_id, void *event_data)
{
    if (event_id == WIFI_EVENT_STA_START) {
        esp_wifi_connect();
    } else if (event_id == WIFI_EVENT_STA_DISCONNECTED) {
        printf("WiFi disconnected, reconnecting...\n");
        esp_wifi_connect();
    } else if (event_id == IP_EVENT_STA_GOT_IP) {
        ip_event_got_ip_t *event = (ip_event_got_ip_t *)event_data;
        printf("Got IP: " IPSTR "\n", IP2STR(&event->ip_info.ip));
    }
}

void wifi_init_sta(void)
{
    nvs_flash_init();
    esp_netif_init();
    esp_event_loop_create_default();
    esp_netif_create_default_wifi_sta();

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    esp_wifi_init(&cfg);

    esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID,
                                &wifi_event_handler, NULL);
    esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP,
                                &wifi_event_handler, NULL);

    wifi_config_t wifi_config = {
        .sta = {
            .ssid = WIFI_SSID,
            .password = WIFI_PASS,
        },
    };
    esp_wifi_set_mode(WIFI_MODE_STA);
    esp_wifi_set_config(WIFI_IF_STA, &wifi_config);
    esp_wifi_start();
}
```

---

### 任务 7.2: ESP-NOW 收发实验

**发送端（键盘端）代码：**

```c
#include "esp_now.h"
#include "esp_wifi.h"

uint8_t receiver_mac[] = {0xXX, 0xXX, 0xXX, 0xXX, 0xXX, 0xXX}; // 接收器MAC

// 按键数据包结构
typedef struct {
    uint8_t modifier;      // 修饰键
    uint8_t keycode[6];    // 按键代码（最多6个）
    uint8_t checksum;      // 校验和
} keyboard_packet_t;

void espnow_send_keys(uint8_t modifier, uint8_t *keys, int count)
{
    keyboard_packet_t packet = {0};
    packet.modifier = modifier;
    for (int i = 0; i < count && i < 6; i++) {
        packet.keycode[i] = keys[i];
    }
    // 计算校验和
    packet.checksum = packet.modifier;
    for (int i = 0; i < 6; i++) {
        packet.checksum ^= packet.keycode[i];
    }

    esp_now_send(receiver_mac, (uint8_t *)&packet, sizeof(packet));
}

void espnow_init(void)
{
    esp_wifi_set_mode(WIFI_MODE_STA);
    esp_wifi_start();

    esp_now_init();

    // 添加接收器为对等设备
    esp_now_peer_info_t peer = {
        .channel = 0,
        .ifidx = WIFI_IF_STA,
        .encrypt = false,
    };
    memcpy(peer.peer_addr, receiver_mac, 6);
    esp_now_add_peer(&peer);
}
```

**接收端（USB Dongle）代码框架：**

```c
void espnow_recv_cb(const esp_now_recv_info_t *info,
                     const uint8_t *data, int len)
{
    if (len != sizeof(keyboard_packet_t)) return;

    keyboard_packet_t *pkt = (keyboard_packet_t *)data;

    // 验证校验和
    uint8_t chk = pkt->modifier;
    for (int i = 0; i < 6; i++) chk ^= pkt->keycode[i];
    if (chk != pkt->checksum) {
        printf("Checksum error!\n");
        return;
    }

    // 通过USB HID发送给电脑
    usb_hid_send_report(pkt->modifier, pkt->keycode);
}

void app_main(void)
{
    esp_now_init();
    esp_now_register_recv_cb(espnow_recv_cb);
    printf("FantasyKB Receiver ready!\n");
}
```

---

## 项目实践 | Project Work (13:30-16:30)

### 任务 7.3: 四模自动切换实现

**核心逻辑：**

```c
typedef enum {
    MODE_USB = 0,
    MODE_BLE,
    MODE_WIFI,
    MODE_ESPNOW,
    MODE_NONE
} connection_mode_t;

static connection_mode_t current_mode = MODE_NONE;

void connection_manager_task(void *arg)
{
    while (1) {
        connection_mode_t new_mode = MODE_NONE;

        // 优先级1: USB有线
        if (usb_is_connected()) {
            new_mode = MODE_USB;
        }
        // 优先级2: ESP-NOW接收器
        else if (espnow_receiver_online()) {
            new_mode = MODE_ESPNOW;
        }
        // 优先级3: BLE连接
        else if (ble_is_connected()) {
            new_mode = MODE_BLE;
        }
        // 优先级4: WiFi
        else if (wifi_is_connected()) {
            new_mode = MODE_WIFI;
        }

        // 模式切换
        if (new_mode != current_mode) {
            printf("Mode switch: %d -> %d\n", current_mode, new_mode);
            current_mode = new_mode;

            // 通知所有子系统模式变化
            on_mode_changed(current_mode);
        }

        vTaskDelay(100 / portTICK_PERIOD_MS);
    }
}

const char* mode_to_string(connection_mode_t mode)
{
    switch (mode) {
        case MODE_USB:     return "USB";
        case MODE_BLE:     return "BLE";
        case MODE_WIFI:    return "WiFi";
        case MODE_ESPNOW:  return "2.4GHz";
        default:           return "None";
    }
}
```

---

### 任务 7.4: 四模式全测试

**测试清单 Test Checklist：**

| 模式 | 测试步骤 | 预期结果 | 实际结果 |
|---|---|---|---|
| USB | 连接USB线到电脑 | 设备管理器识别为键盘 | |
| BLE | 手机蓝牙搜索配对 | 手机连接，可输入文字 | |
| WiFi | 键盘和电脑连同一WiFi | 电脑端接收按键数据 | |
| ESP-NOW | 接收器插电脑USB | 按键数据低延迟到达 | |
| 自动切换 | 拔插USB线 | 自动切换到BLE/WiFi | |
| 双模 | USB+BLE同时连接 | USB优先 | |

**延迟对比测试（选做）：**
使用逻辑分析仪或示波器，测量每种模式下从按键到电脑收到数据的端到端延迟。

---

## 日终总结 | Daily Wrap-up (16:30-17:00)

**今日关键要点：**
1. FantasyKB 的4种连接模式按优先级自动切换：USB > ESP-NOW > BLE > WiFi
2. **WiFi** 适合远距离通信（通过路由器），**ESP-NOW** 适合低延迟近场通信（无需路由器）
3. ESP-NOW 的2.4GHz接收器模式延迟仅2-5ms，适合游戏场景
4. WiFi功耗最高，BLE最省电——根据使用场景自动选择

**明日预告：**
明天学习 WS2812B RGB 灯效——让键盘的80颗LED亮起来！你将实现彩虹波浪、按键响应、呼吸灯等炫酷效果。

---

## 今日作业 | Homework

1. **完成四模式测试报告**：填写测试清单，记录每种模式的测试结果
2. **编程练习**：实现一个简单的WiFi UDP服务器，接收键盘数据包并打印
3. **思考题**：
   - 为什么 USB 模式的优先级最高？（提示：考虑充电和零延迟）
   - ESP-NOW 和 WiFi 都使用 2.4GHz 频段，会互相干扰吗？如何避免？
   - 如果FantasyKB处于WiFi模式，同时收到ESP-NOW接收器的信号，应该切换吗？为什么？
4. **预习 Day 8**：搜索 "WS2812B 协议时序 ESP32 RMT"

---

## 常见问题 | FAQ

**Q: ESP-NOW 发送失败，返回错误？**
A: (1) 确认接收端MAC地址正确 (2) 两端必须在同一WiFi信道 (3) 确认接收端已初始化ESP-NOW (4) 检查距离是否过远。

**Q: WiFi 连接路由器失败？**
A: (1) 确认SSID和密码正确（区分大小写）(2) 路由器是否支持2.4GHz（ESP32-S3不支持5GHz）(3) 路由器是否开启了MAC地址过滤 (4) 检查路由器连接设备数量限制。

**Q: 四种模式切换不稳定？**
A: 检测逻辑需要加入消抖——不要在检测状态变化的瞬间就切换，而是连续检测N次确认后再切换，避免频繁跳变。

---

## 参考资源 | References

- ESP-IDF WiFi 驱动文档：https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/network/esp_wifi.html
- ESP-IDF ESP-NOW 文档：https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/network/esp_now.html
- ESP-NOW 示例代码：https://github.com/espressif/esp-idf/tree/master/examples/wifi/espnow
- B 站搜索 "ESP32 ESP-NOW 教程"
- B 站搜索 "ESP32 WiFi 编程 入门"

---

*最后更新 | Last updated: 2026-05-27*
