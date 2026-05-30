#!/usr/bin/env python3
import subprocess
import sys
import os
from pathlib import Path

# Загружаем .env файл
try:
    from dotenv import load_dotenv
except ImportError:
    print("Ошибка: python-dotenv не установлен")
    print("Установите: pip install python-dotenv")
    sys.exit(1)

# Загружаем .env из той же папки, где скрипт
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

RCLONE_CMD = os.getenv("RCLONE_CMD", "rclone")
# Конфигурация
HOST = os.getenv("SFTP_HOST", "")
PORT = os.getenv("SFTP_PORT", "")
USER = os.getenv("SFTP_USER", "")
PASS = os.getenv("SFTP_PASS", "")

# Выполняем команду
cmd = [
    RCLONE_CMD, "config", "create", "mysftp", "sftp",
    f"host={HOST}",
    f"port={PORT}",
    f"user={USER}",
    f"pass={PASS}"
]

try:
    subprocess.run(cmd, check=True)
    print("Конфигурация создана успешно!")
except subprocess.CalledProcessError as e:
    print(f"Ошибка: {e}")
    sys.exit(1)
except FileNotFoundError:
    print("Ошибка: rclone не найден. Установите rclone.")
    sys.exit(1)