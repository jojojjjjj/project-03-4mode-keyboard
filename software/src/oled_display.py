# -*- coding: utf-8 -*-
"""
GC9A01 圆形 LCD 驱动模拟模块
GC9A01 Round LCD Driver Simulation Module

本项目使用 GC9A01 驱动的 1.28 寸圆形彩色 LCD (240x240 RGB565)，
安装在旋钮模块顶部，显示键盘状态、旋钮信息、动画等。
本模块模拟 SPI 通信和帧缓冲操作，帮助学生理解 LCD 显示原理。

This project uses a GC9A01-driven 1.28" round color LCD (240x240 RGB565),
mounted on top of the knob module to display keyboard status, knob info, etc.
This module simulates SPI communication and framebuffer operations to help
students understand LCD display principles.

=== GC9A01 简介 | GC9A01 Overview ===

GC9A01 是一款 262K 色 TFT LCD 驱动 IC，常用于圆形表盘显示：
  - 分辨率 Resolution: 240 x 240 (圆形有效区域)
  - 颜色深度 Color depth: RGB565 (16-bit, 65536 色)
  - 接口 Interface: SPI (最高 50MHz)
  - 帧缓冲 Frame buffer: 需要外部提供 (240*240*2 = 115,200 字节)
  - 背光驱动 Backlight driver: SY7200AABC 升压驱动

=== SPI 通信协议 | SPI Communication Protocol ===

GC9A01 使用标准 SPI 通信，增加了一个 DC (Data/Command) 引脚：
  - DC = LOW  → 传输的是命令字节 | Command byte
  - DC = HIGH → 传输的是数据字节 | Data byte

  SPI transfer sequence:
  CS → LOW
  DC → LOW  → Send command byte
  DC → HIGH → Send data byte(s)
  CS → HIGH

=== RGB565 颜色格式 | RGB565 Color Format ===

  16 位颜色分布 16-bit color layout:
  RRRRR GGGGGG BBBBB
  43210 543210 43210

  红色 Red:   5 位 (0-31)   → 高 5 位 (bit 15-11)
  绿色 Green: 6 位 (0-63)   → 中 6 位 (bit 10-5)
  蓝色 Blue:  5 位 (0-31)   → 低 5 位 (bit 4-0)

  为什么绿色多 1 位？因为人眼对绿色最敏感。
  Why does green get 1 extra bit? Human eyes are most sensitive to green.

=== 帧缓冲概念 | Framebuffer Concept ===

帧缓冲是一块内存区域，存储屏幕上每个像素的颜色值。
MCU 修改帧缓冲的内容，然后通过 SPI 将整个缓冲区发送到 LCD。

A framebuffer is a memory area storing the color value of each pixel.
The MCU modifies the framebuffer content, then sends the entire buffer
to the LCD via SPI.

  帧缓冲大小 Framebuffer size: 240 x 240 x 2 bytes = 115,200 bytes
  ESP32-S3 的 PSRAM 容量足够存储此缓冲区

=== LVGL 控件层级 | LVGL Widget Hierarchy ===

LVGL (Light and Versatile Graphics Library) 是嵌入式系统最流行的 GUI 库。
控件以树形层级组织：Screen → Container → Widget
本模块实现了简化版的 LVGL 控件系统用于教学。

最后更新 | Last updated: 2026-05-27
"""

import math
from typing import List, Optional, Tuple


# === RGB565 颜色常量 | RGB565 Color Constants ===
RGB565_WHITE  = 0xFFFF
RGB565_BLACK  = 0x0000
RGB565_RED    = 0xF800
RGB565_GREEN  = 0x07E0
RGB565_BLUE   = 0x001F
RGB565_YELLOW = 0xFFE0
RGB565_CYAN   = 0x07FF
RGB565_MAGENTA = 0xF81F
RGB565_ORANGE = 0xFD20


# === RGB565 颜色工具 | RGB565 Color Utilities ===

def rgb_to_rgb565(r: int, g: int, b: int) -> int:
    """
    将 RGB888 (各 8 位) 转换为 RGB565 (16 位)
    Convert RGB888 (8-bit each) to RGB565 (16-bit)

    参数 Args:
        r: 红色 0-255 | Red 0-255
        g: 绿色 0-255 | Green 0-255
        b: 蓝色 0-255 | Blue 0-255

    返回 Returns:
        int: RGB565 值 (0-65535)

    转换公式 Conversion formula:
        R5 = R8 >> 3  (取高 5 位 | take top 5 bits)
        G6 = G8 >> 2  (取高 6 位 | take top 6 bits)
        B5 = B8 >> 3  (取高 5 位 | take top 5 bits)
        RGB565 = (R5 << 11) | (G6 << 5) | B5
    """
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


def rgb565_to_rgb(color565: int) -> Tuple[int, int, int]:
    """
    将 RGB565 (16 位) 转换回 RGB888
    Convert RGB565 (16-bit) back to RGB888

    参数 Args:
        color565: RGB565 值

    返回 Returns:
        tuple: (r, g, b) 各 0-255

    注意：转换回 8 位时有信息损失（低位被补零或近似值）
    Note: Converting back to 8-bit has information loss
    """
    r5 = (color565 >> 11) & 0x1F
    g6 = (color565 >> 5) & 0x3F
    b5 = color565 & 0x1F
    r = (r5 << 3) | (r5 >> 2)
    g = (g6 << 2) | (g6 >> 4)
    b = (b5 << 3) | (b5 >> 2)
    return (r, g, b)


# === GC9A01 命令定义 | GC9A01 Command Definitions ===
GC9A01_CMD = {
    "NOP": 0x00,             # 空操作 | No operation
    "SWRESET": 0x01,         # 软件复位 | Software reset
    "SLPOUT": 0x11,          # 退出睡眠 | Sleep out
    "DISPON": 0x29,          # 开启显示 | Display on
    "CASET": 0x2A,           # 设置列地址 | Column address set
    "RASET": 0x2B,           # 设置行地址 | Row address set
    "RAMWR": 0x2C,           # 写显存 | Memory write
    "MADCTL": 0x36,          # 内存数据访问控制 | Memory data access control
    "COLMOD": 0x3A,          # 像素格式设置 | Pixel format set
}


# === 简化 LVGL 式控件层级 | Simplified LVGL-style Widget Hierarchy ===

class Widget:
    """
    控件基类 | Widget base class

    简化版的 LVGL 控件模型。在真实的嵌入式 GUI 库中，控件以树形层级组织：
    - 每个控件有一个父控件
    - 每个控件可以有多个子控件
    - 坐标相对于父控件
    - 绘制时从根到叶遍历

    Simplified LVGL widget model. In real embedded GUI libraries,
    widgets are organized in a tree hierarchy:
    - Each widget has a parent
    - Each widget can have children
    - Coordinates are relative to parent
    - Drawing traverses from root to leaves
    """

    def __init__(self, x: int = 0, y: int = 0, width: int = 0, height: int = 0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.children: List['Widget'] = []
        self.parent: Optional['Widget'] = None
        self.visible: bool = True
        self.bg_color: Optional[int] = None

    def add_child(self, child: 'Widget') -> None:
        """添加子控件 | Add child widget"""
        child.parent = self
        self.children.append(child)

    def get_absolute_pos(self) -> Tuple[int, int]:
        """
        获取相对于屏幕的绝对坐标（递归累加父控件偏移）
        Get absolute position relative to screen
        """
        if self.parent is None:
            return (self.x, self.y)
        px, py = self.parent.get_absolute_pos()
        return (px + self.x, py + self.y)

    def draw(self, fb: 'GC9A01Display') -> None:
        """绘制自身及所有子控件 | Draw self and all children"""
        if not self.visible:
            return
        self._draw_self(fb)
        for child in self.children:
            child.draw(fb)

    def _draw_self(self, fb: 'GC9A01Display') -> None:
        """子类重写此方法实现自定义绘制 | Override for custom drawing"""
        if self.bg_color is not None:
            abs_x, abs_y = self.get_absolute_pos()
            fb.draw_filled_rect(abs_x, abs_y, self.width, self.height, self.bg_color)


class Label(Widget):
    """文字标签控件 | Text label widget"""

    def __init__(self, x: int = 0, y: int = 0, text: str = "",
                 color: int = RGB565_WHITE, scale: int = 1):
        super().__init__(x, y, len(text) * 6 * scale, 8 * scale)
        self.text = text
        self.color = color
        self.font_scale = scale

    def _draw_self(self, fb: 'GC9A01Display') -> None:
        super()._draw_self(fb)
        abs_x, abs_y = self.get_absolute_pos()
        fb.draw_text(abs_x, abs_y, self.text, self.color, self.font_scale)


class CircleWidget(Widget):
    """圆形控件 | Circle widget"""

    def __init__(self, cx: int, cy: int, radius: int,
                 color: int = RGB565_WHITE, filled: bool = True):
        super().__init__(cx - radius, cy - radius, radius * 2, radius * 2)
        self.cx = cx
        self.cy = cy
        self.radius = radius
        self.color = color
        self.filled = filled

    def _draw_self(self, fb: 'GC9A01Display') -> None:
        abs_x, abs_y = self.get_absolute_pos()
        acx = abs_x + self.radius
        acy = abs_y + self.radius
        if self.filled:
            fb.draw_filled_circle(acx, acy, self.radius, self.color)
        else:
            fb.draw_circle(acx, acy, self.radius, self.color)


class ArcWidget(Widget):
    """
    弧形控件（常用于表盘/旋钮显示）
    Arc widget (commonly used for dial/knob display)
    """

    def __init__(self, cx: int, cy: int, radius: int, thickness: int = 4,
                 start_angle: float = 0, end_angle: float = 360,
                 color: int = RGB565_CYAN):
        super().__init__(cx - radius - thickness, cy - radius - thickness,
                         (radius + thickness) * 2, (radius + thickness) * 2)
        self.cx = cx
        self.cy = cy
        self.radius = radius
        self.thickness = thickness
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.color = color

    def _draw_self(self, fb: 'GC9A01Display') -> None:
        abs_x, abs_y = self.get_absolute_pos()
        acx = abs_x + self.radius + self.thickness
        acy = abs_y + self.radius + self.thickness
        fb.draw_arc(acx, acy, self.radius, self.thickness,
                    self.start_angle, self.end_angle, self.color)


# === GC9A01 显示驱动 | GC9A01 Display Driver ===

class GC9A01Display:
    """
    GC9A01 圆形 LCD 驱动模拟类
    GC9A01 Round LCD Driver Simulator

    模拟 GC9A01 LCD 驱动器，包括帧缓冲管理和基础绘图。

    SPI 接口：CS, SCLK, MOSI(SDA), DC(数据/命令), RES(复位)
    DC=0 发送命令, DC=1 发送数据
    """

    def __init__(self, config: dict):
        """
        参数 Args:
            config: 键盘配置字典 | Keyboard config dict
        """
        lcd_cfg = config.get("display", config.get("lcd", {}))

        self.enabled: bool = lcd_cfg.get("enabled", True)
        self.type: str = lcd_cfg.get("type", "GC9A01")
        self.width: int = lcd_cfg.get("width", 240)
        self.height: int = lcd_cfg.get("height", 240)
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        self.radius = self.width // 2

        # SPI 引脚配置
        self.spi_freq_mhz: int = lcd_cfg.get("spi_freq_mhz", 40)
        self.spi_clk: str = lcd_cfg.get("spi_clk", "GPIO36")
        self.spi_mosi: str = lcd_cfg.get("spi_mosi", "GPIO35")
        self.cs_pin: str = lcd_cfg.get("cs_pin", "GPIO37")
        self.dc_pin: str = lcd_cfg.get("dc_pin", "GPIO38")
        self.rst_pin: str = lcd_cfg.get("rst_pin", "GPIO39")
        self.bl_pin: str = lcd_cfg.get("bl_pin", "GPIO40")

        # 帧缓冲区 (RGB565)，每个像素 2 字节
        # Framebuffer (RGB565), 2 bytes per pixel
        self.framebuffer: List[int] = [RGB565_BLACK] * (self.width * self.height)

        # 控件根节点 | Widget root node
        self.root_widget = Widget(0, 0, self.width, self.height)

        # 初始化命令日志 | Init command log
        self._init_log: List[str] = []

    # --- 基础绘图 Basic Drawing ---

    def _is_in_circle(self, x: int, y: int) -> bool:
        """检查坐标是否在圆形显示区域内 | Check if within circular display area"""
        dx = x - self.center_x
        dy = y - self.center_y
        return (dx * dx + dy * dy) <= (self.radius * self.radius)

    def _set_pixel(self, x: int, y: int, color: int) -> None:
        """
        设置帧缓冲中的像素颜色（内部方法）
        Set pixel color in framebuffer (internal)

        参数 Args:
            x, y: 坐标 | Coordinates
            color: RGB565 颜色值 | RGB565 color value
        """
        if 0 <= x < self.width and 0 <= y < self.height and self._is_in_circle(x, y):
            self.framebuffer[y * self.width + x] = color

    def draw_pixel(self, x: int, y: int, color: int = RGB565_WHITE) -> None:
        """
        绘制单个像素
        Draw single pixel

        参数 Args:
            x, y: 坐标 | Coordinates
            color: RGB565 颜色 | RGB565 color
        """
        self._set_pixel(x, y, color)

    def fill(self, color: int = RGB565_BLACK) -> None:
        """
        用指定颜色填充整个屏幕
        Fill entire screen with specified color
        """
        self.framebuffer = [color] * (self.width * self.height)

    def draw_filled_rect(self, x: int, y: int, w: int, h: int,
                         color: int = RGB565_WHITE) -> None:
        """
        绘制填充矩形 | Draw filled rectangle

        参数 Args:
            x, y: 左上角坐标 | Top-left corner
            w, h: 宽度和高度 | Width and height
            color: RGB565 颜色
        """
        for dy in range(h):
            for dx in range(w):
                self._set_pixel(x + dx, y + dy, color)

    def draw_line(self, x0: int, y0: int, x1: int, y1: int,
                  color: int = RGB565_WHITE) -> None:
        """
        使用 Bresenham 算法绘制直线
        Draw line using Bresenham's algorithm

        Bresenham 算法是计算机图形学中最经典的画线算法，
        只使用整数加减运算，非常适合嵌入式系统。

        Bresenham's algorithm is the classic line-drawing algorithm,
        using only integer addition/subtraction, ideal for embedded systems.
        """
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            self._set_pixel(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def draw_circle(self, cx: int, cy: int, r: int,
                    color: int = RGB565_WHITE) -> None:
        """
        使用中点圆算法绘制圆形边框
        Draw circle outline using midpoint circle algorithm

        利用圆的 8 路对称性，每次计算只需画 8 个对称点。
        Exploits 8-way symmetry of circles, only need to compute 8 points per step.
        """
        x, y, d = r, 0, 1 - r
        while x >= y:
            for ddx, ddy in [(x, y), (y, x), (-x, y), (-y, x),
                             (x, -y), (y, -x), (-x, -y), (-y, -x)]:
                self._set_pixel(cx + ddx, cy + ddy, color)
            y += 1
            if d < 0:
                d += 2 * y + 1
            else:
                x -= 1
                d += 2 * (y - x) + 1

    def draw_filled_circle(self, cx: int, cy: int, r: int,
                           color: int = RGB565_WHITE) -> None:
        """
        绘制填充圆形 | Draw filled circle
        """
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r:
                    self._set_pixel(cx + dx, cy + dy, color)

    def draw_arc(self, cx: int, cy: int, radius: int, thickness: int,
                 start_angle: float, end_angle: float,
                 color: int = RGB565_CYAN) -> None:
        """
        绘制弧线 | Draw arc

        参数 Args:
            cx, cy: 圆心 | Center
            radius: 半径 | Radius
            thickness: 弧线厚度 | Arc thickness
            start_angle, end_angle: 角度范围（度，0=顶部）| Angle range (deg, 0=top)
            color: RGB565 颜色
        """
        for angle_deg in range(int(start_angle), int(end_angle), 1):
            rad = math.radians(angle_deg - 90)  # 0 度在顶部 | 0 deg at top
            cos_a = math.cos(rad)
            sin_a = math.sin(rad)
            for t in range(thickness):
                r = radius - t
                px = int(cx + r * cos_a)
                py = int(cy + r * sin_a)
                self._set_pixel(px, py, color)

    def draw_text(self, x: int, y: int, text: str,
                  color: int = RGB565_WHITE, scale: int = 1) -> None:
        """
        绘制简单文字 | Draw simple text

        使用极简 3x5 像素字体，适合嵌入式教学演示。
        在真实项目中通常使用 LVGL 的字体渲染系统。
        Uses a minimal 3x5 pixel font for embedded education.
        Real projects typically use LVGL's font rendering system.
        """
        SIMPLE_FONT = {
            '0': [0b111, 0b101, 0b101, 0b101, 0b111],
            '1': [0b010, 0b110, 0b010, 0b010, 0b111],
            '2': [0b111, 0b001, 0b111, 0b100, 0b111],
            '3': [0b111, 0b001, 0b111, 0b001, 0b111],
            '4': [0b101, 0b101, 0b111, 0b001, 0b001],
            '5': [0b111, 0b100, 0b111, 0b001, 0b111],
            '6': [0b111, 0b100, 0b111, 0b101, 0b111],
            '7': [0b111, 0b001, 0b001, 0b001, 0b001],
            '8': [0b111, 0b101, 0b111, 0b101, 0b111],
            '9': [0b111, 0b101, 0b111, 0b001, 0b111],
            'A': [0b111, 0b101, 0b111, 0b101, 0b101],
            'B': [0b110, 0b101, 0b110, 0b101, 0b110],
            'C': [0b111, 0b100, 0b100, 0b100, 0b111],
            'D': [0b110, 0b101, 0b101, 0b101, 0b110],
            'E': [0b111, 0b100, 0b111, 0b100, 0b111],
            'F': [0b111, 0b100, 0b111, 0b100, 0b100],
            ' ': [0b000, 0b000, 0b000, 0b000, 0b000],
            '-': [0b000, 0b000, 0b111, 0b000, 0b000],
            ':': [0b000, 0b010, 0b000, 0b010, 0b000],
            '%': [0b101, 0b001, 0b010, 0b100, 0b101],
            '.': [0b000, 0b000, 0b000, 0b000, 0b010],
        }

        cx = x
        for char in text.upper():
            glyph = SIMPLE_FONT.get(char, SIMPLE_FONT.get(' '))
            for row_idx, row_bits in enumerate(glyph):
                for col_idx in range(3):
                    if row_bits & (1 << (2 - col_idx)):
                        for sy in range(scale):
                            for sx in range(scale):
                                self._set_pixel(
                                    cx + col_idx * scale + sx,
                                    y + row_idx * scale + sy,
                                    color
                                )
            cx += 4 * scale

    # --- SPI 通信模拟 | SPI Communication Simulation ---

    def init_sequence(self) -> List[str]:
        """
        模拟 GC9A01 初始化命令序列
        Simulate GC9A01 initialization command sequence

        GC9A01 的初始化需要按特定顺序发送一系列命令：
        1. 硬件复位 (RST)
        2. 软件复位 (SWRESET)
        3. 退出睡眠 (SLPOUT)
        4. 设置像素格式 (COLMOD) → RGB565
        5. 设置显示方向 (MADCTL)
        6. 开启显示 (DISPON)

        返回 Returns:
            List[str]: 初始化命令日志
        """
        self._init_log = [
            "=== GC9A01 初始化序列 | Init Sequence ===",
            "1. RST -> LOW (10ms) -> HIGH -> wait 120ms",
            "   硬件复位，确保 LCD 进入已知状态",
            "   Hardware reset, ensures LCD enters known state",
            "2. CMD 0x01 (SWRESET) -> 软件复位",
            "3. 等待 120ms",
            "4. CMD 0x11 (SLPOUT) -> 退出睡眠模式",
            "   LCD 出厂默认在睡眠模式以省电",
            "   LCD ships in sleep mode to save power",
            "5. 等待 120ms",
            "6. CMD 0x3A (COLMOD) -> DATA 0x05 -> RGB565 format",
            "   0x05 = 16-bit/pixel (RGB565)",
            "7. CMD 0x36 (MADCTL) -> DATA 0x00 -> 正常方向",
            "   控制内存到显示的映射方向",
            "   Controls memory-to-display mapping direction",
            "8. CMD 0x2A (CASET) -> DATA [0,0, 0,239] -> 列范围",
            "9. CMD 0x2B (RASET) -> DATA [0,0, 0,239] -> 行范围",
            "10. CMD 0x29 (DISPON) -> 开启显示",
            "11. 初始化完成 | Init complete",
        ]
        return self._init_log

    def update(self) -> None:
        """
        模拟通过 SPI 发送帧缓冲区到 GC9A01
        Simulate sending framebuffer to GC9A01 via SPI

        实际 SPI 传输过程 Actual SPI transfer:
        1. CS = LOW
        2. DC = LOW → 发送 0x2C (RAMWR) 命令
        3. DC = HIGH → 发送帧缓冲数据 (115,200 字节)
        4. CS = HIGH

        SPI 数据速率 SPI data rate:
        40MHz × 1 bit/clock = 5 MB/s
        115,200 bytes / 5 MB/s ≈ 23ms/帧 ≈ 43 FPS
        """
        pass

    def to_rgb565_bytes(self) -> bytes:
        """
        将帧缓冲转换为 RGB565 字节流
        Convert framebuffer to RGB565 byte stream

        GC9A01 接收数据格式：高字节在前（大端序）

        返回 Returns:
            bytes: RGB565 字节流 (width * height * 2 字节)
        """
        data = bytearray()
        for color in self.framebuffer:
            data.append((color >> 8) & 0xFF)  # 高字节 | High byte
            data.append(color & 0xFF)          # 低字节 | Low byte
        return bytes(data)

    def get_memory_usage(self) -> str:
        """
        获取帧缓冲区内存使用信息
        Get framebuffer memory usage info
        """
        bytes_total = self.width * self.height * 2
        return (f"Framebuffer: {self.width}x{self.height}x2 = "
                f"{bytes_total:,} bytes ({bytes_total / 1024:.1f} KB)")

    def get_display_string(self) -> str:
        """
        将帧缓冲转换为 ASCII 字符画（用于终端显示）
        Convert framebuffer to ASCII art for terminal display
        """
        chars = " .:-=+*#%@"
        step = max(self.width // 40, 4)
        lines = []
        for y in range(0, self.height, step):
            line = ""
            for x in range(0, self.width, step):
                if not self._is_in_circle(x, y):
                    line += " "
                    continue
                c = self.framebuffer[y * self.width + x]
                r, g, b = rgb565_to_rgb(c)
                brightness = (r + g + b) / (3 * 255)
                char_idx = int(brightness * (len(chars) - 1))
                line += chars[min(char_idx, len(chars) - 1)]
            lines.append(line)
        return "\n".join(lines)

    def __repr__(self) -> str:
        return (f"GC9A01Display({self.width}x{self.height}, "
                f"SPI={self.spi_freq_mhz}MHz, "
                f"children={len(self.root_widget.children)})")
