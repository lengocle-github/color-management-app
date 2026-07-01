"""
Try Enable LED — Attempt to turn LED back ON
=============================================
Device 0x50 on Port 3 is likely EEPROM storing LED config.
Original reg[0x00] was 0x06 before our writes changed it to 0x01.

This script tries to:
1. Restore 0x50 to original state
2. Send various "enable" commands
3. Try known Colorful "LED on" sequences

Run as Administrator!
Usage: python try_enable_led.py
"""

import sys
import time
import ctypes
from ctypes import c_ubyte, c_uint32, POINTER, byref, sizeof, c_void_p, c_int
from nvapi_i2c import create_nvapi, NV_I2C_INFO_V3, NVAPI_OK
from logger import setup_logger, log_session_start

log = setup_logger("enable_led")

PORT = 3


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

    reg_hex = ' '.join(f'0x{b:02X}' for b in reg_bytes)
    data_hex = ' '.join(f'0x{b:02X}' for b in data_bytes)
    log.debug(f"WRITE 0x{addr:02X} port={port} reg=[{reg_hex}] data=[{data_hex}] → status={status}")
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
    print("  Try Enable LED — Restore LED to ON state")
    print("=" * 60)
    print()

    log_session_start(log, "try_enable_led.py")

    try:
        api, gpus = create_nvapi()
    except RuntimeError as e:
        log.error(f"Init failed: {e}")
        print(f"[ERROR] {e}")
        sys.exit(1)

    gpu = gpus[0]

    # Step 1: Read current state of 0x50
    print("  [1] Reading current state of 0x50 (Port 3)...")
    data = i2c_read(api, gpu, 0x50, PORT, [0x00], 16)
    if data:
        hex_str = ' '.join(f'{b:02X}' for b in data)
        print(f"      Current: {hex_str}")
        log.info(f"Current 0x50 state: {hex_str}")
    else:
        print("      ❌ Cannot read 0x50!")
        log.error("Cannot read 0x50")

    # Step 2: Try restoring original first byte (was 0x06 before we corrupted it)
    print("\n  [2] Trying to restore reg[0x00] = 0x06 (original value)...")
    status = i2c_write(api, gpu, 0x50, PORT, [0x00], [0x06])
    print(f"      Write 0x06 → status={status}")
    log.info(f"Restore 0x06 → status={status}")
    time.sleep(0.5)

    # Check LED
    print("      👀 Check LED now — did it turn on?")
    input("      Press Enter to continue...")

    # Step 3: Try various "enable" values at reg[0x00]
    print("\n  [3] Trying different enable values at 0x50 reg[0x00]...")
    enable_values = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
                     0x0F, 0x10, 0xFF, 0xAA, 0x55]

    for val in enable_values:
        status = i2c_write(api, gpu, 0x50, PORT, [0x00], [val])
        result = "OK" if status == 0 else f"fail({status})"
        print(f"      reg[0x00] = 0x{val:02X} → {result}")
        log.info(f"Enable 0x50 reg[0x00]=0x{val:02X} → status={status}")
        time.sleep(0.3)
        # Brief check
        data = i2c_read(api, gpu, 0x50, PORT, [0x00], 1)
        if data:
            log.debug(f"  Readback: 0x{data[0]:02X}")

    print("      👀 Check LED — any change?")
    input("      Press Enter to continue...")

    # Step 4: Try writing to OTHER devices too (0x54 had value 0x03)
    print("\n  [4] Trying device 0x54 (had value 0x03)...")
    enable_cmds_54 = [
        ([0x00], [0x01]),  # Enable?
        ([0x00], [0x07]),  # All zones on?
        ([0x00], [0xFF]),  # Max?
        ([0x01], [0x01]),  # Mode on?
        ([0x01], [0xFF]),  # Brightness max?
    ]
    for reg, data in enable_cmds_54:
        status = i2c_write(api, gpu, 0x54, PORT, reg, data)
        reg_hex = ' '.join(f'0x{b:02X}' for b in reg)
        data_hex = ' '.join(f'0x{b:02X}' for b in data)
        print(f"      0x54 reg=[{reg_hex}] data=[{data_hex}] → status={status}")
        log.info(f"0x54 reg=[{reg_hex}] data=[{data_hex}] → status={status}")
        time.sleep(0.2)

    print("      👀 Check LED — any change?")
    input("      Press Enter to continue...")

    # Step 5: Try Port 1 device 0x61 with enable commands
    print("\n  [5] Trying Port 1 device 0x61 with enable/on commands...")
    enable_cmds_61 = [
        ([0x00], [0x01]),           # On
        ([0x00], [0xFF]),           # Full brightness
        ([0x01], [0x01, 0xFF, 0xFF, 0xFF]),  # Mode=static, white
        ([0x00], [0x01, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x00]),  # Full packet white
    ]
    for reg, data in enable_cmds_61:
        status = i2c_write(api, gpu, 0x61, 1, reg, data)
        data_hex = ' '.join(f'0x{b:02X}' for b in data)
        print(f"      0x61 port=1 reg=[0x{reg[0]:02X}] data=[{data_hex}] → status={status}")
        log.info(f"0x61 port=1 reg=[0x{reg[0]:02X}] data=[{data_hex}] → status={status}")
        time.sleep(0.2)

    print("      👀 Check LED — any change?")

    # Final state
    print("\n  [Final] Reading 0x50 final state...")
    data = i2c_read(api, gpu, 0x50, PORT, [0x00], 16)
    if data:
        hex_str = ' '.join(f'{b:02X}' for b in data)
        print(f"      Final: {hex_str}")
        log.info(f"Final 0x50 state: {hex_str}")

    print(f"\n{'='*60}")
    print("  📄 Log saved to: rgb_debug.log")
    print("  Tell me if LED changed at any step!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
