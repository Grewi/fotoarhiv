#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from pathlib import Path

# ==================== АВТОАКТИВАЦИЯ VENV ====================
VENV_PATH = Path(__file__).parent / "venv"

def activate_venv():
    if sys.prefix.startswith(str(VENV_PATH)):
        return
    
    if sys.platform == "win32":
        activate_script = VENV_PATH / "Scripts" / "activate_this.py"
    else:
        activate_script = VENV_PATH / "bin" / "activate_this.py"
    
    if activate_script.exists():
        with open(activate_script) as f:
            exec(f.read(), {'__file__': str(activate_script)})

activate_venv()

import subprocess
from datetime import datetime

try:
    from dotenv import load_dotenv
except ImportError:
    print("ОШИБКА: Установите python-dotenv: pip install python-dotenv")
    sys.exit(1)

# ==================== ЗАГРУЗКА КОНФИГУРАЦИИ ====================
SCRIPT_DIR = Path(__file__).parent
ENV_FILE = SCRIPT_DIR / ".env"

load_dotenv(ENV_FILE)
RCLONE_CMD = os.getenv("RCLONE_CMD", "")
LOCAL_PATH = os.getenv("LOCAL_PATH", "")
REMOTE_PATH = os.getenv("REMOTE_PATH", "")
RCLONE_CONFIG_NAME = os.getenv("RCLONE_CONFIG_NAME", "mysftp")

SFTP_TRANSFERS = os.getenv("SFTP_TRANSFERS", "1")
SFTP_CONCURRENCY = os.getenv("SFTP_CONCURRENCY", "1")
SFTP_BWLIMIT = os.getenv("SFTP_BWLIMIT", "1M")
SFTP_TIMEOUT = os.getenv("SFTP_TIMEOUT", "5m")
SFTP_RETRIES = os.getenv("SFTP_RETRIES", "5")
SFTO_LOW_LEVEL_RETRIES = os.getenv("SFTO_LOW_LEVEL_RETRIES", "10")
SFTP_CHUNK_SIZE = os.getenv("SFTP_CHUNK_SIZE", "4M")


if not LOCAL_PATH or not REMOTE_PATH:
    print("ОШИБКА: LOCAL_PATH и REMOTE_PATH должны быть заданы в .env файле")
    sys.exit(1)

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")
    sys.stdout.flush()

def run_rclone_copy(source, dest, extra_args):
    cmd = [RCLONE_CMD, "sync", source, dest, "--skip-links"] + extra_args
    log(f"Выполняется: {' '.join(cmd)}")
    
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        def read_stream(stream, prefix):
            for line in iter(stream.readline, ''):
                if line:
                    log(f"{prefix}{line.rstrip()}")
            stream.close()
        
        from threading import Thread
        t_out = Thread(target=read_stream, args=(proc.stdout, "  "))
        t_err = Thread(target=read_stream, args=(proc.stderr, "  [stderr] "))
        t_out.start()
        t_err.start()
        
        proc.wait()
        t_out.join()
        t_err.join()
        
        # Возвращаем True даже при ошибке 1 (некритические ошибки)
        if proc.returncode == 0:
            return True
        elif proc.returncode == 1:
            log("ПРЕДУПРЕЖДЕНИЕ: Некоторые файлы не скопированы, но процесс продолжен")
            return True
        else:
            return False
        
    except Exception as e:
        log(f"Ошибка: {e}")
        return False
    
conn_args = [
    "--transfers=1",
    "--bwlimit=1M",
    "--timeout=5m",
    "--retries=5",
    "--low-level-retries=10",
    "--size-only",
    "--progress",
    "--skip-links",
    "--ignore-errors",
    "-v"
]

remote_full = f"{RCLONE_CONFIG_NAME}:{REMOTE_PATH}"

def down():
    log("--- ШАГ 2: СКАЧИВАНИЕ С СЕРВЕРА ---")
    if not run_rclone_copy(remote_full, LOCAL_PATH, conn_args):
        log("ОШИБКА СКАЧИВАНИЯ")
        # sys.exit(1)    
def up():
    log("--- ШАГ 1: ЗАГРУЗКА НА СЕРВЕР ---")
    if not run_rclone_copy(LOCAL_PATH, remote_full, conn_args):
        log("ОШИБКА ЗАГРУЗКИ")
        # sys.exit(1)    

def main():
    er = "Неодходимо указать один из аргуметов\r\n" \
    "up - Загрузить с сервера\r\n" \
    "down - Выгрузить на сервер\r\n" \
    "up-down - Загрузить, а затем выгрузить\r\n" \
    "down-up - Выгрузить, а затем загрузить\r\n"

    log("=== НАЧАЛО СИНХРОНИЗАЦИИ (SFTP) ===")
    if len(sys.argv) < 2:
        print(er)
        sys.exit(1)

    arg = sys.argv[1]
    if arg == 'up':
        up()
    elif arg == 'down':
        down()
    elif arg == 'up-down':
        up()
        down()
    elif arg == 'down-up':
        down()  
        up()          
    else:
        print(er)
        sys.exit(1)
    
    log("=== СИНХРОНИЗАЦИЯ ЗАВЕРШЕНА ===")

if __name__ == "__main__":
    main()