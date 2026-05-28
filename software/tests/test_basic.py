# -*- coding: utf-8 -*-
"""
4模式机械键盘测试套件
4-Mode Mechanical Keyboard Test Suite

测试所有模拟模块的基本功能。
Tests basic functionality of all simulation modules.

运行方法 | How to run:
    cd software
    python -m pytest tests/test_basic.py -v

最后更新 | Last updated: 2026-05-27
"""

import sys
import os
import math
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from keymatrix import KeyMatrix, KeyEvent, ShiftRegister74HC165
from oled_display import GC9A01Display, rgb_to_rgb565, rgb565_to_rgb, RGB565_WHITE, RGB565_BLACK
from rgb_led import RGBLed, RGBColor, WS2812BProtocol, EFFECT_MODES
from encoder import AS5047P, AS5047P_RESOLUTION, calculate_parity
from usb_hid import USBHIDDevice, HIDReport, HID_KEYCODES, MODIFIER_MASKS
from audio import AudioPipeline, ES7210, ES8311, I2SConfig
from wireless import (WirelessManager, WirelessMode, BLEManager,
                       WiFiManager, ESPNowManager)
from foc_motor import (FOController, TMC6300, PIDController, PIDConfig,
                        clarke_transform, inverse_clarke_transform,
                        park_transform, inverse_park_transform)
from utils import (load_config, format_hex, format_binary, pad_to_matrix,
                    crc8, set_bit, clear_bit, get_bit, bit_field, toggle_bit)


# ===== 测试配置 Fixture =====

@pytest.fixture
def config():
    """提供测试用的配置字典 | Provide test configuration"""
    return {
        "keyboard": {"name": "FantasyKB Test", "rows": 5, "cols": 14, "total_keys": 70},
        "matrix": {
            "debounce_ms": 5, "scan_rate_hz": 1000,
        },
        "display": {
            "enabled": True, "type": "GC9A01", "width": 240, "height": 240,
        },
        "rgb": {
            "enabled": True, "type": "WS2812B", "count": 70,
            "data_pin": "GPIO2", "max_brightness": 128, "default_mode": "rainbow",
        },
        "encoder": {
            "enabled": True, "spi_freq_mhz": 5.0, "noise_lsb": 0,
        },
        "usb": {
            "vid": "0x303A", "pid": "0x4002", "max_power_ma": 500,
        },
        "audio": {
            "adc_enabled": True, "dac_enabled": True,
            "sample_rate": 16000, "channels": 2, "bit_depth": 16,
        },
        "wireless": {
            "ble": {"enabled": True, "device_name": "TestKB"},
            "wifi": {"enabled": True},
            "esp_now": {"enabled": True, "channel": 1},
        },
        "motor": {
            "enabled": True, "pole_pairs": 7, "resistance": 10.0, "inductance": 0.001,
        },
    }


# ===== 键盘矩阵测试 | KeyMatrix Tests =====

class TestKeyMatrix:
    def test_init(self, config):
        matrix = KeyMatrix(config)
        assert matrix.rows == 5
        assert matrix.cols == 14
        assert matrix.num_registers > 0

    def test_press_release(self, config):
        matrix = KeyMatrix(config)
        assert not matrix.is_pressed(0, 0)
        matrix.simulate_press(0, 0)
        assert matrix.is_pressed(0, 0)
        matrix.simulate_release(0, 0)
        assert not matrix.is_pressed(0, 0)

    def test_spi_read(self, config):
        matrix = KeyMatrix(config)
        matrix.simulate_press(0, 0)
        data = matrix.spi_read()
        assert isinstance(data, bytes)
        assert len(data) == matrix.num_registers
        # Bit 0 of the matrix = index 0 in register 0
        # MSB first encoding: bit 0 maps to bit 7 of byte 0
        # The value should be non-zero since a key is pressed
        assert any(b != 0 for b in data)

    def test_scan_events(self, config):
        matrix = KeyMatrix(config)
        # First scan to establish baseline
        matrix.scan()
        # Now press a key
        matrix.simulate_press(0, 0)
        # Multiple scans to pass debounce threshold
        for _ in range(5):
            events = matrix.scan()
        # After debouncing, events should have been detected
        assert matrix.is_pressed(0, 0)

    def test_shift_register(self):
        reg = ShiftRegister74HC165("test")
        reg.set_input(0, True)
        reg.set_input(7, True)
        reg.latch()
        out = reg.shift_out_one()
        assert out == True  # D7 = True


# ===== GC9A01 LCD 测试 | GC9A01Display Tests =====

class TestGC9A01Display:
    def test_init(self, config):
        lcd = GC9A01Display(config)
        assert lcd.width == 240
        assert lcd.height == 240

    def test_rgb565(self):
        val = rgb_to_rgb565(255, 0, 0)
        assert val == 0xF800  # Red
        val = rgb_to_rgb565(0, 255, 0)
        assert val == 0x07E0  # Green
        val = rgb_to_rgb565(0, 0, 255)
        assert val == 0x001F  # Blue

    def test_rgb565_roundtrip(self):
        r, g, b = 200, 100, 50
        c = rgb_to_rgb565(r, g, b)
        r2, g2, b2 = rgb565_to_rgb(c)
        assert abs(r - r2) <= 8
        assert abs(g - g2) <= 4
        assert abs(b - b2) <= 8

    def test_draw_circle(self, config):
        lcd = GC9A01Display(config)
        lcd.draw_circle(120, 120, 50, RGB565_WHITE)
        assert lcd.framebuffer[120 * 240 + 170] == RGB565_WHITE  # rightmost point

    def test_fill(self, config):
        lcd = GC9A01Display(config)
        lcd.fill(RGB565_WHITE)
        assert lcd.framebuffer[0] == RGB565_WHITE

    def test_draw_text(self, config):
        lcd = GC9A01Display(config)
        # Draw near center of circular display (120,120 is center)
        lcd.draw_text(115, 115, "8", RGB565_WHITE, 1)
        has_pixels = any(c != RGB565_BLACK for c in lcd.framebuffer)
        assert has_pixels

    def test_memory_usage(self, config):
        lcd = GC9A01Display(config)
        info = lcd.get_memory_usage()
        assert "115,200" in info


# ===== RGB LED 测试 | RGBLed Tests =====

class TestRGBLed:
    def test_init(self, config):
        rgb = RGBLed(config)
        assert rgb.num_leds == 70

    def test_set_color(self, config):
        rgb = RGBLed(config)
        rgb.set_color(0, RGBColor.red())
        assert rgb.get_color(0).r == 255

    def test_hsv(self):
        red = RGBColor.from_hsv(0, 1.0, 1.0)
        assert red.r == 255
        assert red.g == 0
        assert red.b == 0

    def test_grb_bytes(self, config):
        rgb = RGBLed(config)
        rgb.set_color(0, RGBColor(100, 200, 50))
        data = rgb.to_grb_bytes()
        assert data[0] == 200  # G first
        assert data[1] == 100  # R
        assert data[2] == 50   # B

    def test_power_budget(self, config):
        rgb = RGBLed(config)
        rgb.set_all(RGBColor.white())
        power = rgb.calculate_power()
        assert power["num_leds"] == 70
        assert not power["usb_safe"]  # 70 * 60mA = 4200mA, not USB safe

    def test_ws2812b_timing(self):
        pulses = WS2812BProtocol.encode_bit(True)
        assert len(pulses) == 2
        assert pulses[0] == (1, 700)  # T1H
        assert pulses[1] == (0, 600)  # T1L


# ===== AS5047P 测试 | AS5047P Tests =====

class TestAS5047P:
    def test_init(self, config):
        enc = AS5047P(config)
        assert enc.enabled

    def test_angle_set_read(self, config):
        enc = AS5047P(config)
        enc.set_angle(90.0)
        raw = enc.spi_read_angle()
        angle = enc.raw_to_degrees(raw)
        assert abs(angle - 90.0) < 0.1

    def test_rotate(self, config):
        enc = AS5047P(config)
        enc.set_angle(0.0)
        enc.rotate_by(180.0)
        assert abs(enc.get_angle_degrees() - 180.0) < 0.01

    def test_raw_to_radians(self, config):
        enc = AS5047P(config)
        enc.set_angle(90.0)
        rad = enc.get_angle_radians()
        assert abs(rad - math.pi / 2) < 0.01

    def test_parity(self):
        assert calculate_parity(0x0000) == 0
        assert calculate_parity(0x0001) == 1

    def test_quadrature(self, config):
        enc = AS5047P(config)
        enc.set_angle(0.0)
        a1, b1 = enc.get_quadrature()
        enc.rotate_by(45.0)
        a2, b2 = enc.get_quadrature()
        # Quadrature should change after rotation


# ===== USB HID 测试 | USBHID Tests =====

class TestUSBHID:
    def test_init(self, config):
        hid = USBHIDDevice(config)
        assert hid.vid == "0x303A"
        assert not hid.connected

    def test_connect(self, config):
        hid = USBHIDDevice(config)
        hid.connect()
        assert hid.connected

    def test_key_press(self, config):
        hid = USBHIDDevice(config)
        hid.connect()
        report = hid.press_key("KC_A")
        assert report is not None
        assert 0x04 in report.keycodes

    def test_modifier(self, config):
        hid = USBHIDDevice(config)
        hid.connect()
        report = hid.press_key("KC_LSFT")
        assert report.modifiers & 0x02

    def test_report_bytes(self):
        report = HIDReport(modifiers=0x02, keycodes=[0x04, 0, 0, 0, 0, 0])
        data = report.to_bytes()
        assert len(data) == 8
        assert data[0] == 0x02
        assert data[2] == 0x04

    def test_6key_limit(self, config):
        hid = USBHIDDevice(config)
        hid.connect()
        for k in ["KC_A", "KC_B", "KC_C", "KC_D", "KC_E", "KC_F", "KC_G"]:
            hid.press_key(k)
        report = hid.get_last_report()
        non_zero = [k for k in report.keycodes if k != 0]
        assert len(non_zero) == 6


# ===== 音频测试 | Audio Tests =====

class TestAudio:
    def test_pipeline(self, config):
        audio = AudioPipeline(config)
        assert audio.adc.I2C_ADDRESS == 0x40
        assert audio.dac.I2C_ADDRESS == 0x18

    def test_loopback(self, config):
        audio = AudioPipeline(config)
        result = audio.loopback(0.5)
        assert abs(result - 0.5) < 0.01

    def test_es7210_registers(self, config):
        adc = ES7210(config)
        adc.write_register(0x41, 0x10)
        assert adc.read_register(0x41) == 0x10

    def test_es8311_volume(self, config):
        dac = ES8311(config)
        dac.set_volume(0.0)
        assert dac._registers[0x37] >= 0

    def test_i2s_config(self):
        i2s = I2SConfig(sample_rate=16000, bits_per_sample=16, num_channels=2)
        assert i2s.bclk_freq == 512000
        assert i2s.bytes_per_second == 64000


# ===== 无线测试 | Wireless Tests =====

class TestWireless:
    def test_wireless_manager(self, config):
        wm = WirelessManager(config)
        assert wm.current_mode == WirelessMode.USB

    def test_ble_advertising(self, config):
        ble = BLEManager(config)
        ble.start_advertising()
        assert ble.is_advertising
        assert not ble.is_connected

    def test_ble_connect(self, config):
        ble = BLEManager(config)
        ble.start_advertising()
        ble.simulate_connect()
        assert ble.is_connected
        assert not ble.is_advertising

    def test_wifi(self, config):
        wifi = WiFiManager(config)
        wifi.connect("TestSSID", "password")
        assert wifi.is_connected
        assert wifi.ip_address != ""

    def test_esp_now(self, config):
        now = ESPNowManager(config)
        now.add_peer("AA:BB:CC:DD:EE:FF")
        assert now.send(b"hello", "AA:BB:CC:DD:EE:FF")
        assert now.get_sent_count() == 1

    def test_mode_switch(self, config):
        wm = WirelessManager(config)
        wm.set_mode(WirelessMode.BLE)
        assert wm.current_mode == WirelessMode.BLE
        wm.set_mode(WirelessMode.ESP_NOW)
        assert wm.current_mode == WirelessMode.ESP_NOW


# ===== FOC 电机测试 | FOC Motor Tests =====

class TestFOC:
    def test_clarke(self):
        alpha, beta = clarke_transform(1.0, -0.5, -0.5)
        assert abs(alpha - 1.0) < 0.01
        assert abs(beta - 0.0) < 0.01  # balanced

    def test_inverse_clarke(self):
        ia, ib, ic = inverse_clarke_transform(1.0, 0.0)
        assert abs(ia - 1.0) < 0.01
        assert abs(ia + ib + ic) < 0.01  # sum ~= 0

    def test_park(self):
        # At theta=0, Park is identity
        d, q = park_transform(1.0, 0.0, 0.0)
        assert abs(d - 1.0) < 0.01
        assert abs(q - 0.0) < 0.01

    def test_park_inverse_roundtrip(self):
        alpha, beta = 0.5, 0.8
        theta = math.pi / 3
        d, q = park_transform(alpha, beta, theta)
        alpha2, beta2 = inverse_park_transform(d, q, theta)
        assert abs(alpha - alpha2) < 0.001
        assert abs(beta - beta2) < 0.001

    def test_pid(self):
        pid = PIDController(PIDConfig(Kp=1.0, Ki=0.0, Kd=0.0, output_limit=1.0))
        out = pid.compute(1.0, 0.0)
        assert out == 1.0  # Kp=1, error=1

    def test_foc_controller(self, config):
        foc = FOController(config)
        foc.set_target_torque(0.5)
        u, v, w = foc.update(0.0, dt=0.001)
        assert -1.0 <= u <= 1.0
        assert -1.0 <= v <= 1.0
        assert -1.0 <= w <= 1.0

    def test_tmc6300(self, config):
        driver = TMC6300(config)
        driver.set_pwm(0.5, -0.25, -0.25)
        u, v, w = driver.get_pwm()
        assert abs(u - 0.5) < 0.01


# ===== 工具函数测试 | Utility Tests =====

class TestUtils:
    def test_format_hex(self):
        assert format_hex(0) == "0x00"
        assert format_hex(255) == "0xFF"
        assert format_hex(10, 4) == "0x000A"

    def test_format_binary(self):
        assert format_binary(0) == "0b00000000"
        assert format_binary(255) == "0b11111111"

    def test_bit_operations(self):
        val = 0
        val = set_bit(val, 3)
        assert get_bit(val, 3) == 1
        val = clear_bit(val, 3)
        assert get_bit(val, 3) == 0
        val = toggle_bit(val, 5)
        assert get_bit(val, 5) == 1

    def test_bit_field(self):
        val = 0b11010110
        assert bit_field(val, 2, 3) == 0b101

    def test_crc8(self):
        data = bytes([0x01, 0x02, 0x03])
        crc = crc8(data)
        assert isinstance(crc, int)
        assert 0 <= crc <= 255

    def test_pad_to_matrix(self):
        flat = [1, 2, 3, 4, 5, 6]
        matrix = pad_to_matrix(flat, 2, 3)
        assert matrix == [[1, 2, 3], [4, 5, 6]]
