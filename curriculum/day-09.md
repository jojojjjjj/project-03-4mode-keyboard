# Day 09: FOC旋钮模块——硬件 | FOC Knob Module — Hardware

## 今日目标 | Today's Goals
- 理解无刷直流电机（BLDC）的基本结构和工作原理
- 掌握简化的FOC（磁场定向控制）概念
- 学会使用 TMC6300 电机驱动和 SimpleFOC 库
- 使用 AS5047P 磁编码器实现闭环位置控制

## 知识讲解 | Knowledge Lecture (09:15-10:30)

### 无刷电机基础 | Brushless Motor Basics

FantasyKB 的旋钮使用一颗 **2204 无刷电机**，搭配 TMC6300 驱动和 AS5047P 磁编码器，实现精确的力反馈旋钮。

#### 有刷 vs 无刷电机

```
有刷电机 (DC Motor):              无刷电机 (BLDC):
   +---+                            +---+
   |   | 电刷+换向器               |   | 无电刷
   |   | (机械换向)                |   | (电子换向)
   |   |                           |   |
   | 线圈在转子上                  | 磁铁在转子上
   | 磁铁在定子上                  | 线圈在定子上
   +---+                           +---+
   2根线控制                       3根线控制 (U/V/W)
```

**为什么用无刷电机？**
- 寿命长（无电刷磨损）
- 可精确控制角度和力矩
- 手感丝滑——没有电刷的摩擦
- 适合做力反馈旋钮

#### 三相驱动原理（简化版）

无刷电机有3组线圈（U/V/W），通过按特定顺序通电来旋转磁场：

```
步骤1:  U=正  V=负  W=断开   --> 磁场方向 0度
步骤2:  U=正  V=断开 W=负    --> 磁场方向 60度
步骤3:  U=断开 V=正  W=负    --> 磁场方向 120度
...循环...

FOC控制 = 用数学方法精确计算每个时刻每相需要多少电流
         使磁场始终与转子垂直 -> 最大力矩
```

#### TMC6300 驱动芯片

TMC6300 是一颗专为低电压无刷电机设计的驱动芯片：

| 参数 | 值 |
|---|---|
| 供电电压 | 2-11V |
| 最大电流 | 2A（峰值） |
| 接口 | 6路PWM输入 (HU/HV/HW/LU/LV/LW) |
| 封装 | QFN-20 (3x3mm) |

```
ESP32-S3                TMC6300                2204电机
GPIO12 (PWM) -------> HU ----+
GPIO13 (PWM) -------> HV ----+----> U 相线圈
GPIO14 (PWM) -------> HW ----+
GPIO15 (PWM) -------> LU ----+
GPIO16 (PWM) -------> LV ----+----> V 相线圈
GPIO17 (PWM) -------> LW ----+
                                ----> W 相线圈
```

---

### AS5047P 磁编码器 | AS5047P Magnetic Encoder

磁编码器用于精确测量电机转子的角度位置，是实现闭环控制的关键。

#### 工作原理

```
             AS5047P 芯片
             +--------+
径向磁铁 --> | 霍尔   | --> SPI --> 角度值 (14位, 0-16383)
(安装在    | 传感器  |              = 0.022度分辨率
电机轴上)  | 阵列    |
             +--------+

磁铁随电机旋转 -> AS5047P检测磁场方向 -> 输出精确角度
```

#### AS5047P 参数

| 参数 | 值 |
|---|---|
| 分辨率 | 14位 (16384 步/圈) |
| 精度 | 0.05度 |
| 接口 | SPI (最高10MHz) |
| 供电 | 3.3V 或 5V |
| 刷新率 | 11.25kHz (角度寄存器) |

---

### SimpleFOC 库 | SimpleFOC Library

SimpleFOC 是一个开源的FOC电机控制库，简化了复杂的电机控制算法。

**FantasyKB旋钮使用 PlatformIO + SimpleFOC 开发环境**（与键盘主控的ESP-IDF分开）。

#### SimpleFOC 核心概念

```
            +-- BLDCMotor (电机对象)
            |
SimpleFOC --+-- BLDCDriver3PWM (驱动对象, TMC6300)
            |
            +-- MagneticSensorSPI (编码器对象, AS5047P)

控制流程:
1. 读取编码器角度
2. 计算目标角度与当前角度的误差
3. PID控制器计算需要的力矩
4. FOC算法将力矩转换为三相PWM信号
5. 驱动TMC6300输出电流到电机
```

---

## 动手实验 | Hands-on Lab (10:45-12:00)

### 任务 9.1: TMC6300 接线与基本旋转

**所需材料：**
- TMC6300 模块 x 1
- 2204 无刷电机 x 1
- ESP32-S3 开发板 x 1（或使用PlatformIO支持的任意ESP32板）
- 5V 电源（可为USB 5V）

**接线：**

```
ESP32-S3           TMC6300 Module
GPIO12 ----------> HIN1 (U相高侧)
GPIO13 ----------> HIN2 (V相高侧)
GPIO14 ----------> HIN3 (W相高侧)
GPIO15 ----------> LIN1 (U相低侧)
GPIO16 ----------> LIN2 (V相低侧)
GPIO17 ----------> LIN3 (W相低侧)
3.3V   ----------> VCC
GND    ----------> GND
5V     ----------> VM (电机电源)
                 U ----> 电机黄线
                 V ----> 电机蓝线
                 W ----> 电机绿线
```

**SimpleFOC 开环测试代码（PlatformIO）：**

```cpp
// platformio.ini 配置:
// [env:esp32-s3-devkitc-1]
// platform = espressif32
// board = esp32-s3-devkitc-1
// lib_deps = askuric/Simple FOC@^2.2.3

#include <SimpleFOC.h>

// 定义电机和驱动
BLDCMotor motor = BLDCMotor(7);           // 7极对
BLDCDriver3PWM driver = BLDCDriver3PWM(12, 13, 14, 15, 16, 17);

void setup()
{
    Serial.begin(115200);

    // 配置驱动
    driver.voltage_power_supply = 5.0;  // 供电电压5V
    driver.init();

    // 连接电机和驱动
    motor.linkDriver(&driver);
    motor.voltage_limit = 3.0;  // 限制电压3V（安全）
    motor.init();

    // 开环模式：设置目标角度
    Serial.println("Motor ready! Open-loop control.");
}

void loop()
{
    // 缓慢旋转
    motor.move(motor.shaft_angle + 0.1);
    delay(10);
}
```

**预期结果：**
电机开始缓慢旋转。如果旋转方向反了，交换任意两根电机线。

---

### 任务 9.2: AS5047P 磁编码器读取

**接线：**

```
ESP32-S3           AS5047P Module
GPIO5 (CS)  -----> CS
GPIO6 (SCLK)----> CLK
GPIO7 (MISO)<---- MISO
3.3V       -----> VCC
GND        -----> GND
```

**代码：**

```cpp
#include <SPI.h>
#include <SimpleFOC.h>

// AS5047P SPI 磁编码器
MagneticSensorSPI sensor = MagneticSensorSPI(AS5047_SPI, 5);
// 参数: 芯片类型, CS引脚号

void setup()
{
    Serial.begin(115200);
    sensor.init();
    Serial.println("AS5047P ready!");
}

void loop()
{
    sensor.update();
    float angle = sensor.getAngle();
    Serial.println(angle, 3);  // 打印角度（弧度）
    delay(50);
}
```

**预期结果：**
串口输出当前角度值。用手转动电机轴，角度值应该相应变化。旋转一圈，角度从0增加到约6.28（2*PI）。

---

## 项目实践 | Project Work (13:30-16:30)

### 任务 9.3: 闭环位置控制

**将编码器和电机组合，实现精确的角度定位：**

```cpp
#include <SimpleFOC.h>

BLDCMotor motor = BLDCMotor(7);
BLDCDriver3PWM driver = BLDCDriver3PWM(12, 13, 14, 15, 16, 17);
MagneticSensorSPI sensor = MagneticSensorSPI(AS5047_SPI, 5);

float target_angle = 0;

void setup()
{
    Serial.begin(115200);

    // 初始化编码器
    sensor.init();
    motor.linkSensor(&sensor);

    // 初始化驱动
    driver.voltage_power_supply = 5.0;
    driver.init();
    motor.linkDriver(&driver);

    // 控制参数
    motor.PID_velocity.P = 0.5f;
    motor.PID_velocity.I = 0.01f;
    motor.PID_velocity.D = 0.0f;
    motor.voltage_limit = 3.0f;
    motor.velocity_limit = 10.0f;  // rad/s

    // 角度控制模式
    motor.controller = MotionControlType::angle;
    motor.init();
    motor.initFOC();

    Serial.println("Closed-loop position control ready!");
}

void loop()
{
    motor.loopFOC();
    motor.move(target_angle);

    // 串口控制目标角度
    if (Serial.available()) {
        float cmd = Serial.parseFloat();
        if (cmd != 0) {
            target_angle = cmd;
            Serial.print("Target: ");
            Serial.println(target_angle);
        }
    }
}
```

**测试步骤：**
1. 上传代码，打开串口监视器
2. 输入 `1.57`（约90度），电机应转到90度位置并保持
3. 输入 `3.14`（约180度），电机应转到180度
4. 尝试用手指转动电机——电机应该有"弹回"力（力反馈）

---

### 任务 9.4: 力反馈效果

**FantasyKB旋钮的核心功能——触觉反馈（Haptic Feedback）：**

```cpp
// 模拟刻度手感（Detent）
// 每隔一定角度产生一个"咔嗒"感

float last_detent_angle = 0;
float detent_interval = 0.785f;  // 45度 = PI/4

void loop_with_detents(void)
{
    motor.loopFOC();
    sensor.update();
    float current_angle = sensor.getAngle();

    // 计算最近的刻度位置
    float nearest_detent = round(current_angle / detent_interval) * detent_interval;

    // 将目标设为最近的刻度位置（产生弹回效果）
    motor.move(nearest_detent);
}
```

**不同类型的力反馈效果：**

| 效果 | 参数 | 手感描述 |
|---|---|---|
| 自由旋转 | 无PID，低阻力 | 丝滑无阻力 |
| 刻度定位 | 小interval + 中等PID | 类似旋钮的咔嗒感 |
| 弹簧回中 | 目标=0，中等PID | 松手自动回到中心 |
| 阻尼 | 速度相关的反向力矩 | 转动越快阻力越大 |
| 硬限位 | 角度超过范围时增大PID | 碰到墙壁的感觉 |

---

## 日终总结 | Daily Wrap-up (16:30-17:00)

**今日关键要点：**
1. 无刷电机通过3组线圈按特定顺序通电来旋转，FOC算法精确控制每相电流
2. TMC6300 是低压BLDC驱动器，通过6路PWM控制三相桥
3. AS5047P 磁编码器通过检测磁铁方向精确测量角度（14位分辨率）
4. SimpleFOC 库将复杂的FOC算法封装为简洁的API——初始化+move()即可控制
5. 闭环控制 = 编码器反馈 + PID控制器 + FOC驱动

**明日预告：**
明天为FOC旋钮添加圆形显示屏（GC9A01 + LVGL）和压力传感器（HX711），完成完整的旋钮模块原型。

---

## 今日作业 | Homework

1. **完成实验报告**：电机旋转视频 + 编码器角度读数截图
2. **进阶挑战**：实现稳定的位置控制——电机能在任意角度"停住"并抵抗外力
3. **思考题**：
   - 如果AS5047P的磁铁安装偏心了（不在旋转中心），会有什么影响？
   - FOC控制和开环控制相比，有什么优势？为什么FantasyKB必须用闭环？
   - SimpleFOC的PID参数中，P值过大或过小分别会导致什么现象？
4. **预习 Day 10**：搜索 "GC9A01 圆形LCD" 和 "LVGL 嵌入式GUI"

---

## 常见问题 | FAQ

**Q: 电机不转或抖动？**
A: (1) 检查3根电机线是否正确连接 (2) 确认TMC6300供电正常 (3) 检查PWM引脚是否正确 (4) 尝试增大电压限制 (5) 如果电机发出"嘀嘀"声但不转，可能是PWM频率不对。

**Q: 编码器角度值乱跳？**
A: (1) 确认磁铁已安装在电机轴上 (2) 磁铁与芯片的距离应在1-3mm (3) 确保磁铁极性正确（径向磁化）(4) 检查SPI接线和速度。

**Q: 闭环控制不稳定，电机振荡？**
A: 降低PID参数。先只调P（从0.1开始），逐渐增大到有明显的力反馈但不振荡。I值保持很小（0.01左右），D值一般设为0。

---

## 参考资源 | References

- SimpleFOC 官方文档：https://docs.simplefoc.com/
- SimpleFOC Arduino库：https://github.com/simplefoc/Arduino-FOC
- TMC6300 数据手册（搜索 "TMC6300 datasheet"）
- AS5047P 数据手册（搜索 "AS5047P datasheet"）
- X-Knob 项目（FantasyKB旋钮参考）：https://github.com/SmallPond/X-Knob
- B 站搜索 "SimpleFOC 教程"
- B 站搜索 "FOC 无刷电机 入门"

---

*最后更新 | Last updated: 2026-05-27*
