import json
import os
import re
import subprocess
import sys
import winreg
from pathlib import Path


_CONFIG_PATH = Path(os.environ.get("APPDATA", "")) / "MangaReader" / "config.json"

_KNOWN_READERS = [
    r"%ProgramFiles(x86)%\Foxit Software\Foxit PDF Reader\FoxitPDFReader.exe",
    r"%ProgramFiles%\Foxit Software\Foxit PDF Reader\FoxitPDFReader.exe",
    r"%ProgramFiles(x86)%\Foxit Software\Foxit Reader\FoxitReader.exe",
    r"%ProgramFiles%\Adobe\Acrobat DC\Acrobat\Acrobat.exe",
    r"%ProgramFiles(x86)%\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe",
    r"%ProgramFiles%\SumatraPDF\SumatraPDF.exe",
    r"%LocalAppData%\SumatraPDF\SumatraPDF.exe",
    r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe",
]

_OWN_NAMES = {"mangareader.exe", "mangareader"}


def _is_own_exe(path: str) -> bool:
    name = Path(path).stem.lower()
    return name in _OWN_NAMES or Path(sys.executable).stem.lower() == name


def _resolve_env(path: str) -> str:
    return os.path.expandvars(path)


def _exe_from_command(command: str) -> str | None:
    """Extract executable path from a shell open command string."""
    command = command.strip()
    if command.startswith('"'):
        m = re.match(r'"([^"]+)"', command)
        if m:
            return m.group(1)
    else:
        parts = command.split()
        if parts:
            return parts[0]
    return None


def _find_via_registry() -> str | None:
    candidates: list[str] = []

    # Source 1: OpenWithList for .pdf (apps the user has previously used)
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.pdf\OpenWithList"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    if name != "MRUList" and value.lower().endswith(".exe"):
                        candidates.append(value)
                    i += 1
                except OSError:
                    break
    except OSError:
        pass

    # Source 2: OpenWithProgids → resolve exe via shell\open\command
    try:
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r".pdf\OpenWithProgids") as key:
            i = 0
            while True:
                try:
                    progid, _, _ = winreg.EnumValue(key, i)
                    i += 1
                    if not progid:
                        continue
                    try:
                        cmd_path = progid + r"\shell\open\command"
                        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, cmd_path) as cmd_key:
                            cmd, _, _ = winreg.EnumValue(cmd_key, 0)
                            exe = _exe_from_command(cmd)
                            if exe:
                                candidates.append(exe)
                    except OSError:
                        pass
                except OSError:
                    break
    except OSError:
        pass

    for candidate in candidates:
        path = _resolve_env(candidate)
        if not _is_own_exe(path) and os.path.isfile(path):
            return path

    return None


def _find_via_known_paths() -> str | None:
    for template in _KNOWN_READERS:
        path = _resolve_env(template)
        if not _is_own_exe(path) and os.path.isfile(path):
            return path
    return None


def detect_and_save_fallback_reader() -> None:
    reader = _find_via_registry() or _find_via_known_paths()
    _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    existing = _load_config()
    existing["fallback_pdf_reader"] = reader
    with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)


def _load_config() -> dict:
    try:
        with open(_CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def load_fallback_reader() -> str | None:
    return _load_config().get("fallback_pdf_reader")


def open_with_fallback(path: str) -> bool:
    reader = load_fallback_reader()
    if reader and os.path.isfile(reader):
        subprocess.Popen([reader, path])
        return True
    return False
