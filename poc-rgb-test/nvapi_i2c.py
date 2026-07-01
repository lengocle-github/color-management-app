"""
NvAPI I2C Wrapper for GPU RGB LED Control
==========================================
Provides low-level I2C read/write access to NVIDIA GPU via NvAPI.
This is the same method OpenRGB uses on Windows to communicate with GPU LED controllers.

SAFE: Only communicates with I2C bus on GPU. Cannot modify GPU core settings.
"""

import ctypes
import ctypes.wintypes
import os
import sys
from ctypes import (
    Structure, POINTER, c_uint, c_int, c_ubyte, c_void_p, c_uint32, byref, sizeof
)

# NvAPI Constants
NVAPI_OK = 0
NVAPI_MAX_PHYSICAL_GPUS = 64
NVAPI_SHORT_STRING_MAX = 64

# I2C Speed constants
NVAPI_I2C_SPEED_DEFAULT = 0
NVAPI_I2C_SPEED_3KHZ = 1
NVAPI_I2C_SPEED_10KHZ = 2
NVAPI_I2C_SPEED_33KHZ = 3
NVAPI_I2C_SPEED_100KHZ = 4
NVAPI_I2C_SPEED_200KHZ = 5
NVAPI_I2C_SPEED_400KHZ = 6

# NvAPI function IDs (from NVIDIA documentation)
NVAPI_INITIALIZE = 0x0150E828
NVAPI_ENUMPHYSICALGPUS = 0xE5AC921F
NVAPI_GPU_GETFULLNAME = 0xCEEE8E9F
NVAPI_I2CREADEX = 0x4D7B0709
NVAPI_I2CWRITEEX = 0x283AC65A
NVAPI_GPU_GETBUSID = 0x1BE0B8E5


class NV_I2C_INFO_V3(Structure):
    """NvAPI I2C info structure version 3."""
    _fields_ = [
        ("version", c_uint32),
        ("displayMask", c_uint32),
        ("bIsDDCPort", c_ubyte),
        ("i2cDevAddress", c_ubyte),
        ("pbI2cRegAddress", POINTER(c_ubyte)),
        ("regAddrSize", c_uint32),
        ("pbData", POINTER(c_ubyte)),
        ("cbSize", c_uint32),
        ("i2cSpeed", c_uint32),
        ("i2cSpeedKhz", c_uint32),
        ("portId", c_ubyte),
        ("bIsPortIdSet", c_uint32),
    ]


class NvAPI:
    """Wrapper for NVIDIA NvAPI to access I2C on GPU."""

    def __init__(self):
        self._nvapi = None
        self._gpu_handles = []
        self._query_interface = None
        self._initialized = False
        self._load_nvapi()

    def _load_nvapi(self):
        """Load nvapi64.dll and initialize."""
        # Try to find nvapi64.dll
        possible_paths = [
            os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "System32", "nvapi64.dll"),
            "nvapi64.dll",
        ]

        for path in possible_paths:
            try:
                self._nvapi = ctypes.WinDLL(path)
                break
            except OSError:
                continue

        if self._nvapi is None:
            raise RuntimeError(
                "nvapi64.dll not found. Make sure NVIDIA drivers are installed.\n"
                "Download from: https://www.nvidia.com/drivers"
            )

        # Get QueryInterface function
        self._nvapi.nvapi_QueryInterface.restype = c_void_p
        self._nvapi.nvapi_QueryInterface.argtypes = [c_uint]
        self._query_interface = self._nvapi.nvapi_QueryInterface

    def _get_func(self, func_id):
        """Get NvAPI function pointer by ID."""
        ptr = self._query_interface(func_id)
        if not ptr:
            raise RuntimeError(f"Failed to get NvAPI function 0x{func_id:08X}")
        return ptr

    def initialize(self):
        """Initialize NvAPI."""
        func = ctypes.CFUNCTYPE(c_int)(self._get_func(NVAPI_INITIALIZE))
        status = func()
        if status != NVAPI_OK:
            raise RuntimeError(f"NvAPI_Initialize failed with status {status}")
        self._initialized = True
        print("[OK] NvAPI initialized successfully")

    def enum_gpus(self):
        """Enumerate physical GPUs."""
        gpu_handles = (c_void_p * NVAPI_MAX_PHYSICAL_GPUS)()
        gpu_count = c_uint(0)

        func = ctypes.CFUNCTYPE(c_int, POINTER(c_void_p), POINTER(c_uint))(
            self._get_func(NVAPI_ENUMPHYSICALGPUS)
        )
        status = func(gpu_handles, byref(gpu_count))
        if status != NVAPI_OK:
            raise RuntimeError(f"NvAPI_EnumPhysicalGPUs failed with status {status}")

        self._gpu_handles = [gpu_handles[i] for i in range(gpu_count.value)]
        print(f"[OK] Found {gpu_count.value} GPU(s)")
        return self._gpu_handles

    def get_gpu_name(self, gpu_handle):
        """Get GPU full name."""
        name = ctypes.create_string_buffer(NVAPI_SHORT_STRING_MAX)
        func = ctypes.CFUNCTYPE(c_int, c_void_p, ctypes.c_char_p)(
            self._get_func(NVAPI_GPU_GETFULLNAME)
        )
        status = func(gpu_handle, name)
        if status != NVAPI_OK:
            return "Unknown GPU"
        return name.value.decode("utf-8", errors="replace")

    def i2c_write(self, gpu_handle, dev_address, reg_address_bytes, data_bytes,
                  speed=NVAPI_I2C_SPEED_100KHZ, port=1):
        """Write data to I2C device on GPU."""
        # Prepare register address buffer
        reg_size = len(reg_address_bytes)
        reg_buf = (c_ubyte * reg_size)(*reg_address_bytes)

        # Prepare data buffer
        data_size = len(data_bytes)
        data_buf = (c_ubyte * data_size)(*data_bytes)

        # Fill I2C info structure
        i2c_info = NV_I2C_INFO_V3()
        i2c_info.version = sizeof(NV_I2C_INFO_V3) | (3 << 16)
        i2c_info.displayMask = 0
        i2c_info.bIsDDCPort = 0
        i2c_info.i2cDevAddress = dev_address << 1  # 7-bit to 8-bit address
        i2c_info.pbI2cRegAddress = ctypes.cast(reg_buf, POINTER(c_ubyte))
        i2c_info.regAddrSize = reg_size
        i2c_info.pbData = ctypes.cast(data_buf, POINTER(c_ubyte))
        i2c_info.cbSize = data_size
        i2c_info.i2cSpeed = speed
        i2c_info.i2cSpeedKhz = 100
        i2c_info.portId = port
        i2c_info.bIsPortIdSet = 1

        func = ctypes.CFUNCTYPE(c_int, c_void_p, POINTER(NV_I2C_INFO_V3), POINTER(c_uint32))(
            self._get_func(NVAPI_I2CWRITEEX)
        )
        unknown = c_uint32(0)
        status = func(gpu_handle, byref(i2c_info), byref(unknown))
        return status

    def i2c_read(self, gpu_handle, dev_address, reg_address_bytes, read_size,
                 speed=NVAPI_I2C_SPEED_100KHZ, port=1):
        """Read data from I2C device on GPU."""
        # Prepare register address buffer
        reg_size = len(reg_address_bytes)
        reg_buf = (c_ubyte * reg_size)(*reg_address_bytes)

        # Prepare data buffer for reading
        data_buf = (c_ubyte * read_size)()

        # Fill I2C info structure
        i2c_info = NV_I2C_INFO_V3()
        i2c_info.version = sizeof(NV_I2C_INFO_V3) | (3 << 16)
        i2c_info.displayMask = 0
        i2c_info.bIsDDCPort = 0
        i2c_info.i2cDevAddress = (dev_address << 1) | 1  # Read bit
        i2c_info.pbI2cRegAddress = ctypes.cast(reg_buf, POINTER(c_ubyte))
        i2c_info.regAddrSize = reg_size
        i2c_info.pbData = ctypes.cast(data_buf, POINTER(c_ubyte))
        i2c_info.cbSize = read_size
        i2c_info.i2cSpeed = speed
        i2c_info.i2cSpeedKhz = 100
        i2c_info.portId = port
        i2c_info.bIsPortIdSet = 1

        func = ctypes.CFUNCTYPE(c_int, c_void_p, POINTER(NV_I2C_INFO_V3), POINTER(c_uint32))(
            self._get_func(NVAPI_I2CREADEX)
        )
        unknown = c_uint32(0)
        status = func(gpu_handle, byref(i2c_info), byref(unknown))

        if status == NVAPI_OK:
            return [data_buf[i] for i in range(read_size)]
        return None


def create_nvapi():
    """Create and initialize NvAPI instance."""
    if sys.platform != "win32":
        raise RuntimeError("This script only works on Windows (requires NvAPI)")

    api = NvAPI()
    api.initialize()
    gpus = api.enum_gpus()

    if not gpus:
        raise RuntimeError("No NVIDIA GPU found!")

    for i, gpu in enumerate(gpus):
        name = api.get_gpu_name(gpu)
        print(f"  GPU {i}: {name}")

    return api, gpus
