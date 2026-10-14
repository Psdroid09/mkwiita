#!/usr/bin/env python3
"""Windows helper for preparing MKWiita game files from the player's own disc.

The ISO/WBFS and converted Nintendo assets remain on this PC. No VitaSDK,
admin rights, GitHub token or manual terminal commands are required.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / "build-assets-log.txt"
OUTPUT = ROOT / "build" / "vita" / "data" / "mkw"


class ConversionError(Exception):
    pass


def emit(message="", log=None):
    print(message, flush=True)
    if log:
        log.write(message + "\n")
        log.flush()


def choose_disc(argument=None):
    if argument:
        return Path(argument.strip().strip('"')).expanduser()
    selected = ""
    try:
        import tkinter as tk
        from tkinter import filedialog
        window = tk.Tk()
        window.withdraw()
        window.attributes("-topmost", True)
        selected = filedialog.askopenfilename(
            parent=window,
            title="Selecciona Mario Kart Wii USA (ISO o WBFS)",
            filetypes=[("Wii ISO / WBFS", "*.iso *.wbfs"), ("Todos los archivos", "*.*")],
        )
        window.destroy()
    except (ImportError, RuntimeError, OSError, ValueError):
        pass
    if not selected:
        try:
            selected = input("Ruta del ISO/WBFS (Enter para cancelar): ").strip().strip('"')
        except EOFError:
            selected = ""
    if not selected:
        raise ConversionError("No seleccionaste ningun archivo.")
    return Path(selected).expanduser()


def inspect_disc(disc):
    """Fast preflight only; the original build validates every expected file."""
    if not disc.is_file():
        raise ConversionError("El archivo seleccionado no existe: " + str(disc))
    if disc.suffix.lower() not in (".iso", ".wbfs"):
        raise ConversionError("El archivo debe ser ISO o WBFS, no RVZ/NKit/ZIP.")
    with disc.open("rb") as stream:
        header = stream.read(0x204)
        if header[:4] == b"WBFS":
            if len(header) < 13:
                raise ConversionError("Encabezado WBFS incompleto.")
            hd_shift = header[8]
            if not 9 <= hd_shift <= 25:
                raise ConversionError("Tamano de sector WBFS invalido.")
            slot = next((v for v in header[12:512] if v), None)
            if slot is None:
                raise ConversionError("WBFS sin disco.")
            stream.seek(slot * (1 << hd_shift))
            header = stream.read(0x204)
    if len(header) < 0x204:
        raise ConversionError("Archivo demasiado pequeno o incompleto.")
    if header[0x200:0x204] == b"NKIT":
        raise ConversionError(
            "Este archivo aun es NKit. No basta con renombrarlo .iso; "
            "restaura una imagen convencional de tu propio disco primero."
        )
    game_id = header[:6].decode("ascii", errors="replace")
    if game_id != "RMCE01":
        raise ConversionError(
            "Region o juego incorrectos (ID: " + repr(game_id) +
            "). MKWiita requiere Mario Kart Wii USA: RMCE01."
        )
    if header[0x18:0x1C] != bytes.fromhex("5d1c9ea3"):
        raise ConversionError("No es una imagen Wii ISO/WBFS valida.")
    return game_id


def run_step(command, description, log, env=None):
    emit("\n=== " + description + " ===", log)
    emit("> " + " ".join(str(part) for part in command), log)
    try:
        process = subprocess.Popen(
            [str(part) for part in command],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        with process.stdout:
            for line in process.stdout:
                emit(line.rstrip("\r\n"), log)
        result = process.wait()
    except OSError as exc:
        raise ConversionError(f"No se pudo ejecutar {description}: {exc}") from exc
    if result:
        raise ConversionError(
            f"Fallo: {description} (codigo {result}). "
            "Mira build-assets-log.txt; puedes volver a ejecutar para continuar."
        )


def prepare(disc, log):
    if sys.version_info < (3, 11):
        raise ConversionError("Instala Python 3.11+ desde https://www.python.org/downloads/")
    needed = {
        "Git": ("git", "https://git-scm.com/downloads"),
        "Node.js": ("node", "https://nodejs.org/"),
        "npm": ("npm.cmd" if os.name == "nt" else "npm", "https://nodejs.org/"),
    }
    missing = [f"{name}: {url}" for name, (tool, url) in needed.items() if not shutil.which(tool)]
    if missing:
        raise ConversionError(
            "Faltan herramientas. Instala y vuelve a abrir el conversor:\n" +
            "\n".join(missing)
        )
    usage = shutil.disk_usage(ROOT)
    free_gib = usage.free / (1024 ** 3)
    emit(f"Espacio libre en la unidad del proyecto: {free_gib:.1f} GiB", log)
    if free_gib < 15:
        raise ConversionError(
            "Se recomiendan al menos 15 GiB libres para la conversion. "
            "Libera espacio o mueve el proyecto a otra unidad."
        )

    game_id = inspect_disc(disc)
    emit("Imagen verificada (encabezado): " + game_id, log)
    emit("La verificacion completa de hashes se realiza durante la conversion.", log)

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONUNBUFFERED"] = "1"
    env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
    run_step([sys.executable, "tools/bootstrap.py"],
             "Descargar dependencias publicas", log, env)

    venv_python = ROOT / ".venv" / "Scripts" / "python.exe" if os.name == "nt" \
        else ROOT / ".venv" / "bin" / "python"
    if not venv_python.is_file():
        run_step([sys.executable, "-m", "venv", str(ROOT / ".venv")],
                 "Preparar Python del proyecto", log, env)
    run_step([venv_python, "-m", "pip", "install", "-r", "requirements.txt"],
             "Instalar librerias necesarias", log, env)
    run_step([venv_python, "tools/vita/build.py", "--assets-only", str(disc.resolve())],
             "Convertir datos del juego (puede tardar 30-60 minutos o mas)", log, env)

    if not (OUTPUT / "content.txt").is_file():
        raise ConversionError(
            "La conversion termino sin generar content.txt. "
            "Revisa el registro antes de copiar archivos."
        )
    emit("\nCONVERSION COMPLETADA.", log)
    emit("Carpeta: " + str(OUTPUT), log)
    emit("Copia el CONTENIDO de esa carpeta a ux0:data/mkw/ en VitaShell.", log)
    emit("Instala por separado el VPK experimental de GitHub Actions.", log)


def main():
    print("\nMKWiita PSD09 | Convertidor de recursos para PS Vita\n", flush=True)
    with LOG.open("w", encoding="utf-8") as log:
        emit("Proyecto: " + str(ROOT), log)
        try:
            disc = choose_disc(sys.argv[1] if len(sys.argv) > 1 else None)
            emit("Disco: " + str(disc), log)
            prepare(disc, log)
        except (ConversionError, KeyboardInterrupt) as exc:
            emit("\nERROR: " + str(exc or "Proceso cancelado"), log)
            emit("Registro: " + str(LOG), log)
            return 1
        except Exception as exc:
            # Preserve the full Python traceback for unexpected bugs.
            import traceback
            emit("\nERROR INESPERADO:", log)
            for line in traceback.format_exception(type(exc), exc, exc.__traceback__):
                for part in line.rstrip().splitlines():
                    emit(part, log)
            emit("Registro: " + str(LOG), log)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
