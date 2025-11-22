"""
Hardware Stats Component
Fetches real-time GPU, CPU, and RAM usage.
"""

import psutil
import shutil
from typing import Dict, Any, List

# Try to import pynvml for NVIDIA GPU stats
try:
    import pynvml
    HAS_NVIDIA = True
except ImportError:
    HAS_NVIDIA = False

def get_system_stats() -> Dict[str, Any]:
    """
    Get current system telemetry.
    """
    stats = {
        "cpu": {
            "percent": psutil.cpu_percent(interval=None),
            "cores": psutil.cpu_count(logical=False),
            "threads": psutil.cpu_count(logical=True)
        },
        "ram": {
            "total_gb": round(psutil.virtual_memory().total / (1024**3), 1),
            "available_gb": round(psutil.virtual_memory().available / (1024**3), 1),
            "percent": psutil.virtual_memory().percent
        },
        "disk": {
            "percent": round((shutil.disk_usage("/").used / shutil.disk_usage("/").total) * 100, 1)
        },
        "gpus": []
    }

    if HAS_NVIDIA:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle)
                if isinstance(name, bytes):
                    name = name.decode("utf-8")
                
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                
                # NOTE: Ollama lazy-loads models into VRAM.
                # If VRAM usage is low (~0.5-1GB), the model is currently unloaded (idle).
                # It will spike to ~5-7GB when you send a message.
                stats["gpus"].append({
                    "index": i,
                    "name": name,
                    "memory_total_gb": round(mem_info.total / (1024**3), 1),
                    "memory_used_gb": round(mem_info.used / (1024**3), 1),
                    "memory_percent": round((mem_info.used / mem_info.total) * 100, 1),
                    "gpu_util_percent": util.gpu,
                    "note": "Model loads on-demand (saves VRAM)"
                })
            pynvml.nvmlShutdown()
        except Exception as e:
            # Fallback or log error if NVML fails despite import
            stats["gpu_error"] = str(e)
            
    return stats
