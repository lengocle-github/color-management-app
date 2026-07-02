"""
Fix EDID — Restore corrupted EDID on Port 3 device 0x50
========================================================
Script ghi đã corrupt data trên 0x50 port 3.
Cách fix: Ghi lại EDID header đúng hoặc xóa sạch data.

QUAN TRỌNG: Chỉ chạy nếu monitor đang bị lỗi trên 1 cổng cụ thể!

Run as Administrator!
Usage: python fix_edid.py
"""

import sys
import time
import ctypes
from ctypes import c_ubyte, c_uint32, POINTER, byref, sizeof, c_void_p, c_int
from nvapi_i2c import create_nvapi, NV_I2C_INFO_V3, NVAPI_OK
from logger import setup_logger, log_session_start

log = setup_logger("fix_edid")

PORT = 3
ADDR = 0x50


def i2c_write(api, gpu, addr, port, reg_bytes, data_bytes, speed=0):
    """Write to I2C device."""
    reg_size = len(reg_bytes)
    reg_buf = (c_ubyte * max(reg_size, 1))(*reg_bytes) if reg_size > 0 else (c_ubyte * 1)(0)
    data_size = len(data_bytes)
    data_buf = (c_ubyte * max(data_size, 1))(*data_bytes) if data_size > 0 else (c_ubyte * 1)(0)

    i2c_info = NV_I2C_INFO_V3()
    i2c_info.version = sizeof(NV_I2C_INFO_V3) | (3 << 16)
    i2c_info.displayMask = 0
    i2c_info.bIsDDCPort = 0
    i2c_info.i2cDevAddress = addr << 1
    i2c_info.pbI2cRegAddress = ctypes.cast(reg_buf, POINTER(c_ubyte))
    i2c_info.regAddrSize = reg_size
    i2c_info.pbData = ctypes.cast(data_buf, POINTER(c_ubyte))
    i2c_info.cbSize = data_size
    i2c_info.i2cSpeed = speed
    i2c_info.i2cSpeedKhz = 100
    i2c_info.portId = port
    i2c_info.bIsPortIdSet = 1

    func = ctypes.CFUNCTYPE(c_int, c_void_p, POINTER(NV_I2C_INFO_V3), POINTER(c_uint32))(
        api._get_func(0x283AC65A)
    )
    unknown = c_uint32(0)
    status = func(gpu, byref(i2c_info), byref(unknown))
    return status


def i2c_read(api, gpu, addr, port, reg_bytes, read_size, speed=0):
    """Read from I2C device."""
    reg_size = len(reg_bytes)
    reg_buf = (c_ubyte * max(reg_size, 1))(*reg_bytes) if reg_size > 0 else (c_ubyte * 1)(0)
    data_buf = (c_ubyte * read_size)()

    i2c_info = NV_I2C_INFO_V3()
    i2c_info.version = sizeof(NV_I2C_INFO_V3) | (3 << 16)
    i2c_info.displayMask = 0
    i2c_info.bIsDDCPort = 0
    i2c_info.i2cDevAddress = (addr << 1) | 1
    i2c_info.pbI2cRegAddress = ctypes.cast(reg_buf, POINTER(c_ubyte))
    i2c_info.regAddrSize = reg_size
    i2c_info.pbData = ctypes.cast(data_buf, POINTER(c_ubyte))
    i2c_info.cbSize = read_size
    i2c_info.i2cSpeed = speed
    i2c_info.i2cSpeedKhz = 100
    i2c_info.portId = port
    i2c_info.bIsPortIdSet = 1

    func = ctypes.CFUNCTYPE(c_int, c_void_p, POINTER(NV_I2C_INFO_V3), POINTER(c_uint32))(
        api._get_func(0x4D7B0709)
    )
    unknown = c_uint32(0)
    status = func(gpu, byref(i2c_info), byref(unknown))

    if status == NVAPI_OK:
        return [data_buf[i] for i in range(read_size)]
    return None


def main():
    print("=" * 60)
    print("  EDID Fix — Restore corrupted 0x50 on Port 3")
    print("=" * 60)
    print()

    log_session_start(log, "fix_edid.py")

    try:
        api, gpus = create_nvapi()
    except RuntimeError as e:
        log.error(f"Init failed: {e}")
        print(f"[ERROR] {e}")
        sys.exit(1)

    gpu = gpus[0]

    # Step 1: Read current corrupted state
    print("  [1] Reading current (corrupted) state of 0x50 Port 3...")
    data = i2c_read(api, gpu, ADDR, PORT, [0x00], 16)
    if data:
        hex_str = ' '.join(f'{b:02X}' for b in data)
        print(f"      Current: {hex_str}")
        log.info(f"Current corrupted: {hex_str}")
    else:
        print("      Cannot read device!")
        sys.exit(1)

    # Step 2: Original data from FIRST scan (before we corrupted it)
    # From log: Multi-read 0x00-0x0F: 06 B3 6C 27 01 01 01 01 0E 1F 01 03 80 3C 22 78
    original_data = [0x06, 0xB3, 0x6C, 0x27, 0x01, 0x01, 0x01, 0x01,
                     0x0E, 0x1F, 0x01, 0x03, 0x80, 0x3C, 0x22, 0x78]

    print(f"\n  [2] Original data (from first scan before corruption):")
    print(f"      {' '.join(f'{b:02X}' for b in original_data)}")
    log.info(f"Original: {' '.join(f'{b:02X}' for b in original_data)}")

    # Step 3: Restore byte by byte
    print(f"\n  [3] Restoring original data to 0x50 Port 3...")
    print(f"      Writing 16 bytes one register at a time...")

    success = 0
    failed = 0
    for i, byte in enumerate(original_data):
        status = i2c_write(api, gpu, ADDR, PORT, [i], [byte])
        if status == NVAPI_OK:
            success += 1
            log.debug(f"  Reg 0x{i:02X} = 0x{byte:02X} → OK")
        else:
            failed += 1
            log.warning(f"  Reg 0x{i:02X} = 0x{byte:02X} → FAILED (status={status})")
            print(f"      ⚠️  Reg 0x{i:02X} write failed (status={status})")
        time.sleep(0.02)

    print(f"      Done: {success} OK, {failed} failed")

    # Step 4: Verify
    print(f"\n  [4] Verifying restore...")
    verify = i2c_read(api, gpu, ADDR, PORT, [0x00], 16)
    if verify:
        hex_str = ' '.join(f'{b:02X}' for b in verify)
        print(f"      After restore: {hex_str}")
        log.info(f"After restore: {hex_str}")

        match = verify == original_data
        if match:
            print(f"      ✅ Data matches original!")
        else:
            print(f"      ⚠️  Data does not match perfectly")
            for i in range(16):
                if verify[i] != original_data[i]:
                    print(f"         Reg 0x{i:02X}: got 0x{verify[i]:02X}, expected 0x{original_data[i]:02X}")

    print(f"\n{'='*60}")
    print("  NEXT STEPS:")
    print("  1. Restart PC: shutdown /r /t 0")
    print("  2. Cắm lại dây cũ vào cổng bị lỗi")
    print("  3. Xem monitor X có nhận đúng độ phân giải không")
    print(f"{'='*60}")
    print(f"\n  📄 Log: rgb_debug.log")


if __name__ == "__main__":
    main()
