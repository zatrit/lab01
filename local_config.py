"""Файл конфигурации для настройки громкости, так как
возникли разногласия по поводу громкости игры"""
import tomllib
import os

DEFAULT = {"volume": 0.5}
CONFIG_FILE = "config.toml"
__config = {}
get_property = __config.get

if os.path.isfile(CONFIG_FILE):
    with open(CONFIG_FILE, "rb") as file:
        __config.update(tomllib.load(file))
else:
    with open(CONFIG_FILE, "w") as file:
        # Этот кусок кода позволяет не использовать toml,
        # что уменьшает размер зависимостей проекта
        file.writelines(" = ".join(map(str, kv)) for kv in DEFAULT.items())
        __config.update(DEFAULT)
