# -*- coding: utf-8 -*-
"""
I2S 音频管道模拟 (ES7210 + ES8311 + NS4150B)
I2S Audio Pipeline Simulation

音频信号链：
  麦克风x2 -> ES7210 (ADC) -> I2S -> ESP32-S3 -> I2S -> ES8311 (DAC) -> NS4150B x2 -> 扬声器x2

I2S 总线 (Inter-IC Sound):
- BCLK: 位时钟 (Bit Clock)
- WS: 字选择 (Word Select / LRCLK)
- SDI: 串行数据输入 (ESP32 -> ADC读取)
- SDO: 串行数据输出 (ESP32 -> DAC写入)

ES7210 (4通道音频ADC):
- I2C 地址: 0x40
- 采样率: 8kHz ~ 96kHz
- 位深: 16/24位
- 通道: 4输入 (本项目用2通道双麦克风)

ES8311 (音频DAC):
- I2C 地址: 0x18
- 采样率: 8kHz ~ 96kHz
- 位深: 16/24/32位
- 输出: 立体声

NS4150B (D类功放):
- 输入: 差分/单端
- 输出: 桥接负载 (BTL)
- 增益: 由外部电阻设定

Last updated: 2026-05-27
"""

from typing import Tuple, List

class AudioPipeline:
    """
    音频管道模拟 (ES7210 + ES8311 + NS4150B)
    """

    def __init__(self, config: dict):
        audio_cfg = config.get("audio", {})
        self.sample_rate: int = audio_cfg.get("sample_rate", 16000)
        self.channels: int = audio_cfg.get("channels", 2)
        self.bit_depth: int = audio_cfg.get("bit_depth", 16)

        # I2S引脚
        self.i2s_bclk: str = audio_cfg.get("i2s_bclk", "GPIO41")
        self.i2s_ws: str = audio_cfg.get("i2s_ws", "GPIO42")
        self.i2s_sdi: str = audio_cfg.get("i2s_sdi", "GPIO39")  # ADC数据输入
        self.i2s_sdo: str = audio_cfg.get("i2s_sdo", "GPIO40")  # DAC数据输出

        # I2C地址
        self.es7210_addr: int = 0x40  # ADC
        self.es8311_addr: int = 0x18  # DAC

    def read_microphone(self, channel: int = 0) -> List[int]:
        """
        模拟从ES7210读取麦克风数据

        I2S 数据格式 (I2S Philips):
        - WS=0: 左声道
        - WS=1: 右声道
        - 每个采样 = bit_depth 位 (MSB first)
        - BCLK频率 = sample_rate x channels x bit_depth
        """
        return [0] * 160  # 模拟10ms的音频数据

    def write_speaker(self, data: List[int], channel: int = 0) -> None:
        """
        模拟通过ES8311+NS4150B播放音频

        信号流：
        1. ESP32-S3 将PCM数据写入I2S TX缓冲区
        2. ES8311 通过I2S接收PCM数据
        3. ES8311 DAC将数字信号转换为模拟信号
        4. NS4150B放大模拟信号驱动扬声器
        """
        pass

    def get_i2s_timing(self) -> str:
        """I2S时序图（教学用）"""
        bclk_freq = self.sample_rate * self.channels * self.bit_depth
        return (
            f"I2S 时序参数:\n"
            f"  采样率: {self.sample_rate} Hz\n"
            f"  通道数: {self.channels}\n"
            f"  位深: {self.bit_depth} bit\n"
            f"  BCLK频率: {bclk_freq:,} Hz ({bclk_freq/1e6:.2f} MHz)\n"
            f"  WS频率: {self.sample_rate} Hz\n"
            f"\n"
            f"BCLK: _|‾|_|‾|_|‾|_|‾|_|‾|_|‾|_...\n"
            f"WS:   ‾‾‾‾‾‾‾‾‾‾‾‾|___________|\n"
            f"SDI:  <--- 左声道 ---><--- 右声道 --->\n"
        )

    def get_codec_config_example(self) -> str:
        """ES7210/ES8311 I2C配置示例"""
        return (
            f"I2C 配置示例:\n"
            f"ES7210 (ADC @ 0x{self.es7210_addr:02X}):\n"
            f"  REG 0x00 = 0x00  # 复位\n"
            f"  REG 0x01 = 0x20  # 时钟管理\n"
            f"  REG 0x03 = 0x00  # ADC1输入选择 = MIC1P/MIC1N\n"
            f"  REG 0x04 = 0x01  # ADC2输入选择 = MIC2P/MIC2N\n"
            f"  REG 0x06 = 0x03  # ADC1+ADC2 使能\n"
            f"\n"
            f"ES8311 (DAC @ 0x{self.es8311_addr:02X}):\n"
            f"  REG 0x00 = 0x80  # 复位\n"
            f"  REG 0x01 = 0x00  # 时钟管理\n"
            f"  REG 0x04 = 0x14  # DAC音量 = 20\n"
            f"  REG 0x0D = 0x01  # ADC/DAC使能\n"
        )

    def __repr__(self) -> str:
        return f"AudioPipeline({self.sample_rate}Hz, {self.channels}ch, {self.bit_depth}bit)"
