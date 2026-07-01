"""
Logging module for RGB PoC
===========================
Ghi log chi tiết ra file để debug khi gặp vấn đề.
Log file: poc-rgb-test/rgb_debug.log
"""

import logging
import os
import sys
import datetime

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rgb_debug.log")


def setup_logger(name="rgb_poc"):
    """Setup logger that writes to both console and file."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Clear existing handlers
    logger.handlers.clear()

    # File handler — ghi TẤT CẢ chi tiết (DEBUG level)
    file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_format)

    # Console handler — chỉ hiện INFO trở lên
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_format)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def log_session_start(logger, script_name):
    """Log session header."""
    logger.info("")
    logger.info("=" * 60)
    logger.info(f"  SESSION START: {script_name}")
    logger.info(f"  Time: {datetime.datetime.now().isoformat()}")
    logger.info(f"  Python: {sys.version}")
    logger.info(f"  Platform: {sys.platform}")
    logger.info(f"  Working Dir: {os.getcwd()}")
    logger.info("=" * 60)
    logger.info("")


def log_nvapi_status(logger, operation, status, extra=""):
    """Log NvAPI call result with status code interpretation."""
    status_names = {
        0: "NVAPI_OK",
        -1: "NVAPI_ERROR",
        -2: "NVAPI_LIBRARY_NOT_FOUND",
        -3: "NVAPI_NO_IMPLEMENTATION",
        -4: "NVAPI_API_NOT_INITIALIZED",
        -5: "NVAPI_INVALID_ARGUMENT",
        -6: "NVAPI_NVIDIA_DEVICE_NOT_FOUND",
        -7: "NVAPI_END_ENUMERATION",
        -14: "NVAPI_INVALID_HANDLE",
        -15: "NVAPI_INCOMPATIBLE_STRUCT_VERSION",
        -22: "NVAPI_EXPECTED_PHYSICAL_GPU_HANDLE",
        -56: "NVAPI_I2C_SPEED_NOT_SUPPORTED",
        -100: "NVAPI_TIMEOUT",
    }
    status_name = status_names.get(status, f"UNKNOWN_STATUS_{status}")

    if status == 0:
        logger.debug(f"[OK] {operation} → {status_name} {extra}")
    else:
        logger.warning(f"[FAIL] {operation} → {status_name} (code={status}) {extra}")


def log_i2c_operation(logger, op_type, address, port, reg, data, status):
    """Log detailed I2C operation."""
    reg_hex = f"reg=[{', '.join(f'0x{b:02X}' for b in reg)}]" if reg else "reg=[]"
    data_hex = f"data=[{', '.join(f'0x{b:02X}' for b in data)}]" if data else "data=[]"

    logger.debug(
        f"I2C {op_type} | addr=0x{address:02X} | port={port} | "
        f"{reg_hex} | {data_hex} | status={status}"
    )
