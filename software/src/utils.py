# -*- coding: utf-8 -*-
"""
工具函数 | Utility Functions

Last updated: 2026-05-27
"""

import logging
import yaml
from pathlib import Path
from typing import Any, Dict


def load_config(config_path: Path) -> Dict[str, Any]:
    """加载YAML配置文件"""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def setup_logging(verbose: bool = False) -> logging.Logger:
    """设置日志"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    return logging.getLogger("FantasyKB")


def bytes_to_hex(data: bytes) -> str:
    """字节数组转十六进制字符串"""
    return " ".join(f"{b:02X}" for b in data)


def bit_set(value: int, bit: int) -> bool:
    """检查指定位是否为1"""
    return bool(value & (1 << bit))


def angle_normalize(angle: float) -> float:
    """角度归一化到 0-360"""
    return angle % 360


def lerp(a: float, b: float, t: float) -> float:
    """线性插值"""
    return a + (b - a) * max(0.0, min(1.0, t))
