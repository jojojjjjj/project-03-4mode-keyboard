# -*- coding: utf-8 -*-
"""
无线通信模式模拟 (WiFi / BLE / ESP-NOW)
Wireless Communication Modes Simulation

本项目支持4种连接模式：
1. USB 有线 — 直接USB-C连接电脑
2. BLE 蓝牙 — BLE HID键盘协议
3. WiFi — TCP/UDP通信
4. ESP-NOW — 2.4GHz点对点低延迟协议

BLE HID:
- GAP: Generic Access Profile (广播、扫描、连接)
- GATT: Generic Attribute Profile (服务、特征值)
- HID Service UUID: 0x1812
- Report Characteristic: 0x2A4D

ESP-NOW:
- Espressif私有协议，无需配对
- 点对点直连，延迟<1ms
- 最大 payload: 250字节
- 加密: 可选 CCMP加密

WiFi:
- STA模式: 连接到路由器
- AP模式: 键盘作为热点
- 传输: TCP/UDP socket

Last updated: 2026-05-27
"""

from typing import List, Optional
from enum import Enum


class WirelessMode(Enum):
    USB = "usb"
    BLE = "ble"
    WIFI = "wifi"
    ESP_NOW = "esp_now"


class WirelessManager:
    """
    无线通信管理器模拟

    管理USB/BLE/WiFi/ESP-NOW四种模式的切换
    """

    def __init__(self, config: dict):
        wl_cfg = config.get("wireless", {})
        self.current_mode: WirelessMode = WirelessMode(
            wl_cfg.get("default_mode", "usb")
        )
        self.auto_switch: bool = wl_cfg.get("auto_switch", True)
        self.ble_device_name: str = wl_cfg.get("ble_name", "FantasyKB")
        self.wifi_ssid: str = wl_cfg.get("wifi_ssid", "")
        self.esp_now_channel: int = wl_cfg.get("esp_now_channel", 1)

        self._connected: bool = False
        self._paired_devices: List[str] = []

    def get_available_modes(self) -> List[str]:
        """获取可用的无线模式"""
        return [m.value for m in WirelessMode]

    def switch_mode(self, mode: str) -> bool:
        """
        切换无线模式

        ESP32-S3 WiFi/BLE共存注意事项：
        - WiFi 和 BLE 共享2.4GHz射频
        - 同时使用时需分时复用
        - ESP-NOW 与 WiFi 共存（同一射频）
        - USB 不受影响（独立USB PHY）
        """
        try:
            new_mode = WirelessMode(mode)
            self.current_mode = new_mode
            self._connected = False
            return True
        except ValueError:
            return False

    def ble_advertise(self) -> dict:
        """
        BLE 广播模拟

        GAP 广播数据包:
        - Flags: 0x02, 0x06 (LE General Discoverable, BR/EDR Not Supported)
        - Complete Local Name: "FantasyKB"
        - Appearance: 0x03C1 (Keyboard)
        - HID Service UUID: 0x1812
        """
        return {
            "type": "BLE Advertisement",
            "device_name": self.ble_device_name,
            "appearance": "Keyboard (0x03C1)",
            "service_uuid": "0x1812 (HID)",
            "connectable": True,
        }

    def esp_now_send(self, data: bytes, peer_mac: str) -> dict:
        """
        ESP-NOW 发送模拟

        特点：
        - 无需连接建立
        - 发送即忘 (Fire and Forget)
        - 最大 250 字节 payload
        - 支持加密和确认回调
        """
        return {
            "type": "ESP-NOW Send",
            "peer": peer_mac,
            "payload_size": len(data),
            "max_payload": 250,
            "encrypted": True,
            "ack": True,
        }

    def wifi_connect(self, ssid: str, password: str = "") -> dict:
        """WiFi STA连接模拟"""
        self._connected = True
        return {
            "type": "WiFi STA",
            "ssid": ssid,
            "status": "connected" if self._connected else "disconnected",
        }

    def auto_detect_mode(self) -> WirelessMode:
        """
        自动检测最佳连接模式

        优先级：USB > BLE > ESP-NOW > WiFi
        - USB连接时优先使用USB（最低延迟、可充电）
        - 无USB时尝试BLE（低功耗、通用性强）
        - 无BLE时使用ESP-NOW（低延迟、配接收器）
        - WiFi作为备用方案
        """
        if self.current_mode == WirelessMode.USB:
            return WirelessMode.USB
        return self.current_mode

    def __repr__(self) -> str:
        return f"WirelessManager(mode={self.current_mode.value}, connected={self._connected})"
