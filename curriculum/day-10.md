# Day 10: FOC旋钮模块——显示与力反馈 | FOC Knob Module — Display & Haptic Feedback

## 今日目标 | Today's Goals
- 驱动 GC9A01 圆形LCD显示屏（SPI接口）
- 了解 LVGL 嵌入式GUI框架的基本使用
- 在圆形屏幕上显示层指示器和动画效果
- 实现 HX711 压力传感器 + 应变计的压力检测
- 将显示、力反馈、压力传感集成为完整的旋钮原型

## 知识讲解 | Knowledge Lecture (09:15-10:30)

### GC9A01 圆形LCD | GC9A01 Round LCD

FantasyKB 的旋钮顶部安装了一颗 **GC9A01 驱动的1.28寸圆形LCD**，用于显示当前层号、模式、旋钮值等信息。

#### GC9A01 参数

| 参数 | 值 |
|---|---|
| 尺寸 | 1.28 英寸 |
| 分辨率 | 240 x 240 像素 |
| 形状 | 圆形 |
| 驱动IC | GC9A01 |
| 接口 | SPI (最高约60MHz) |
| 颜色 | 65K色 (RGB565, 16位) |
| 供电 | 3.3V |

#### SPI 接线

```
ESP32-S3 (旋钮主控)       GC9A01 模块
GPIO35 (MOSI)  ------->  DIN (SDA)
GPIO36 (SCLK)  ------->  CLK
GPIO37 (CS)    ------->  CS
GPIO38 (DC)    ------->  DC (数据/命令选择)
GPIO39 (RST)   ------->  RST (复位)
3.3V           ------->  VCC
GND            ------->  BLK (背光，接GND=常亮)
```

**为什么用SPI而不是I2C？**
- 240x240像素 @ 16位色 = 115,200字节/帧
- I2C 400kHz传输一帧需要约2.3秒——太慢
- SPI 30MHz传输一帧仅需约3ms——流畅

---

### LVGL 嵌入式GUI框架 | LVGL GUI Framework

LVGL（Light and Versatile Graphics Library）是最流行的开源嵌入式GUI库。

#### LVGL 架构

```
+----------------------------------+
|         应用层 Application       |  <-- 你写的UI代码
+----------------------------------+
|         LVGL 核心 Core           |  <-- 控件、布局、动画
+----------------------------------+
|         显示驱动 Display Driver  |  <-- GC9A01 SPI 驱动
+----------------------------------+
|         输入驱动 Input Driver    |  <-- 编码器旋转
+----------------------------------+
```

#### 常用控件

| 控件 | 用途 | FantasyKB应用 |
|---|---|---|
| `lv_label` | 文本显示 | 层号、模式名称 |
| `lv_arc` | 弧形进度条 | 旋钮值指示器 |
| `lv_img` | 图片显示 | 自定义图标 |
| `lv_bar` | 条形进度条 | 电量/音量 |
| `lv_spinner` | 旋转动画 | 加载/状态指示 |

---

### HX711 压力传感器 | HX711 Pressure Sensor

FantasyKB旋钮使用 **HX711 + 应变计** 检测按下旋钮的压力。

#### 工作原理

```
应变计 (Strain Gauge)
+---+---+---+---+
|   |   |   |   |    <-- 电阻网格，粘贴在旋钮底座上
+---+---+---+---+
按下旋钮 -> 底座微小形变 -> 应变计电阻变化

HX711 (24位ADC + 放大器)
应变计 -> 惠斯通电桥 -> HX711 -> SPI/UART -> ESP32-S3
```

#### 压力检测应用

- **轻按**：选择/确认
- **重按**：切换模式
- **持续按压**：触发特殊功能
- 也可以用来检测旋钮是否被触摸（非接触式检测）

---

## 动手实验 | Hands-on Lab (10:45-12:00)

### 任务 10.1: GC9A01 基础显示

**使用 TFT_eSPI 库快速驱动GC9A01（PlatformIO）：**

```cpp
// platformio.ini:
// lib_deps = bodmer/TFT_eSPI@^2.5.43
// build_flags = -DUSER_SETUP_LOADED=1 -DGC9A01_DRIVER=1
//              -DTFT_WIDTH=240 -DTFT_HEIGHT=240
//              -DTFT_MOSI=35 -DTFT_SCLK=36 -DTFT_CS=37
//              -DTFT_DC=38 -DTFT_RST=39

#include <TFT_eSPI.h>
#include <SPI.h>

TFT_eSPI tft = TFT_eSPI(240, 240);

void setup()
{
    tft.init();
    tft.setRotation(0);
    tft.fillScreen(TFT_BLACK);

    // 显示文字
    tft.setTextColor(TFT_WHITE, TFT_BLACK);
    tft.setTextSize(3);
    tft.drawString("FantasyKB", 30, 100);
    tft.setTextSize(2);
    tft.drawString("Layer: 0", 60, 140);

    // 画圆弧（模拟旋钮指示器）
    tft.drawCircleArc(120, 120, 100, 0, 270, TFT_CYAN, TFT_CYAN);
}

void loop() {}
```

**预期结果：**
圆形屏幕显示 "FantasyKB" 文字和一段青色圆弧。

---

### 任务 10.2: LVGL 圆形界面

**LVGL 基础设置代码：**

```cpp
#include <lvgl.h>
#include <TFT_eSPI.h>

TFT_eSPI tft = TFT_eSPI(240, 240);
static lv_disp_draw_buf_t draw_buf;
static lv_color_t buf[240 * 10];  // 缓冲区

// LVGL 显示刷新回调
void my_disp_flush(lv_disp_drv_t *disp, const lv_area_t *area,
                    lv_color_t *color_p)
{
    uint32_t w = area->x2 - area->x1 + 1;
    uint32_t h = area->y2 - area->y1 + 1;
    tft.startWrite();
    tft.setAddrWindow(area->x1, area->y1, w, h);
    tft.pushColors((uint16_t *)&color_p->full, w * h, true);
    tft.endWrite();
    lv_disp_flush_ready(disp);
}

void lv_init_display(void)
{
    tft.init();
    tft.setRotation(0);

    lv_init();
    lv_disp_draw_buf_init(&draw_buf, buf, NULL, 240 * 10);

    static lv_disp_drv_t disp_drv;
    lv_disp_drv_init(&disp_drv);
    disp_drv.hor_res = 240;
    disp_drv.ver_res = 240;
    disp_drv.flush_cb = my_disp_flush;
    disp_drv.draw_buf = &draw_buf;
    lv_disp_drv_register(&disp_drv);
}

// 创建旋钮UI
void create_knob_ui(void)
{
    // 圆弧指示器
    lv_obj_t *arc = lv_arc_create(lv_scr_act());
    lv_obj_set_size(arc, 200, 200);
    lv_obj_center(arc);
    lv_arc_set_range(arc, 0, 100);
    lv_arc_set_value(arc, 50);
    lv_arc_set_rotation(arc, 270);

    // 中间文字
    lv_obj_t *label = lv_label_create(lv_scr_act());
    lv_label_set_text(label, "50%");
    lv_obj_center(label);

    // 模式标签
    lv_obj_t *mode_label = lv_label_create(lv_scr_act());
    lv_label_set_text(mode_label, "BLE");
    lv_obj_align(mode_label, LV_ALIGN_TOP_RIGHT, -10, 10);
}
```

---

## 项目实践 | Project Work (13:30-16:30)

### 任务 10.3: 力反馈图案模式

**将Day 9的电机控制与显示结合：**

```cpp
// 力反馈模式枚举
typedef enum {
    HAPTIC_FREE = 0,      // 自由旋转
    HAPTIC_DETENTS,       // 刻度感
    HAPTIC_SPRING,        // 弹簧回中
    HAPTIC_BOUNDARY,      // 边界限制
} haptic_mode_t;

// 在屏幕上显示当前模式
void update_display(haptic_mode_t mode, float value)
{
    static char buf[32];

    // 更新圆弧
    lv_arc_set_value(arc, (int)(value * 100));

    // 更新数值文字
    snprintf(buf, sizeof(buf), "%.0f%%", value * 100);
    lv_label_set_text(value_label, buf);

    // 更新模式文字
    const char *mode_names[] = {"Free", "Detents", "Spring", "Boundary"};
    lv_label_set_text(mode_label, mode_names[mode]);
}

// 力反馈循环
void haptic_task(void *arg)
{
    haptic_mode_t current_mode = HAPTIC_DETENTS;

    while (1) {
        motor.loopFOC();
        sensor.update();
        float angle = sensor.getAngle();

        switch (current_mode) {
            case HAPTIC_FREE:
                // 无力反馈
                motor.move(angle);  // 跟随当前位置
                break;

            case HAPTIC_DETENTS: {
                // 刻度感
                float interval = 0.785f;  // 45度
                float nearest = round(angle / interval) * interval;
                motor.move(nearest);
                break;
            }

            case HAPTIC_SPRING:
                // 弹簧回中
                motor.move(0);
                break;

            case HAPTIC_BOUNDARY: {
                // 边界限制 (-PI to PI)
                float clamped = constrain(angle, -M_PI, M_PI);
                motor.move(clamped);
                break;
            }
        }

        // 更新显示
        float normalized = angle / (2 * M_PI);
        update_display(current_mode, normalized);

        // 检测压力传感器切换模式
        if (pressure_pressed()) {
            current_mode = (haptic_mode_t)((current_mode + 1) % 4);
            delay(300);  // 防抖
        }

        delay(1);
    }
}
```

---

### 任务 10.4: HX711 压力传感器集成

**HX711 接线与代码：**

```
ESP32-S3           HX711 Module
GPIO40 --------->  SCK (时钟)
GPIO41 <---------  DOUT (数据)
3.3V   --------->  VCC
GND    --------->  GND

HX711 的 A+/A- 连接应变计（通常已焊好在模块上）
```

```cpp
#include <HX711.h>

HX711 scale;

void pressure_init(void)
{
    scale.begin(41, 40);  // DOUT, SCK
    scale.set_scale(2280.f);  // 校准系数（需要实际校准）
    scale.tare();              // 去皮（零点校准）
}

bool pressure_pressed(void)
{
    if (scale.is_ready()) {
        float val = scale.get_units(3);  // 3次采样平均
        return val > 5000;  // 阈值
    }
    return false;
}

float pressure_value(void)
{
    return scale.get_units(5);  // 5次采样平均，返回压力值
}

// 压力等级检测
typedef enum {
    PRESSURE_NONE = 0,
    PRESSURE_LIGHT,    // 轻触
    PRESSURE_MEDIUM,   // 中等
    PRESSURE_HEAVY,    // 重压
} pressure_level_t;

pressure_level_t get_pressure_level(void)
{
    float val = pressure_value();
    if (val < 5000) return PRESSURE_NONE;
    if (val < 20000) return PRESSURE_LIGHT;
    if (val < 50000) return PRESSURE_MEDIUM;
    return PRESSURE_HEAVY;
}
```

---

### 任务 10.5: 完整旋钮原型集成

**将所有模块整合到一起：**

```cpp
// 主程序结构
void setup()
{
    Serial.begin(115200);

    // 1. 初始化编码器
    sensor.init();

    // 2. 初始化电机驱动
    driver.voltage_power_supply = 5.0;
    driver.init();
    motor.linkDriver(&driver);
    motor.linkSensor(&sensor);
    motor.controller = MotionControlType::angle;
    motor.PID_velocity.P = 0.5f;
    motor.PID_velocity.I = 0.01f;
    motor.voltage_limit = 3.0f;
    motor.init();
    motor.initFOC();

    // 3. 初始化显示
    lv_init_display();
    create_knob_ui();

    // 4. 初始化压力传感器
    pressure_init();

    Serial.println("FantasyKB Knob Module ready!");
}

void loop()
{
    // 主循环已在haptic_task中处理
    // LVGL定时器
    lv_timer_handler();
    delay(5);
}
```

---

## 日终总结 | Daily Wrap-up (16:30-17:00)

**今日关键要点：**
1. GC9A01 是240x240圆形LCD，通过高速SPI驱动，适合显示旋钮状态
2. LVGL 是强大的嵌入式GUI框架，提供丰富的控件和动画效果
3. HX711 + 应变计实现压力检测，区分轻按/重按/长按
4. 完整旋钮 = 电机控制 + 编码器反馈 + 显示 + 压力检测

**阶段二回顾（Day 6-10）：**
- Day 6: 蓝牙BLE键盘
- Day 7: WiFi + ESP-NOW 四模切换
- Day 8: WS2812B RGB灯效
- Day 9: FOC无刷电机 + AS5047P编码器
- Day 10: GC9A01显示 + LVGL + HX711压力传感

**明日预告：**
明天进入阶段三——PCB设计！你将使用嘉立创EDA开始设计FantasyKB的12块PCB，从EDA工具入门开始。

---

## 今日作业 | Homework

1. **提交旋钮原型演示视频**：展示力反馈效果 + 屏幕显示 + 压力响应
2. **提交阶段二进度汇报**（500字以上）：
   - 5天中最大的技术挑战是什么？如何解决的？
   - 无线通信和电机控制的心得体会
   - 对项目最终成品的期待
3. **思考题**：
   - FantasyKB 的旋钮模块为什么使用单独的主控，而不是和键盘共用ESP32-S3？
   - 如果GC9A01的刷新率只有10fps，用户体验会有什么影响？
   - LVGL的显示缓冲区大小如何选择？缓冲区越大越好吗？
4. **预习 Day 11**：注册嘉立创EDA账号 https://lceda.cn/

---

## 常见问题 | FAQ

**Q: GC9A01 屏幕白屏不显示？**
A: (1) 确认SPI接线正确（尤其是CS和DC）(2) 检查RST引脚是否连接 (3) 确认背光控制（BLK接GND=常亮）(4) 尝试降低SPI时钟频率。

**Q: LVGL 编译报错内存不足？**
A: LVGL需要较多RAM。ESP32-S3有512KB SRAM，应该够用。检查是否分配了过大的缓冲区，尝试减小缓冲区大小或使用PSRAM。

**Q: HX711 读数不稳定？**
A: (1) 应变计对温度敏感，需要预热 (2) 增加采样次数（取平均值）(3) 确保接线牢固 (4) 避免电机驱动的高频噪声干扰。

**Q: 电机控制和LVGL刷新冲突？**
A: 确保电机FOC循环运行在高优先级任务中（delay(1)），LVGL的lv_timer_handler()放在低优先级。SimpleFOC的loopFOC()需要至少10kHz的调用频率。

---

## 参考资源 | References

- GC9A01 数据手册（搜索 "GC9A01 datasheet"）
- LVGL 官方文档：https://docs.lvgl.io/
- LVGL 圆形表盘示例：https://docs.lvgl.io/master/widgets/extra/meter.html
- TFT_eSPI 库：https://github.com/Bodmer/TFT_eSPI
- HX711 Arduino库：https://github.com/bogde/HX711
- X-Knob 项目（FantasyKB旋钮核心参考）：https://github.com/SmallPond/X-Knob
- SmartKnob 项目（力反馈旋钮先驱）：https://github.com/scottbez1/smartknob
- B 站搜索 "GC9A01 圆形屏 教程"
- B 站搜索 "LVGL 入门教程"

---

*最后更新 | Last updated: 2026-05-27*
