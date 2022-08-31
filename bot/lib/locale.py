import yaml
import os
path = "./locale"
files = os.listdir(path)

# デフォルトの言語
__DEFAULT_LANG = "en-US"

__LANGS = dict()
__COMMAND_LANGS: dict[str, dict[str, str]] = dict()

for file in files:
    with open(f"{path}/{str(file)}") as f:
        lang = yaml.safe_load(f)
        __LANGS[lang["locale"]] = lang


for k, v in __LANGS.items():
    for command, description in v["command"].items():
        if command in __COMMAND_LANGS:
            __COMMAND_LANGS[command][k] = description
        else:
            __COMMAND_LANGS[command] = {k: description}


def get_lang(locale: str) -> dict:
    try:
        return __LANGS[locale]
    except KeyError:
        return __LANGS[__DEFAULT_LANG]


def get_command_description(command: str) -> dict[str, str]:
    return __COMMAND_LANGS[command]


def get_default_command_description(command: str) -> str:
    return __COMMAND_LANGS[command][__DEFAULT_LANG]
