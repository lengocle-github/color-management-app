"""
List USB Devices — Find Colorful iGame LED Controller
=====================================================
Scans all USB devices looking for potential LED controllers.

Usage: python list_usb.py
"""

import subprocess
import sys
from logger import setup_logger, log_session_start

log = setup_logger("list_usb")


def run_powershell(cmd):
    """Run PowerShell command and return output."""
    try:
        result = subprocess.run(
            ["powershell", "-Command", cmd],
            capture_output=True, text=True, timeout=15
        )
        return result.stdout.strip()
    except Exception as e:
        return f"ERROR: {e}"


def main():
    print("=" * 60)
    print("  USB Device Scanner — Looking for LED Controller")
    print("=" * 60)
    print()

    log_session_start(log, "list_usb.py")

    # Method 1: Get all USB devices with VID/PID
    print("  [1] All USB devices (VID/PID):\n")
    cmd1 = "Get-PnpDevice -Class USB | Select-Object Status, InstanceId, FriendlyName | Format-Table -AutoSize"
    output1 = run_powershell(cmd1)
    print(output1)
    log.info(f"USB devices:\n{output1}")

    # Method 2: Look for HID devices (LED controllers often show as HID)
    print("\n\n  [2] HID devices (LED controllers often use HID):\n")
    cmd2 = "Get-PnpDevice -Class HIDClass | Select-Object Status, InstanceId, FriendlyName | Format-Table -AutoSize"
    output2 = run_powershell(cmd2)
    print(output2)
    log.info(f"HID devices:\n{output2}")

    # Method 3: Unknown/Other devices
    print("\n\n  [3] Unknown or unclassified devices:\n")
    cmd3 = "Get-PnpDevice | Where-Object { $_.Class -eq $null -or $_.Class -eq '' -or $_.Class -eq 'Other' } | Select-Object Status, InstanceId, FriendlyName | Format-Table -AutoSize"
    output3 = run_powershell(cmd3)
    if output3:
        print(output3)
    else:
        print("    (none found)")
    log.info(f"Unknown devices:\n{output3}")

    # Method 4: Search for anything with "Colorful" or "iGame"
    print("\n\n  [4] Searching for 'Colorful' or 'iGame' in ALL devices:\n")
    cmd4 = "Get-PnpDevice | Where-Object { $_.FriendlyName -match 'Colorful|iGame|Color|RGB' } | Select-Object Status, Class, InstanceId, FriendlyName | Format-Table -AutoSize"
    output4 = run_powershell(cmd4)
    if output4:
        print(output4)
    else:
        print("    (none found)")
    log.info(f"Colorful/iGame search:\n{output4}")

    # Method 5: All VID/PID pairs
    print("\n\n  [5] All USB VID/PID pairs:\n")
    cmd5 = "Get-PnpDevice -Class USB | ForEach-Object { $_.InstanceId } | Select-String 'VID'"
    output5 = run_powershell(cmd5)
    print(output5)
    log.info(f"VID/PID pairs:\n{output5}")

    print(f"\n{'='*60}")
    print("  📄 Full log: rgb_debug.log")
    print("  Share output above or the log file.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
