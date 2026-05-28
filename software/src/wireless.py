# -*- coding: utf-8 -*-
"""
无线通信模式模拟模块
Wireless Communication Modes Simulation Module

本项目支持四种连接模式：USB / BLE / WiFi / 2.4GHz(ESP-NOW)。
本模块模拟 BLE、WiFi 和 ESP-NOW 的通信协议，
帮助学生理解无线通信的基本概念。

This project supports 4 connection modes: USB / BLE / WiFi / 2.4GHz(ESP-NOW).
This module simulates BLE, WiFi, and ESP-NOW communication protocols
to help students understand wireless communication fundamentals.

=== 蓝牙低功耗 (BLE) | Bluetooth Low Energy ===

BLE 是蓝牙 4.0 引入的低功耗无线协议：
  - 通信距离 Range: ~10m (Class 2)
  - 数据速率 Data rate: 1-2 Mbps
  - 功耗 Power: 非常低 (uA 级待机)
  - 适用场景 Use case: 键盘、鼠标、健康监测

BLE 核心概念 Core concepts:
  - GAP (Generic Access Profile): 控制连接和广播
    - 广播 Advertising: 设备周期性发送广播包
    - 扫描 Scanning: 主动搜索附近的广播设备
    - 连接 Connection: 建立双向通信通道

  - GATT (Generic Attribute Profile): 数据组织方式
    - Service (服务): 一组相关的 Characteristic
    - Characteristic (特征值): 单个数据点，可读/写/通知
    - Descriptor (描述符): Characteristic 的元数据
    - UUID: 每个服务/特征值有唯一标识符

  HID over GATT Profile (HOGP):
  - BLE 键盘使用 HOGP 协议
  - Report Characteristic: 发送键盘报告
  - Report Map Characteristic: 描述报告格式

=== WiFi | WiFi STA/AP ===

ESP32-S3 支持 WiFi 4 (802.11n)：
  - 频段 Band: 2.4GHz
  - 速率 Speed: 最高 150 Mbps
  - 模式 Modes: STA (客户端), AP (热点), STA+AP

本项目 WiFi 模式用于：
  - 连接局域网进行远程控制
  - OTA (Over-The-Air) 固件更新
  - MQTT 物联网通信

=== ESP-NOW (2.4GHz 点对点) ===

ESP-NOW 是 Espressif 的专有点对点协议：
  - 无需路由器，设备直接通信
  - 延迟极低 (~1ms)
  - 最大 250 字节/包
  - 支持加密通信
  - 最多配对 20 个设备 (加密) 或不限 (不加密)

本项目 ESP-NOW 用于键盘 → 接收器的 2.4GHz 无线模式：
  - 键盘端发送按键数据
  - 接收器 (USB dongle) 接收并转发给 PC

最后更新 | Last updated: 2026-05-27
"""

import time
import random
from enum import Enum
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass


class WirelessMode(Enum):
    """无线模式枚举 | Wireless mode enum"""
    USB = "usb"          # 有线 USB | Wired USB
    BLE = "ble"          # 蓝牙低功耗 | Bluetooth LE
    WIFI = "wifi"        # WiFi | WiFi
    ESP_NOW = "esp_now"  # ESP-NOW 2.4GHz | ESP-NOW 2.4GHz


# === BLE 模拟 | BLE Simulation ===

@dataclass
class GATTCharacteristic:
    """
    GATT 特征值
    GATT Characteristic

    属性 Properties:
    - READ: 主机可以读取值
    - WRITE: 主机可以写入值
    - NOTIFY: 设备可以主动通知主机
    """
    uuid: str
    value: bytes
    readable: bool = True
    writable: bool = False
    notifiable: bool = True


@dataclass
class GATTService:
    """GATT 服务 | GATT Service"""
    uuid: str
    characteristics: List[GATTCharacteristic]


class BLEManager:
    """
    BLE 通信管理器模拟
    BLE Communication Manager Simulation

    模拟 BLE HID 键盘的 GAP/GATT 行为。
    Simulates BLE HID keyboard GAP/GATT behavior.
    """

    # HID Service UUID
    HID_SERVICE_UUID = "1812"
    # Report Characteristic UUID
    REPORT_CHAR_UUID = "2A4D"
    # Report Map Characteristic UUID
    REPORT_MAP_UUID = "2A4B"

    def __init__(self, config: dict):
        ble_cfg = config.get("wireless", {}).get("ble", {})
        self.device_name: str = ble_cfg.get("device_name", "FantasyKB-BLE")
        self.enabled: bool = ble_cfg.get("enabled", True)

        # GAP 状态 | GAP state
        self._advertising: bool = False
        self._connected: bool = False
        self._peer_address: Optional[str] = None

        # GATT 服务表 | GATT service table
        self._services: List[GATTService] = []
        self._setup_hid_service()

        # 连接参数 | Connection parameters
        self.conn_interval_ms: float = 7.5  # BLE 连接间隔
        self.latency_ms: float = 3.0  # 典型 BLE 延迟

        # 事件回调 | Event callbacks
        self._connect_callback: Optional[Callable] = None
        self._disconnect_callback: Optional[Callable] = None

    def _setup_hid_service(self) -> None:
        """
        设置 HID over GATT 服务
        Setup HID over GATT service

        BLE 键盘必须提供以下 GATT 服务：
        1. Generic Access (0x1800) — 设备名称等
        2. Device Information (0x180A) — 厂商信息
        3. HID Service (0x1812) — 键盘报告

        BLE keyboard must provide these GATT services:
        1. Generic Access (0x1800) — device name etc.
        2. Device Information (0x180A) — manufacturer info
        3. HID Service (0x1812) — keyboard reports
        """
        # HID 服务
        # HID Service — 包含键盘报告特征值
        self._services.append(GATTService(
            uuid=self.HID_SERVICE_UUID,
            characteristics=[
                GATTCharacteristic(
                    uuid=self.REPORT_CHAR_UUID,
                    value=bytes(8),  # 8 字节 HID 报告
                    notifiable=True,
                    readable=True,
                    writable=False,
                ),
                GATTCharacteristic(
                    uuid=self.REPORT_MAP_UUID,
                    value=bytes([0x05, 0x01, 0x09, 0x06]),  # HID 描述符片段
                    readable=True,
                    notifiable=False,
                ),
            ]
        ))

    def start_advertising(self) -> bool:
        """
        开始 BLE 广播
        Start BLE advertising

        广播包含以下信息 Advertising contains:
        - 设备名称
        - 支持的服务 UUID (HID)
        - 外观 (键盘)
        - 连接参数请求
        """
        self._advertising = True
        return True

    def stop_advertising(self) -> None:
        """停止广播 | Stop advertising"""
        self._advertising = False

    def simulate_connect(self, peer_address: str = "AA:BB:CC:DD:EE:FF") -> bool:
        """
        模拟 BLE 连接
        Simulate BLE connection
        """
        self._connected = True
        self._peer_address = peer_address
        self._advertising = False
        if self._connect_callback:
            self._connect_callback(peer_address)
        return True

    def disconnect(self) -> None:
        """断开连接 | Disconnect"""
        self._connected = False
        self._peer_address = None
        if self._disconnect_callback:
            self._disconnect_callback()

    def send_hid_report(self, report: bytes) -> bool:
        """
        通过 BLE GATT Notification 发送 HID 报告
        Send HID report via BLE GATT Notification

        流程 Flow:
        1. 更新 Report Characteristic 的值
        2. 触发 Notification
        3. 主机通过 BLE 连接接收数据

        参数 Args:
            report: 8 字节 HID 报告
        """
        if not self._connected:
            return False
        # 更新特征值 | Update characteristic value
        for svc in self._services:
            for char in svc.characteristics:
                if char.uuid == self.REPORT_CHAR_UUID:
                    char.value = report
                    return True
        return False

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def is_advertising(self) -> bool:
        return self._advertising

    def __repr__(self) -> str:
        state = "connected" if self._connected else ("advertising" if self._advertising else "idle")
        return f"BLEManager({self.device_name}, {state})"


# === WiFi 模拟 | WiFi Simulation ===

class WiFiManager:
    """
    WiFi 通信管理器模拟
    WiFi Communication Manager Simulation
    """

    def __init__(self, config: dict):
        wifi_cfg = config.get("wireless", {}).get("wifi", {})
        self.enabled: bool = wifi_cfg.get("enabled", True)
        self.ssid: str = wifi_cfg.get("ssid", "")
        self.password: str = wifi_cfg.get("password", "")
        self.mode: str = wifi_cfg.get("mode", "STA")  # STA / AP / STA+AP

        self._connected: bool = False
        self._ip_address: str = ""
        self._rssi: int = -50

    def connect(self, ssid: str = "", password: str = "") -> bool:
        """
        连接 WiFi 网络
        Connect to WiFi network

        WiFi 连接流程 Connection flow:
        1. 扫描信道寻找 AP
        2. 发送认证请求 (Authentication)
        3. 关联 (Association)
        4. DHCP 获取 IP 地址
        """
        self.ssid = ssid or self.ssid
        self.password = password or self.password
        self._connected = True
        self._ip_address = f"192.168.1.{random.randint(100, 200)}"
        self._rssi = random.randint(-70, -30)
        return True

    def disconnect(self) -> None:
        self._connected = False
        self._ip_address = ""

    def start_ap(self, ssid: str = "FantasyKB-AP") -> bool:
        """
        启动 AP (热点) 模式
        Start AP (Access Point) mode

        AP 模式下键盘创建一个 WiFi 热点，
        手机/电脑可以连接进行配置。
        """
        self.mode = "AP"
        self._ip_address = "192.168.4.1"
        return True

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def ip_address(self) -> str:
        return self._ip_address

    def __repr__(self) -> str:
        state = "connected" if self._connected else "disconnected"
        return f"WiFiManager({self.mode}, {state}, ip={self._ip_address})"


# === ESP-NOW 模拟 | ESP-NOW Simulation ===

@dataclass
class ESPNowPeer:
    """ESP-NOW 对端设备 | ESP-NOW peer device"""
    mac_address: str
    encrypted: bool = False
    channel: int = 1


class ESPNowManager:
    """
    ESP-NOW 通信管理器模拟
    ESP-NOW Communication Manager Simulation

    ESP-NOW 是 Espressif 的点对点协议：
    - 无需 WiFi 路由器
    - 延迟 ~1ms
    - 最大 250 字节/包
    - 使用 WiFi 物理层但不需要完整 WiFi 协议栈

    本项目使用 ESP-NOW 实现键盘 → 接收器的 2.4GHz 无线模式。
    This project uses ESP-NOW for keyboard → receiver 2.4GHz wireless mode.
    """

    def __init__(self, config: dict):
        now_cfg = config.get("wireless", {}).get("esp_now", {})
        self.enabled: bool = now_cfg.get("enabled", True)
        self.channel: int = now_cfg.get("channel", 1)

        self._peers: Dict[str, ESPNowPeer] = {}
        self._sent_packets: List[bytes] = []
        self._recv_queue: List[bytes] = []

        # 延迟模拟 | Latency simulation
        self.latency_ms: float = 1.0

    def add_peer(self, mac_address: str, encrypted: bool = False) -> bool:
        """
        添加对端设备
        Add peer device

        ESP-NOW 通信前必须先注册对端 MAC 地址。
        Must register peer MAC address before ESP-NOW communication.
        """
        self._peers[mac_address] = ESPNowPeer(
            mac_address=mac_address,
            encrypted=encrypted,
            channel=self.channel,
        )
        return True

    def remove_peer(self, mac_address: str) -> bool:
        """移除对端 | Remove peer"""
        if mac_address in self._peers:
            del self._peers[mac_address]
            return True
        return False

    def send(self, data: bytes, peer_mac: str = None) -> bool:
        """
        发送数据
        Send data

        ESP-NOW 发送流程 Send flow:
        1. 检查对端是否已注册
        2. 如果加密，进行 AES 加密
        3. 通过 WiFi 物理层发送
        4. 等待 ACK

        参数 Args:
            data: 数据 (最大 250 字节)
            peer_mac: 目标 MAC 地址
        """
        if len(data) > 250:
            return False

        if peer_mac and peer_mac not in self._peers:
            return False

        self._sent_packets.append(data)

        # 模拟对端接收 | Simulate peer receive
        self._recv_queue.append(data)

        return True

    def recv(self) -> Optional[bytes]:
        """
        接收数据
        Receive data
        """
        if self._recv_queue:
            return self._recv_queue.pop(0)
        return None

    def get_sent_count(self) -> int:
        return len(self._sent_packets)

    def __repr__(self) -> str:
        return f"ESPNowManager(ch={self.channel}, peers={len(self._peers)})"


# === 无线模式切换 | Wireless Mode Switching ===

class WirelessManager:
    """
    无线通信总管理器
    Wireless Communication Manager

    管理四种连接模式的切换。
    Manages switching between 4 connection modes.

    模式切换逻辑 Mode switching logic:
    1. USB 插入时自动切换到 USB 模式（优先级最高）
    2. 拔出 USB 时恢复上次的无线模式
    3. 用户可通过快捷键手动切换模式
    4. 模式切换时断开当前连接，建立新连接
    """

    def __init__(self, config: dict):
        self.current_mode: WirelessMode = WirelessMode.USB
        self.ble = BLEManager(config)
        self.wifi = WiFiManager(config)
        self.esp_now = ESPNowManager(config)

        # USB 优先级最高 | USB has highest priority
        self._usb_connected: bool = False
        self._previous_mode: WirelessMode = WirelessMode.BLE

    def set_mode(self, mode: WirelessMode) -> bool:
        """
        切换无线模式
        Switch wireless mode

        切换步骤 Switching steps:
        1. 断开当前模式的连接
        2. 初始化新模式
        3. 建立新连接
        """
        # 断开旧模式 | Disconnect old mode
        if self.current_mode == WirelessMode.BLE:
            self.ble.disconnect()
        elif self.current_mode == WirelessMode.WIFI:
            self.wifi.disconnect()

        # 切换 | Switch
        self._previous_mode = self.current_mode
        self.current_mode = mode

        # 连接新模式 | Connect new mode
        if mode == WirelessMode.BLE:
            self.ble.start_advertising()
        elif mode == WirelessMode.WIFI:
            self.wifi.connect()
        elif mode == WirelessMode.ESP_NOW:
            pass  # ESP-NOW 不需要连接 | No connection needed

        return True

    def on_usb_plug(self) -> None:
        """USB 插入回调 | USB plug callback"""
        self._usb_connected = True
        self._previous_mode = self.current_mode
        self.set_mode(WirelessMode.USB)

    def on_usb_unplug(self) -> None:
        """USB 拔出回调 | USB unplug callback"""
        self._usb_connected = False
        self.set_mode(self._previous_mode)

    def send_key_data(self, data: bytes) -> bool:
        """
        通过当前模式发送按键数据
        Send key data via current mode
        """
        if self.current_mode == WirelessMode.USB:
            return True  # USB 由 CH9350 直接处理
        elif self.current_mode == WirelessMode.BLE:
            return self.ble.send_hid_report(data)
        elif self.current_mode == WirelessMode.ESP_NOW:
            return self.esp_now.send(data)
        elif self.current_mode == WirelessMode.WIFI:
            return True  # WiFi 通过 TCP/UDP 发送
        return False

    def explain_modes(self) -> str:
        """生成模式说明 | Generate mode explanation"""
        return (
            "=== 4-Mode Wireless ===\n"
            "\n"
            "USB:    有线, 零延迟, 充电 | Wired, zero latency, charging\n"
            "BLE:    蓝牙, ~7ms延迟, 省电 | BT, ~7ms latency, power saving\n"
            "WiFi:   WiFi, OTA更新, 远程控制 | WiFi, OTA, remote control\n"
            "ESP-NOW: 2.4G, ~1ms延迟, 配对接收器 | 2.4G, ~1ms, paired receiver\n"
            "\n"
            f"当前模式 Current: {self.current_mode.value}\n"
        )

    def __repr__(self) -> str:
        return f"WirelessManager(mode={self.current_mode.value})"
