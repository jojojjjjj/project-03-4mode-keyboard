# -*- coding: utf-8 -*-
"""
USB HID 键盘协议模拟模块
USB HID Keyboard Protocol Simulation Module

本项目键盘通过 CH9350 USB HID 芯片将按键数据上传到 PC。
本模块模拟 USB HID 协议的报告格式和通信流程。

This keyboard uploads key data to PC via CH9350 USB HID chip.
This module simulates USB HID report format and communication.

=== 键盘报告格式 | Keyboard Report Format ===

  8 字节报告 8-byte report:
  Byte 0: 修饰键 (Ctrl/Shift/Alt/GUI bitmask)
  Byte 1: 保留 (0x00)
  Byte 2-7: 按键码 (最多 6 个同时按下, 6KRO)

=== Boot vs Report Protocol ===

  Boot Protocol: BIOS 阶段，固定 8 字节格式
  Report Protocol: OS 阶段，支持自定义描述符和 NKRO

最后更新 | Last updated: 2026-05-27
"""

from dataclasses import dataclass, field
from typing import List, Optional


# USB HID 键码 | USB HID Keycodes
HID_KEYCODES = {
    'KC_A': 0x04, 'KC_B': 0x05, 'KC_C': 0x06, 'KC_D': 0x07,
    'KC_E': 0x08, 'KC_F': 0x09, 'KC_G': 0x0A, 'KC_H': 0x0B,
    'KC_I': 0x0C, 'KC_J': 0x0D, 'KC_K': 0x0E, 'KC_L': 0x0F,
    'KC_M': 0x10, 'KC_N': 0x11, 'KC_O': 0x12, 'KC_P': 0x13,
    'KC_Q': 0x14, 'KC_R': 0x15, 'KC_S': 0x16, 'KC_T': 0x17,
    'KC_U': 0x18, 'KC_V': 0x19, 'KC_W': 0x1A, 'KC_X': 0x1B,
    'KC_Y': 0x1C, 'KC_Z': 0x1D,
    'KC_1': 0x1E, 'KC_2': 0x1F, 'KC_3': 0x20, 'KC_4': 0x21,
    'KC_5': 0x22, 'KC_6': 0x23, 'KC_7': 0x24, 'KC_8': 0x25,
    'KC_9': 0x26, 'KC_0': 0x27,
    'KC_ENTER': 0x28, 'KC_ESC': 0x29, 'KC_BSPC': 0x2A,
    'KC_TAB': 0x2B, 'KC_SPACE': 0x2C,
    'KC_F1': 0x3A, 'KC_F2': 0x3B, 'KC_F3': 0x3C, 'KC_F4': 0x3D,
    'KC_F5': 0x3E, 'KC_F6': 0x3F, 'KC_F7': 0x40, 'KC_F8': 0x41,
    'KC_F9': 0x42, 'KC_F10': 0x43, 'KC_F11': 0x44, 'KC_F12': 0x45,
    'KC_RIGHT': 0x4F, 'KC_LEFT': 0x50, 'KC_DOWN': 0x51, 'KC_UP': 0x52,
    'KC_P1': 0x59, 'KC_P2': 0x5A, 'KC_P3': 0x5B, 'KC_P4': 0x5C,
    'KC_P5': 0x5D, 'KC_P6': 0x5E, 'KC_P7': 0x5F, 'KC_P8': 0x60,
    'KC_P9': 0x61, 'KC_P0': 0x62, 'KC_PDOT': 0x63, 'KC_PENT': 0x58,
    'KC_PPLS': 0x57, 'KC_PMNS': 0x56, 'KC_PAST': 0x55, 'KC_PSLS': 0x54,
}

# 修饰键位掩码 | Modifier bitmasks
MODIFIER_MASKS = {
    'KC_LCTL': 0x01, 'KC_LSFT': 0x02, 'KC_LALT': 0x04, 'KC_LGUI': 0x08,
    'KC_RCTL': 0x10, 'KC_RSFT': 0x20, 'KC_RALT': 0x40, 'KC_RGUI': 0x80,
}


@dataclass
class HIDReport:
    """
    USB HID 键盘报告 (8 字节)
    Byte 0: 修饰键, Byte 1: 保留, Byte 2-7: 6 个键码 (6KRO)
    """
    modifiers: int = 0
    reserved: int = 0
    keycodes: List[int] = field(default_factory=lambda: [0] * 6)

    def to_bytes(self) -> bytes:
        """转换为 8 字节报告 | Convert to 8-byte report"""
        result = bytearray()
        result.append(self.modifiers & 0xFF)
        result.append(self.reserved)
        for i in range(6):
            result.append(self.keycodes[i] if i < len(self.keycodes) else 0)
        return bytes(result)

    def __repr__(self) -> str:
        keys = [f'0x{k:02X}' for k in self.keycodes if k != 0]
        return f"HIDReport(mod=0x{self.modifiers:02X}, keys=[{', '.join(keys)}])"


class USBHIDDevice:
    """
    USB HID 键盘设备模拟类
    USB HID Keyboard Device Simulator

    模拟通过 CH9350 芯片将键盘数据发送给 PC。
    Simulates sending keyboard data to PC via CH9350 chip.

    通信流程 Communication flow:
    ESP32-S3 → UART → CH9350 → USB HID → PC
    """

    def __init__(self, config: dict):
        usb_cfg = config.get("usb", {})
        self.vid: str = usb_cfg.get("vid", "0x303A")
        self.pid: str = usb_cfg.get("pid", "0x4002")
        self.max_power: int = usb_cfg.get("max_power_ma", 500)
        self.poll_interval_ms: int = usb_cfg.get("poll_interval_ms", 1)
        self._modifier: int = 0
        self._pressed_keys: List[int] = []
        self._report_history: List[HIDReport] = []
        self.connected: bool = False

    def connect(self) -> None:
        """模拟 USB 连接 | Simulate USB connection"""
        self.connected = True

    def disconnect(self) -> None:
        """模拟 USB 断开 | Simulate USB disconnection"""
        self.connected = False
        self._modifier = 0
        self._pressed_keys = []

    def press_key(self, keycode_name: str) -> Optional[HIDReport]:
        """模拟按下按键 | Simulate key press"""
        if not self.connected:
            return None
        if keycode_name in MODIFIER_MASKS:
            self._modifier |= MODIFIER_MASKS[keycode_name]
            return self._build_report()
        if keycode_name in HID_KEYCODES:
            hid_code = HID_KEYCODES[keycode_name]
            if hid_code not in self._pressed_keys and len(self._pressed_keys) < 6:
                self._pressed_keys.append(hid_code)
        return self._build_report()

    def release_key(self, keycode_name: str) -> Optional[HIDReport]:
        """模拟释放按键 | Simulate key release"""
        if not self.connected:
            return None
        if keycode_name in MODIFIER_MASKS:
            self._modifier &= ~MODIFIER_MASKS[keycode_name]
            return self._build_report()
        if keycode_name in HID_KEYCODES:
            hid_code = HID_KEYCODES[keycode_name]
            if hid_code in self._pressed_keys:
                self._pressed_keys.remove(hid_code)
        return self._build_report()

    def release_all(self) -> Optional[HIDReport]:
        """释放所有按键 | Release all keys"""
        self._modifier = 0
        self._pressed_keys = []
        return self._build_report()

    def _build_report(self) -> HIDReport:
        """构建 8 字节 HID 报告 | Build 8-byte HID report"""
        keycodes = [0] * 6
        for i, code in enumerate(self._pressed_keys[:6]):
            keycodes[i] = code
        report = HIDReport(modifiers=self._modifier, keycodes=keycodes)
        self._report_history.append(report)
        return report

    def get_last_report(self) -> Optional[HIDReport]:
        """获取最后一次报告 | Get last report"""
        return self._report_history[-1] if self._report_history else None

    def get_report_history(self) -> List[HIDReport]:
        """获取报告历史 | Get report history"""
        return list(self._report_history)

    def clear_history(self) -> None:
        """清除报告历史 | Clear report history"""
        self._report_history.clear()

    def explain_report(self) -> str:
        """生成 HID 报告格式说明 | Generate report format explanation"""
        report = self.get_last_report()
        data_str = " ".join(f"0x{b:02X}" for b in report.to_bytes()) if report else "N/A"
        return (
            f"=== USB HID Keyboard Report ===\n"
            f"VID:PID = {self.vid}:{self.pid}\n"
            f"Poll: {self.poll_interval_ms}ms\n"
            f"Byte 0: Modifiers (bitmask)\n"
            f"Byte 1: Reserved (0x00)\n"
            f"Byte 2-7: Keycodes (max 6, 6KRO)\n"
            f"Current: {data_str}\n"
        )

    def __repr__(self) -> str:
        return (f"USBHIDDevice(vid={self.vid}, pid={self.pid}, "
                f"connected={self.connected}, pressed={len(self._pressed_keys)})")
