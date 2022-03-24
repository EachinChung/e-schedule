from enum import unique

from pydantic import BaseModel, HttpUrl

from components.config import load_yaml_config
from components.enum import StrEnum


@unique
class Mode(StrEnum):
    debug = "debug"
    test = "test"
    release = "release"


class Subconverter(BaseModel):
    host: HttpUrl
    url: HttpUrl
    config: HttpUrl


class Redis(BaseModel):
    host: str
    port: int
    password: str


class Monitor(BaseModel):
    wecom: str


class Account(BaseModel):
    airport: HttpUrl
    email: str
    password: str


class Setting(BaseModel):
    mode: Mode
    clash: HttpUrl
    account: Account
    subconverter: Subconverter
    redis: Redis
    monitor: Monitor


def register_setting() -> Setting:
    cfg = load_yaml_config("config/base.yaml")
    return Setting(**cfg)


setting = register_setting()
