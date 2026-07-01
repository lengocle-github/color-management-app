"""
Port 3 Deep Scan — Target the REAL LED controller
==================================================
Port 3 had devices with actual varying data (not 0xAA dummy):
  0x37 — data changes between reads (active device)
  0x3A — 0x00
  0x4A — 0x00
  0x4B — 0x00
  0x50 — 0x00/0xFF (has state)
  0x54 — 0x03 (specific value)

This script will:
1. Deep-scan Port 3 devices with register dumps
2. Try writing color data to each device
3. Log everything for analysis

Run as Administrator!
Usage: python scan_port3.py
"""

import sys
import time
import ctypes
from ctypes import c_ubyte, c_uint32, POINTER, byref, sizeof, c_void_p, c_int
from nvapi_i2c import create_nvapi, NV_I2C_INFO_V3, NVAPI_OK
from logger import setup_logger, log_session_start

log = setup_logger("scan_port3")

PORT = 3
TARGET_ADDRESSES = [0x37, 0x3A, 0x4A, 0x4B, 0x50, 0x54]

# Also scan nearby addresses that might have been missed
EXTRA_ADDRESSES = [0x34, 0x35, 0x36, 0x38, 0x39, 0x3B, 0x3C,
                   0x48, 0x49, 0x4C, 0x4D, 0x4E, 0x4F,
                   0x51, 0x52, 0x53, 0x55, 0x56, 0x57, 0x58]

# Blue color
R, G, B = 0x00, 0x66, 0xFF


def i2c_read(api, gpu, addr, reg_bytes, read_size, speed=0):
    """Read from device on Port 3."""
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
    i2c_info.portId = PORT
    i2c_info.bIsPortIdSet = 1

    func = ctypes.CFUNCTYPE(c_int, c_void_p, POINTER(NV_I2C_INFO_V3), POINTER(c_uint32))(
        api._get_func(0x4D7B0709)
    )
    unknown = c_uint32(0)
    status = func(gpu, byref(i2c_info), byref(unknown))

    if status == NVAPI_OK:
        result = [data_buf[i] for i in range(read_size)]
        return status, result
    return status, None


def i2c_write(api, gpu, addr, reg_bytes, data_bytes, speed=0):
    """Write to device on Port 3."""
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
    i2c_info.portId = PORT
    i2c_info.bIsPortIdSet = 1

    func = ctypes.CFUNCTYPE(c_int, c_void_p, POINTER(NV_I2C_INFO_V3), POINTER(c_uint32))(
        api._get_func(0x283AC65A)
    )
    unknown = c_uint32(0)
    status = func(gpu, byref(i2c_info), byref(unknown))

    reg_hex = ' '.join(f'0x{b:02X}' for b in reg_bytes)
    data_hex = ' '.join(f'0x{b:02X}' for b in data_bytes)
    log.debug(f"WRITE 0x{addr:02X} port={PORT} reg=[{reg_hex}] data=[{data_hex}] → status={status}")
    return status


def i2c_read_multi(api, gpu, addr, reg_byte, count):
    """Read multiple bytes from a single register."""
    reg_buf = (c_ubyte * 1)(reg_byte)
    data_buf = (c_ubyte * count)()

    i2c_info = NV_I2C_INFO_V3()
    i2c_info.version = sizeof(NV_I2C_INFO_V3) | (3 << 16)
    i2c_info.displayMask = 0
    i2c_info.bIsDDCPort = 0
    i2c_info.i2cDevAddress = (addr << 1) | 1
    i2c_info.pbI2cRegAddress = ctypes.cast(reg_buf, POINTER(c_ubyte))
    i2c_info.regAddrSize = 1
    i2c_info.pbData = ctypes.cast(data_buf, POINTER(c_ubyte))
    i2c_info.cbSize = count
    i2c_info.i2cSpeed = 0
    i2c_info.i2cSpeedKhz = 100
    i2c_info.portId = PORT
    i2c_info.bIsPortIdSet = 1

    func = ctypes.CFUNCTYPE(c_int, c_void_p, POINTER(NV_I2C_INFO_V3), POINTER(c_uint32))(
        api._get_func(0x4D7B0709)
    )
    unknown = c_uint32(0)
    status = func(gpu, byref(i2c_info), byref(unknown))

    if status == NVAPI_OK:
        return [data_buf[i] for i in range(count)]
    return None


def step1_verify_devices(api, gpu):
    """Verify which devices respond on Port 3."""
    log.info("=" * 50)
    log.info("STEP 1: Verify Port 3 devices...")
    log.info("=" * 50)
    print("\n  [Step 1] Verifying devices on Port 3...\n")

    all_addrs = sorted(set(TARGET_ADDRESSES + EXTRA_ADDRESSES))
    found = []

    for addr in all_addrs:
        status, data = i2c_read(api, gpu, addr, [0x00], 1)
        if status == NVAPI_OK:
            val = data[0]
            found.append((addr, val))
            print(f"    0x{addr:02X} → responds (reg 0x00 = 0x{val:02X})")
            log.info(f"  0x{addr:02X} responds: reg[0x00]=0x{val:02X}")
        else:
            log.debug(f"  0x{addr:02X} no response (status={status})")

    print(f"\n    Total: {len(found)} devices found on Port 3")
    return found


def step2_dump_registers(api, gpu, devices):
    """Dump registers for each found device."""
    log.info("=" * 50)
    log.info("STEP 2: Register dump for each device...")
    log.info("=" * 50)
    print("\n  [Step 2] Dumping registers (0x00-0x20) for each device...\n")

    for addr, _ in devices:
        print(f"    --- Device 0x{addr:02X} ---")
        log.info(f"  --- Device 0x{addr:02X} register dump ---")

        # Read 16 bytes from reg 0x00 in one shot
        multi_data = i2c_read_multi(api, gpu, addr, 0x00, 16)
        if multi_data:
            hex_str = ' '.join(f'{b:02X}' for b in multi_data)
            print(f"      Regs 0x00-0x0F (multi): {hex_str}")
            log.info(f"    Multi-read 0x00-0x0F: {hex_str}")

            # Check if all same value (dummy device)
            if len(set(multi_data)) == 1:
                print(f"      ⚠️  All same value (0x{multi_data[0]:02X}) — likely NOT LED controller")
                log.warning(f"    All same value — likely dummy/bus artifact")
            else:
                print(f"      ✅ Different values — this is a REAL device!")
                log.info(f"    Different values detected — real device")

        # Also try reading individual registers
        values = []
        for reg in range(0x00, 0x21):
            status, data = i2c_read(api, gpu, addr, [reg], 1)
            if status == NVAPI_OK:
                values.append((reg, data[0]))
            time.sleep(0.005)

        if values:
            unique_vals = set(v for _, v in values)
            log.info(f"    Individual reads: {len(values)} OK, {len(unique_vals)} unique values")
            if len(unique_vals) > 1:
                for reg, val in values:
                    if val != values[0][1]:  # Show registers different from first
                        log.info(f"    Reg 0x{reg:02X} = 0x{val:02X} (different!)")

        print()


def step3_try_color_writes(api, gpu, devices):
    """Try writing color to each real device."""
    log.info("=" * 50)
    log.info("STEP 3: Try color writes on Port 3 devices...")
    log.info("=" * 50)
    print(f"\n  [Step 3] Trying to set BLUE (R={R} G={G} B={B}) on each device...\n")

    for addr, initial_val in devices:
        print(f"    --- Device 0x{addr:02X} (initial=0x{initial_val:02X}) ---")
        log.info(f"  --- Writing color to 0x{addr:02X} ---")

        protocols = [
            ("Direct RGB @0x00", [0x00], [R, G, B]),
            ("Mode+RGB @0x01", [0x01], [0x01, R, G, B]),
            ("Colorful @0x04", [0x04], [0x00, R, G, B, 0xFF]),
            ("Separate R/G/B @0x01-0x03", None, None),  # Special handling
            ("CMD packet @0xE0", [0xE0], [0x35, 0x01, R, G, B]),
            ("Full @0x00 long", [0x00], [0x01, 0x01, R, G, B, 0xFF, 0x00]),
            ("Reg 0x10 RGB", [0x10], [R, G, B]),
            ("Colorful v2 @0x80", [0x80], [0x01, R, G, B]),
            ("Apply @0xFF", [0xFF], [0x01]),
        ]

        for name, reg, data in protocols:
            if reg is None:
                # Separate write
                s1 = i2c_write(api, gpu, addr, [0x01], [R])
                s2 = i2c_write(api, gpu, addr, [0x02], [G])
                s3 = i2c_write(api, gpu, addr, [0x03], [B])
                ok = s1 == 0 and s2 == 0 and s3 == 0
                status_str = f"R={s1} G={s2} B={s3}"
            else:
                status = i2c_write(api, gpu, addr, reg, data)
                ok = status == NVAPI_OK
                status_str = f"status={status}"

            result = "✅" if ok else "❌"
            print(f"      {result} {name} → {status_str}")
            log.info(f"    {name} → {status_str}")
            time.sleep(0.05)

        # Read back after writes
        status, post_data = i2c_read(api, gpu, addr, [0x00], 1)
        if status == NVAPI_OK:
            changed = "CHANGED!" if post_data[0] != initial_val else "unchanged"
            print(f"      Post-write reg[0x00] = 0x{post_data[0]:02X} ({changed})")
            log.info(f"    Post-write: 0x{post_data[0]:02X} ({changed})")

        print()


def step4_check_port3_full(api, gpu):
    """Full address scan on Port 3 to find anything we missed."""
    log.info("=" * 50)
    log.info("STEP 4: Full scan Port 3 (0x08-0x77)...")
    log.info("=" * 50)
    print("\n  [Step 4] Full address scan Port 3 (finding ALL devices)...\n")

    found = []
    for addr in range(0x08, 0x78):
        status, data = i2c_read(api, gpu, addr, [0x00], 1)
        if status == NVAPI_OK:
            found.append((addr, data[0]))

    print(f"    All responding addresses on Port 3:")
    for addr, val in found:
        is_target = "⭐" if addr in TARGET_ADDRESSES else "  "
        all_aa = " (dummy?)" if val == 0xAA else ""
        print(f"    {is_target} 0x{addr:02X} = 0x{val:02X}{all_aa}")
        log.info(f"  Full scan: 0x{addr:02X} = 0x{val:02X}")

    print(f"\n    Total: {len(found)} devices")
    return found


def main():
    print("=" * 60)
    print("  Port 3 Deep Scan — Finding the REAL LED Controller")
    print(f"  Target color: #{R:02X}{G:02X}{B:02X} (Blue)")
    print("=" * 60)

    log_session_start(log, "scan_port3.py")

    try:
        api, gpus = create_nvapi()
    except RuntimeError as e:
        log.error(f"Init failed: {e}")
        print(f"[ERROR] {e}")
        sys.exit(1)

    gpu = gpus[0]

    # Step 1
    devices = step1_verify_devices(api, gpu)
    if not devices:
        print("\n  ❌ No devices found on Port 3!")
        log.error("No devices on Port 3")
        sys.exit(1)

    # Step 2
    step2_dump_registers(api, gpu, devices)

    # Step 3
    step3_try_color_writes(api, gpu, devices)

    # Step 4
    all_devices = step4_check_port3_full(api, gpu)

    # Summary
    print(f"\n{'='*60}")
    print("  SUMMARY")
    print(f"{'='*60}")
    print(f"  Port 3 devices: {len(all_devices)}")
    print(f"  👀 Check GPU LED — did color change?")
    print(f"  📄 Full log: rgb_debug.log")
    print(f"{'='*60}")

    log.info("Scan complete.")


if __name__ == "__main__":
    main()
