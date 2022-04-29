import inspect
from os import path
from typing import Dict, Optional

import yaml
from aiofile import async_open


def get_real_path(cfg_file: str, base_file: Optional[str] = None) -> str:
    if not path.isabs(cfg_file):
        if base_file is None:
            frame = inspect.stack()[2]
            module = inspect.getmodule(frame[0])
            base_file = module.__file__
        dirname = path.dirname(path.realpath(base_file))
        cfg_file = path.join(dirname, cfg_file)
    return cfg_file


async def async_load_yaml_config(cfg_file: str, base_file: Optional[str] = None) -> Dict:
    async with async_open(get_real_path(cfg_file, base_file), "r") as file:
        cfg = yaml.load(await file.read(), Loader=yaml.FullLoader)
    return cfg


def load_yaml_config(cfg_file: str, base_file: Optional[str] = None) -> Dict:
    cfg_file = get_real_path(cfg_file, base_file)
    with open(cfg_file, "r", encoding="utf-8") as file:
        cfg = yaml.load(file.read(), Loader=yaml.FullLoader)
    return cfg
