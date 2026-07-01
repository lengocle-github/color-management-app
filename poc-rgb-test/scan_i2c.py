"""
I2C Bus Scanner for Colorful iGame GPU LED Controller
=====================================================
Scans all I2C addresses on the GPU's I2C bus to find the LED controller.

Common Colorful iGame LED controller addresses:
- 0x50-0x57: EEPROM (not LED)
- 0x60-0x68: Possible LED controllers (ENE/ITE chips)
- 0x30-0x38: Possible LED controllers (newer models)

Run as Administrator!
Usage: python scan_i2c.py
"""

import sys
from nvapi_i2c import create_nvapi, NVAPI_OK


def scan_i2c_bus(api, gpu_handle, port=1):
    """Scan I2C bus for responding devices."""
    print(f"\n{'='*60}")
    print(f"  Scanning I2C bus (port {port})...")
    print(f"{'='*60}")
    print()
    print("     0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F")

    found_devices = []

    for row in range(0, 128, 16):
        line = f"{row:02X}: "
        for col in range(16):
            addr = row + col

            # Skip reserved addresses
            if addr < 0x08 or addr > 0x77:
                line += "   "
                continue

            # Try to read 1 byte from address 0x00
            status = api.i2c_write(gpu_handle, addr, [0x00], [], port=port)
            if status == NVAPI_OK:
                line += f"{addr:02X} "
                found_devices.append(addr)
            else:
                line += "-- "

        print(line)

    return found_devices


def main():
    print("=" * 60)
    print("  Colorful iGame RTX 5070 — I2C Bus Scanner")
    print("  Purpose: Find LED controller address on GPU")
    print("=" * 60)
    print()

    try:
        api, gpus = create_nvapi()
    except RuntimeError as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)

    gpu = gpus[0]  # Use first GPU

    # Scan multiple ports (GPU may have I2C on different ports)
    all_found = {}
    for port in range(0, 4):
        devices = scan_i2c_bus(api, gpu, port=port)
        if devices:
            all_found[port] = devices

    # Summary
    print(f"\n{'='*60}")
    print("  SCAN RESULTS")
    print(f"{'='*60}")

    if not all_found:
        print("\n  [!] No I2C devices found on any port.")
        print("  Possible reasons:")
        print("  - LED controller uses a different protocol (not standard I2C)")
        print("  - Need to try different I2C speeds")
        print("  - Controller may need initialization sequence first")
        print("\n  Next step: Try running scan_i2c_extended.py with different speeds")
    else:
        for port, devices in all_found.items():
            print(f"\n  Port {port}: Found {len(devices)} device(s)")
            for addr in devices:
                label = identify_device(addr)
                print(f"    0x{addr:02X} — {label}")

        print("\n  [!] Note addresses in 0x30-0x38 or 0x60-0x68 range")
        print("  These are likely LED controllers for Colorful iGame.")
        print("  Use these addresses with set_blue.py")

    print()


def identify_device(addr):
    """Guess device type based on I2C address."""
    if 0x50 <= addr <= 0x57:
        return "EEPROM (probably not LED controller)"
    elif 0x60 <= addr <= 0x6F:
        return "⭐ Possible LED controller (ENE/ITE range)"
    elif 0x30 <= addr <= 0x3F:
        return "⭐ Possible LED controller (alternate range)"
    elif 0x20 <= addr <= 0x27:
        return "I/O Expander (probably not LED)"
    elif 0x48 <= addr <= 0x4F:
        return "Temperature sensor"
    elif 0x68 == addr:
        return "⭐ Possible LED controller (common for GPU RGB)"
    else:
        return "Unknown device"


if __name__ == "__main__":
    main()
