# -*- coding: utf-8 -*-
"""
4模式机械键盘 "幻想键盘" 主程序
4-Mode Mechanical Keyboard "FantasyKB" Main Entry Point

PC端协议模拟与测试工具，用于学习以下硬件协议：
1. 74HC165 移位寄存器 SPI 键扫描
2. GC9A01 圆形 LCD 显示驱动
3. WS2812B RGB LED 控制
4. AS5047P 磁编码器角度读取
5. ES7210/ES8311 I2S 音频管道
6. TMC6300 FOC 电机控制
7. USB HID 键盘协议
8. WiFi/BLE/ESP-NOW 无线通信

Last updated: 2026-05-27
"""

import sys
import argparse
from pathlib import Path

from keymatrix import ShiftRegisterScanner
from oled_display import GC9A01Display
from rgb_led import WS2812BController
from encoder import AS5047PEncoder
from usb_hid import HIDKeyboard
from audio import AudioPipeline
from wireless import WirelessManager
from foc_motor import FOCMotorController
from utils import load_config, setup_logging


def parse_args():
    parser = argparse.ArgumentParser(
        description="幻想键盘 FantasyKB 协议模拟工具"
    )
    parser.add_argument("--config", "-c", type=str, default="config.yaml")
    parser.add_argument("--action", "-a",
        choices=["test", "demo", "info"],
        default="test"
    )
    parser.add_argument("--module", "-m",
        choices=["all", "keys", "display", "rgb", "encoder", "audio", "motor", "hid", "wireless"],
        default="all"
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    return parser.parse_args()


def show_keyboard_info(config: dict):
    """显示键盘硬件配置信息"""
    kb = config.get("keyboard", {})
    print(f"=== {kb.get('name', 'FantasyKB')} ===")
    print(f"连接模式: USB / BLE / WiFi / ESP-NOW")
    print(f"按键数: {kb.get('total_keys', 75)}")
    print(f"移位寄存器: {kb.get('shift_registers', 10)}x 74HC165")
    print(f"RGB LED: {config.get('rgb', {}).get('count', 95)}x WS2812B")
    print(f"显示屏: GC9A01 1.28\" 240x240")
    print(f"旋钮: TMC6300 FOC + AS5047P")
    print(f"音频: ES7210 + ES8311 + NS4150B x2")
    print(f"PCB: 12块 (4x4层 + 8x2层)")
    print()


def run_module_test(module_name: str, config: dict):
    """运行单个模块测试"""
    if module_name in ("all", "keys"):
        scanner = ShiftRegisterScanner(config)
        print(f"[PASS] 74HC165扫描器: {scanner.num_chips}片, {scanner.total_keys}键")
    if module_name in ("all", "display"):
        display = GC9A01Display(config)
        print(f"[PASS] GC9A01显示: {display.width}x{display.height}")
    if module_name in ("all", "rgb"):
        rgb = WS2812BController(config)
        print(f"[PASS] WS2812B: {rgb.num_leds}颗LED")
    if module_name in ("all", "encoder"):
        enc = AS5047PEncoder(config)
        print(f"[PASS] AS5047P编码器: {enc.resolution}位, 角度={enc.read_angle():.1f}°")
    if module_name in ("all", "audio"):
        audio = AudioPipeline(config)
        print(f"[PASS] 音频管道: {audio.sample_rate}Hz, {audio.channels}通道")
    if module_name in ("all", "motor"):
        motor = FOCMotorController(config)
        print(f"[PASS] FOC电机: 目标角度={motor.target_angle:.1f}°")
    if module_name in ("all", "hid"):
        hid = HIDKeyboard(config)
        print(f"[PASS] USB HID: {hid.max_keys}键同时按下")
    if module_name in ("all", "wireless"):
        wl = WirelessManager(config)
        modes = wl.get_available_modes()
        print(f"[PASS] 无线: {', '.join(modes)}")


def run_demo(config: dict):
    """运行交互式演示"""
    print("=== 幻想键盘协议演示 ===")
    print()

    scanner = ShiftRegisterScanner(config)
    display = GC9A01Display(config)
    rgb = WS2812BController(config)
    enc = AS5047PEncoder(config)

    print("--- 74HC165 移位寄存器扫描演示 ---")
    scanner.simulate_key_press(0)
    scanner.simulate_key_press(42)
    scan_result = scanner.scan()
    print(f"检测到 {len(scan_result)} 个按键事件")
    for event in scan_result[:5]:
        print(f"  键{event['key_index']}: {'按下' if event['pressed'] else '释放'}")
    print()

    print("--- GC9A01 圆形LCD演示 ---")
    display.draw_circle(120, 120, 100, color=(0, 255, 0))
    display.draw_text(80, 110, "FantasyKB", color=(255, 255, 255))
    print(f"帧缓冲区: {display.width}x{display.height} = {len(display.framebuffer)} 像素")
    print()

    print("--- WS2812B RGB演示 ---")
    rgb.set_all(255, 0, 0)
    print(f"已设置全部 {rgb.num_leds} 颗LED为红色")
    rgb.set_rainbow()
    print("已设置彩虹效果")
    print()

    print("--- AS5047P 磁编码器演示 ---")
    for i in range(5):
        angle = enc.read_angle()
        velocity = enc.get_velocity()
        print(f"  角度: {angle:7.2f}° | 角速度: {velocity:6.1f}°/s")
    print()

    print("演示完成！")


def main():
    args = parse_args()
    logger = setup_logging(verbose=args.verbose)

    config_path = Path(args.config)
    if not config_path.exists():
        config_path = Path("config.template.yaml")

    config = load_config(config_path)

    if args.action == "info":
        show_keyboard_info(config)
    elif args.action == "test":
        print("=== 幻想键盘 FantasyKB 模块测试 ===\n")
        run_module_test(args.module, config)
        print("\n所有测试通过！| All tests passed!")
    elif args.action == "demo":
        run_demo(config)


if __name__ == "__main__":
    main()
