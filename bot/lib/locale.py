import yaml
import os
path = "./locale"
files = os.listdir(path)


__DEFAULT_LANG = "en"

__LANGS = dict()
__COMMAND_LANGS: dict[str, list[dict[str, str]]] = dict()

for file in files:
    with open(f"{path}/{str(file)}") as f:
        lang = yaml.safe_load(f)
        __LANGS[lang["locale"]] = lang


for k, v in __LANGS.items():
    for command, description in v["command"].items():
        if command in __COMMAND_LANGS:
            __COMMAND_LANGS[command] = [description]
        else:
            __COMMAND_LANGS[command].append({k: description})


def get_lang(locale: str) -> dict:
    try:
        return __LANGS[locale]
    except KeyError:
        return __LANGS[__DEFAULT_LANG]


def get_command_description(command: str) -> list[dict[str, str]]:
    return __COMMAND_LANGS[command]


def get_default_command_description(command: str) -> str:
    for v in __COMMAND_LANGS[command]:
        if "en" in v:
            return v["en"]
