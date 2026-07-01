"""
Set GPU LED to Blue — TARGETED for Colorful iGame RTX 5070
===========================================================
Based on scan results:
  - LED Controller: Address 0x61, Port 1
  - Signature byte: 0xAA (confirmed responding)

Tries multiple protocol variations specifically targeting 0x61.

Run as Administrator!
Usage: python set_blue_targeted.py
"""

import sys
import time
import ctypes
from ctypes import c_ubyte, c_uint32, POINTER, byref, sizeof, c_void_p, c_int
from nvapi_i2c import create_nvapi, NvAPI, NV_I2C_INFO_V3, NVAPI_OK
from logger import setup_logger, log_session_start

log = setup_logger("set_blue_targeted")

# ===== CONFIRMED FROM SCAN =====
LED_ADDRESS = 0x61
LED_PORT = 1
# ================================

# Nice blue color
TARGET_R = 0x00
TARGET_G = 0x66
TARGET_B = 0xFF


def i2c_write_targeted(api, gpu, reg_bytes, data_bytes, speed=0):
    """Write to confirmed LED address with full logging."""
    reg_size = len(reg_bytes)
    reg_buf = (c_ubyte * max(reg_size, 1))(*reg_bytes) if reg_size > 0 else (c_ubyte * 1)(0)

    data_size = len(data_bytes)
    data_buf = (c_ubyte * max(data_size, 1))(*data_bytes) if data_size > 0 else (c_ubyte * 1)(0)

    i2c_info = NV_I2C_INFO_V3()
    i2c_info.version = sizeof(NV_I2C_INFO_V3) | (3 << 16)
    i2c_info.displayMask = 0
    i2c_info.bIsDDCPort = 0
    i2c_info.i2cDevAddress = LED_ADDRESS << 1  # 7-bit → 8-bit (write)
    i2c_info.pbI2cRegAddress = ctypes.cast(reg_buf, POINTER(c_ubyte))
    i2c_info.regAddrSize = reg_size
    i2c_info.pbData = ctypes.cast(data_buf, POINTER(c_ubyte))
    i2c_info.cbSize = data_size
    i2c_info.i2cSpeed = speed
    i2c_info.i2cSpeedKhz = 100
    i2c_info.portId = LED_PORT
    i2c_info.bIsPortIdSet = 1

    func = ctypes.CFUNCTYPE(c_int, c_void_p, POINTER(NV_I2C_INFO_V3), POINTER(c_uint32))(
        api._get_func(0x283AC65A)  # NVAPI_I2CWRITEEX
    )
    unknown = c_uint32(0)
    status = func(gpu, byref(i2c_info), byref(unknown))

    reg_hex = ' '.join(f'0x{b:02X}' for b in reg_bytes)
    data_hex = ' '.join(f'0x{b:02X}' for b in data_bytes)
    log.debug(f"WRITE addr=0x{LED_ADDRESS:02X} port={LED_PORT} reg=[{reg_hex}] data=[{data_hex}] → status={status}")

    return status


def i2c_read_targeted(api, gpu, reg_bytes, read_size, speed=0):
    """Read from confirmed LED address with full logging."""
    reg_size = len(reg_bytes)
    reg_buf = (c_ubyte * max(reg_size, 1))(*reg_bytes) if reg_size > 0 else (c_ubyte * 1)(0)

    data_buf = (c_ubyte * read_size)()

    i2c_info = NV_I2C_INFO_V3()
    i2c_info.version = sizeof(NV_I2C_INFO_V3) | (3 << 16)
    i2c_info.displayMask = 0
    i2c_info.bIsDDCPort = 0
    i2c_info.i2cDevAddress = (LED_ADDRESS << 1) | 1  # Read bit
    i2c_info.pbI2cRegAddress = ctypes.cast(reg_buf, POINTER(c_ubyte))
    i2c_info.regAddrSize = reg_size
    i2c_info.pbData = ctypes.cast(data_buf, POINTER(c_ubyte))
    i2c_info.cbSize = read_size
    i2c_info.i2cSpeed = speed
    i2c_info.i2cSpeedKhz = 100
    i2c_info.portId = LED_PORT
    i2c_info.bIsPortIdSet = 1

    func = ctypes.CFUNCTYPE(c_int, c_void_p, POINTER(NV_I2C_INFO_V3), POINTER(c_uint32))(
        api._get_func(0x4D7B0709)  # NVAPI_I2CREADEX
    )
    unknown = c_uint32(0)
    status = func(gpu, byref(i2c_info), byref(unknown))

    reg_hex = ' '.join(f'0x{b:02X}' for b in reg_bytes)
    if status == NVAPI_OK:
        result = [data_buf[i] for i in range(read_size)]
        result_hex = ' '.join(f'0x{b:02X}' for b in result)
        log.debug(f"READ  addr=0x{LED_ADDRESS:02X} port={LED_PORT} reg=[{reg_hex}] → [{result_hex}] status=OK")
        return status, result
    else:
        log.debug(f"READ  addr=0x{LED_ADDRESS:02X} port={LED_PORT} reg=[{reg_hex}] → FAILED status={status}")
        return status, None


def probe_device(api, gpu):
    """Step 1: Verify device is still responding."""
    log.info("=" * 50)
    log.info("STEP 1: Probing device at 0x61, Port 1...")
    log.info("=" * 50)

    status, data = i2c_read_targeted(api, gpu, [0x00], 1)
    if status == NVAPI_OK:
        log.info(f"  ✅ Device responds! Read byte: 0x{data[0]:02X}")
        print(f"  ✅ Device at 0x61 responds! (byte=0x{data[0]:02X})")
        return True
    else:
        log.error(f"  ❌ Device not responding. Status: {status}")
        print(f"  ❌ Device at 0x61 not responding!")
        return False


def dump_registers(api, gpu):
    """Step 2: Read multiple registers to understand device layout."""
    log.info("=" * 50)
    log.info("STEP 2: Dumping registers 0x00-0x20...")
    log.info("=" * 50)

    print("\n  Register dump (0x00 - 0x20):")
    print("  " + "-" * 40)

    for reg in range(0x00, 0x21):
        status, data = i2c_read_targeted(api, gpu, [reg], 1)
        if status == NVAPI_OK:
            val = data[0]
            print(f"    Reg 0x{reg:02X} = 0x{val:02X} ({val:3d}) {'█' * (val // 16)}")
            log.info(f"  Reg 0x{reg:02X} = 0x{val:02X} ({val})")
        else:
            print(f"    Reg 0x{reg:02X} = [read failed, status={status}]")
            log.warning(f"  Reg 0x{reg:02X} = FAILED (status={status})")
        time.sleep(0.01)

    # Also read some higher registers that might be color-related
    log.info("  Reading extended registers (0x30-0x40, 0x80-0x90)...")
    print("\n  Extended registers:")
    for reg in list(range(0x30, 0x41)) + list(range(0x80, 0x91)):
        status, data = i2c_read_targeted(api, gpu, [reg], 1)
        if status == NVAPI_OK:
            val = data[0]
            print(f"    Reg 0x{reg:02X} = 0x{val:02X} ({val:3d})")
            log.info(f"  Reg 0x{reg:02X} = 0x{val:02X} ({val})")
        time.sleep(0.01)


def try_set_color(api, gpu, r, g, b):
    """Step 3: Try multiple protocols to set color."""
    log.info("=" * 50)
    log.info(f"STEP 3: Attempting to set color R={r} G={g} B={b}...")
    log.info("=" * 50)

    protocols = []

    # Protocol 1: Colorful iGame style — mode byte + RGB
    protocols.append(("Colorful-A: reg=0x01, data=[mode=0x01, R, G, B]",
                      [0x01], [0x01, r, g, b]))

    # Protocol 2: Colorful iGame style — reg=0x04
    protocols.append(("Colorful-B: reg=0x04, data=[mode=0x00, R, G, B, brightness=0xFF]",
                      [0x04], [0x00, r, g, b, 0xFF]))

    # Protocol 3: Direct RGB at reg 0x00
    protocols.append(("Direct-RGB: reg=0x00, data=[R, G, B]",
                      [0x00], [r, g, b]))

    # Protocol 4: ENE-style — set mode then color
    protocols.append(("ENE-mode: reg=0x35, data=[0x00] (set direct mode)",
                      [0x35], [0x00]))

    # Protocol 5: ENE-style color write
    protocols.append(("ENE-color: reg=0x36, data=[R, G, B]",
                      [0x36], [r, g, b]))

    # Protocol 6: Header + zone + RGB
    protocols.append(("Header-zone: reg=0xB0, data=[0x01, zone=0x00, R, G, B]",
                      [0xB0], [0x01, 0x00, r, g, b]))

    # Protocol 7: Some controllers use reg=0x10 for color
    protocols.append(("Reg-0x10: reg=0x10, data=[R, G, B]",
                      [0x10], [r, g, b]))

    # Protocol 8: Write R, G, B to separate registers
    protocols.append(("Separate-R: reg=0x01, data=[R]",
                      [0x01], [r]))
    protocols.append(("Separate-G: reg=0x02, data=[G]",
                      [0x02], [g]))
    protocols.append(("Separate-B: reg=0x03, data=[B]",
                      [0x03], [b]))

    # Protocol 9: Some use reg 0x04, 0x05, 0x06 for R, G, B
    protocols.append(("Separate-R@04: reg=0x04, data=[R]",
                      [0x04], [r]))
    protocols.append(("Separate-G@05: reg=0x05, data=[G]",
                      [0x05], [g]))
    protocols.append(("Separate-B@06: reg=0x06, data=[B]",
                      [0x06], [b]))

    # Protocol 10: Colorful newer — command packet
    protocols.append(("Colorful-CMD: reg=0xE0, data=[0x35, 0x01, R, G, B]",
                      [0xE0], [0x35, 0x01, r, g, b]))

    # Protocol 11: Apply/commit byte after color set
    protocols.append(("Apply-commit: reg=0xFF, data=[0x01]",
                      [0xFF], [0x01]))

    # Protocol 12: Write full packet at reg 0x00
    protocols.append(("Full-packet: reg=0x00, data=[0x01, 0x01, R, G, B, 0xFF, 0x00]",
                      [0x00], [0x01, 0x01, r, g, b, 0xFF, 0x00]))

    print(f"\n  Trying {len(protocols)} protocol variations...")
    print(f"  Target: R={r} G={g} B={b} (#{r:02X}{g:02X}{b:02X})")
    print()

    success_count = 0
    for name, reg, data in protocols:
        status = i2c_write_targeted(api, gpu, reg, data)
        result = "✅ OK" if status == NVAPI_OK else f"❌ status={status}"
        print(f"    {name}")
        print(f"      → {result}")
        log.info(f"  {name} → status={status}")

        if status == NVAPI_OK:
            success_count += 1

        time.sleep(0.05)

    return success_count


def verify_after_write(api, gpu):
    """Step 4: Read back registers to see if anything changed."""
    log.info("=" * 50)
    log.info("STEP 4: Verifying — reading registers after write...")
    log.info("=" * 50)

    print("\n  Reading registers after write (checking for changes):")
    for reg in range(0x00, 0x10):
        status, data = i2c_read_targeted(api, gpu, [reg], 1)
        if status == NVAPI_OK:
            val = data[0]
            print(f"    Reg 0x{reg:02X} = 0x{val:02X} ({val:3d})")
            log.info(f"  Post-write Reg 0x{reg:02X} = 0x{val:02X}")
        time.sleep(0.01)


def main():
    print("=" * 60)
    print("  Colorful iGame RTX 5070 — Set LED to BLUE")
    print(f"  Target: 0x61 Port 1 | Color: #{TARGET_R:02X}{TARGET_G:02X}{TARGET_B:02X}")
    print("=" * 60)
    print()

    log_session_start(log, "set_blue_targeted.py")
    log.info(f"Target device: addr=0x{LED_ADDRESS:02X}, port={LED_PORT}")
    log.info(f"Target color: R={TARGET_R} G={TARGET_G} B={TARGET_B}")

    try:
        api, gpus = create_nvapi()
    except RuntimeError as e:
        log.error(f"Init failed: {e}")
        print(f"[ERROR] {e}")
        sys.exit(1)

    gpu = gpus[0]

    # Step 1: Verify device
    if not probe_device(api, gpu):
        log.error("Device probe failed. Aborting.")
        print("\n  Cannot proceed — device not responding.")
        print("  Make sure no other RGB software is running.")
        sys.exit(1)

    # Step 2: Dump registers (understand current state)
    print("\n")
    dump_registers(api, gpu)

    # Step 3: Try setting color
    print("\n")
    success_count = try_set_color(api, gpu, TARGET_R, TARGET_G, TARGET_B)

    # Step 4: Verify
    print("\n")
    verify_after_write(api, gpu)

    # Summary
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    print(f"  Protocols that returned OK: {success_count}")
    print()
    if success_count > 0:
        print("  👀 Check your GPU LED now!")
        print("  - If it turned BLUE → we found the right protocol!")
        print("  - If no change → the protocol accepted data but format was wrong")
        print()
    else:
        print("  All writes were rejected by the controller.")
        print()
    print(f"  📄 Full log saved to: rgb_debug.log")
    print(f"  Please share the log so I can analyze the register dump")
    print(f"  and determine the correct protocol.")
    print(f"{'='*60}")

    log.info(f"Complete. success_count={success_count}")


if __name__ == "__main__":
    main()
