# -*- coding: utf-8 -*-
"""
TMC6300 FOC (磁场定向控制) 无刷电机控制模拟
TMC6300 FOC (Field Oriented Control) Brushless Motor Control Simulation

FOC 控制简化原理：
1. 读取电机角度 (AS5047P)
2. 计算 3相电流的目标值 (逆Park变换)
3. 通过 SVPWM 生成 PWM 信号
4. TMC6300 驱动 3相桥输出电流到电机

Clarke 变换 (3相 → 2相):
  Iα = Ia
  Iβ = (Ia + 2*Ib) / √3

Park 变换 (旋转坐标系 → 静止坐标系):
  Id = Iα*cos(θ) + Iβ*sin(θ)
  Iq = -Iα*sin(θ) + Iβ*cos(θ)

逆Park 变换 (静止坐标系 → 旋转坐标系):
  Vα = Vd*cos(θ) - Vq*sin(θ)
  Vβ = Vd*sin(θ) + Vq*cos(θ)

PID 控制器：
  角度环 -> 速度目标 -> 速度环 -> Iq目标 -> 电流环 -> 电压输出

TMC6300:
- 3相半桥驱动器 (6个MOSFET)
- 输入: 3对PWM信号 (UH/UL, VH/VL, WH/WL)
- 电源: 5-12V
- 电流: 峰值2A

SimpleFOC 库提供上述所有变换和控制器的实现

Last updated: 2026-05-27
"""

import math
from typing import Tuple


class FOCMotorController:
    """
    FOC 电机控制器模拟

    用法：
        motor = FOCMotorController(config)
        motor.set_target_angle(90.0)
        motor.update()
        print(f"当前角度: {motor.current_angle:.1f}°")
    """

    def __init__(self, config: dict):
        motor_cfg = config.get("motor", {})
        self.pole_pairs: int = motor_cfg.get("pole_pairs", 7)
        self.voltage_limit: float = motor_cfg.get("voltage_limit", 5.0)
        self.pid_p: float = motor_cfg.get("pid_p", 0.5)
        self.pid_i: float = motor_cfg.get("pid_i", 0.01)
        self.pid_d: float = motor_cfg.get("pid_d", 0.0)

        # 电机状态
        self.target_angle: float = 0.0
        self.current_angle: float = 0.0
        self.velocity: float = 0.0

        # PID 积分项
        self._integral: float = 0.0
        self._prev_error: float = 0.0

    def set_target_angle(self, angle: float) -> None:
        """设置目标角度（度）"""
        self.target_angle = angle % 360

    def clarke_transform(self, ia: float, ib: float, ic: float) -> Tuple[float, float]:
        """
        Clarke 变换: 3相(a,b,c) -> 2相(α,β)

        假设 Ia + Ib + Ic = 0 (星形连接)
        """
        ialpha = ia
        ibeta = (ia + 2 * ib) / math.sqrt(3)
        return (ialpha, ibeta)

    def park_transform(self, ialpha: float, ibeta: float, theta: float) -> Tuple[float, float]:
        """
        Park 变换: (α,β) -> (d,q) 旋转坐标系

        theta: 电角度（弧度）
        """
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        id_val = ialpha * cos_t + ibeta * sin_t
        iq_val = -ialpha * sin_t + ibeta * cos_t
        return (id_val, iq_val)

    def inverse_park(self, vd: float, vq: float, theta: float) -> Tuple[float, float]:
        """
        逆Park 变换: (d,q) -> (α,β)
        """
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        valpha = vd * cos_t - vq * sin_t
        vbeta = vd * sin_t + vq * cos_t
        return (valpha, vbeta)

    def svpwm(self, valpha: float, vbeta: float) -> Tuple[float, float, float]:
        """
        SVPWM (空间矢量PWM): (α,β) -> 3相占空比 (U, V, W)

        将2相电压转换为3相PWM占空比 (0.0 - 1.0)
        """
        # 简化SVPWM
        va = valpha
        vb = -0.5 * valpha + (math.sqrt(3) / 2) * vbeta
        vc = -0.5 * valpha - (math.sqrt(3) / 2) * vbeta

        # 归一化到 [0, 1]
        max_v = max(abs(va), abs(vb), abs(vc), 0.001)
        scale = self.voltage_limit / max_v if max_v > self.voltage_limit else 1.0

        duty_u = 0.5 + 0.5 * va * scale / self.voltage_limit
        duty_v = 0.5 + 0.5 * vb * scale / self.voltage_limit
        duty_w = 0.5 + 0.5 * vc * scale / self.voltage_limit

        return (max(0, min(1, duty_u)), max(0, min(1, duty_v)), max(0, min(1, duty_w)))

    def pid_update(self, error: float, dt: float = 0.001) -> float:
        """PID控制器"""
        self._integral += error * dt
        self._integral = max(-10, min(10, self._integral))  # 积分限幅
        derivative = (error - self._prev_error) / dt if dt > 0 else 0
        self._prev_error = error
        return self.pid_p * error + self.pid_i * self._integral + self.pid_d * derivative

    def update(self) -> None:
        """FOC控制循环（一步）"""
        error = self.target_angle - self.current_angle
        if error > 180:
            error -= 360
        elif error < -180:
            error += 360

        voltage_q = self.pid_update(error)
        voltage_d = 0  # FOC中Id通常设为0（最大扭矩）

        theta_e = math.radians(self.current_angle * self.pole_pairs)
        valpha, vbeta = self.inverse_park(voltage_d, voltage_q, theta_e)
        duty_u, duty_v, duty_w = self.svpwm(valpha, vbeta)

        # 模拟电机运动
        self.velocity = voltage_q * 10  # 简化
        self.current_angle += self.velocity * 0.001
        self.current_angle %= 360

    def get_foc_pipeline(self) -> str:
        """FOC控制管道示意图（教学用）"""
        return (
            "FOC 控制管道:\n"
            f"  目标角度: {self.target_angle:.1f}°\n"
            f"  当前角度: {self.current_angle:.1f}°\n"
            f"  误差: {self.target_angle - self.current_angle:.1f}°\n"
            "  ┌───────────────────────────────────┐\n"
            "  │ PID(角度误差) → Vq                 │\n"
            "  │ 逆Park(Vd=0, Vq) → (Vα, Vβ)       │\n"
            "  │ SVPWM(Vα, Vβ) → (PWM_U, PWM_V, PWM_W)│\n"
            "  │ TMC6300 → 3相电流 → 电机转动       │\n"
            "  │ AS5047P → 反馈角度 → 下一循环      │\n"
            "  └───────────────────────────────────┘\n"
        )

    def __repr__(self) -> str:
        return f"FOCMotor(target={self.target_angle:.1f}°, current={self.current_angle:.1f}°)"
