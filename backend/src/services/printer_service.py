"""
printer_service.py – Orchestriert alle Bambu-Drucker-Operationen.
Ruft die Scripts per subprocess auf und gibt strukturierte Ergebnisse zurück.
"""

import subprocess
import json
import os
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
PYTHON = sys.executable


def _run(script: str, *args, timeout: int = 30) -> tuple[int, str, str]:
    """Führt ein Script aus und gibt (returncode, stdout, stderr) zurück."""
    cmd = [PYTHON, str(SCRIPTS_DIR / script)] + [str(a) for a in args]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return 1, "", "Timeout"
    except Exception as e:
        return 1, "", str(e)


def get_status(ip: str, serial: str, access_code: str) -> dict | None:
    """Fragt den aktuellen Druckerstatus ab."""
    rc, out, err = _run("printer_status.py", ip, serial, access_code, timeout=25)
    if rc != 0 or not out or out == "null":
        return None
    try:
        return json.loads(out)
    except Exception:
        return None


def start_print(
    ip: str,
    serial: str,
    access_code: str,
    filename: str,
    ams_slot: int = 0,
    plate: int = 1,
    bed_leveling: bool = True,
    timelapse: bool = False,
    flow_cali: bool = False,
    vibration_cali: bool = False,
) -> dict:
    """Startet einen Druckauftrag."""
    rc, out, err = _run(
        "start_print.py",
        ip, serial, access_code, filename, ams_slot, plate,
        str(bed_leveling).lower(),
        str(timelapse).lower(),
        str(flow_cali).lower(),
        str(vibration_cali).lower(),
        timeout=25,
    )
    return {"success": rc == 0, "message": out or err}


def stop_print(ip: str, serial: str, access_code: str) -> dict:
    """Stoppt den laufenden Druck."""
    rc, out, err = _run("stop_print.py", ip, serial, access_code, timeout=25)
    return {"success": rc == 0, "message": out or err}


def home_printer(ip: str, serial: str, access_code: str) -> dict:
    """Fährt den Druckkopf in die Ausgangsposition."""
    rc, out, err = _run("home_printer.py", ip, serial, access_code, timeout=25)
    return {"success": rc == 0, "message": out or err}


def clear_error(ip: str, serial: str, access_code: str) -> dict:
    """Löscht Druckerfehler."""
    rc, out, err = _run("clear_printer_error.py", ip, serial, access_code, timeout=20)
    return {"success": rc == 0, "message": out or err}


def list_files(ip: str, access_code: str, path: str = "/") -> dict:
    """Listet Dateien auf dem Drucker."""
    rc, out, err = _run("list_files.py", ip, access_code, path, timeout=20)
    if rc != 0:
        return {"files": [], "error": err}
    try:
        return json.loads(out)
    except Exception:
        return {"files": [], "error": out}


def upload_file(ip: str, access_code: str, local_path: str, remote_path: str) -> dict:
    """Lädt eine Datei auf den Drucker."""
    rc, out, err = _run("upload_gcode.py", ip, access_code, local_path, remote_path, timeout=120)
    return {"success": "upload ok" in out, "message": out or err}


def delete_file(ip: str, access_code: str, remote_path: str) -> dict:
    """Löscht eine Datei auf dem Drucker."""
    rc, out, err = _run("delete_file.py", ip, access_code, remote_path, timeout=20)
    return {"success": rc == 0, "message": out or err}


def slice_stl(stl_path: str, output_path: str, nozzle: str = "0.4") -> dict:
    """Sliced eine STL-Datei mit OrcaSlicer."""
    rc, out, err = _run("slice_stl.py", stl_path, output_path, nozzle, timeout=180)
    return {"success": rc == 0, "output_path": output_path if rc == 0 else None, "message": out or err}


def control_light(ip: str, serial: str, access_code: str, mode: str = "on") -> dict:
    """Steuert die Arbeitslampe des Druckers. mode: on, off, flashing"""
    if mode not in ("on", "off", "flashing"):
        return {"success": False, "message": f"Ungültiger Modus: {mode}"}
    rc, out, err = _run("light_control.py", ip, serial, access_code, mode, timeout=15)
    return {"success": rc == 0, "message": out or err}


def pause_print(ip: str, serial: str, access_code: str) -> dict:
    """Pausiert den laufenden Druck."""
    rc, out, err = _run("pause_print.py", ip, serial, access_code, timeout=15)
    return {"success": rc == 0, "message": out or err}


def resume_print(ip: str, serial: str, access_code: str) -> dict:
    """Setzt den pausierten Druck fort."""
    rc, out, err = _run("resume_print.py", ip, serial, access_code, timeout=15)
    return {"success": rc == 0, "message": out or err}
