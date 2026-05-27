# -*- coding: utf-8 -*-
"""
USB HID 键盘协议模拟
USB HID Keyboard Protocol Simulation

USB HID 键盘报告格式 (Boot Protocol):
- 报告长度: 8 字节
- Byte 0: 修饰键 (Ctrl/Shift/Alt/GUI)
  - bit0: Left Ctrl
  - bit1: Left Shift
  - bit2: Left Alt
  - bit3: Left GUI (Win/Cmd)
  - bit4: Right Ctrl
  - bit5: Right Shift
  - bit6: Right Alt
  - bit7: Right GUI
- Byte 1: 保留 (0x00)
- Byte 2-7: 同时按下的键码 (最多6键, 0=无键)

HID 描述符中的关键值:
- Usage Page: 0x01 (Generic Desktop)
- Usage: 0x06 (Keyboard)
- Collection: Application

TinyUSB 在 ESP32-S3 上实现 USB HID 设备

Last updated: 2026-05-27
"""

from typing import List, Tuple

# 修饰键位掩码
MOD_LCTRL  = 0x01
MOD_LSHIFT = 0x02
MOD_LALT   = 0x04
MOD_LGUI   = 0x08
MOD_RCTRL  = 0x10
MOD_RSHIFT = 0x20
MOD_RALT   = 0x40
MOD_RGUI   = 0x80

# 常用 HID 键码
KEY_NONE = 0x00
KEY_A = 0x04
KEY_B = 0x05
KEY_1 = 0x1E
KEY_2 = 0x1F
KEY_ENTER = 0x28
KEY_ESCAPE = 0x29
KEY_BACKSPACE = 0x2A
KEY_TAB = 0x2B
KEY_SPACE = 0x2C
KEY_LEFT = 0x50
KEY_RIGHT = 0x51
KEY_UP = 0x52
KEY_DOWN = 0x53
KEY_VOL_UP = 0x80
KEY_VOL_DOWN = 0x81
KEY_MUTE = 0x7F


class HIDKeyboard:
    """
    USB HID 键盘模拟器

    用法：
        hid = HIDKeyboard(config)
        report = hid.create_report([KEY_A], modifiers=[MOD_LSHIFT])  # 大写A
        print(hid.decode_report(report))  # "Shift + A"
    """

    def __init__(self, config: dict):
        hid_cfg = config.get("hid", {})
        self.max_keys: int = hid_cfg.get("max_keys", 6)  # Boot协议最多6键同时
        self.report_size: int = 8

    def create_report(self, keys: List[int] = None, modifiers: List[int] = None) -> bytes:
        """
        创建 HID 键盘报告

        参数:
            keys: HID键码列表 (最多6个)
            modifiers: 修饰键位掩码列表
        返回:
            8字节 HID 报告
        """
        keys = keys or []
        modifiers = modifiers or []

        modifier_byte = 0
        for mod in modifiers:
            modifier_byte |= mod

        key_bytes = [0] * self.max_keys
        for i, key in enumerate(keys[:self.max_keys]):
            key_bytes[i] = key

        report = bytes([modifier_byte, 0x00] + key_bytes)
        return report

    def decode_report(self, report: bytes) -> str:
        """解码 HID 报告为可读字符串"""
        if len(report) < 8:
            return "Invalid report"

        modifier = report[0]
        keys = [k for k in report[2:8] if k != 0x00]

        parts = []
        mod_names = {
            MOD_LCTRL: "LCtrl", MOD_LSHIFT: "LShift",
            MOD_LALT: "LAlt", MOD_LGUI: "LGUI",
            MOD_RCTRL: "RCtrl", MOD_RSHIFT: "RShift",
            MOD_RALT: "RAlt", MOD_RGUI: "RGUI",
        }
        for bit, name in mod_names.items():
            if modifier & bit:
                parts.append(name)

        for key in keys:
            parts.append(f"Key_0x{key:02X}")

        return " + ".join(parts) if parts else "(no keys)"

    def create_nkro_report(self, pressed_keys: List[int], modifiers: List[int] = None) -> dict:
        """
        NKRO (N-Key Roll Over) 报告格式

        Boot协议最多6键同时。NKRO扩展使用位图报告：
        - 每个键码对应1个bit
        - 支持同时按下任意数量的键
        - 本项目75键键盘使用NKRO

        返回 NKRO 位图字典
        """
        modifiers = modifiers or []
        modifier_byte = 0
        for mod in modifiers:
            modifier_byte |= mod

        bitmap = {}
        for key in pressed_keys:
            byte_idx = key // 8
            bit_idx = key % 8
            if byte_idx not in bitmap:
                bitmap[byte_idx] = 0
            bitmap[byte_idx] |= (1 << bit_idx)

        return {
            "type": "NKRO",
            "modifier": modifier_byte,
            "key_bitmap": bitmap,
            "total_pressed": len(pressed_keys),
        }

    def get_report_descriptor(self) -> str:
        """USB HID 报告描述符（简化版，教学用）"""
        return (
            "HID Report Descriptor (Keyboard Boot Protocol):\n"
            "  Usage Page (Generic Desktop)    0x05 0x01\n"
            "  Usage (Keyboard)                0x09 0x06\n"
            "  Collection (Application)        0xA1 0x01\n"
            "    Usage Page (Key Codes)        0x05 0x07\n"
            "    Usage Minimum (224)           0x19 0xE0\n"
            "    Usage Maximum (231)           0x29 0xE7\n"
            "    Logical Minimum (0)           0x15 0x00\n"
            "    Logical Maximum (1)           0x25 0x01\n"
            "    Report Size (1)               0x75 0x01\n"
            "    Report Count (8)              0x95 0x08\n"
            "    Input (Data,Var,Abs)          0x81 0x02  <- 修饰键\n"
            "    Report Count (1)              0x95 0x01\n"
            "    Report Size (8)               0x75 0x08\n"
            "    Input (Const)                 0x81 0x01  <- 保留字节\n"
            "    Report Count (6)              0x95 0x06\n"
            "    Report Size (8)               0x75 0x08\n"
            "    Logical Maximum (101)         0x25 0x65\n"
            "    Input (Data,Ary,Abs)          0x81 0x00  <- 键码\n"
            "  End Collection                  0xC0\n"
        )

    def __repr__(self) -> str:
        return f"HIDKeyboard(max_keys={self.max_keys})"
