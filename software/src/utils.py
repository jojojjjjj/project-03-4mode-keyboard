# -*- coding: utf-8 -*-
"""
工具函数模块
Utility Functions Module

提供项目通用的辅助功能：配置加载、日志设置、位操作、CRC、格式化工具。

Provides common utility functions: config loading, logging, bit manipulation,
CRC, formatting tools.

最后更新 | Last updated: 2026-05-27
"""

import logging
import sys
from pathlib import Path
from typing import Optional, List

import yaml


# === 配置加载 | Configuration Loading ===

def load_config(path: Path) -> dict:
    """
    加载 YAML 配置文件
    Load YAML configuration file

    参数 Args:
        path: 配置文件路径 | Config file path

    返回 Returns:
        dict: 配置字典 | Configuration dictionary
    """
    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config or {}


def setup_logging(verbose: bool = False) -> logging.Logger:
    """
    设置日志系统
    Setup logging system

    参数 Args:
        verbose: 是否详细输出 | Enable verbose output

    返回 Returns:
        logging.Logger: 配置好的日志器
    """
    logger = logging.getLogger("fantasykb")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG if verbose else logging.INFO)
        formatter = logging.Formatter("[%(levelname)s] %(message)s", datefmt="%H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


# === 格式化工具 | Formatting Tools ===

def format_hex(value: int, width: int = 2) -> str:
    """格式化为十六进制字符串 | Format as hex string"""
    return f"0x{value:0{width}X}"


def format_binary(value: int, width: int = 8) -> str:
    """格式化为二进制字符串 | Format as binary string"""
    return f"0b{value:0{width}b}"


# === 位操作工具 | Bit Manipulation Tools ===

def set_bit(value: int, bit: int) -> int:
    """设置指定位为 1 | Set specified bit to 1"""
    return value | (1 << bit)


def clear_bit(value: int, bit: int) -> int:
    """清除指定位为 0 | Clear specified bit to 0"""
    return value & ~(1 << bit)


def toggle_bit(value: int, bit: int) -> int:
    """翻转指定位 | Toggle specified bit"""
    return value ^ (1 << bit)


def get_bit(value: int, bit: int) -> int:
    """获取指定位的值 | Get specified bit value"""
    return (value >> bit) & 1


def bit_field(value: int, start: int, width: int) -> int:
    """
    提取位域
    Extract bit field

    参数 Args:
        value: 原始值 | Original value
        start: 起始位 | Start bit
        width: 位宽 | Bit width

    返回 Returns:
        int: 提取的位域值 | Extracted bit field
    """
    mask = (1 << width) - 1
    return (value >> start) & mask


# === CRC 校验 | CRC Checksum ===

def crc8(data: bytes, polynomial: int = 0x07, init: int = 0x00) -> int:
    """
    CRC-8 校验计算
    CRC-8 checksum calculation

    常用于 SPI 通信中的数据校验。
    Commonly used for data verification in SPI communication.

    参数 Args:
        data: 输入数据 | Input data
        polynomial: CRC 多项式 | CRC polynomial (default: 0x07 for CRC-8/ITU)
        init: 初始值 | Initial value

    返回 Returns:
        int: CRC-8 校验值 | CRC-8 checksum
    """
    crc = init
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ polynomial
            else:
                crc <<= 1
            crc &= 0xFF
    return crc


# === 矩阵工具 | Matrix Tools ===

def pad_to_matrix(flat_list: list, rows: int, cols: int, fill=None) -> list:
    """
    将一维列表转换为二维矩阵
    Convert flat list to 2D matrix
    """
    matrix = []
    for r in range(rows):
        row = []
        for c in range(cols):
            idx = r * cols + c
            row.append(flat_list[idx] if idx < len(flat_list) else fill)
        matrix.append(row)
    return matrix


def generate_keymap_table(keymap: list, layer_names: list = None) -> str:
    """
    生成键位映射的 ASCII 表格
    Generate ASCII table of keymap
    """
    lines = []
    for layer_idx, layer in enumerate(keymap):
        name = layer_names[layer_idx] if layer_names and layer_idx < len(layer_names) else f"Layer {layer_idx}"
        lines.append(f"\n=== {name} ===")
        keys = layer.get("keys", []) if isinstance(layer, dict) else layer
        for row in keys:
            line = " | ".join(f"{k:>8}" for k in row)
            lines.append(f"| {line} |")
        lines.append("")
    return "\n".join(lines)


# === SPI 工具 | SPI Utilities ===

def spi_word(addr: int, data: int = 0, write: bool = False) -> int:
    """
    构建 SPI 命令字
    Build SPI command word

    参数 Args:
        addr: 寄存器地址 (14 bit) | Register address
        data: 数据 | Data
        write: 是否写操作 | Write operation

    返回 Returns:
        int: 16 位 SPI 命令字 | 16-bit SPI command word
    """
    cmd = (addr & 0x3FFF)
    if write:
        cmd |= (1 << 15)
    return cmd


def swap_bytes(value: int) -> int:
    """交换 16 位值的高低字节 | Swap high and low bytes of 16-bit value"""
    return ((value & 0xFF) << 8) | ((value >> 8) & 0xFF)
