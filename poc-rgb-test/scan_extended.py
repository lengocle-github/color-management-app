"""
Extended I2C Scanner — Try ALL possible configurations
======================================================
Tries different speeds, ports, displayMasks, and read vs write detection.

Run as Administrator!
Usage: python scan_extended.py
"""

import sys
import ctypes
from ctypes import c_ubyte, c_uint32, POINTER, byref, sizeof, c_void_p, c_int
from nvapi_i2c import (
    create_nvapi, NvAPI, NV_I2C_INFO_V3, NVAPI_OK,
    NVAPI_I2C_SPEED_DEFAULT, NVAPI_I2C_SPEED_3KHZ,
    NVAPI_I2C_SPEED_10KHZ, NVAPI_I2C_SPEED_33KHZ,
    NVAPI_I2C_SPEED_100KHZ, NVAPI_I2C_SPEED_200KHZ,
    NVAPI_I2C_SPEED_400KHZ
)
from logger import setup_logger, log_session_start

log = setup_logger("scan_ext")

SPEEDS = [
    ("DEFAULT", NVAPI_I2C_SPEED_DEFAULT),
    ("3KHz", NVAPI_I2C_SPEED_3KHZ),
    ("10KHz", NVAPI_I2C_SPEED_10KHZ),
    ("33KHz", NVAPI_I2C_SPEED_33KHZ),
    ("100KHz", NVAPI_I2C_SPEED_100KHZ),
    ("200KHz", NVAPI_I2C_SPEED_200KHZ),
    ("400KHz", NVAPI_I2C_SPEED_400KHZ),
]

# Addresses most likely to be LED controllers
LED_ADDRESSES = list(range(0x08, 0x78))


def scan_with_write(api, gpu, addr, speed, port, use_port_id):
    """Try detecting device by writing empty data."""
    reg_buf = (c_ubyte * 1)(0x00)
    data_buf = (c_ubyte * 1)(0x00)

    i2c_info = NV_I2C_INFO_V3()
    i2c_info.version = sizeof(NV_I2C_INFO_V3) | (3 << 16)
    i2c_info.displayMask = 0 if use_port_id else 1
    i2c_info.bIsDDCPort = 0
    i2c_info.i2cDevAddress = addr << 1
    i2c_info.pbI2cRegAddress = ctypes.cast(reg_buf, POINTER(c_ubyte))
    i2c_info.regAddrSize = 1
    i2c_info.pbData = ctypes.cast(data_buf, POINTER(c_ubyte))
    i2c_info.cbSize = 0  # zero-length write = probe
    i2c_info.i2cSpeed = speed
    i2c_info.i2cSpeedKhz = 100
    i2c_info.portId = port
    i2c_info.bIsPortIdSet = 1 if use_port_id else 0

    try:
        func = ctypes.CFUNCTYPE(c_int, c_void_p, POINTER(NV_I2C_INFO_V3), POINTER(c_uint32))(
            api._get_func(0x283AC65A)  # NVAPI_I2CWRITEEX
        )
        unknown = c_uint32(0)
        status = func(gpu, byref(i2c_info), byref(unknown))
        return status
    except Exception:
        return -999


def scan_with_read(api, gpu, addr, speed, port, use_port_id):
    """Try detecting device by reading 1 byte."""
    reg_buf = (c_ubyte * 1)(0x00)
    data_buf = (c_ubyte * 1)(0x00)

    i2c_info = NV_I2C_INFO_V3()
    i2c_info.version = sizeof(NV_I2C_INFO_V3) | (3 << 16)
    i2c_info.displayMask = 0 if use_port_id else 1
    i2c_info.bIsDDCPort = 0
    i2c_info.i2cDevAddress = (addr << 1) | 1  # read bit
    i2c_info.pbI2cRegAddress = ctypes.cast(reg_buf, POINTER(c_ubyte))
    i2c_info.regAddrSize = 1
    i2c_info.pbData = ctypes.cast(data_buf, POINTER(c_ubyte))
    i2c_info.cbSize = 1
    i2c_info.i2cSpeed = speed
    i2c_info.i2cSpeedKhz = 100
    i2c_info.portId = port
    i2c_info.bIsPortIdSet = 1 if use_port_id else 0

    try:
        func = ctypes.CFUNCTYPE(c_int, c_void_p, POINTER(NV_I2C_INFO_V3), POINTER(c_uint32))(
            api._get_func(0x4D7B0709)  # NVAPI_I2CREADEX
        )
        unknown = c_uint32(0)
        status = func(gpu, byref(i2c_info), byref(unknown))
        return status, data_buf[0] if status == NVAPI_OK else None
    except Exception:
        return -999, None


def scan_ddc_port(api, gpu, addr, speed):
    """Try with bIsDDCPort = 1 (some GPUs expose I2C via DDC)."""
    reg_buf = (c_ubyte * 1)(0x00)
    data_buf = (c_ubyte * 1)(0x00)

    i2c_info = NV_I2C_INFO_V3()
    i2c_info.version = sizeof(NV_I2C_INFO_V3) | (3 << 16)
    i2c_info.displayMask = 1
    i2c_info.bIsDDCPort = 1
    i2c_info.i2cDevAddress = (addr << 1) | 1
    i2c_info.pbI2cRegAddress = ctypes.cast(reg_buf, POINTER(c_ubyte))
    i2c_info.regAddrSize = 1
    i2c_info.pbData = ctypes.cast(data_buf, POINTER(c_ubyte))
    i2c_info.cbSize = 1
    i2c_info.i2cSpeed = speed
    i2c_info.i2cSpeedKhz = 100
    i2c_info.portId = 0
    i2c_info.bIsPortIdSet = 0

    try:
        func = ctypes.CFUNCTYPE(c_int, c_void_p, POINTER(NV_I2C_INFO_V3), POINTER(c_uint32))(
            api._get_func(0x4D7B0709)  # NVAPI_I2CREADEX
        )
        unknown = c_uint32(0)
        status = func(gpu, byref(i2c_info), byref(unknown))
        return status
    except Exception:
        return -999


def main():
    print("=" * 60)
    print("  EXTENDED I2C Scanner — Colorful iGame RTX 5070")
    print("  Trying ALL combinations of speed/port/method")
    print("=" * 60)
    print()

    log_session_start(log, "scan_extended.py")

    try:
        api, gpus = create_nvapi()
    except RuntimeError as e:
        log.error(f"Init failed: {e}")
        print(f"[ERROR] {e}")
        sys.exit(1)

    gpu = gpus[0]
    found_any = False

    # ===== Method 1: Port-based scan with different speeds =====
    print("\n[1/4] Scanning with PORT ID + WRITE probe...")
    for speed_name, speed_val in SPEEDS:
        for port in range(0, 8):
            hits = []
            for addr in LED_ADDRESSES:
                status = scan_with_write(api, gpu, addr, speed_val, port, use_port_id=True)
                if status == NVAPI_OK:
                    hits.append(addr)
            if hits:
                found_any = True
                msg = f"  FOUND! Speed={speed_name}, Port={port}: {[f'0x{a:02X}' for a in hits]}"
                print(msg)
                log.info(msg)

    # ===== Method 2: Port-based scan with READ =====
    print("\n[2/4] Scanning with PORT ID + READ probe...")
    for speed_name, speed_val in SPEEDS:
        for port in range(0, 8):
            hits = []
            for addr in LED_ADDRESSES:
                status, data = scan_with_read(api, gpu, addr, speed_val, port, use_port_id=True)
                if status == NVAPI_OK:
                    hits.append((addr, data))
            if hits:
                found_any = True
                msg = f"  FOUND! Speed={speed_name}, Port={port}: {[(f'0x{a:02X}', f'data=0x{d:02X}') for a, d in hits]}"
                print(msg)
                log.info(msg)

    # ===== Method 3: DisplayMask-based (no port ID) =====
    print("\n[3/4] Scanning with DISPLAY MASK (no port ID)...")
    for speed_name, speed_val in SPEEDS:
        hits = []
        for addr in LED_ADDRESSES:
            status, data = scan_with_read(api, gpu, addr, speed_val, 0, use_port_id=False)
            if status == NVAPI_OK:
                hits.append((addr, data))
        if hits:
            found_any = True
            msg = f"  FOUND! Speed={speed_name}, DisplayMask: {[(f'0x{a:02X}', f'data=0x{d:02X}') for a, d in hits]}"
            print(msg)
            log.info(msg)

    # ===== Method 4: DDC port =====
    print("\n[4/4] Scanning with DDC port flag...")
    for speed_name, speed_val in SPEEDS:
        hits = []
        for addr in LED_ADDRESSES:
            status = scan_ddc_port(api, gpu, addr, speed_val)
            if status == NVAPI_OK:
                hits.append(addr)
        if hits:
            found_any = True
            msg = f"  FOUND! Speed={speed_name}, DDC: {[f'0x{a:02X}' for a in hits]}"
            print(msg)
            log.info(msg)

    # ===== Summary =====
    print(f"\n{'='*60}")
    if found_any:
        print("  ✅ Device(s) found! Check output above for addresses.")
        print("  Share rgb_debug.log and I'll create a targeted set_blue script.")
    else:
        print("  ❌ No I2C devices found with ANY configuration.")
        print()
        print("  This means one of:")
        print("  1. RTX 5070 Colorful uses USB-based LED control (not I2C)")
        print("  2. LED controller needs a special unlock/init sequence")
        print("  3. NVIDIA driver blocks I2C access on this GPU generation")
        print()
        print("  Next steps:")
        print("  - Check if there's a USB device from Colorful in Device Manager")
        print("  - Try with a different NVIDIA driver version")
        print("  - Check rgb_debug.log for error codes")
    print(f"{'='*60}")
    print(f"\n  📄 Debug log: rgb_debug.log")

    log.info(f"Scan complete. found_any={found_any}")


if __name__ == "__main__":
    main()
