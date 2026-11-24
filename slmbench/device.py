"""Best-effort host profiling, with separate fields for detected hardware vendors."""
from __future__ import annotations
import platform, subprocess
import psutil

def detect_device() -> dict:
    nvidia_name, nvidia_vram = "N/A", None
    try:
        result = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=2, check=True)
        first = result.stdout.strip().splitlines()[0].split(",", 1)
        nvidia_name, nvidia_vram = first[0].strip(), round(float(first[1].strip()) / 1024, 2)
    except (FileNotFoundError, subprocess.SubprocessError, ValueError, IndexError):
        pass
    intel_graphics = "N/A"
    if platform.system() == "Windows":
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command",
                 "(Get-CimInstance Win32_VideoController | Where-Object { $_.Name -match 'Intel' } | Select-Object -ExpandProperty Name) -join '; '"],
                capture_output=True, text=True, timeout=5, check=True,
            )
            intel_graphics = result.stdout.strip() or "N/A — Intel graphics not reported by Windows"
        except (FileNotFoundError, subprocess.SubprocessError):
            intel_graphics = "N/A — Windows graphics query unavailable"
    return {
        "device_model": "Lenovo 83DL (user-reported; exact model string not independently detected)",
        "cpu": platform.processor() or platform.machine() or "N/A",
        "logical_cores": psutil.cpu_count(logical=True),
        "physical_cores": psutil.cpu_count(logical=False),
        "ram_gb": round(psutil.virtual_memory().total / 1024**3, 2),
        "os": platform.platform(),
        "architecture": platform.machine(),
        "intel_graphics_detected": intel_graphics,
        "intel_graphics_user_reported": "Intel integrated graphics (user-provided device specification)",
        "intel_acceleration": "Not measured; no acceleration claim",
        "nvidia_gpu": nvidia_name,
        "nvidia_vram_gb": nvidia_vram,
        "inference_target": "CPU (primary benchmark target)",
    }
