# -*- coding: utf-8 -*-
"""
AS5047P 磁编码器模拟模块
AS5047P Magnetic Encoder Simulation Module

本项目使用 AS5047P 磁编码器检测旋钮的精确旋转角度，用于 FOC 电机控制。
AS5047P 通过 SPI 接口与 ESP32-S3 通信，提供 14 位 (16384 级) 角度分辨率。
本模块模拟 SPI 通信、角度计算和速度估计。

This project uses the AS5047P magnetic encoder to detect precise knob rotation
angle for FOC motor control. AS5047P communicates via SPI with ESP32-S3,
providing 14-bit (16384 levels) angular resolution.
This module simulates SPI communication, angle calculation, and velocity estimation.

=== AS5047P 简介 | AS5047P Overview ===

AS5047P 是一款 14 位高分辨率磁旋转编码器：
  - 分辨率: 14 位 = 16,384 个位置/圈
  - 精度: ±0.05°
  - 接口: SPI (最高 10MHz), Mode 1 (CPOL=0, CPHA=1)
  - 支持绝对角度模式和增量正交输出
  - 内置偶校验 CRC

=== 工作原理 | Working Principle ===

  1. 径向磁化磁铁安装在电机轴顶端
  2. AS5047P 位于磁铁正下方 (距离 0.5-2.0mm)
  3. 霍尔效应传感器阵列检测磁场方向
  4. 内部 DSP 计算出精确角度
  5. 通过 SPI 输出 14 位角度值

=== SPI 通信格式 | SPI Communication Format ===

  AS5047P 使用 16 位 SPI 帧，"发命令→下次读结果"模式:
  常用寄存器: 0x3FFF = 补偿后角度 (14 位)

=== 正交输出 | Quadrature Output ===

  A/B 两路方波信号，相位差 90 度。
  正向: A 上升沿时 B=LOW
  反向: A 上升沿时 B=HIGH

最后更新 | Last updated: 2026-05-27
"""

import math
import time
import random
from typing import List, Tuple


# AS5047P 常量 | AS5047P Constants
AS5047P_RESOLUTION = 16384  # 2^14
AS5047P_DEG_PER_BIT = 360.0 / AS5047P_RESOLUTION  # ~0.02197 deg/bit

AS5047P_REG = {
    "NOP": 0x0000,
    "ERRFL": 0x0001,
    "DIAAGC": 0x3FFC,
    "MAG": 0x3FFD,
    "ANGLEUNC": 0x3FFE,
    "ANGLECOM": 0x3FFF,
}


def calculate_parity(value: int) -> int:
    """
    计算偶校验位 | Calculate even parity bit
    AS5047P 使用偶校验: 数据中 1 的个数 + parity = 偶数
    """
    parity = 0
    for i in range(16):
        if value & (1 << i):
            parity ^= 1
    return parity


class AS5047P:
    """
    AS5047P 磁编码器模拟类
    AS5047P Magnetic Encoder Simulator

    模拟 SPI 通信、角度读取、速度计算和正交输出。
    Simulates SPI communication, angle reading, velocity calculation
    and quadrature output.
    """

    def __init__(self, config: dict):
        enc_cfg = config.get("encoder", config.get("magnetic_encoder", {}))
        self.enabled: bool = enc_cfg.get("enabled", True)
        self.spi_freq_mhz: float = enc_cfg.get("spi_freq_mhz", 5.0)

        # 模拟角度 | Simulated angle
        self._angle_deg: float = 0.0

        # 角度历史（速度计算用）| Angle history for velocity calc
        self._angle_history: List[Tuple[float, float]] = []
        self._max_history: int = 10

        # 噪声 | Noise
        self._noise_lsb: int = enc_cfg.get("noise_lsb", 1)

        # 正交输出 | Quadrature output
        self._quad_a: bool = False
        self._quad_b: bool = False
        self._quad_resolution: int = enc_cfg.get("quad_resolution", 2048)

        # 速度和加速度 | Velocity and acceleration
        self._velocity_dps: float = 0.0
        self._acceleration_dps2: float = 0.0

    # --- 角度控制（测试用）| Angle Control (testing) ---

    def set_angle(self, degrees: float) -> None:
        """设置模拟角度 | Set simulated angle (degrees)"""
        self._angle_deg = degrees % 360.0
        now = time.time()
        self._angle_history.append((now, self._angle_deg))
        if len(self._angle_history) > self._max_history:
            self._angle_history.pop(0)
        self._update_velocity()
        self._update_quadrature()

    def rotate_by(self, delta_degrees: float) -> None:
        """旋转指定角度 | Rotate by delta degrees"""
        self.set_angle(self._angle_deg + delta_degrees)

    # --- SPI 通信 | SPI Communication ---

    def spi_read_angle(self) -> int:
        """
        模拟 SPI 读取补偿后角度 (0x3FFF)
        Simulate SPI read of compensated angle

        返回 Returns:
            int: 14 位角度值 (0-16383)

        AS5047P SPI 读取需要两步：
        1. 发送读命令 0x3FFF
        2. 发送 NOP 0x0000，此时返回角度数据
        """
        raw = int(self._angle_deg / 360.0 * AS5047P_RESOLUTION) % AS5047P_RESOLUTION
        noise = random.randint(-self._noise_lsb, self._noise_lsb)
        raw = max(0, min(AS5047P_RESOLUTION - 1, raw + noise))
        return raw

    def spi_read_register(self, address: int) -> int:
        """模拟 SPI 读取寄存器 | Simulate SPI register read"""
        if address in (0x3FFF, 0x3FFE):
            return self.spi_read_angle()
        elif address == 0x3FFD:
            return 8000  # 模拟正常磁场 | Simulate normal field
        elif address == 0x3FFC:
            return 0x8000  # 正常状态 | Normal status
        elif address == 0x0001:
            return 0x0000  # 无错误 | No error
        return 0x0000

    # --- 角度转换 | Angle Conversion ---

    def get_angle_degrees(self) -> float:
        """获取当前角度（度）| Get angle in degrees"""
        return self._angle_deg

    def get_angle_radians(self) -> float:
        """获取当前角度（弧度）| Get angle in radians"""
        return math.radians(self._angle_deg)

    @staticmethod
    def raw_to_degrees(raw: int) -> float:
        """14 位原始值 → 角度（度）| 14-bit raw → degrees"""
        return (raw & 0x3FFF) * AS5047P_DEG_PER_BIT

    @staticmethod
    def raw_to_radians(raw: int) -> float:
        """14 位原始值 → 弧度 | 14-bit raw → radians"""
        return math.radians((raw & 0x3FFF) * AS5047P_DEG_PER_BIT)

    # --- 正交输出 | Quadrature Output ---

    def _update_quadrature(self) -> None:
        """
        更新 A/B 相正交输出

        正交编码器原理 Quadrature encoder principle:
        A 和 B 相位差 90 度。通过 A/B 边沿的先后顺序判断方向。
        正转: A 先于 B    反转: B 先于 A
        """
        quad_pos = int(self._angle_deg / 360.0 * self._quad_resolution * 4)
        quad_pos %= (self._quad_resolution * 4)
        self._quad_a = bool(quad_pos & 0x01)
        self._quad_b = bool(quad_pos & 0x02)

    def get_quadrature(self) -> Tuple[bool, bool]:
        """获取 A/B 相状态 | Get A/B phase state"""
        return (self._quad_a, self._quad_b)

    # --- 速度和加速度 | Velocity & Acceleration ---

    def _update_velocity(self) -> None:
        """
        使用有限差分法计算角速度和角加速度
        Calculate velocity and acceleration via finite difference
        """
        if len(self._angle_history) < 2:
            self._velocity_dps = 0.0
            self._acceleration_dps2 = 0.0
            return

        t0, a0 = self._angle_history[-2]
        t1, a1 = self._angle_history[-1]
        dt = t1 - t0
        if dt < 1e-6:
            return

        da = a1 - a0
        if da > 180:
            da -= 360
        elif da < -180:
            da += 360

        new_velocity = da / dt
        if abs(new_velocity - self._velocity_dps) < 10000:
            self._acceleration_dps2 = (new_velocity - self._velocity_dps) / dt
        self._velocity_dps = new_velocity

    def get_velocity_dps(self) -> float:
        """获取角速度（度/秒）| Get velocity in degrees/second"""
        return self._velocity_dps

    def get_velocity_rpm(self) -> float:
        """获取转速 (RPM) | Get speed in RPM"""
        return self._velocity_dps / 6.0

    def get_acceleration(self) -> float:
        """获取角加速度（度/秒^2）| Get acceleration in deg/s^2"""
        return self._acceleration_dps2

    def explain_spi(self) -> str:
        """生成 SPI 通信说明 | Generate SPI explanation"""
        return (
            f"=== AS5047P SPI 通信 | SPI Communication ===\n"
            f"\n"
            f"SPI 频率: {self.spi_freq_mhz} MHz (max 10MHz)\n"
            f"SPI 模式: Mode 1 (CPOL=0, CPHA=1)\n"
            f"分辨率: 14 bit = {AS5047P_RESOLUTION} positions/rev\n"
            f"精度: {AS5047P_DEG_PER_BIT:.4f} deg/bit\n"
            f"\n"
            f"读取角度步骤:\n"
            f"  1. CS=LOW → 发送 0x3FFF (16 CLK)\n"
            f"  2. CS=HIGH\n"
            f"  3. CS=LOW → 发送 0x0000 NOP (16 CLK) → 接收角度\n"
            f"  4. CS=HIGH\n"
        )

    def __repr__(self) -> str:
        return (f"AS5047P(angle={self._angle_deg:.1f}deg, "
                f"vel={self._velocity_dps:.1f}dps)")
