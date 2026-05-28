# -*- coding: utf-8 -*-
"""
FOC (磁场定向控制) 无刷电机控制模拟模块
FOC (Field Oriented Control) Brushless Motor Control Simulation Module

本项目使用 TMC6300 无刷电机驱动芯片控制 2204 电机，
配合 AS5047P 磁编码器实现精确的旋钮力度反馈。
本模块模拟 FOC 算法的核心数学变换，帮助学生理解电机控制原理。

This project uses TMC6300 brushless motor driver to control a 2204 motor,
combined with AS5047P magnetic encoder for precise knob force feedback.
This module simulates the core mathematical transforms of FOC algorithm
to help students understand motor control principles.

=== FOC 简介 | FOC Overview ===

FOC (Field Oriented Control，磁场定向控制) 是无刷电机最高效的控制方法：
  - 将三相交流电机的问题转换为直流电机的问题
  - 通过数学变换将三相电流分解为两个独立的控制量
  - 实现精确的转矩和磁通控制
  - 常用于机器人关节、无人机、电动工具

FOC is the most efficient control method for brushless motors:
- Converts 3-phase AC motor problem into DC motor problem
- Decomposes 3-phase current into two independent control quantities
- Achieves precise torque and flux control

=== FOC 核心数学变换 | FOC Core Mathematical Transforms ===

FOC 控制需要三个关键变换：

1. Clarke 变换 (Clarke Transform):
   将三相静止坐标系 (a, b, c) 转换为两相静止坐标系 (alpha, beta)
   3-phase stationary frame → 2-phase stationary frame

2. Park 变换 (Park Transform):
   将两相静止坐标系 (alpha, beta) 转换为旋转坐标系 (d, q)
   2-phase stationary frame → rotating frame (d=flux, q=torque)

3. 逆变换 (Inverse Transform):
   将控制量从旋转坐标系转换回三相电流
   d,q → alpha,beta → a,b,c

=== 为什么要变换？Why Transform? ===

在旋转坐标系 (d, q) 中：
  - d 轴 (Direct): 控制磁通，对于表贴式永磁电机设为 0
  - q 轴 (Quadrature): 控制转矩，直接正比于电机力矩

这样就可以像控制直流电机一样控制无刷电机了！

In the rotating frame (d, q):
  - d-axis: controls flux, set to 0 for surface-mounted PMSM
  - q-axis: controls torque, directly proportional to motor torque

=== TMC6300 简介 | TMC6300 Overview ===

TMC6300 是 Trinamic 的低压三相无刷直流电机驱动器：
  - 电源电压: 2-11V
  - 输出电流: 最大 2A
  - 接口: SPI 或 STEP/DIR
  - 内置 MOSFET 半桥
  - QFN-20 封装

最后更新 | Last updated: 2026-05-27
"""

import math
from typing import Tuple, List
from dataclasses import dataclass


# === PID 控制器 | PID Controller ===

@dataclass
class PIDConfig:
    """
    PID 控制器参数
    PID Controller parameters

    Kp: 比例增益 — 响应速度 | Proportional gain — response speed
    Ki: 积分增益 — 消除稳态误差 | Integral gain — eliminate steady-state error
    Kd: 微分增益 — 抑制超调 | Derivative gain — reduce overshoot
    output_limit: 输出限幅 | Output limit
    """
    Kp: float = 0.5
    Ki: float = 0.01
    Kd: float = 0.001
    output_limit: float = 1.0


class PIDController:
    """
    PID 控制器模拟
    PID Controller Simulation

    PID 控制是工业中最常用的闭环控制算法：
    output = Kp * error + Ki * integral(error) + Kd * d(error)/dt

    PID is the most common closed-loop control algorithm in industry.
    """

    def __init__(self, config: PIDConfig = None):
        self.config = config or PIDConfig()
        self._integral: float = 0.0
        self._prev_error: float = 0.0
        self._prev_time: float = 0.0

    def compute(self, setpoint: float, measurement: float, dt: float = 0.001) -> float:
        """
        计算 PID 输出
        Compute PID output

        参数 Args:
            setpoint: 目标值 | Target value
            measurement: 当前测量值 | Current measurement
            dt: 时间步长（秒）| Time step (seconds)

        返回 Returns:
            float: 控制输出 | Control output
        """
        error = setpoint - measurement

        # 比例项 P: 当前误差 × 增益
        # Proportional: current error × gain
        p_term = self.config.Kp * error

        # 积分项 I: 累计误差 × 增益
        # Integral: accumulated error × gain
        self._integral += error * dt
        # 积分限幅（防止积分饱和）| Anti-windup
        i_limit = self.config.output_limit / max(self.config.Ki, 0.001)
        self._integral = max(-i_limit, min(i_limit, self._integral))
        i_term = self.config.Ki * self._integral

        # 微分项 D: 误差变化率 × 增益
        # Derivative: error rate of change × gain
        d_term = 0.0
        if dt > 0:
            d_term = self.config.Kd * (error - self._prev_error) / dt

        self._prev_error = error

        output = p_term + i_term + d_term
        return max(-self.config.output_limit, min(self.config.output_limit, output))

    def reset(self) -> None:
        """重置 PID 状态 | Reset PID state"""
        self._integral = 0.0
        self._prev_error = 0.0


# === 数学变换 | Mathematical Transforms ===

def clarke_transform(ia: float, ib: float, ic: float) -> Tuple[float, float]:
    """
    Clarke 变换（克拉克变换）
    Clarke Transform

    将三相静止坐标系 (a, b, c) 转换为两相静止坐标系 (alpha, beta)

    3-phase stationary (a,b,c) → 2-phase stationary (alpha, beta)

    数学公式 Mathematical formula:
      alpha = ia
      beta  = (ia + 2*ib) / sqrt(3)

    简化版（假设 ia + ib + ic = 0，即中性点不接地时成立）：
    Simplified (assuming ia + ib + ic = 0):
      alpha = ia
      beta  = (ia/sqrt(3) + 2*ib/sqrt(3))

    参数 Args:
        ia, ib, ic: 三相电流 | 3-phase currents

    返回 Returns:
        (alpha, beta): 两相静止坐标系值 | 2-phase stationary frame values
    """
    alpha = ia
    beta = (ia + 2 * ib) / math.sqrt(3)
    return (alpha, beta)


def inverse_clarke_transform(alpha: float, beta: float) -> Tuple[float, float, float]:
    """
    逆 Clarke 变换
    Inverse Clarke Transform

    将两相静止坐标系 (alpha, beta) 转换回三相 (a, b, c)
    Convert 2-phase stationary back to 3-phase

    参数 Args:
        alpha, beta: 两相值 | 2-phase values

    返回 Returns:
        (ia, ib, ic): 三相电流 | 3-phase currents
    """
    ia = alpha
    ib = (-alpha + math.sqrt(3) * beta) / 2
    ic = (-alpha - math.sqrt(3) * beta) / 2
    return (ia, ib, ic)


def park_transform(alpha: float, beta: float, theta: float) -> Tuple[float, float]:
    """
    Park 变换（帕克变换）
    Park Transform

    将两相静止坐标系 (alpha, beta) 转换为旋转坐标系 (d, q)

    2-phase stationary (alpha,beta) → rotating frame (d,q)

    数学公式 Mathematical formula:
      d =  alpha * cos(theta) + beta * sin(theta)
      q = -alpha * sin(theta) + beta * cos(theta)

    物理意义 Physical meaning:
      d (direct): 磁通方向分量 | Flux axis component
      q (quadrature): 转矩方向分量 | Torque axis component

    theta 是转子电角度（从 AS5047P 获取并转换为电角度）

    参数 Args:
        alpha, beta: 两相静止坐标值 | 2-phase stationary values
        theta: 电角度（弧度）| Electrical angle (radians)

    返回 Returns:
        (d, q): 旋转坐标系值 | Rotating frame values
    """
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    d = alpha * cos_t + beta * sin_t
    q = -alpha * sin_t + beta * cos_t
    return (d, q)


def inverse_park_transform(d: float, q: float, theta: float) -> Tuple[float, float]:
    """
    逆 Park 变换
    Inverse Park Transform

    将旋转坐标系 (d, q) 转换回两相静止坐标系 (alpha, beta)
    Convert rotating frame back to 2-phase stationary

    参数 Args:
        d, q: 旋转坐标系值 | Rotating frame values
        theta: 电角度（弧度）| Electrical angle (radians)

    返回 Returns:
        (alpha, beta): 两相静止坐标值
    """
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    alpha = d * cos_t - q * sin_t
    beta = d * sin_t + q * cos_t
    return (alpha, beta)


# === TMC6300 驱动模拟 | TMC6300 Driver Simulation ===

class TMC6300:
    """
    TMC6300 无刷电机驱动器模拟
    TMC6300 Brushless Motor Driver Simulation

    模拟 TMC6300 的 SPI 接口和三相 PWM 输出控制。
    Simulates TMC6300 SPI interface and 3-phase PWM output control.
    """

    def __init__(self, config: dict):
        motor_cfg = config.get("motor", config.get("foc", {}))
        self.enabled: bool = motor_cfg.get("enabled", True)
        self.spi_freq_mhz: float = motor_cfg.get("spi_freq_mhz", 1.0)

        # 电机参数 | Motor parameters
        self.pole_pairs: int = motor_cfg.get("pole_pairs", 7)  # 2204 电机极对数
        self.resistance: float = motor_cfg.get("resistance", 10.0)  # 相电阻 (ohm)
        self.inductance: float = motor_cfg.get("inductance", 0.001)  # 相电感 (H)

        # 输出状态 | Output state
        self._pwm_u: float = 0.0  # U 相 PWM 占空比
        self._pwm_v: float = 0.0  # V 相 PWM 占空比
        self._pwm_w: float = 0.0  # W 相 PWM 占空比

    def set_pwm(self, u: float, v: float, w: float) -> None:
        """
        设置三相 PWM 占空比
        Set 3-phase PWM duty cycles

        参数 Args:
            u, v, w: 占空比 (-1.0 到 +1.0) | Duty cycles (-1.0 to +1.0)

        TMC6300 内部有 3 个半桥，通过 PWM 控制每个半桥的通断时间。
        正值表示正向电流，负值表示反向电流。
        """
        self._pwm_u = max(-1.0, min(1.0, u))
        self._pwm_v = max(-1.0, min(1.0, v))
        self._pwm_w = max(-1.0, min(1.0, w))

    def get_pwm(self) -> Tuple[float, float, float]:
        """获取当前 PWM 状态 | Get current PWM state"""
        return (self._pwm_u, self._pwm_v, self._pwm_w)

    def mechanical_to_electrical_angle(self, mech_angle_rad: float) -> float:
        """
        将机械角度转换为电角度
        Convert mechanical angle to electrical angle

        电角度 = 机械角度 × 极对数
        Electrical angle = mechanical angle × pole_pairs

        因为电机有多对磁极，转子旋转一圈产生多圈电周期。
        """
        return (mech_angle_rad * self.pole_pairs) % (2 * math.pi)


# === FOC 控制器 | FOC Controller ===

class FOController:
    """
    FOC 磁场定向控制器
    FOC Field Oriented Controller

    完整的 FOC 控制循环：
    1. 读取 AS5047P 角度 → 机械角度
    2. 转换为电角度
    3. 测量三相电流 (ia, ib, ic)
    4. Clarke 变换 → (alpha, beta)
    5. Park 变换 → (d, q)
    6. PID 控制 → 目标 d, q 电压
    7. 逆 Park 变换 → (alpha, beta)
    8. 逆 Clarke 变换 / SVPWM → 三相 PWM
    9. 输出到 TMC6300

    Complete FOC control loop:
    1. Read AS5047P angle → mechanical angle
    2. Convert to electrical angle
    3. Measure 3-phase currents (ia, ib, ic)
    4. Clarke transform → (alpha, beta)
    5. Park transform → (d, q)
    6. PID control → target d, q voltages
    7. Inverse Park → (alpha, beta)
    8. Inverse Clarke / SVPWM → 3-phase PWM
    9. Output to TMC6300
    """

    def __init__(self, config: dict):
        self.driver = TMC6300(config)

        # PID 控制器 | PID controllers
        self.pid_d = PIDController(PIDConfig(Kp=0.5, Ki=0.01, Kd=0.001))
        self.pid_q = PIDController(PIDConfig(Kp=0.5, Ki=0.01, Kd=0.001))

        # 目标值 | Targets
        self.target_torque: float = 0.0  # 目标力矩 | Target torque
        self.target_d: float = 0.0       # d 轴目标（磁通，通常为 0）

        # 当前状态 | Current state
        self._angle_rad: float = 0.0     # 机械角度 | Mechanical angle
        self._velocity: float = 0.0      # 角速度 | Angular velocity

    def set_target_torque(self, torque: float) -> None:
        """
        设置目标力矩
        Set target torque

        参数 Args:
            torque: 力矩值 (-1.0 到 +1.0) | Torque value

        正值 = 顺时针旋转，负值 = 逆时针旋转
        Positive = CW, Negative = CCW
        """
        self.target_torque = max(-1.0, min(1.0, torque))

    def update(self, mech_angle_rad: float,
               ia: float = 0.0, ib: float = 0.0, ic: float = 0.0,
               dt: float = 0.001) -> Tuple[float, float, float]:
        """
        执行一次 FOC 控制循环
        Execute one FOC control loop iteration

        参数 Args:
            mech_angle_rad: 机械角度（弧度）| Mechanical angle (rad)
            ia, ib, ic: 三相电流测量值 | 3-phase current measurements
            dt: 时间步长 | Time step

        返回 Returns:
            (u, v, w): 三相 PWM 占空比 | 3-phase PWM duty cycles
        """
        self._angle_rad = mech_angle_rad

        # 步骤 1: 机械角度 → 电角度
        # Step 1: Mechanical angle → electrical angle
        elec_angle = self.driver.mechanical_to_electrical_angle(mech_angle_rad)

        # 步骤 2: Clarke 变换
        # Step 2: Clarke transform
        alpha, beta = clarke_transform(ia, ib, ic)

        # 步骤 3: Park 变换
        # Step 3: Park transform
        d, q = park_transform(alpha, beta, elec_angle)

        # 步骤 4: PID 控制
        # Step 4: PID control
        # d 轴控制磁通（目标为 0）| d-axis controls flux (target 0)
        # q 轴控制转矩 | q-axis controls torque
        vd = self.pid_d.compute(self.target_d, d, dt)
        vq = self.pid_q.compute(self.target_torque, q, dt)

        # 步骤 5: 逆 Park 变换
        # Step 5: Inverse Park transform
        alpha_out, beta_out = inverse_park_transform(vd, vq, elec_angle)

        # 步骤 6: 逆 Clarke 变换 → 三相
        # Step 6: Inverse Clarke → 3-phase
        u, v, w = inverse_clarke_transform(alpha_out, beta_out)

        # 步骤 7: 输出到驱动器
        # Step 7: Output to driver
        self.driver.set_pwm(u, v, w)

        return (u, v, w)

    def explain_foc(self) -> str:
        """生成 FOC 算法说明 | Generate FOC algorithm explanation"""
        return (
            "=== FOC (Field Oriented Control) ===\n"
            "\n"
            "Control loop:\n"
            "1. Read encoder angle (AS5047P)\n"
            "2. mech_angle * pole_pairs = elec_angle\n"
            "3. Measure Ia, Ib, Ic\n"
            "4. Clarke: (a,b,c) -> (alpha,beta)\n"
            "5. Park:   (alpha,beta) -> (d,q)\n"
            "6. PID on d (flux=0) and q (torque)\n"
            "7. Inv Park:   (d,q) -> (alpha,beta)\n"
            "8. Inv Clarke: (alpha,beta) -> (a,b,c)\n"
            "9. PWM to TMC6300\n"
            "\n"
            f"Pole pairs: {self.driver.pole_pairs}\n"
            f"Target torque: {self.target_torque:.2f}\n"
        )

    def __repr__(self) -> str:
        return (f"FOC(torque={self.target_torque:.2f}, "
                f"poles={self.driver.pole_pairs})")
