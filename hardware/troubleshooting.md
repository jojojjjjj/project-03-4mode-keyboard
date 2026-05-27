# 故障排查指南 | Troubleshooting Guide

## 概述 | Overview

本指南帮助排查四模键盘（ESP32-S3）项目中常见的硬件和软件问题。问题按子系统分组，每类提供症状、可能原因和解决方法。

This guide helps troubleshoot common issues in the 4-mode keyboard (ESP32-S3) project. Issues are grouped by subsystem with symptoms, likely causes, and solutions.

---

## 一、电源问题 | Power Issues

### 1.1 设备无法启动 / No Boot

| 现象 Symptom | 可能原因 Cause | 解决方法 Solution |
|---|---|---|
| 通电后完全无反应 | VCC 与 GND 短路 | 万用表蜂鸣档测 VCC/GND 阻抗，应 > 1k ohm |
| 通电后完全无反应 | AMS1117-3.3 损坏或虚焊 | 测量 AMS1117 输出端，应为 3.3V；补焊或更换 |
| 通电后完全无反应 | Type-C 母座焊盘脱落 | 目视检查焊盘，必要时飞线修复 |
| 电流过大（> 500mA） | 某处短路 | 逐个断开子板定位短路源 |
| ESP32-S3 发热严重 | 电源电压过高 | 确认供电 3.3V 而非 5V 直接接入 |

### 1.2 电压异常 / Voltage Wrong

| 现象 Symptom | 可能原因 Cause | 解决方法 Solution |
|---|---|---|
| 3.3V 偏低（< 3.1V） | 负载过大 | 断开子板逐一排查；检查是否有 IC 短路 |
| 3.3V 偏高（> 3.5V） | AMS1117 输入输出接反 | 检查 AMS1117 引脚 1(GND) 2(OUT) 3(IN) |
| 5V 不稳 | USB 供电不足或线缆差 | 更换优质 USB-C 数据线；使用带外部供电的 HUB |
| 3.3V 波纹大 | 去耦电容缺失 | 每个 IC 的 VCC 引脚旁添加 100nF 陶瓷电容 |

### 1.3 电池不充电 / Battery Not Charging

| 现象 Symptom | 可能原因 Cause | 解决方法 Solution |
|---|---|---|
| 插入 USB 后充电灯不亮 | TP4056 虚焊 | 补焊 TP4056 |
| 充电灯常亮不熄灭 | 电池损坏或接触不良 | 检查电池电压；测量内阻 |
| 充电后使用时间很短 | 电池容量不足或保护电路误触发 | 测量放电截止电压是否正常（应 2.5-3.0V） |
| 电池鼓包 | 过充或老化 | 立即停止使用，安全处理，更换电池 |

---

## 二、ESP32-S3 问题 | ESP32-S3 Issues

### 2.1 无法刷写固件 / Won't Flash

| 现象 Symptom | 可能原因 Cause | 解决方法 Solution |
|---|---|---|
| esptool 报 "No serial device found" | CH342F 驱动未安装 | 安装 CH340/CH342 驱动；检查设备管理器 |
| esptool 报 "Failed to connect" | BOOT 模式未进入 | 按住 BOOT 键 → 按 EN → 松开 BOOT |
| esptool 报 "Wrong boot mode" | Strapping 引脚电平错误 | 检查 GPIO0/3/45/46 上拉下拉电阻 |
| 串口识别但刷写失败 | 波特率太高 | 降低波特率：`-b 115200` |
| USB-COM 口不停出现消失 | USB 接触不良 | 更换 USB 线；检查 Type-C 焊接 |

### 2.2 启动循环 / Boot Loop

| 现象 Symptom | 可能原因 Cause | 解决方法 Solution |
|---|---|---|
| 串口不停输出重启日志 | 固件崩溃（panic） | 读取串口日志，定位 crash 原因 |
| 启动循环 + 看门狗超时 | FreeRTOS 任务死锁 | 检查任务优先级和互斥锁 |
| 启动循环 + brownout | 供电不足 | 参见 2.3 |
| 刷入后立即重启 | 分区表错误 | 检查 partitions.csv，使用正确偏移地址 |

### 2.3 欠压检测 / Brownout

| 现象 Symptom | 可能原因 Cause | 解决方法 Solution |
|---|---|---|
| "brownout detector was triggered" | 电源电压跌落 | 增大 VCC 去耦电容（100uF + 100nF） |
| WiFi 开启时 brownout | WiFi 发射瞬间电流大（> 300mA） | 确保电源能提供 500mA+ 峰值电流 |
| 全部 LED 亮时 brownout | LED 总电流超限 | 降低 LED 亮度或限制同时亮灯数量 |

---

## 三、键扫描问题 | Key Scanning Issues

### 3.1 按键无响应 / Keys Not Responding

| 现象 Symptom | 可能原因 Cause | 解决方法 Solution |
|---|---|---|
| 单个按键不工作 | 轴体引脚弯曲或轴座虚焊 | 拔出轴体检查引脚；补焊轴座 |
| 整行不工作 | 74HC138 译码器输出断开 | 测量译码器到该行的连接 |
| 整列不工作 | 74HC165 对应输入断开 | 检查移位寄存器引脚焊接 |
| 所有按键不工作 | SPI 总线未初始化或断线 | 示波器检查 SPI CLK/CS/MOSI/MISO 信号 |
| 部分按键不工作 | 74HC165 链路中间断裂 | 检查 Q7' → SER 的链路连接 |

### 3.2 按键误触发 / Ghost Keys

| 现象 Symptom | 可能原因 Cause | 解决方法 Solution |
|---|---|---|
| 按一个键出多个字符 | 1N4148 二极管缺失或方向反 | 检查每个按键的串联二极管方向（阴极朝列线） |
| 三键同按时出鬼键 | 二极管防鬼键矩阵不完整 | 确认每个按键都有二极管 |
| 随机触发 | 74HC165 输入浮空 | 添加 10k 下拉电阻到每个输入 |

### 3.3 按键重复或延迟 / Key Repeat or Delay

| 现象 Symptom | 可能原因 Cause | 解决方法 Solution |
|---|---|---|
| 按一次出多个字符 | 消抖时间太短 | 增大 debounce 参数（5-15ms） |
| 按键响应慢 | 消抖时间太长或扫描频率低 | 减小 debounce；提高 SPI 时钟频率 |
| 偶尔丢键 | 扫描周期不均匀 | 检查是否有高优先级任务阻塞扫描 |

---

## 四、USB 问题 | USB Issues

### 4.1 设备不被识别 / Not Recognized

| 现象 Symptom | 可能原因 Cause | 解决方法 Solution |
|---|---|---|
| 电脑提示"无法识别的设备" | D+/D- 接线错误或 22 ohm 电阻虚焊 | 检查 USB 差分对走线 |
| 设备管理器无反应 | Type-C 焊接不良 | 目视检查 Type-C 各引脚 |
| 提示"未知 USB 设备" | 固件 USB 描述符错误 | 检查 USB Device Descriptor 配置 |

### 4.2 USB HUB 问题 / HUB Not Working

| 现象 Symptom | 可能原因 Cause | 解决方法 Solution |
|---|---|---|
| HUB 不被识别 | GL850G 虚焊或配置错误 | 检查 GL850G 的晶振/电阻配置 |
| HUB 下行端口不工作 | 下行端口电源开关未开启 | 检查 GL850G PWRSW 引脚 |
| HUB 枚举但设备不稳定 | 上行端口信号质量差 | 检查上行 D+/D- 走线等长 |

### 4.3 CH342F 不被检测 / CH342F Not Detected

| 现象 Symptom | 可能原因 Cause | 解决方法 Solution |
|---|---|---|
| 无 COM 口出现 | CH342F 驱动未安装 | 安装 CH342 最新驱动 |
| COM 口出现但无法打开 | 端口被其他程序占用 | 关闭串口监视器，重新打开 |
| 波特率错误 | 固件使用了非标准波特率 | 尝试 115200 和 460800 |

---

## 五、音频问题 | Audio Issues

### 5.1 无声音 / No Sound

| 现象 Symptom | 可能原因 Cause | 解决方法 Solution |
|---|---|---|
| 扬声器无输出 | ES8311 未初始化 | I2C 扫描确认 ES8311 地址 (0x18) 响应 |
| 扬声器无输出 | NS4150 功放未使能 | 检查 NS4150 SD/EN 引脚电平 |
| 扬声器有底噪无音频 | I2S 时钟未输出 | 示波器测 BCLK/LRCK 是否有波形 |
| 只有单声道 | I2S 数据线有一根断开 | 检查 DIN/DOUT 连线 |

### 5.2 静音或噪声 / Static Noise

| 现象 Symptom | 可能原因 Cause | 解决方法 Solution |
|---|---|---|
| 持续白噪声 | I2S 时钟抖动 | 确保 I2S BCLK 稳定；减少中断干扰 |
| 50/60Hz 嗡嗡声 | 地线环路或电源纹波 | 音频地与数字地单点连接；加大滤波电容 |
| 啵啵声 | 采样率不匹配 | 确认 ESP32-S3 I2S 采样率与 ADC/DAC 一致 |
| 噪声随 WiFi 活动 | WiFi 射频干扰 | WiFi 天线远离音频电路；音频走线加屏蔽 |

### 5.3 麦克风不工作 / Microphone Not Working

| 现象 Symptom | 可能原因 Cause | 解决方法 Solution |
|---|---|---|
| 录音全零 | ES7210 未初始化 | I2C 扫描确认 ES7210 地址 (0x40) |
| 录音音量极低 | 麦克风增益设置不当 | 调整 ES7210 寄存器的增益值 |
| 录音有削波失真 | 输入信号过强 | 降低增益或加输入衰减电阻 |

---

## 六、无线问题 | Wireless Issues

### 6.1 BLE 无法配对 / BLE Won't Pair

| 现象 Symptom | 可能原因 Cause | 解决方法 Solution |
|---|---|---|
| 手机搜索不到设备 | BLE 广播未开启或间隔太长 | 检查 `esp_ble_gap_config_adv_data()` 参数 |
| 配对后立即断开 | GATT 服务配置错误 | 检查 HID GATT Service UUID 和 Characteristic |
| 配对成功但无数据 | Notification 未使能 | 客户端需使能 CCCD (0x2902) |
| 传输延迟高 | 连接参数不优 | 调整 Connection Interval (7.5ms-4000ms) |

### 6.2 WiFi 断连 / WiFi Disconnects

| 现象 Symptom | 可能原因 Cause | 解决方法 Solution |
|---|---|---|
| 无法连接路由器 | SSID/密码错误 | 确认 WiFi 配置正确 |
| 连接后频繁断开 | 信号弱或信道拥挤 | 更换信道；检查天线连接 |
| 获取 IP 失败 | DHCP 超时 | 增加 DHCP 超时时间；尝试静态 IP |
| 大量丢包 | ESP32-S3 WiFi 负载过高 | 降低发送频率；使用 WiFi 日志分析 |

### 6.3 ESP-NOW 超时 / ESP-NOW Timeout

| 现象 Symptom | 可能原因 Cause | 解决方法 Solution |
|---|---|---|
| 发送失败 | 对端未注册 | 确认 `esp_now_add_peer()` 已调用 |
| 发送回调报错 | 对端 MAC 地址错误 | 检查接收器的 MAC 地址 |
| 延迟过高 | WiFi 信道不匹配 | ESP-NOW 要求发送和接收端在同一信道 |
| 通信距离短 | 天线效率低或被遮挡 | 确保天线远离金属；检查天线阻抗匹配 |

---

## 七、RGB 灯效问题 | RGB LED Issues

### 7.1 LED 不亮 / LEDs Not Lighting

| 现象 Symptom | 可能原因 Cause | 解决方法 Solution |
|---|---|---|
| 全部不亮 | 数据线断路 | 检查 GPIO → 第一颗 LED DIN 连线 |
| 全部不亮 | 5V 供电缺失 | 测量 LED VCC 是否有 5V |
| 前几颗亮后面不亮 | 中间某颗 LED 虚焊 | 找到不亮的第一颗，检查其 DOUT 焊接 |

### 7.2 颜色错误 / Wrong Colors

| 现象 Symptom | 可能原因 Cause | 解决方法 Solution |
|---|---|---|
| 全部偏红/绿/蓝 | GRB 顺序错误 | 确认发送数据使用 GRB 顺序（非 RGB） |
| 颜色随机跳变 | 时序不满足 WS2812B 要求 | 检查 RMT 或 SPI 发送频率 |
| 亮度不一致 | 电压沿线路跌落 | 增加供电注入点 |

### 7.3 LED 闪烁 / Flickering

| 现象 Symptom | 可能原因 Cause | 解决方法 Solution |
|---|---|---|
| 随机闪烁 | 电源纹波 | VCC 和 GND 间加 100uF 电解电容 |
| 全部闪烁 | 数据线被干扰 | DIN 串联 330-470 ohm 电阻 |
| 特定 LED 闪烁 | 该 LED 焊接不良 | 补焊该 LED |

---

## 八、旋钮问题 | Knob Issues

### 8.1 电机不转 / Motor Won't Spin

| 现象 Symptom | 可能原因 Cause | 解决方法 Solution |
|---|---|---|
| 完全不动 | TMC6300 未初始化 | 检查 SPI 通信；确认驱动寄存器配置 |
| 完全不动 | 电机相线断开 | 测量 TMC6300 到电机的 U/V/W 连线 |
| 抖动但不转 | FOC 校准失败 | 重新校准电机电气参数（极对数、电阻、电感） |
| 发热严重 | PWM 频率太低或电流设置过高 | 提高 PWM 频率 (>20kHz)；降低运行电流 |
| 只能单向转 | AS5047P 角度方向反 | 交换电机任意两根相线 |

### 8.2 编码器读数异常 / Encoder Wrong Readings

| 现象 Symptom | 可能原因 Cause | 解决方法 Solution |
|---|---|---|
| 角度值固定不变 | AS5047P SPI 通信失败 | 示波器测 SPI 总线；检查 CS/CLK/MOSI/MISO |
| 角度跳变 | 磁铁距离不当 | 调整磁铁高度至 0.5-2.0mm |
| 角度非线性 | 磁铁偏心 | 重新对准磁铁与 AS5047P 中心 |
| 噪声大 | SPI 走线被干扰 | 远离电机驱动线；缩短 SPI 走线 |

### 8.3 LCD 不显示 / LCD Blank

| 现象 Symptom | 可能原因 Cause | 解决方法 Solution |
|---|---|---|
| 完全黑屏 | GC9A01 未初始化 | 检查 SPI 命令序列；确认 RESET 引脚电平 |
| 完全黑屏 | FPC 排线松动 | 重新插拔 FPC 排线，确认锁扣扣紧 |
| 背光亮但无内容 | SPI 数据线断开 | 检查 MOSI（数据）线 |
| 显示花屏 | SPI 时钟太快 | 降低 SPI 时钟到 10MHz 以下 |
| 颜色反转 | 颜色格式设置错误 | GC9A01 使用 RGB565 格式 |

---

## 九、PCB 问题 | PCB Issues

### 9.1 短路 / Short Circuit

| 检查方法 Method | 说明 Description |
|---|---|
| 万用表蜂鸣档 | 测量 VCC/GND 之间，应不导通 |
| 热成像仪 | 短路点会发热 |
| 分割法 | 逐个断开子板/功能区定位短路 |
| 电压注入 | 注入低电压（1V/限流 100mA），用热成像找热点 |

### 9.2 开路 / Open Circuit

| 检查方法 Method | 说明 Description |
|---|---|
| 万用表通断档 | 两点之间应导通 |
| 逐步测量 | 沿着信号线逐段测量 |
| 对比 PCB 走线图 | 与设计文件对比是否有加工缺陷 |

### 9.3 设计错误 / Design Errors

| 常见错误 Common Error | 检查方法 Check Method |
|---|---|
| 走线间距不足 | DRC 检查；目视检查走线间距 |
| 过孔未打或位置偏 | 对照原理图检查网络连通性 |
| 封装与实际元件不匹配 | 焊接前对比元件与 PCB 焊盘 |
| 丝印层错误 | 焊接前核对丝印标识 |

---

## 十、焊接缺陷 | Soldering Defects

### 10.1 虚焊 / Cold Joints

| 现象 Symptom | 特征 Characteristic | 修复 Fix |
|---|---|---|
| 连接不稳定 | 焊点暗淡、粗糙 | 补焊：加助焊剂，重新加热 |
| 功能时好时坏 | 焊点呈颗粒状 | 补焊：加少量新焊锡 |

### 10.2 焊桥 / Solder Bridges

| 现象 Symptom | 特征 Characteristic | 修复 Fix |
|---|---|---|
| 相邻引脚短路 | 引脚间有多余焊锡 | 用吸锡带吸除；或用助焊剂 + 烙铁尖分开 |
| 功能异常 | IC 引脚粘连 | 用放大镜检查，逐一排除 |

### 10.3 立碑 / Tombstoning

| 现象 Symptom | 特征 Characteristic | 修复 Fix |
|---|---|---|
| 贴片元件一端翘起 | 元件一端未接触焊盘 | 用镊子压住 + 烙铁加热；或热风枪重焊 |
| 电路断路 | 只有一端焊接 | 添加助焊剂，用烙铁轻压焊接 |

### 10.4 焊盘脱落 / Lifted Pads

| 现象 Symptom | 特征 Characteristic | 修复 Fix |
|---|---|---|
| 铜箔从 PCB 剥离 | 过热或暴力操作 | 飞线到同网络的最近焊盘 |
| 连接断开 | 焊盘完全脱离 | 刮开绿油露出铜，用焊锡桥接 |

---

## 附录：调试工具速查 | Appendix: Debug Tool Quick Reference

### 万用表常用测量 | Multimeter Common Measurements

| 测量项 Measurement | 档位 Setting | 正常值 Normal Value |
|---|---|---|
| VCC 对 GND 电压 | DCV 20V | 3.25-3.35V (3.3V 轨) |
| USB VBUS | DCV 20V | 4.8-5.2V |
| 电池电压 | DCV 20V | 3.0-4.2V |
| VCC-GND 阻抗 | 电阻 欧姆档 | > 1k ohm（不通电时） |
| VCC-GND 短路 | 蜂鸣档 | 不应蜂鸣 |
| 二极管方向 | 二极管档 | 正向 ~0.6V，反向 OL |

### ESP-IDF 常用调试命令 | ESP-IDF Debug Commands

```bash
# 查看串口输出 | View serial output
idf.py monitor

# 擦除 flash 后重刷 | Erase flash and reflash
idf.py erase-flash
idf.py flash monitor

# 查看 flash 分区 | View flash partitions
esptool.py --port COMx read_flash 0x8000 0x1000 partitions.bin

# 内存使用分析 | Memory usage analysis
idf.py size
idf.py size-components
```

### I2C 设备扫描 | I2C Device Scan

```c
// ESP-IDF I2C 扫描代码片段
#include "driver/i2c.h"

void i2c_scan(i2c_port_t port) {
    for (uint8_t addr = 1; addr < 127; addr++) {
        i2c_cmd_handle_t cmd = i2c_cmd_link_create();
        i2c_master_start(cmd);
        i2c_master_write_byte(cmd, (addr << 1) | I2C_MASTER_WRITE, true);
        i2c_master_stop(cmd);
        esp_err_t ret = i2c_master_cmd_begin(port, cmd, 100 / portTICK_PERIOD_MS);
        i2c_cmd_link_delete(cmd);
        if (ret == ESP_OK) {
            printf("I2C device found at 0x%02X\n", addr);
        }
    }
}
// 预期设备 Expected devices:
// 0x18 — ES8311 (DAC)
// 0x40 — ES7210 (ADC)
```

---

*最后更新 | Last updated: 2026-05-27*
