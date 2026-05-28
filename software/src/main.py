# -*- coding: utf-8 -*-
"""
4模式机械键盘 "幻想键盘" 主程序
4-Mode Mechanical Keyboard "FantasyKB" Main Entry Point

本模块是所有模拟模块的入口，提供以下功能：
1. 加载配置文件
2. 运行所有模块的演示/模拟
3. 运行基础测试
4. 显示硬件信息

This module is the entry point for all simulation modules:
1. Load configuration
2. Run demos/simulations for all modules
3. Run basic tests
4. Display hardware information

最后更新 | Last updated: 2026-05-27
"""

import sys
import argparse
from pathlib import Path

# 导入项目模块
from keymatrix import KeyMatrix, KeyEvent, ShiftRegister74HC165
from oled_display import GC9A01Display, rgb_to_rgb565, RGB565_WHITE, RGB565_CYAN
from rgb_led import RGBLed, RGBColor, WS2812BProtocol, EFFECT_MODES
from encoder import AS5047P, AS5047P_RESOLUTION
from usb_hid import USBHIDDevice, HIDReport, HID_KEYCODES, MODIFIER_MASKS
from audio import AudioPipeline, ES7210, ES8311, I2SConfig
from wireless import WirelessManager, WirelessMode, BLEManager, WiFiManager, ESPNowManager
from foc_motor import FOController, clarke_transform, park_transform, PIDController
from utils import load_config, setup_logging, format_hex, format_binary, crc8


def parse_args():
    """解析命令行参数 | Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="4模式机械键盘工具 | 4-Mode Keyboard Tools"
    )
    parser.add_argument("--config", "-c", type=str, default="config.yaml",
                        help="配置文件路径 | Config file path")
    parser.add_argument("--action", "-a",
                        choices=["test", "demo", "info"],
                        default="demo",
                        help="执行的动作: test/demo/info")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="详细输出 | Verbose output")
    return parser.parse_args()


def show_hardware_info(config: dict):
    """显示硬件配置信息 | Display hardware configuration"""
    kb = config.get("keyboard", {})
    print(f"=== {kb.get('name', 'FantasyKB')} ===")
    print(f"矩阵 Matrix: {kb.get('rows', 5)}x{kb.get('cols', 14)}")
    print(f"连接模式 Modes: USB / BLE / WiFi / 2.4GHz")
    print()

    # 矩阵
    matrix_cfg = config.get("matrix", {})
    print(f"[矩阵扫描 Matrix] SPI + 74HC165 x5 + 74HC138 x2")
    print(f"  消抖 Debounce: {matrix_cfg.get('debounce_ms', 5)}ms")
    print()

    # LCD
    print(f"[圆形LCD] GC9A01 240x240 RGB565 via SPI")
    print()

    # RGB
    rgb_cfg = config.get("rgb", {})
    print(f"[RGB] WS2812B x{rgb_cfg.get('count', 70)} via RMT")
    print()

    # 编码器
    print(f"[磁编码器] AS5047P 14-bit via SPI")
    print()

    # 音频
    print(f"[音频] ES7210(ADC) + ES8311(DAC) + NS4150 via I2S")
    print()

    # 无线
    print(f"[无线] BLE + WiFi + ESP-NOW")
    print()

    # FOC
    print(f"[旋钮电机] TMC6300 + 2204 FOC控制")


def run_demo(config: dict):
    """运行所有模块的演示 | Run demos for all modules"""
    print("=" * 60)
    print("  4模式机械键盘模拟演示 | 4-Mode Keyboard Simulation Demo")
    print("=" * 60)
    print()

    # 1. 键扫描演示
    print("--- 1. 键盘矩阵扫描 (74HC165) ---")
    matrix = KeyMatrix(config)
    print(f"    矩阵: {matrix.rows}x{matrix.cols}, 移位寄存器: {matrix.num_registers}片")
    matrix.simulate_press(0, 0)
    matrix.simulate_press(1, 2)
    data = matrix.spi_read()
    print(f"    按下 (0,0) 和 (1,2) 后 SPI 数据: {data.hex()}")
    events = matrix.scan()
    print(f"    扫描事件: {len(events)} 个按键变化")
    print(f"    {matrix.get_state_string()}")
    print()

    # 2. LCD 演示
    print("--- 2. GC9A01 圆形 LCD ---")
    lcd = GC9A01Display(config)
    print(f"    分辨率: {lcd.width}x{lcd.height}, 内存: {lcd.get_memory_usage()}")
    lcd.draw_filled_circle(120, 120, 50, RGB565_CYAN)
    lcd.draw_text(100, 115, "FOC", RGB565_WHITE, 2)
    init_log = lcd.init_sequence()
    print(f"    初始化命令数: {len(init_log)}")
    print()

    # 3. RGB LED 演示
    print("--- 3. WS2812B RGB LED ---")
    rgb = RGBLed(config)
    print(f"    LED 数量: {rgb.num_leds}, 模式: {rgb.effect_mode}")
    rgb.set_effect("rainbow")
    rgb.update_effect()
    power = rgb.calculate_power()
    print(f"    功率: {power['power_watts']:.2f}W, 电流: {power['total_current_ma']:.0f}mA")
    print(f"    USB 安全: {'是' if power['usb_safe'] else '否'}")
    transfer_time = WS2812BProtocol.calculate_transfer_time(rgb.num_leds)
    print(f"    传输时间: {transfer_time:.0f}us")
    print()

    # 4. 磁编码器演示
    print("--- 4. AS5047P 磁编码器 ---")
    enc = AS5047P(config)
    enc.set_angle(90.0)
    raw = enc.spi_read_angle()
    angle = enc.raw_to_degrees(raw)
    print(f"    设置 90.0 度, 读取: {angle:.2f} 度 (原始值: 0x{raw:04X})")
    enc.rotate_by(45.0)
    raw2 = enc.spi_read_angle()
    angle2 = enc.raw_to_degrees(raw2)
    print(f"    旋转 +45 度后: {angle2:.2f} 度")
    print()

    # 5. USB HID 演示
    print("--- 5. USB HID 键盘 ---")
    hid = USBHIDDevice(config)
    hid.connect()
    report = hid.press_key("KC_A")
    print(f"    按下 A 键: {report}")
    data = report.to_bytes()
    print(f"    8 字节报告: {' '.join(f'0x{b:02X}' for b in data)}")
    hid.release_key("KC_A")
    print()

    # 6. 音频管线演示
    print("--- 6. 音频管线 (ES7210 + ES8311) ---")
    audio = AudioPipeline(config)
    result = audio.loopback(0.5)
    print(f"    回环测试: 输入 0.5 → ADC → DAC → 输出 {result:.4f}")
    print(f"    {audio.explain_pipeline()}")
    print()

    # 7. 无线模式演示
    print("--- 7. 无线通信 (BLE/WiFi/ESP-NOW) ---")
    wireless = WirelessManager(config)
    print(f"    当前模式: {wireless.current_mode.value}")
    wireless.set_mode(WirelessMode.BLE)
    print(f"    切换到 BLE: {wireless.ble.is_advertising}")
    wireless.set_mode(WirelessMode.ESP_NOW)
    wireless.esp_now.add_peer("AA:BB:CC:DD:EE:FF")
    wireless.esp_now.send(b'\x00\x00\x04\x00\x00\x00\x00\x00')
    print(f"    ESP-NOW 发送: {wireless.esp_now.get_sent_count()} 包")
    print()

    # 8. FOC 电机演示
    print("--- 8. FOC 无刷电机控制 ---")
    foc = FOController(config)
    foc.set_target_torque(0.5)
    # 模拟电机在 0 度位置
    import math
    u, v, w = foc.update(0.0, dt=0.001)
    print(f"    力矩 0.5 @ 0deg: U={u:.3f} V={v:.3f} W={w:.3f}")
    u2, v2, w2 = foc.update(math.pi / 2, dt=0.001)
    print(f"    力矩 0.5 @ 90deg: U={u2:.3f} V={v2:.3f} W={w2:.3f}")
    print(f"    Clarke(1,0,-1) = {clarke_transform(1.0, 0.0, -1.0)}")
    print()

    print("=" * 60)
    print("  所有演示完成 | All demos complete!")
    print("=" * 60)


def run_basic_test(config: dict):
    """运行基础测试 | Run basic tests"""
    print("=== 运行基础测试 | Running Basic Tests ===\n")

    modules = [
        ("KeyMatrix", lambda: KeyMatrix(config)),
        ("GC9A01Display", lambda: GC9A01Display(config)),
        ("RGBLed", lambda: RGBLed(config)),
        ("AS5047P", lambda: AS5047P(config)),
        ("USBHIDDevice", lambda: USBHIDDevice(config)),
        ("AudioPipeline", lambda: AudioPipeline(config)),
        ("WirelessManager", lambda: WirelessManager(config)),
        ("FOController", lambda: FOController(config)),
    ]

    for name, factory in modules:
        try:
            obj = factory()
            print(f"[PASS] {name}: {obj}")
        except Exception as e:
            print(f"[FAIL] {name}: {e}")

    print("\n所有测试通过！| All tests passed!")


def main():
    """主函数 | Main function"""
    args = parse_args()
    logger = setup_logging(verbose=args.verbose)

    config_path = Path(args.config)
    if not config_path.exists():
        template_path = Path("config.template.yaml")
        if template_path.exists():
            logger.warning(f"Config {config_path} not found, using template")
            config_path = template_path
        else:
            print(f"Error: Config file not found: {config_path}")
            sys.exit(1)

    config = load_config(config_path)

    if args.action == "info":
        show_hardware_info(config)
    elif args.action == "demo":
        run_demo(config)
    elif args.action == "test":
        run_basic_test(config)


if __name__ == "__main__":
    main()
