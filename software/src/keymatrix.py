# -*- coding: utf-8 -*-
"""
74HC165 移位寄存器键扫描模拟模块
74HC165 Shift Register Key Scanning Simulation Module

本项目使用 5 片 74HC165 级联（daisy-chain）读取大量按键状态，
配合 2 片 74HC138 译码器选择扫描行/列。
本模块模拟此硬件协议，帮助学生理解移位寄存器和 SPI 的工作原理。

This project uses 5 daisy-chained 74HC165 shift registers to read many key states,
with 2 x 74HC138 decoders for row/column selection.
This module simulates the hardware protocol to help students understand
shift registers and SPI communication.

=== 协议原理 | Protocol Principles ===

74HC165 是 8 位并行转串行移位寄存器：
  - 8 个并行输入 (D0-D7) 可同时读取 8 个开关状态
  - PL (Parallel Load) 引脚：低电平时将并行输入锁存到内部寄存器
  - CLK (Clock) 引脚：每个上升沿将数据右移一位
  - SER (Serial Input) 引脚：串行输入（级联时接前一片的 Q7'）
  - Q7 (Serial Output) 引脚：串行输出

  The 74HC165 is an 8-bit parallel-to-serial shift register:
  - 8 parallel inputs (D0-D7) simultaneously read 8 switch states
  - PL (Parallel Load): LOW latches parallel inputs into internal register
  - CLK (Clock): each rising edge shifts data right by one bit
  - SER (Serial Input): serial input (connected to previous chip's Q7')
  - Q7 (Serial Output): serial output

=== SPI 读取时序 | SPI Read Timing ===

  1. PL 拉低 → 并行数据锁存到寄存器（所有芯片同时锁存）
  2. PL 拉高 → 准备移位
  3. 第 1 个 CLK 上升沿 → Q7 输出第 1 片 D7 的值
  4. 第 2 个 CLK 上升沿 → Q7 输出第 1 片 D6 的值...
  5. 第 8 个 CLK → Q7 输出第 1 片 D0 的值，同时第 2 片 D7 进入
  6. ...继续 40 个 CLK（5 片 x 8 位 = 40 位）
  7. 5 片级联共输出 40 位 = 5 字节

  1. PL LOW  → parallel data latched (all chips simultaneously)
  2. PL HIGH → ready to shift
  3. 1st CLK rising edge → Q7 outputs chip 1's D7 value
  4. 2nd CLK → Q7 outputs chip 1's D6 value...
  5. 8th CLK → Q7 outputs chip 1's D0, chip 2's D7 enters
  6. ...continue for 40 CLKs (5 chips x 8 bits = 40 bits)
  7. 5 daisy-chained chips output 40 bits = 5 bytes total

=== 级联连接图 | Daisy-chain Connection Diagram ===

  ESP32-S3 SPI
  ┌───────────────────────────────────────────────────────────┐
  │  GPIO_CS  ────────────┬──────────┬──────────┬────────── │
  │                       │PL        │PL        │PL         │
  │  GPIO_CLK ────────────┬──────────┬──────────┬────────── │
  │                       │CLK       │CLK       │CLK        │
  │  GPIO_MISO ─── Q7 [165 #5] Q7'[165 #4] Q7'[165 #3] ... │
  │                       │          │          │           │
  │               [D0-D7]   [D0-D7]   [D0-D7]              │
  │               按键输入    按键输入    按键输入              │
  └───────────────────────────────────────────────────────────┘

最后更新 | Last updated: 2026-05-27
"""

from dataclasses import dataclass, field
from typing import List, Optional, Callable


@dataclass
class KeyEvent:
    """
    按键事件数据类
    Key event data class

    属性 Attributes:
        row (int): 按键所在行 | Row of the key
        col (int): 按键所在列 | Column of the key
        pressed (bool): 是否按下 | Whether pressed
        timestamp (float): 事件时间戳（模拟）| Simulated timestamp
    """
    row: int
    col: int
    pressed: bool
    timestamp: float = 0.0


class ShiftRegister74HC165:
    """
    单片 74HC165 移位寄存器模拟
    Single 74HC165 shift register simulation

    模拟一片 74HC165 的行为：
    - 8 个并行输入 D0-D7
    - PL 锁存功能
    - CLK 移位功能
    - Q7 串行输出
    - SER 串行输入（用于级联）

    Simulates one 74HC165:
    - 8 parallel inputs D0-D7
    - PL latch function
    - CLK shift function
    - Q7 serial output
    - SER serial input (for daisy-chaining)
    """

    def __init__(self, name: str = "HC165"):
        """
        初始化移位寄存器
        Initialize shift register

        参数 Args:
            name: 芯片标识名 | Chip identifier name
        """
        self.name = name

        # 并行输入状态 (D0-D7)，True = 低电平（按键按下时拉低）
        # Parallel input states (D0-D7), True = LOW (key pressed pulls LOW)
        self.parallel_inputs: List[bool] = [False] * 8

        # 内部移位寄存器（8 位），锁存后存入此
        # Internal shift register (8 bits), latched value stored here
        self._shift_reg: List[bool] = [False] * 8

        # 串行输入（来自前一片的 Q7'）
        # Serial input (from previous chip's Q7')
        self.serial_input: bool = False

        # PL (Parallel Load) 引脚状态
        # PL (Parallel Load) pin state
        self._pl_active: bool = False

    def set_input(self, pin: int, value: bool) -> None:
        """
        设置并行输入引脚的值
        Set parallel input pin value

        参数 Args:
            pin: 引脚号 0-7 | Pin number 0-7
            value: True = 低电平（按下）| True = LOW (pressed)

        在实际电路中，按键一端接 D0-D7，另一端通过二极管接行扫描线。
        当行扫描线拉低且按键按下时，对应输入被拉低。
        In real circuits, one end of the key connects to D0-D7,
        the other end connects to the row scan line through a diode.
        When the row line is LOW and key is pressed, the input is pulled LOW.
        """
        if 0 <= pin < 8:
            self.parallel_inputs[pin] = value

    def latch(self) -> None:
        """
        锁存并行输入到内部寄存器（PL 拉低时触发）
        Latch parallel inputs to internal register (triggered by PL LOW)

        对应硬件操作：将 PL 引脚从高拉低再拉高
        Corresponds to hardware: pull PL LOW then HIGH

        这是 SPI 读取的第一步：在 PL 低电平期间，
        8 个并行输入的值被同时"拍摄"到内部 8 位移位寄存器中。
        This is the first step of SPI read: while PL is LOW,
        the 8 parallel input values are simultaneously "snapshotted"
        into the internal 8-bit shift register.
        """
        # 复制并行输入到移位寄存器
        # Copy parallel inputs to shift register
        self._shift_reg = list(self.parallel_inputs)

    def shift_out_one(self) -> bool:
        """
        移位一次并返回最高位（Q7 输出）
        Shift once and return MSB (Q7 output)

        每个 CLK 上升沿调用此函数：
        1. 输出当前最高位 (Q7)
        2. 所有位右移一位
        3. SER 输入填入最低位

        Called on each CLK rising edge:
        1. Output current MSB (Q7)
        2. Shift all bits right by one
        3. SER input fills the LSB position

        返回 Returns:
            bool: Q7 输出值 | Q7 output value
        """
        # Q7 输出最高位
        # Q7 outputs the MSB
        output = self._shift_reg[7]

        # 右移一位，最低位填入 SER
        # Shift right by one, SER fills LSB
        self._shift_reg = [self.serial_input] + self._shift_reg[:7]

        return output

    def __repr__(self) -> str:
        bits = ''.join('1' if b else '0' for b in self._shift_reg)
        return f"{self.name}(reg=0b{bits})"


class KeyMatrix:
    """
    基于 74HC165 级联的键扫描管理类
    Key scanning manager based on daisy-chained 74HC165

    使用方法 Usage:
        matrix = KeyMatrix(config)
        matrix.simulate_press(0, 0)  # 模拟按下第 0 行第 0 列
        data = matrix.spi_read()      # 模拟 SPI 读取
        events = matrix.scan()        # 执行一次完整扫描
    """

    def __init__(self, config: dict):
        """
        初始化键扫描矩阵
        Initialize key scanning matrix

        参数 Args:
            config: 键盘配置字典 | Keyboard config dict
        """
        matrix_cfg = config.get("matrix", {})
        kb_cfg = config.get("keyboard", {})

        # 矩阵尺寸
        # Matrix dimensions
        self.rows: int = kb_cfg.get("rows", 5)
        self.cols: int = kb_cfg.get("cols", 14)

        # 移位寄存器数量：每个 74HC165 有 8 个输入，需要覆盖 rows*cols 个键
        # Number of shift registers: each 74HC165 has 8 inputs, need to cover rows*cols keys
        self.total_keys: int = self.rows * self.cols
        self.num_registers: int = (self.total_keys + 7) // 8  # 向上取整 | Ceiling division

        # 创建级联的 74HC165 芯片
        # Create daisy-chained 74HC165 chips
        self._registers: List[ShiftRegister74HC165] = [
            ShiftRegister74HC165(f"HC165_#{i}") for i in range(self.num_registers)
        ]

        # 按键状态矩阵（True = 按下）
        # Key state matrix (True = pressed)
        self._state: List[List[bool]] = [
            [False for _ in range(self.cols)] for _ in range(self.rows)
        ]

        # 上一次扫描状态（用于检测变化）
        # Previous scan state (for change detection)
        self._prev_state: List[List[bool]] = [
            [False for _ in range(self.cols)] for _ in range(self.rows)
        ]

        # 消抖计数器矩阵
        # Debounce counter matrix
        self.debounce_ms: int = matrix_cfg.get("debounce_ms", 5)
        self._debounce_count: List[List[int]] = [
            [0 for _ in range(self.cols)] for _ in range(self.rows)
        ]
        self._debounce_threshold: int = 3  # 连续 3 次读数相同才确认 | 3 consecutive reads to confirm

        # 扫描频率
        # Scan rate
        self.scan_rate_hz: int = matrix_cfg.get("scan_rate_hz", 1000)

        # SPI 引脚配置（仅记录，用于信息显示）
        # SPI pin config (informational only)
        self.spi_mosi_pin: str = matrix_cfg.get("spi_mosi_pin", "GPIO11")
        self.spi_miso_pin: str = matrix_cfg.get("spi_miso_pin", "GPIO13")
        self.spi_clk_pin: str = matrix_cfg.get("spi_clk_pin", "GPIO12")
        self.spi_cs_pin: str = matrix_cfg.get("spi_cs_pin", "GPIO10")
        self.pl_pin: str = matrix_cfg.get("pl_pin", "GPIO9")

        # 事件回调
        # Event callbacks
        self._event_callbacks: List[Callable[[KeyEvent], None]] = []

        # 扫描帧计数
        # Scan frame count
        self.scan_count: int = 0

    def simulate_press(self, row: int, col: int) -> None:
        """
        模拟按键按下（用于测试）
        Simulate key press (for testing)

        参数 Args:
            row: 行号 | Row number
            col: 列号 | Column number

        按下按键后，对应 74HC165 的并行输入被拉低。
        实际硬件中，按键接在行扫描线和 74HC165 输入之间。
        After pressing, the corresponding 74HC165 parallel input is pulled LOW.
        In hardware, the key sits between the row scan line and the 74HC165 input.
        """
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self._state[row][col] = True
            # 更新对应移位寄存器的并行输入
            # Update corresponding shift register's parallel input
            bit_index = row * self.cols + col
            reg_index = bit_index // 8
            pin_index = bit_index % 8
            if reg_index < len(self._registers):
                self._registers[reg_index].set_input(pin_index, True)

    def simulate_release(self, row: int, col: int) -> None:
        """
        模拟按键释放（用于测试）
        Simulate key release (for testing)

        参数 Args:
            row: 行号 | Row number
            col: 列号 | Column number
        """
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self._state[row][col] = False
            bit_index = row * self.cols + col
            reg_index = bit_index // 8
            pin_index = bit_index % 8
            if reg_index < len(self._registers):
                self._registers[reg_index].set_input(pin_index, False)

    def is_pressed(self, row: int, col: int) -> bool:
        """
        检查指定按键是否按下
        Check if a specific key is pressed
        """
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self._state[row][col]
        return False

    def spi_read(self) -> bytes:
        """
        模拟一次完整的 SPI 读取
        Simulate one complete SPI read

        这模拟了 ESP32-S3 通过 SPI 读取 5 片 74HC165 级联数据的完整过程：

        步骤 Steps:
        1. CS 拉低 → 选中设备
        2. PL 拉低 → 并行数据锁存到所有芯片
        3. PL 拉高 → 准备移位
        4. 发送 40 个 CLK 脉冲 → 逐位读出数据
        5. CS 拉高 → 结束传输

        数据流（5 片级联）：
        第一个 CLK → 第 5 片的 D7（最远的芯片先出）
        第二个 CLK → 第 5 片的 D6
        ...
        第 8 个 CLK → 第 5 片的 D0，同时第 4 片的 D7 移入第 5 片
        ...
        第 40 个 CLK → 第 1 片的 D0

        This simulates ESP32-S3 reading 5 daisy-chained 74HC165 via SPI:
        Data flows from the last chip (furthest from SPI master) first.
        Total: 5 chips x 8 bits = 40 bits = 5 bytes.

        返回 Returns:
            bytes: 读取到的数据（每字节对应一片 74HC165）
                  Data read (each byte corresponds to one 74HC165)
        """
        # 步骤 1-2: PL 拉低，锁存所有并行输入
        # Steps 1-2: PL LOW, latch all parallel inputs
        for reg in self._registers:
            reg.latch()

        # 步骤 3-4: 级联移位读取
        # Steps 3-4: Daisy-chain shift read
        total_bits = self.num_registers * 8
        all_bits: List[bool] = []

        for _ in range(total_bits):
            # 设置级联连接：每片 SER 接前一片的 Q7 输出
            # Set daisy-chain: each chip's SER connects to previous chip's Q7
            for i in range(self.num_registers - 1, 0, -1):
                # 后面的芯片先移位，其输出连到前面芯片的 SER
                # Later chips shift first, output connects to earlier chip's SER
                self._registers[i - 1].serial_input = self._registers[i].shift_out_one()

            # 最前面（最靠近 SPI master）的芯片最后移位
            # The first chip (closest to SPI master) shifts last
            q7 = self._registers[0].shift_out_one()
            all_bits.append(q7)

        # 将位列表转换为字节
        # Convert bit list to bytes
        result = bytearray()
        for byte_idx in range(self.num_registers):
            byte_val = 0
            for bit_idx in range(8):
                if all_bits[byte_idx * 8 + bit_idx]:
                    byte_val |= (1 << (7 - bit_idx))
            result.append(byte_val)

        return bytes(result)

    def debounce(self, row: int, col: int, current: bool) -> Optional[bool]:
        """
        消抖算法
        Debounce algorithm

        使用计数消抖法：连续 N 次读数相同才确认状态变化。
        这是键盘固件中最常用的消抖方法之一。

        Uses counter-based debounce: state change is confirmed only after
        N consecutive identical readings. This is one of the most common
        debounce methods in keyboard firmware.

        参数 Args:
            row: 行号 | Row number
            col: 列号 | Column number
            current: 当前读数 | Current reading

        返回 Returns:
            Optional[bool]: 确认后的状态，None 表示尚未确认
                           Confirmed state, None means not yet confirmed
        """
        previous = self._prev_state[row][col]

        if current != previous:
            # 读数与上次确认状态不同，增加计数
            # Reading differs from last confirmed state, increment counter
            self._debounce_count[row][col] += 1

            if self._debounce_count[row][col] >= self._debounce_threshold:
                # 达到阈值，确认状态变化
                # Threshold reached, confirm state change
                self._debounce_count[row][col] = 0
                self._prev_state[row][col] = current
                return current
        else:
            # 读数与上次一致，重置计数
            # Reading matches last state, reset counter
            self._debounce_count[row][col] = 0

        return None  # 尚未确认 | Not yet confirmed

    def scan(self) -> List[KeyEvent]:
        """
        执行一次完整的矩阵扫描
        Perform one complete matrix scan

        扫描流程 Scan flow:
        1. 通过 SPI 读取所有 74HC165 数据
        2. 解析每个按键的当前状态
        3. 消抖处理
        4. 检测按键事件（按下/释放）
        5. 触发回调

        返回 Returns:
            List[KeyEvent]: 检测到的按键事件列表
                           List of detected key events
        """
        events = []
        self.scan_count += 1

        # 步骤 1: SPI 读取
        # Step 1: SPI read
        raw_data = self.spi_read()

        # 步骤 2-4: 解析、消抖、事件检测
        # Steps 2-4: Parse, debounce, event detection
        for row in range(self.rows):
            for col in range(self.cols):
                bit_index = row * self.cols + col
                byte_index = bit_index // 8
                bit_offset = bit_index % 8

                # 从 SPI 数据中提取该按键的当前读数
                # Extract current reading for this key from SPI data
                if byte_index < len(raw_data):
                    current = bool(raw_data[byte_index] & (1 << (7 - bit_offset)))
                else:
                    current = False

                # 消抖处理
                # Debounce processing
                confirmed = self.debounce(row, col, current)

                if confirmed is not None and confirmed != self._state[row][col]:
                    # 状态变化确认，生成事件
                    # State change confirmed, generate event
                    event = KeyEvent(
                        row=row,
                        col=col,
                        pressed=confirmed,
                        timestamp=self.scan_count / self.scan_rate_hz
                    )
                    events.append(event)
                    self._state[row][col] = confirmed

                    # 触发回调 | Trigger callbacks
                    for callback in self._event_callbacks:
                        callback(event)

        return events

    def get_all_pressed(self) -> List[tuple]:
        """
        获取所有当前按下的按键
        Get all currently pressed keys

        返回 Returns:
            List[tuple]: [(row, col), ...]
        """
        pressed = []
        for row in range(self.rows):
            for col in range(self.cols):
                if self._state[row][col]:
                    pressed.append((row, col))
        return pressed

    def register_callback(self, callback: Callable[[KeyEvent], None]) -> None:
        """
        注册按键事件回调
        Register key event callback
        """
        self._event_callbacks.append(callback)

    def get_state_string(self) -> str:
        """
        获取矩阵状态的可视化字符串
        Get visual string representation of matrix state

        返回 Returns:
            str: 矩阵的 ASCII 表示
        """
        header = "     " + "".join(f"C{i:<3}" for i in range(min(self.cols, 14)))
        lines = [header]
        for row in range(self.rows):
            line = f"R{row:<2} "
            for col in range(min(self.cols, 14)):
                line += f" [{'X' if self._state[row][col] else '.'}] "
            lines.append(line)
        return "\n".join(lines)

    def explain_spi_timing(self) -> str:
        """
        生成 SPI 读取时序的详细说明
        Generate detailed explanation of SPI read timing

        返回 Returns:
            str: 时序说明文本
        """
        lines = [
            "=== 74HC165 SPI 读取时序 | SPI Read Timing ===",
            "",
            f"级联芯片数 Daisy-chained chips: {self.num_registers}",
            f"总位数 Total bits: {self.num_registers * 8}",
            f"总按键数 Total keys: {self.total_keys}",
            "",
            "时序步骤 Timing steps:",
            "  1. CS (GPIO10) → LOW   选中设备 | Select device",
            "  2. PL (GPIO9)  → LOW   锁存并行输入 | Latch parallel inputs",
            "  3. PL (GPIO9)  → HIGH  准备移位 | Ready to shift",
            f"  4. CLK ×{self.num_registers * 8}         移位输出 | Shift out data",
            "  5. CS (GPIO10) → HIGH  结束传输 | End transfer",
            "",
            "SPI 模式 SPI Mode: Mode 0 (CPOL=0, CPHA=0)",
            f"时钟频率 Clock freq: up to {self.scan_rate_hz} Hz",
        ]
        return "\n".join(lines)

    def __repr__(self) -> str:
        return (f"KeyMatrix({self.rows}x{self.cols}, "
                f"regs={self.num_registers}, "
                f"pressed={len(self.get_all_pressed())})")
