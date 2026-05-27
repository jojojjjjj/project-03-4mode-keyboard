# -*- coding: utf-8 -*-
"""
幻想键盘基础测试套件
FantasyKB Basic Test Suite

Last updated: 2026-05-27
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from keymatrix import ShiftRegisterScanner
from oled_display import GC9A01Display
from rgb_led import WS2812BController
from encoder import AS5047PEncoder
from usb_hid import HIDKeyboard, KEY_A, KEY_ENTER, MOD_LSHIFT
from audio import AudioPipeline
from wireless import WirelessManager, WirelessMode
from foc_motor import FOCMotorController


def _config():
    return {
        "keyboard": {"total_keys": 75, "shift_registers": 10},
        "scanner": {"num_chips": 10},
        "display": {"width": 240, "height": 240},
        "rgb": {"count": 95, "data_pin": "GPIO8", "max_brightness": 128},
        "encoder": {},
        "hid": {"max_keys": 6},
        "audio": {"sample_rate": 16000, "channels": 2, "bit_depth": 16},
        "wireless": {"default_mode": "usb"},
        "motor": {"pole_pairs": 7, "voltage_limit": 5.0},
    }


def test_shift_register_scanner():
    """测试74HC165移位寄存器扫描器"""
    scanner = ShiftRegisterScanner(_config())
    assert scanner.num_chips == 10
    assert scanner.total_keys == 80

    scanner.simulate_key_press(0)
    scanner.simulate_key_press(42)
    events = scanner.scan()
    assert len(events) > 0
    assert any(e.key_index == 0 and e.pressed for e in events)


def test_gc9a01_display():
    """测试GC9A01圆形LCD显示"""
    display = GC9A01Display(_config())
    assert display.width == 240
    assert display.height == 240
    assert len(display.framebuffer) == 240 * 240

    display.draw_pixel(120, 120, (255, 0, 0))
    assert display.framebuffer[120 * 240 + 120] != 0


def test_ws2812b_rgb():
    """测试WS2812B RGB控制"""
    rgb = WS2812BController(_config())
    assert rgb.num_leds == 95

    rgb.set_all(255, 0, 0)
    assert rgb._colors[0] == (128, 0, 0)  # max_brightness=128

    rgb.set_rainbow()
    assert rgb._colors[0] != rgb._colors[47]


def test_as5047p_encoder():
    """测试AS5047P磁编码器"""
    enc = AS5047PEncoder(_config())
    assert enc.resolution == 14
    assert enc.steps_per_rev == 16384

    enc.set_angle(90.0)
    assert abs(enc.read_angle() - 90.0) < 0.1

    raw = enc.read_raw()
    assert 0 <= raw < 16384


def test_usb_hid():
    """测试USB HID键盘协议"""
    hid = HIDKeyboard(_config())

    report = hid.create_report([KEY_A], [MOD_LSHIFT])
    assert len(report) == 8
    assert report[0] == MOD_LSHIFT
    assert report[2] == KEY_A

    decoded = hid.decode_report(report)
    assert "LShift" in decoded
    assert "0x04" in decoded


def test_audio_pipeline():
    """测试音频管道"""
    audio = AudioPipeline(_config())
    assert audio.sample_rate == 16000
    assert audio.channels == 2
    assert audio.bit_depth == 16


def test_wireless_manager():
    """测试无线通信管理"""
    wl = WirelessManager(_config())
    assert wl.current_mode == WirelessMode.USB

    assert wl.switch_mode("ble")
    assert wl.current_mode == WirelessMode.BLE

    modes = wl.get_available_modes()
    assert len(modes) == 4


def test_foc_motor():
    """测试FOC电机控制"""
    motor = FOCMotorController(_config())
    assert motor.pole_pairs == 7

    motor.set_target_angle(90.0)
    assert motor.target_angle == 90.0

    # Clarke变换
    ia, ib = motor.clarke_transform(1.0, -0.5, -0.5)
    assert abs(ia - 1.0) < 0.01

    # Park变换
    id_val, iq_val = motor.park_transform(1.0, 0.0, 0.0)
    assert abs(id_val - 1.0) < 0.01

    # SVPWM
    du, dv, dw = motor.svpwm(0.5, 0.0)
    assert 0 <= du <= 1
    assert 0 <= dv <= 1
    assert 0 <= dw <= 1


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
