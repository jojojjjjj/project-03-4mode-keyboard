# -*- coding: utf-8 -*-
"""
音频管线模拟模块
Audio Pipeline Simulation Module

本项目使用 ES7210 (ADC) 和 ES8311 (DAC) 构建音频输入/输出管线，
通过 I2S 总线与 ESP32-S3 交换音频数据。
本模块模拟 I2S 总线时序、ADC/DAC 配置和音频信号流。

This project uses ES7210 (ADC) and ES8311 (DAC) to build an audio I/O pipeline,
exchanging audio data with ESP32-S3 via the I2S bus.
This module simulates I2S bus timing, ADC/DAC configuration, and audio signal flow.

=== I2S 总线简介 | I2S Bus Overview ===

I2S (Inter-IC Sound) 是飞利浦定义的数字音频传输标准：
  - 三线制：BCLK (位时钟)、WS/LRCK (声道选择)、SDI/SDO (数据)
  - BCLK频率 = 采样率 x 声道数 x 位深
  - WS=0 左声道, WS=1 右声道
  - ESP32-S3 有两个 I2S 外设 (I2S0, I2S1)

=== 音频信号链 | Audio Signal Chain ===

录音 Recording:
  麦克风 -> 模拟信号 -> ES7210 (ADC) -> I2S -> ESP32-S3

播放 Playback:
  ESP32-S3 -> I2S -> ES8311 (DAC) -> NS4150B (功放) -> 扬声器

最后更新 | Last updated: 2026-05-27
"""

from typing import List, Dict
from dataclasses import dataclass


@dataclass
class I2SConfig:
    """
    I2S 总线配置
    I2S bus configuration
    """
    sample_rate: int = 16000
    bits_per_sample: int = 16
    num_channels: int = 2
    bclk_pin: str = "GPIO4"
    ws_pin: str = "GPIO5"
    sdi_pin: str = "GPIO6"     # 数据输入 (ADC -> ESP32)
    sdo_pin: str = "GPIO7"     # 数据输出 (ESP32 -> DAC)

    @property
    def bclk_freq(self) -> int:
        """BCLK 频率 = 采样率 x 位深 x 声道数"""
        return self.sample_rate * self.bits_per_sample * self.num_channels

    @property
    def bytes_per_second(self) -> int:
        """每秒数据量"""
        return self.sample_rate * (self.bits_per_sample // 8) * self.num_channels


class ES7210:
    """
    ES7210 4 通道音频 ADC 模拟
    ES7210 4-channel audio ADC simulation

    I2C 地址: 0x40
    功能: 将 4 路模拟音频信号转换为 I2S 数字信号
    24 位 ADC, 信噪比 102dB, 可编程增益放大器 (PGA)
    """

    I2C_ADDRESS = 0x40

    def __init__(self, config: dict):
        audio_cfg = config.get("audio", {})
        self.enabled: bool = audio_cfg.get("adc_enabled", True)
        self._registers: Dict[int, int] = {}
        self._init_defaults()

    def _init_defaults(self) -> None:
        """初始化寄存器默认值 | Initialize register defaults"""
        self._registers = {
            0x00: 0x00, 0x01: 0x3F, 0x02: 0xC1, 0x03: 0x00,
            0x06: 0x00, 0x07: 0x20, 0x08: 0x00,
            0x40: 0x00, 0x41: 0x1B, 0x42: 0x00, 0x43: 0x1B,
        }

    def write_register(self, reg: int, value: int) -> bool:
        """模拟 I2C 写寄存器 | Simulate I2C register write"""
        self._registers[reg] = value & 0xFF
        return True

    def read_register(self, reg: int) -> int:
        """模拟 I2C 读寄存器 | Simulate I2C register read"""
        return self._registers.get(reg, 0x00)

    def set_gain(self, channel: int, gain_db: int) -> None:
        """
        设置 ADC 增益 (0-36dB, 步进 0.75dB)
        Set ADC gain
        """
        if 1 <= channel <= 4:
            reg = 0x40 + (channel - 1) * 2 + 1
            self._registers[reg] = min(int(gain_db / 0.75), 0x3F)

    def simulate_adc(self, analog_signal: float) -> int:
        """
        模拟 ADC: 模拟信号 -> 24 位数字采样
        Simulate ADC: analog signal -> 24-bit digital sample
        """
        analog_signal = max(-1.0, min(1.0, analog_signal))
        return int(analog_signal * 0x7FFFFF)

    def init_sequence(self) -> List[str]:
        """ES7210 初始化命令序列 | ES7210 init command sequence"""
        return [
            "=== ES7210 ADC Init ===",
            f"I2C addr: 0x{self.I2C_ADDRESS:02X}",
            "1. REG 0x00 = 0xFF -> Reset",
            "2. REG 0x00 = 0x32 -> Release reset",
            "3. REG 0x01 = 0x3F -> Enable all clocks",
            "4. REG 0x07 = 0x20 -> I2S 16bit format",
            "5. REG 0x08 = 0x00 -> Slave mode",
            "6. REG 0x41 = 0x1B -> ADC1 gain 27dB",
            "7. REG 0x10 = 0x10 -> Enable analog power",
        ]


class ES8311:
    """
    ES8311 音频 DAC 模拟
    ES8311 Audio DAC simulation

    I2C 地址: 0x18
    功能: 将 I2S 数字信号转换为模拟音频
    24 位 DAC, 信噪比 100dB, 内置耳机放大器
    """

    I2C_ADDRESS = 0x18

    def __init__(self, config: dict):
        audio_cfg = config.get("audio", {})
        self.enabled: bool = audio_cfg.get("dac_enabled", True)
        self._registers: Dict[int, int] = {}
        self._init_defaults()

    def _init_defaults(self) -> None:
        self._registers = {
            0x00: 0x00, 0x01: 0x7F, 0x02: 0x80,
            0x0A: 0x0C, 0x0B: 0x00, 0x0F: 0x40,
            0x33: 0x04, 0x37: 0x00, 0x4C: 0x01,
        }

    def write_register(self, reg: int, value: int) -> bool:
        """模拟 I2C 写寄存器 | Simulate I2C register write"""
        self._registers[reg] = value & 0xFF
        return True

    def read_register(self, reg: int) -> int:
        """模拟 I2C 读寄存器 | Simulate I2C register read"""
        return self._registers.get(reg, 0x00)

    def set_volume(self, volume_db: float) -> None:
        """
        设置 DAC 音量 (-95.5 到 +32 dB, 步进 0.5dB)
        Set DAC volume
        """
        reg_val = max(0, min(255, int((-volume_db + 32) / 0.5)))
        self._registers[0x37] = reg_val

    def simulate_dac(self, digital_sample: int) -> float:
        """
        模拟 DAC: 24 位数字采样 -> 模拟信号 (-1.0 到 +1.0)
        Simulate DAC: 24-bit digital -> analog
        """
        return max(-1.0, min(1.0, digital_sample / 0x7FFFFF))

    def init_sequence(self) -> List[str]:
        """ES8311 初始化序列 | ES8311 init sequence"""
        return [
            "=== ES8311 DAC Init ===",
            f"I2C addr: 0x{self.I2C_ADDRESS:02X}",
            "1. REG 0x00 = 0x80 -> Reset",
            "2. REG 0x00 = 0x00 -> Release reset",
            "3. REG 0x01 = 0x7F -> Enable clocks",
            "4. REG 0x0A = 0x0C -> I2S 16bit input",
            "5. REG 0x0F = 0x40 -> Select DAC path",
            "6. REG 0x37 = 0x00 -> Volume max",
            "7. REG 0x4C = 0x01 -> Enable HP driver",
        ]


class AudioPipeline:
    """
    音频管线模拟类
    Audio Pipeline Simulator

    完整信号流 Complete signal flow:
    Mic -> ES7210(ADC) -> I2S -> ESP32-S3 -> I2S -> ES8311(DAC) -> NS4150B -> Speaker
    """

    def __init__(self, config: dict):
        self.i2s_config = I2SConfig()
        self.adc = ES7210(config)
        self.dac = ES8311(config)

    def read_microphone(self, channel: int = 0) -> List[int]:
        """
        模拟从 ES7210 读取麦克风数据
        Simulate reading mic data from ES7210

        I2S 数据格式 I2S data format:
        WS=0: 左声道, WS=1: 右声道
        每个采样 = bit_depth 位 (MSB first)
        """
        return [0] * 160

    def write_speaker(self, data: List[int], channel: int = 0) -> None:
        """
        模拟通过 ES8311+NS4150B 播放音频
        Simulate playing audio via ES8311+NS4150B

        信号流 Signal flow:
        1. ESP32-S3 将 PCM 数据写入 I2S TX 缓冲区
        2. ES8311 通过 I2S 接收 PCM 数据
        3. ES8311 DAC 将数字信号转换为模拟信号
        4. NS4150B 放大模拟信号驱动扬声器
        """
        pass

    def record_sample(self, analog_input: float) -> int:
        """模拟录音: 模拟 -> ADC -> 数字 | Simulate recording"""
        return self.adc.simulate_adc(analog_input)

    def play_sample(self, digital_sample: int) -> float:
        """模拟播放: 数字 -> DAC -> 模拟 | Simulate playback"""
        return self.dac.simulate_dac(digital_sample)

    def loopback(self, analog_input: float) -> float:
        """回环测试: 录音 -> 播放 | Loopback: record -> playback"""
        digital = self.record_sample(analog_input)
        return self.play_sample(digital)

    def get_i2s_timing(self) -> str:
        """I2S 时序图（教学用）| I2S timing diagram for teaching"""
        bclk_freq = self.i2s_config.bclk_freq
        return (
            f"I2S Timing:\n"
            f"  Sample rate: {self.i2s_config.sample_rate} Hz\n"
            f"  Channels: {self.i2s_config.num_channels}\n"
            f"  Bit depth: {self.i2s_config.bits_per_sample} bit\n"
            f"  BCLK: {bclk_freq:,} Hz ({bclk_freq / 1e6:.2f} MHz)\n"
            f"  WS: {self.i2s_config.sample_rate} Hz\n"
            f"\n"
            f"BCLK: _|\\u2574|_|\\u2574|_|\\u2574|_|\\u2574|_|\\u2574|_|\\u2574|_...\n"
            f"WS:   \\u2575\\u2575\\u2575\\u2575\\u2575\\u2575\\u2575\\u2575\\u2575\\u2575\\u2575|___________|\n"
            f"SDI:  <--- Left ch ---><--- Right ch --->\n"
        )

    def get_codec_config_example(self) -> str:
        """ES7210/ES8311 I2C 配置示例 | Codec config example"""
        return (
            f"ES7210 (ADC @ 0x{self.adc.I2C_ADDRESS:02X}):\n"
            f"  REG 0x00 = 0x00  # Reset\n"
            f"  REG 0x01 = 0x20  # Clock manager\n"
            f"  REG 0x03 = 0x00  # ADC1 input = MIC1P/MIC1N\n"
            f"  REG 0x06 = 0x03  # Enable ADC1+ADC2\n"
            f"\n"
            f"ES8311 (DAC @ 0x{self.dac.I2C_ADDRESS:02X}):\n"
            f"  REG 0x00 = 0x80  # Reset\n"
            f"  REG 0x01 = 0x00  # Clock manager\n"
            f"  REG 0x04 = 0x14  # DAC volume = 20\n"
            f"  REG 0x0D = 0x01  # Enable ADC/DAC\n"
        )

    def explain_pipeline(self) -> str:
        """音频管线说明 | Audio pipeline explanation"""
        return (
            "=== Audio Signal Flow ===\n"
            "Recording: Mic -> Analog -> ES7210(ADC) -> I2S -> ESP32-S3\n"
            "Playback:  ESP32-S3 -> I2S -> ES8311(DAC) -> NS4150B -> Speaker\n"
            f"ADC I2C: 0x{self.adc.I2C_ADDRESS:02X}  DAC I2C: 0x{self.dac.I2C_ADDRESS:02X}\n"
            f"Sample rate: {self.i2s_config.sample_rate} Hz\n"
            f"BCLK: {self.i2s_config.bclk_freq:,} Hz\n"
        )

    def __repr__(self) -> str:
        return (f"AudioPipeline(ADC=0x{self.adc.I2C_ADDRESS:02X}, "
                f"DAC=0x{self.dac.I2C_ADDRESS:02X}, "
                f"SR={self.i2s_config.sample_rate}Hz)")
