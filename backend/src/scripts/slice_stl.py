import sys
import subprocess
import os
import glob

stl_path    = sys.argv[1]
output_path = sys.argv[2]  # z.B. /tmp/datei_sliced.3mf
nozzle      = sys.argv[3] if len(sys.argv) > 3 else "0.4"

ORCA_BIN     = "/usr/local/bin/orca-slicer"
PROFILE_BASE = "/var/www/orca-profiles/BBL"

MACHINE_MAP = {
    "0.2": f"{PROFILE_BASE}/machine/Bambu Lab A1 0.2 nozzle.json",
    "0.4": f"{PROFILE_BASE}/machine/Bambu Lab A1 0.4 nozzle.json",
    "0.6": f"{PROFILE_BASE}/machine/Bambu Lab A1 0.6 nozzle.json",
    "0.8": f"{PROFILE_BASE}/machine/Bambu Lab A1 0.8 nozzle.json",
}

PROCESS_MAP = {
    "0.2": f"{PROFILE_BASE}/process/0.10mm High Quality @BBL A1 0.2 nozzle.json",
    "0.4": f"{PROFILE_BASE}/process/0.20mm Standard @BBL A1.json",
    "0.6": f"{PROFILE_BASE}/process/0.30mm Standard @BBL A1 0.6 nozzle.json",
    "0.8": f"{PROFILE_BASE}/process/0.40mm Standard @BBL A1 0.8 nozzle.json",
}

FILAMENT = f"{PROFILE_BASE}/filament/Generic PLA @BBL A1.json"

machine  = MACHINE_MAP.get(nozzle, MACHINE_MAP["0.4"])
process  = PROCESS_MAP.get(nozzle, PROCESS_MAP["0.4"])
output_dir = os.path.dirname(output_path)
basename   = os.path.splitext(os.path.basename(stl_path))[0]

cmd = [
    ORCA_BIN,
    "--slice", "0",
    "--load-settings", process,
    "--load-filaments", FILAMENT,
    "--load-settings", machine,
    "--export-3mf", output_path,
    stl_path
]

result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

if result.returncode != 0:
    sys.stderr.write(f"OrcaSlicer error (code {result.returncode}): {result.stderr}\n")
    sys.exit(1)

# Falls --export-3mf die Datei woanders hinlegt, suchen
if not os.path.exists(output_path):
    matches = glob.glob(os.path.join(output_dir, basename + "*.3mf"))
    if not matches:
        matches = glob.glob(os.path.join(output_dir, "*.3mf"))
        if matches:
            matches = [max(matches, key=os.path.getmtime)]
    if matches and matches[0] != output_path:
        os.rename(matches[0], output_path)

if os.path.exists(output_path):
    print(f"sliced ok: {output_path}")
else:
    sys.stderr.write(f"3mf nicht gefunden. Output:\n{result.stdout}\n{result.stderr}\n")
    sys.exit(1)