"""
Set GPU LED to Blue — Colorful iGame RTX 5070 PoC
==================================================
Attempts to set the RGB LED on Colorful iGame GPU to a nice blue color.

This script tries multiple known Colorful iGame protocols:
1. Protocol A: Based on RTX 4080 Advanced OC (OpenRGB implementation)
2. Protocol B: Based on RTX 3060 iGame (older protocol)
3. Protocol C: Direct RGB write (generic approach)

Run as Administrator!
Usage: python set_blue.py
"""

import sys
import time
from nvapi_i2c import create_nvapi, NVAPI_OK

# Nice blue color
TARGET_COLOR = (0x00, 0x66, 0xFF)  # R=0, G=102, B=255 — vivid blue

# Known Colorful iGame LED controller addresses to try
COLORFUL_ADDRESSES = [0x60, 0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68,
                      0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38]


def try_protocol_a(api, gpu, addr, r, g, b):
    """
    Protocol A: Colorful iGame RTX 4080 style
    Based on OpenRGB's ColorfulGPUController implementation.
    Register 0x01 = mode, then RGB data follows.
    """
    print(f"    Protocol A (RTX 4080 style) @ 0x{addr:02X}...")

    # Set mode to static (0x01) and write RGB
    # Format: [mode, R, G, B]
    status = api.i2c_write(gpu, addr, [0x01], [0x01, r, g, b])
    if status == NVAPI_OK:
        print(f"    ✅ Protocol A SUCCESS! Wrote R={r} G={g} B={b}")
        return True

    return False


def try_protocol_b(api, gpu, addr, r, g, b):
    """
    Protocol B: Colorful iGame older style
    Some models use register 0x04 for color data.
    Format: reg=0x04, data=[mode, R, G, B, brightness]
    """
    print(f"    Protocol B (older style) @ 0x{addr:02X}...")

    # Mode 0x00 = static, brightness 0xFF = max
    status = api.i2c_write(gpu, addr, [0x04], [0x00, r, g, b, 0xFF])
    if status == NVAPI_OK:
        print(f"    ✅ Protocol B SUCCESS! Wrote R={r} G={g} B={b}")
        return True

    return False


def try_protocol_c(api, gpu, addr, r, g, b):
    """
    Protocol C: Direct RGB write
    Some controllers accept RGB at register 0x00 directly.
    """
    print(f"    Protocol C (direct RGB) @ 0x{addr:02X}...")

    status = api.i2c_write(gpu, addr, [0x00], [r, g, b])
    if status == NVAPI_OK:
        print(f"    ✅ Protocol C SUCCESS! Wrote R={r} G={g} B={b}")
        return True

    return False


def try_protocol_d(api, gpu, addr, r, g, b):
    """
    Protocol D: Header + payload style
    Some newer Colorful models use a command header byte.
    Format: reg=0xB0, data=[0x01, zone, R, G, B]
    """
    print(f"    Protocol D (header style) @ 0x{addr:02X}...")

    # Zone 0 = all LEDs, 0x01 = static mode
    status = api.i2c_write(gpu, addr, [0xB0], [0x01, 0x00, r, g, b])
    if status == NVAPI_OK:
        print(f"    ✅ Protocol D SUCCESS! Wrote R={r} G={g} B={b}")
        return True

    return False


def try_protocol_e(api, gpu, addr, r, g, b):
    """
    Protocol E: ENE-style (common RGB controller chip)
    Many GPU RGB controllers use ENE chips.
    Write sequence: set direct mode, then write colors.
    """
    print(f"    Protocol E (ENE-style) @ 0x{addr:02X}...")

    # Set to direct/static mode
    status = api.i2c_write(gpu, addr, [0x35], [0x00])
    if status != NVAPI_OK:
        return False

    time.sleep(0.05)

    # Write RGB color
    status = api.i2c_write(gpu, addr, [0x36], [r, g, b])
    if status == NVAPI_OK:
        print(f"    ✅ Protocol E SUCCESS! Wrote R={r} G={g} B={b}")
        return True

    return False


def main():
    r, g, b = TARGET_COLOR
    print("=" * 60)
    print("  Colorful iGame RTX 5070 — Set LED to Blue")
    print(f"  Target color: R={r} G={g} B={b} (#{r:02X}{g:02X}{b:02X})")
    print("=" * 60)
    print()

    try:
        api, gpus = create_nvapi()
    except RuntimeError as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)

    gpu = gpus[0]

    protocols = [
        ("A", try_protocol_a),
        ("B", try_protocol_b),
        ("C", try_protocol_c),
        ("D", try_protocol_d),
        ("E", try_protocol_e),
    ]

    success = False

    # Try each port
    for port in range(0, 4):
        if success:
            break
        print(f"\n--- Trying Port {port} ---")

        for addr in COLORFUL_ADDRESSES:
            if success:
                break

            # First check if device responds at this address
            check = api.i2c_write(gpu, addr, [0x00], [], port=port)
            if check != NVAPI_OK:
                continue

            print(f"\n  Found device at 0x{addr:02X} on port {port}")

            for proto_name, proto_func in protocols:
                if success:
                    break
                result = proto_func(api, gpu, addr, r, g, b)
                if result:
                    success = True
                    print(f"\n{'='*60}")
                    print(f"  🎉 SUCCESS!")
                    print(f"  LED should now be BLUE (#{r:02X}{g:02X}{b:02X})")
                    print(f"  Protocol: {proto_name}")
                    print(f"  Address: 0x{addr:02X}")
                    print(f"  Port: {port}")
                    print(f"{'='*60}")
                time.sleep(0.1)

    if not success:
        print(f"\n{'='*60}")
        print("  ❌ No protocol worked.")
        print()
        print("  Possible next steps:")
        print("  1. Run scan_i2c.py first to see which addresses respond")
        print("  2. Check if GPU I2C access requires different permissions")
        print("  3. The RTX 5070 may use a new protocol not covered here")
        print("  4. Try running with '--extended' flag for more protocol attempts")
        print()
        print("  Please share the output of scan_i2c.py with me")
        print("  so I can analyze which addresses respond and adjust the protocol.")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()
