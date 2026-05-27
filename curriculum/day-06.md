# Day 06: 无线通信——蓝牙BLE | Wireless Communication — Bluetooth BLE

## 今日目标 | Today's Goals
- 理解蓝牙BLE的基本概念（GAP、GATT、Service、Characteristic）
- 学会使用 ESP32-S3 的 BLE 功能
- 实现 BLE HID 键盘，让手机/电脑通过蓝牙识别你的键盘
- 了解BLE配对安全和连接管理

## 知识讲解 | Knowledge Lecture (09:15-10:30)

### 蓝牙BLE架构 | Bluetooth Low Energy Architecture

蓝牙BLE是FantasyKB的4种连接模式之一，特点是低功耗、快速连接。

#### BLE 协议栈

```
+-----------------------------------+
|          应用层 Application        |   <-- 你的键盘代码
+-----------------------------------+
|    GATT (通用属性配置文件)          |   <-- 数据组织方式
+-----------------------------------+
|    ATT  (属性协议)                 |   <-- 数据读写机制
+-----------------------------------+
|    GAP  (通用访问配置文件)          |   <-- 连接管理
+-----------------------------------+
|    SM   (安全管理)                 |   <-- 加密配对
+-----------------------------------+
|    L2CAP (逻辑链路控制)            |   <-- 数据分包
+-----------------------------------+
|    LL   (链路层)                   |   <-- 物理通道
+-----------------------------------+
|    PHY  (物理层) 2.4GHz            |   <-- 射频
+-----------------------------------+
```

#### 核心概念

**GAP（Generic Access Profile）—— 负责连接**

| 角色 Role | 说明 Description | FantasyKB 的角色 |
|---|---|---|
| Broadcaster | 广播数据，不连接 | -- |
| Observer | 监听广播，不连接 | -- |
| **Peripheral** | 等待连接（从设备） | **键盘** |
| Central | 发起连接（主设备） | 手机/电脑 |

**GATT（Generic Attribute Profile）—— 负责数据**

```
GATT Server (键盘端)                     GATT Client (电脑端)
+----------------------------------+      +------------------+
|  Service: HID Service            |<---->|  读取/写入数据     |
|  +-- Characteristic: Report      |      |                  |
|  |     (按键数据)                  |      |  写入: 发送按键   |
|  +-- Characteristic: Protocol Mode|     |  读取: 获取模式   |
|  +-- Characteristic: Control Point|     |                  |
+----------------------------------+      +------------------+
```

- **Service**：一组相关数据的集合（如HID服务包含键盘相关的所有数据）
- **Characteristic**：具体的数据项（如键盘报告、电池电量等）
- 每个Service和Characteristic都有唯一的UUID标识

#### HID over GATT Profile (HOGP)

BLE键盘使用 **HOGP（HID over GATT Profile）** 协议：

```
电脑搜索BLE设备 --> 发现 "FantasyKB"
        |
    配对连接
        |
    发现HID Service (UUID: 0x1812)
        |
    订阅 Report Characteristic
        |
    键盘发送按键报告 --> 电脑识别为键盘输入
```

---

## 动手实验 | Hands-on Lab (10:45-12:00)

### 任务 6.1: BLE 扫描器——发现周围设备

**代码——BLE扫描：**

```c
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "nimble/nimble_port.h"
#include "nimble/nimble_port_freertos.h"
#include "host/ble_gap.h"

// 扫描回调函数
static int ble_gap_event(struct ble_gap_event *event, void *arg)
{
    switch (event->type) {
    case BLE_GAP_EVENT_DISC:
        // 发现一个BLE设备
        printf("Device found: ");
        for (int i = 0; i < event->disc.addr.val_len; i++) {
            printf("%02X:", event->disc.addr.val[i]);
        }
        printf(" RSSI=%d ", event->disc.rssi);
        if (event->disc.length_data > 0) {
            printf("Name: %.*s", event->disc.length_data, event->disc.data);
        }
        printf("\n");
        break;
    }
    return 0;
}

void ble_scan_task(void *arg)
{
    // 初始化NimBLE协议栈
    nimble_port_init();

    struct ble_gap_disc_params disc_params = {
        .itvl = 0,
        .window = 0,
        .filter_policy = 0,
        .limited = 0,
        .passive = 1,
        .filter_duplicates = 1,
    };

    // 开始扫描10秒
    ble_gap_disc(BLE_OWN_ADDR_PUBLIC, 10000, &disc_params,
                 ble_gap_event, NULL);
}

void app_main(void)
{
    xTaskCreate(ble_scan_task, "ble_scan", 4096, NULL, 5, NULL);
}
```

**预期结果：**
串口输出周围所有BLE设备的MAC地址、信号强度和名称。

---

### 任务 6.2: BLE HID 键盘——让手机识别你的键盘

ESP-IDF 提供了 BLE HID 的示例代码，可以直接使用：

**快速实现步骤：**

1. 在 ESP-IDF 中打开示例：`examples/bluetooth/nimble/BLE_HID`
2. 修改设备名称为 `"FantasyKB"`
3. 编译并烧录
4. 在手机的蓝牙设置中搜索并连接 "FantasyKB"
5. 连接成功后，ESP32-S3 发送的按键数据会直接输入到手机

**发送按键报告的核心代码：**

```c
#include "host/ble_hs.h"
#include "services/hid/ble_svc_hid.h"

// HID键盘报告（8字节，符合USB HID标准）
// 字节0: 修饰键 (Ctrl/Shift/Alt/GUI)
// 字节1: 保留
// 字节2-7: 同时按下的按键代码（最多6个）

uint8_t keyboard_report[8] = {0};

void send_key_press(uint8_t hid_keycode)
{
    keyboard_report[0] = 0;           // 无修饰键
    keyboard_report[2] = hid_keycode; // 按键代码
    // 通过BLE HID发送报告
    ble_hid_svc_send_report(keyboard_report, sizeof(keyboard_report));
}

void send_key_release(void)
{
    keyboard_report[2] = 0;  // 清除按键
    ble_hid_svc_send_report(keyboard_report, sizeof(keyboard_report));
}

// 常用按键代码 (HID Usage Table)
#define HID_KEY_A     0x04
#define HID_KEY_B     0x05
#define HID_KEY_ENTER 0x28
#define HID_KEY_SPACE 0x2C
#define HID_KEY_LCTRL 0xE0
```

---

## 项目实践 | Project Work (13:30-16:30)

### 任务 6.3: BLE 配对安全与连接管理

**BLE 配对方式：**

| 方式 | 安全级别 | 适用场景 |
|---|---|---|
| Just Works | 低 | 无需认证（不推荐用于键盘） |
| Passkey Entry | 中 | 输入6位数字配对 |
| Numeric Comparison | 高 | 确认双方显示的数字相同 |
| OOB（带外） | 最高 | 通过其他通道交换密钥 |

**FantasyKB 使用 Passkey Entry 方式**——配对时在键盘上输入显示的数字，防止误连接。

**连接管理策略：**

```c
// 自动重连逻辑（伪代码）
void ble_connection_manager(void)
{
    while (1) {
        if (!is_connected) {
            // 1. 尝试连接上次配对的设备
            if (bonded_device_exists()) {
                attempt_reconnect();
            }
            // 2. 等待3秒
            vTaskDelay(3000 / portTICK_PERIOD_MS);
        } else {
            // 已连接，检查连接质量
            int rssi = get_connection_rssi();
            if (rssi < -85) {  // 信号很弱
                printf("BLE signal weak, may disconnect\n");
            }
        }
    }
}
```

---

### 任务 6.4: BLE 键盘延迟测试

**实验方法：**
1. 编写测试代码：按下按键时翻转一个GPIO
2. 用逻辑分析仪同时捕获GPIO翻转和BLE数据包
3. 测量从按键按下到手机收到数据的时间

**预期延迟参考：**

| 连接间隔 | 典型延迟 | 说明 |
|---|---|---|
| 7.5ms | 10-15ms | 最快，功耗较高 |
| 15ms | 15-25ms | 平衡选择 |
| 30ms | 30-45ms | 省电，打字可能感觉到延迟 |
| 100ms | 100-120ms | 非常省电，不适合打字 |

**FantasyKB 推荐连接间隔：15ms**（平衡延迟和功耗）

**优化练习：**
修改BLE连接参数，测试不同连接间隔下的打字体验：

```c
struct ble_gap_upd_params conn_params = {
    .itvl_min = 12,   // 12 * 1.25ms = 15ms
    .itvl_max = 15,   // 15 * 1.25ms = 18.75ms
    .latency = 0,     // 无跳过
    .supervision_timeout = 500,  // 5秒超时
};
```

---

## 日终总结 | Daily Wrap-up (16:30-17:00)

**今日关键要点：**
1. BLE 键盘使用 **HOGP（HID over GATT Profile）** 协议，让设备即插即用
2. **GAP** 管理连接（广播、扫描、配对），**GATT** 管理数据（Service/Characteristic）
3. 连接间隔直接影响输入延迟——15ms是打字场景的最佳平衡点
4. 配对安全很重要——键盘输入包含密码等敏感信息

**明日预告：**
明天学习 WiFi 和 ESP-NOW——FantasyKB 的另外两种无线模式。你将实现4种连接模式之间的自动切换！

---

## 今日作业 | Homework

1. **完成实验**：手机成功通过BLE连接键盘并发送文字，截图蓝牙设置页面
2. **编写BLE键盘报告发送代码**：
   - 发送 "Hello FantasyKB" 字符串（逐个字符）
   - 每个字符之间间隔50ms
3. **思考题**：
   - BLE 键盘报告为什么是8个字节？每个字节的作用是什么？
   - 为什么 BLE 连接间隔不能设为 0（持续连接）？
   - 如果同时连接了BLE和USB，两个输入源同时发送按键会怎样？
4. **预习 Day 7**：搜索 "ESP-NOW 协议 原理" 和 "WiFi STA AP 模式"

---

## 常见问题 | FAQ

**Q: 手机搜索不到 "FantasyKB" 怎么办？**
A: (1) 确认ESP32-S3的BLE已初始化并在广播 (2) 检查手机蓝牙是否开启 (3) 某些手机需要在"添加蓝牙设备"或"配对新设备"中搜索 (4) 重启ESP32-S3和手机蓝牙。

**Q: 配对后键盘不输入文字？**
A: (1) 确认HID Report Descriptor正确声明了键盘类型 (2) 检查是否发送了按键释放报告（只发按下不发释放会导致"卡键"）(3) 部分手机需要允许"输入设备"权限。

**Q: BLE连接经常断开？**
A: (1) 检查信号强度（RSSI），距离过远会断开 (2) 检查供电是否稳定（BLE对电源噪声敏感）(3) 增大 supervision_timeout (4) 确认没有其他设备尝试连接同一键盘。

---

## 参考资源 | References

- ESP-IDF BLE 示例代码：https://github.com/espressif/esp-idf/tree/master/examples/bluetooth/nimble
- Bluetooth SIG HID Service 规范：https://www.bluetooth.com/specifications/specs/hid-service-1-0/
- BLE 连接参数优化指南：https://punchthrough.com/maximizing-ble-throughput-part-2-use-larger-att-mtu-3/
- B 站搜索 "蓝牙BLE 开发 教程"
- B 站搜索 "ESP32 BLE HID 键盘"

---

*最后更新 | Last updated: 2026-05-27*
