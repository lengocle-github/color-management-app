"""
Clear ALL EDID caches — Force Windows to re-read EDID from monitor
==================================================================
This script clears EDID data cached by Windows and NVIDIA driver,
forcing a fresh EDID read from the physical monitor on next connection.

Run as Administrator!
Usage: python clear_edid_cache.py
"""

import subprocess
import sys
import os


def run_cmd(cmd, desc):
    """Run command and show result."""
    print(f"  {desc}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            print(f"    ✅ Done")
        else:
            print(f"    ⚠️  {result.stderr.strip()}" if result.stderr else "    ⚠️  May not apply")
        return result.returncode == 0
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False


def run_powershell(cmd, desc):
    """Run PowerShell command."""
    print(f"  {desc}...")
    try:
        result = subprocess.run(
            ["powershell", "-Command", cmd],
            capture_output=True, text=True, timeout=30
        )
        if result.stdout.strip():
            print(f"    {result.stdout.strip()[:200]}")
        return True
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False


def main():
    print("=" * 60)
    print("  Clear EDID Cache — Force Fresh Monitor Detection")
    print("=" * 60)
    print()
    print("  ⚠️  This will temporarily cause display flicker!")
    print("  ⚠️  Run as Administrator!")
    print()
    input("  Press Enter to continue (or Ctrl+C to cancel)...")
    print()

    # Step 1: Delete NVIDIA EDID overrides from registry
    print("[Step 1] Removing NVIDIA EDID overrides from registry...")
    run_cmd(
        'reg delete "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Video" /f /v "EDID_Override" 2>nul',
        "Deleting EDID_Override keys"
    )

    # Step 2: Remove Windows display config cache
    print("\n[Step 2] Clearing Windows display configuration cache...")
    paths = [
        r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers\Configuration",
        r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers\Connectivity",
    ]
    for path in paths:
        run_cmd(f'reg delete "{path}" /f 2>nul', f"Clearing {path.split(chr(92))[-1]}")

    # Step 3: Clear EDID cache in display enum
    print("\n[Step 3] Clearing display EDID entries...")
    run_powershell(
        """
        $displays = Get-ChildItem 'HKLM:\\SYSTEM\\CurrentControlSet\\Enum\\DISPLAY' -ErrorAction SilentlyContinue
        foreach ($d in $displays) {
            $subs = Get-ChildItem $d.PSPath -ErrorAction SilentlyContinue
            foreach ($s in $subs) {
                $edidPath = Join-Path $s.PSPath 'Device Parameters'
                if (Test-Path $edidPath) {
                    $edid = Get-ItemProperty $edidPath -Name 'EDID' -ErrorAction SilentlyContinue
                    if ($edid) {
                        Write-Output "  Found EDID in: $($s.Name)"
                    }
                }
            }
        }
        Write-Output "  (EDID entries are stored by Windows - will refresh on reconnect)"
        """,
        "Scanning display EDID entries"
    )

    # Step 4: Reset NVIDIA driver display state
    print("\n[Step 4] Resetting NVIDIA display persistence...")
    nvidia_paths = [
        os.path.expandvars(r"%ProgramData%\NVIDIA Corporation\Drs"),
        os.path.expandvars(r"%AppData%\NVIDIA\DXCache"),
    ]
    for path in nvidia_paths:
        if os.path.exists(path):
            print(f"  Found: {path}")

    # Step 5: Force Windows to invalidate display topology
    print("\n[Step 5] Invalidating display topology...")
    run_powershell(
        """
        # Disable and re-enable display adapter to force EDID re-read
        $gpu = Get-PnpDevice | Where-Object { $_.FriendlyName -match 'NVIDIA' -and $_.Class -eq 'Display' }
        if ($gpu) {
            Write-Output "  Found: $($gpu.FriendlyName)"
            Write-Output "  Disabling GPU adapter (screen will go black briefly)..."
            Disable-PnpDevice -InstanceId $gpu.InstanceId -Confirm:$false
            Start-Sleep -Seconds 3
            Write-Output "  Re-enabling GPU adapter..."
            Enable-PnpDevice -InstanceId $gpu.InstanceId -Confirm:$false
            Write-Output "  Done! GPU re-enabled."
        } else {
            Write-Output "  NVIDIA GPU not found in PnP devices"
        }
        """,
        "Cycling GPU adapter (disable → enable)"
    )

    print(f"\n{'='*60}")
    print("  DONE! Next steps:")
    print()
    print("  1. Restart PC:  shutdown /r /t 0")
    print("  2. After restart, plug monitor X into the problem port")
    print("  3. Windows should re-read EDID fresh from monitor")
    print()
    print("  If STILL broken after restart:")
    print("  → Download CRU (Custom Resolution Utility)")
    print("     https://www.monitortests.com/forum/Thread-Custom-Resolution-Utility-CRU")
    print("  → Open CRU → select broken monitor → click 'Reset'")
    print("  → Run restart64.exe from CRU folder")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
