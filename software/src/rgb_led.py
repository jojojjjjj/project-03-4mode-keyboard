# -*- coding: utf-8 -*-
"""
WS2812B RGB LED 控制模拟模块
WS2812B RGB LED Control Simulation Module

本项目使用大量 WS2812B 可寻址 RGB LED 用于键盘背光和灯效。
本模块模拟 WS2812B 的单线通信协议、颜色处理和灯效动画。

This project uses many WS2812B addressable RGB LEDs for keyboard backlighting
and lighting effects. This module simulates the WS2812B single-wire protocol,
color processing, and lighting animations.

=== WS2812B 协议原理 | WS2812B Protocol Principles ===

WS2812B 使用单线归零码 (NRZ) 协议：
  - 只需要一根数据线即可控制多颗 LED（级联）
  - 每颗 LED 接收 24 位数据 (GRB 顺序，各 8 位)
  - 数据从第一颗 LED 传入，第一颗"截留"自己的 24 位，
    剩余数据通过 DOUT 传给下一颗

  WS2812B uses a single-wire NRZ protocol:
  - Only one data line controls many LEDs (daisy-chain)
  - Each LED receives 24 bits (GRB order, 8 bits each)
  - Data enters first LED, which keeps its 24 bits,
    passing the rest through DOUT to the next LED

=== 位编码时序 | Bit Encoding Timing ===

  逻辑 0: 高电平 0.35us + 低电平 0.80us = 1.15us
  逻辑 1: 高电平 0.70us + 低电平 0.60us = 1.30us
  复位:   低电平 > 50us

  ESP32-S3 通过 RMT (Remote Control) 外设精确生成此时序。
  ESP32-S3 generates this timing via RMT peripheral.

=== 功率预算 | Power Budgeting ===

  每颗 WS2812B 全白最大电流: 3 x 20mA = 60mA
  USB 2.0 最大 500mA，必须做好功率预算！

最后更新 | Last updated: 2026-05-27
"""

import math
import time
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class RGBColor:
    """
    RGB 颜色数据类
    RGB color data class

    属性 Attributes:
        r (int): 红色分量 (0-255) | Red component
        g (int): 绿色分量 (0-255) | Green component
        b (int): 蓝色分量 (0-255) | Blue component
    """
    r: int = 0
    g: int = 0
    b: int = 0

    def to_grb(self) -> Tuple[int, int, int]:
        """
        转换为 WS2812B 的 GRB 数据格式
        Convert to WS2812B GRB data format

        WS2812B 数据顺序是 GRB（绿、红、蓝），不是 RGB！
        WS2812B data order is GRB (Green, Red, Blue), NOT RGB!
        """
        return (self.g, self.r, self.b)

    def current_ma(self) -> float:
        """估算该颜色的电流消耗（毫安）| Estimate current in mA"""
        return (self.r + self.g + self.b) / 255.0 * 20.0

    @staticmethod
    def from_hsv(hue: float, saturation: float = 1.0, value: float = 1.0) -> 'RGBColor':
        """
        从 HSV 颜色空间转换为 RGB
        Convert from HSV to RGB

        参数 Args:
            hue: 色相 (0.0-360.0 度) | Hue in degrees
            saturation: 饱和度 (0.0-1.0) | Saturation
            value: 明度 (0.0-1.0) | Value/Brightness
        """
        hue = hue % 360
        c = value * saturation
        x = c * (1 - abs((hue / 60) % 2 - 1))
        m = value - c

        if hue < 60:
            r, g, b = c, x, 0
        elif hue < 120:
            r, g, b = x, c, 0
        elif hue < 180:
            r, g, b = 0, c, x
        elif hue < 240:
            r, g, b = 0, x, c
        elif hue < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x

        return RGBColor(
            r=int((r + m) * 255),
            g=int((g + m) * 255),
            b=int((b + m) * 255)
        )

    @staticmethod
    def black() -> 'RGBColor':
        return RGBColor(0, 0, 0)

    @staticmethod
    def white() -> 'RGBColor':
        return RGBColor(255, 255, 255)

    @staticmethod
    def red() -> 'RGBColor':
        return RGBColor(255, 0, 0)

    @staticmethod
    def green() -> 'RGBColor':
        return RGBColor(0, 255, 0)

    @staticmethod
    def blue() -> 'RGBColor':
        return RGBColor(0, 0, 255)


# 灯效模式 | Effect modes
EFFECT_MODES = ["static", "breathing", "rainbow", "rainbow_swirl",
                "gradient", "reactive", "wave", "theater_chase"]


class WS2812BProtocol:
    """
    WS2812B 单线协议模拟
    WS2812B single-wire protocol simulation

    模拟 ESP32-S3 RMT 外设生成 WS2812B 时序信号。
    Simulates ESP32-S3 RMT generating WS2812B timing.

    时序参数（纳秒）Timing parameters (nanoseconds):
      T0H = 350ns (逻辑 0 高电平)  T0L = 800ns (逻辑 0 低电平)
      T1H = 700ns (逻辑 1 高电平)  T1L = 600ns (逻辑 1 低电平)
      T_RESET > 50000ns (>50us)
    """

    @staticmethod
    def encode_bit(bit: bool) -> List[Tuple[int, int]]:
        """
        编码一个位为 RMT 脉冲序列
        Encode one bit as RMT pulse sequence

        返回 Returns:
            [(level, duration_ns), ...] — 2 个脉冲
        """
        if bit:
            return [(1, 700), (0, 600)]  # 逻辑 1
        else:
            return [(1, 350), (0, 800)]  # 逻辑 0

    @staticmethod
    def encode_byte(value: int) -> List[Tuple[int, int]]:
        """
        编码一个字节为 WS2812B 脉冲序列（MSB 优先）
        Encode one byte as WS2812B pulses (MSB first)

        返回 Returns:
            16 个脉冲
        """
        pulses = []
        for i in range(7, -1, -1):
            bit = bool(value & (1 << i))
            pulses.extend(WS2812BProtocol.encode_bit(bit))
        return pulses

    @staticmethod
    def encode_color(color: RGBColor) -> List[Tuple[int, int]]:
        """
        编码一个 GRB 颜色值（24 位）为脉冲序列
        Encode one GRB color (24 bits) as pulse sequence

        注意顺序：先绿(G)，再红(R)，最后蓝(B)
        Note: Green first, then Red, then Blue

        返回 Returns:
            48 个脉冲
        """
        g, r, b = color.to_grb()
        pulses = []
        pulses.extend(WS2812BProtocol.encode_byte(g))
        pulses.extend(WS2812BProtocol.encode_byte(r))
        pulses.extend(WS2812BProtocol.encode_byte(b))
        return pulses

    @staticmethod
    def calculate_transfer_time(num_leds: int) -> float:
        """
        计算 N 颗 LED 传输时间（微秒）
        Calculate transfer time for N LEDs (microseconds)

        每颗 LED: 24 bits x ~1.25us = 30us + 50us RESET
        """
        return num_leds * 24 * 1.25 + 50


class RGBLed:
    """
    RGB LED 管理类
    RGB LED Manager

    管理 WS2812B 灯珠的颜色和灯效。
    Manages colors and effects for WS2812B LEDs.
    """

    def __init__(self, config: dict):
        """
        参数 Args:
            config: 键盘配置字典 | Keyboard config dict
        """
        rgb_cfg = config.get("rgb", {})
        self.enabled: bool = rgb_cfg.get("enabled", True)
        self.type: str = rgb_cfg.get("type", "WS2812B")
        self.num_leds: int = rgb_cfg.get("count", 70)
        self.data_pin: str = rgb_cfg.get("data_pin", "GPIO2")
        self.max_brightness: int = rgb_cfg.get("max_brightness", 128)
        self.effect_mode: str = rgb_cfg.get("default_mode", "rainbow")

        # LED 颜色缓冲区 | LED color buffer
        self._colors: List[RGBColor] = [RGBColor.black() for _ in range(self.num_leds)]
        self._brightness: float = self.max_brightness / 255.0
        self._frame: int = 0
        self._key_times: List[float] = [0.0] * self.num_leds

    def set_color(self, index: int, color: RGBColor) -> None:
        """设置指定 LED 的颜色 | Set color of specified LED"""
        if 0 <= index < self.num_leds:
            self._colors[index] = color

    def set_all(self, color: RGBColor) -> None:
        """设置所有 LED 为同一颜色 | Set all LEDs to same color"""
        for i in range(self.num_leds):
            self._colors[i] = color

    def get_color(self, index: int) -> RGBColor:
        """获取指定 LED 的颜色 | Get color of specified LED"""
        if 0 <= index < self.num_leds:
            return self._colors[index]
        return RGBColor.black()

    def set_brightness(self, brightness: int) -> None:
        """设置全局亮度 | Set global brightness (0-255)"""
        self._brightness = max(0.0, min(1.0, brightness / 255.0))

    def set_effect(self, mode: str) -> None:
        """设置灯效模式 | Set effect mode"""
        if mode in EFFECT_MODES:
            self.effect_mode = mode

    def trigger_key(self, index: int) -> None:
        """触发反应式灯效 | Trigger reactive effect"""
        if 0 <= index < self.num_leds:
            self._key_times[index] = time.time()

    def update_effect(self) -> None:
        """更新一帧灯效动画 | Update one frame of effect animation"""
        self._frame += 1
        now = time.time()

        if self.effect_mode == "static":
            pass

        elif self.effect_mode == "breathing":
            # 呼吸灯：正弦函数平滑变化
            brightness = (math.sin(self._frame * 0.05) + 1) / 2
            val = int(brightness * 255 * self._brightness)
            self.set_all(RGBColor(val, 0, val // 2))

        elif self.effect_mode == "rainbow":
            # 彩虹：每颗 LED 不同色相
            for i in range(self.num_leds):
                hue = (i * 360 / self.num_leds + self._frame * 2) % 360
                self._colors[i] = RGBColor.from_hsv(hue, 1.0, self._brightness)

        elif self.effect_mode == "rainbow_swirl":
            for i in range(self.num_leds):
                hue = (i * 360 / self.num_leds + self._frame * 3) % 360
                self._colors[i] = RGBColor.from_hsv(hue, 1.0, self._brightness)

        elif self.effect_mode == "gradient":
            for i in range(self.num_leds):
                ratio = i / max(1, self.num_leds - 1)
                self._colors[i] = RGBColor(
                    r=int(255 * (1 - ratio) * self._brightness),
                    g=0,
                    b=int(255 * ratio * self._brightness)
                )

        elif self.effect_mode == "reactive":
            # 反应式：按键后亮起然后渐灭
            for i in range(self.num_leds):
                elapsed = now - self._key_times[i]
                if elapsed < 0.5:
                    fade = max(0, 1.0 - elapsed / 0.5)
                    self._colors[i] = RGBColor.from_hsv(
                        (i * 360 / self.num_leds) % 360, 1.0,
                        fade * self._brightness)
                else:
                    self._colors[i] = RGBColor.black()

        elif self.effect_mode == "wave":
            for i in range(self.num_leds):
                wave = (math.sin(self._frame * 0.1 + i * 0.3) + 1) / 2
                hue = (i * 360 / self.num_leds) % 360
                self._colors[i] = RGBColor.from_hsv(hue, 1.0, wave * self._brightness)

        elif self.effect_mode == "theater_chase":
            for i in range(self.num_leds):
                if (i + self._frame // 3) % 3 == 0:
                    hue = (self._frame * 5 + i * 10) % 360
                    self._colors[i] = RGBColor.from_hsv(hue, 1.0, self._brightness)
                else:
                    self._colors[i] = RGBColor.black()

    def to_grb_bytes(self) -> bytes:
        """将所有 LED 颜色转换为 GRB 字节序列 | Convert all colors to GRB bytes"""
        data = bytearray()
        for color in self._colors:
            g, r, b = color.to_grb()
            data.extend([g & 0xFF, r & 0xFF, b & 0xFF])
        return bytes(data)

    def calculate_power(self) -> dict:
        """
        计算功率消耗 | Calculate power consumption

        功率计算 Power calculation:
        总电流 = sum(每颗LED电流)
        每颗LED电流 = (R+G+B)/255 × 20mA × brightness
        功率 = 5V × 电流
        """
        total_current_ma = sum(c.current_ma() for c in self._colors) * self._brightness
        power_w = 5.0 * total_current_ma / 1000.0
        return {
            "total_current_ma": round(total_current_ma, 1),
            "power_watts": round(power_w, 2),
            "num_leds": self.num_leds,
            "brightness_pct": round(self._brightness * 100, 1),
            "usb_safe": total_current_ma < 500,
        }

    def get_display_string(self) -> str:
        """生成 LED 状态可视化字符串 | Generate visual LED status string"""
        cols = min(self.num_leds, 20)
        rows = (self.num_leds + cols - 1) // cols
        lines = []
        for row in range(rows):
            line = ""
            for col in range(cols):
                idx = row * cols + col
                if idx < self.num_leds:
                    c = self._colors[idx]
                    if c.r == 0 and c.g == 0 and c.b == 0:
                        line += " [OFF] "
                    elif c.r > 200 and c.g < 50 and c.b < 50:
                        line += " [RED] "
                    elif c.r < 50 and c.g > 200 and c.b < 50:
                        line += " [GRN] "
                    elif c.r < 50 and c.g < 50 and c.b > 200:
                        line += " [BLU] "
                    else:
                        line += f"[{c.r:02X}{c.g:02X}{c.b:02X}]"
            lines.append(line)
        return "\n".join(lines)

    def __repr__(self) -> str:
        return (f"RGBLed(count={self.num_leds}, mode={self.effect_mode}, "
                f"brightness={self._brightness:.0%})")
