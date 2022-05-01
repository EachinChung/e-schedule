import asyncio
import logging
from typing import List

import yaml
from aiofile import async_open
from pydantic import BaseModel, Field

from components.config import get_real_path
from components.monitor import monitor
from components.requests import Response, close_requests, get, register_requests
from components.retry import retry
from setting import setting

PROXY_GROUP_SET = {
    "🆎 AdBlock",
    "🍃 应用净化",
    "🎯 全球直连",
    "📺 巴哈姆特",
    "🌍 国外媒体",
    "🧱 快速破墙",
    "🔧 手动切换",
    "🇰🇷 韩国节点",
    "♻️ 自动选择",
    "🇨🇳 台湾节点",
    "🐟 漏网之鱼",
    "🔯 故障转移",
    "🌏 国内媒体",
    "📺 哔哩哔哩",
    "🛑 广告拦截",
    "🍎 苹果服务",
    "🎮 游戏平台",
    "🇺🇲 美国节点",
    "🇭🇰 香港节点",
    "📹 油管视频",
    "🔮 负载均衡",
    "📲 电报消息",
    "🇯🇵 日本节点",
    "Ⓜ️ 微软云盘",
    "🚀 节点选择",
    "Ⓜ️ 微软服务",
    "🎶 网易音乐",
    "📢 谷歌FCM",
    "🎥 奈飞视频",
    "🛡️ 隐私防护",
}


class ClashConfig(BaseModel):
    port: int = 7890
    socks_port: int = Field(7891, alias="socks-port")
    external_controller: str = Field("127.0.0.1:9090", alias="external-controller")
    allow_lan: bool = Field(False, alias="allow-lan")
    log_level: str = Field("info", alias="log-level")
    proxy_groups: list = Field(alias="proxy-groups")
    mode: str = "rule"
    proxies: list
    rules: List[str]


@retry(retries=5)
async def get_config() -> Response:
    rsp = await get(
        setting.subconverter.host,
        params={
            "target": "clash",
            "url": setting.subconverter.url,
            "insert": "false",
            "config": setting.subconverter.config,
            "emoji": "true",
            "list": "false",
            "tfo": "false",
            "scv": "false",
            "fdn": "false",
            "sort": "false",
            "new_name": "true",
        },
    )
    assert rsp.ok
    return rsp


async def save_config(config: ClashConfig):
    path = get_real_path("../config/clash.yaml")
    async with async_open(path, "w") as file:
        await file.write(yaml.safe_dump(config.dict(by_alias=True), allow_unicode=True, width=800))


@monitor
async def refresh_clash_config():
    logging.info("start refreshing the config of clash")
    result = await get_config()
    config = yaml.safe_load(result.text)
    config = ClashConfig(**config)

    for rule in config.rules:
        try:
            proxy_group = rule.split(",")[2]
        except IndexError as err:
            if "MATCH" in rule:
                continue
            raise ValueError(f"rule {rule} is invalid") from err
        else:
            assert proxy_group in PROXY_GROUP_SET, f"clash 配置发现错误: {rule}"

    config.proxies = []
    config.proxy_groups = [
        {
            "name": "🚀 节点选择",
            "type": "select",
            "proxies": [
                "🧱 快速破墙",
                "♻️ 自动选择",
                "🔯 故障转移",
                "🔮 负载均衡",
                "🇭🇰 香港节点",
                "🇨🇳 台湾节点",
                "🇯🇵 日本节点",
                "🇺🇲 美国节点",
                "🇰🇷 韩国节点",
                "🔧 手动切换",
                "DIRECT",
            ],
        },
        {"name": "🔧 手动切换", "type": "select", "proxies": []},
        {
            "name": "🧱 快速破墙",
            "type": "url-test",
            "url": "http://www.gstatic.com/generate_204",
            "interval": 300,
            "proxies": [],
        },
        {
            "name": "♻️ 自动选择",
            "type": "url-test",
            "url": "http://www.gstatic.com/generate_204",
            "interval": 300,
            "proxies": [],
        },
        {
            "name": "🔯 故障转移",
            "type": "fallback",
            "url": "http://www.gstatic.com/generate_204",
            "interval": 300,
            "proxies": [],
        },
        {
            "name": "🔮 负载均衡",
            "type": "load-balance",
            "strategy": "consistent-hashing",
            "url": "http://www.gstatic.com/generate_204",
            "interval": 300,
            "proxies": [],
        },
        {
            "name": "📲 电报消息",
            "type": "select",
            "proxies": [
                "🚀 节点选择",
                "🧱 快速破墙",
                "♻️ 自动选择",
                "🇭🇰 香港节点",
                "🇨🇳 台湾节点",
                "🇯🇵 日本节点",
                "🇺🇲 美国节点",
                "🇰🇷 韩国节点",
                "🔧 手动切换",
                "DIRECT",
            ],
        },
        {
            "name": "📹 油管视频",
            "type": "select",
            "proxies": [
                "🚀 节点选择",
                "🧱 快速破墙",
                "♻️ 自动选择",
                "🇭🇰 香港节点",
                "🇨🇳 台湾节点",
                "🇯🇵 日本节点",
                "🇺🇲 美国节点",
                "🇰🇷 韩国节点",
                "🔧 手动切换",
                "DIRECT",
            ],
        },
        {
            "name": "🎥 奈飞视频",
            "type": "select",
            "proxies": [
                "🚀 节点选择",
                "🧱 快速破墙",
                "♻️ 自动选择",
                "🇭🇰 香港节点",
                "🇨🇳 台湾节点",
                "🇯🇵 日本节点",
                "🇺🇲 美国节点",
                "🇰🇷 韩国节点",
                "🔧 手动切换",
                "DIRECT",
            ],
        },
        {"name": "📺 巴哈姆特", "type": "select", "proxies": ["🇨🇳 台湾节点", "🚀 节点选择", "🔧 手动切换", "DIRECT"]},
        {"name": "📺 哔哩哔哩", "type": "select", "proxies": ["🎯 全球直连", "🇨🇳 台湾节点", "🇭🇰 香港节点"]},
        {
            "name": "🌍 国外媒体",
            "type": "select",
            "proxies": [
                "🚀 节点选择",
                "🧱 快速破墙",
                "♻️ 自动选择",
                "🇭🇰 香港节点",
                "🇨🇳 台湾节点",
                "🇯🇵 日本节点",
                "🇺🇲 美国节点",
                "🇰🇷 韩国节点",
                "🔧 手动切换",
                "DIRECT",
            ],
        },
        {
            "name": "🌏 国内媒体",
            "type": "select",
            "proxies": ["DIRECT", "🇭🇰 香港节点", "🇨🇳 台湾节点", "🇯🇵 日本节点", "🔧 手动切换"],
        },
        {
            "name": "📢 谷歌FCM",
            "type": "select",
            "proxies": [
                "🚀 节点选择",
                "🇺🇲 美国节点",
                "🇭🇰 香港节点",
                "🇨🇳 台湾节点",
                "🇯🇵 日本节点",
                "🇰🇷 韩国节点",
                "🔧 手动切换",
                "DIRECT",
            ],
        },
        {
            "name": "Ⓜ️ 微软云盘",
            "type": "select",
            "proxies": [
                "DIRECT",
                "🚀 节点选择",
                "🇺🇲 美国节点",
                "🇭🇰 香港节点",
                "🇨🇳 台湾节点",
                "🇯🇵 日本节点",
                "🇰🇷 韩国节点",
                "🔧 手动切换",
            ],
        },
        {
            "name": "Ⓜ️ 微软服务",
            "type": "select",
            "proxies": [
                "🚀 节点选择",
                "🇺🇲 美国节点",
                "🇭🇰 香港节点",
                "🇨🇳 台湾节点",
                "🇯🇵 日本节点",
                "🇰🇷 韩国节点",
                "🔧 手动切换",
                "DIRECT",
            ],
        },
        {
            "name": "🍎 苹果服务",
            "type": "select",
            "proxies": [
                "DIRECT",
                "🚀 节点选择",
                "🇺🇲 美国节点",
                "🇭🇰 香港节点",
                "🇨🇳 台湾节点",
                "🇯🇵 日本节点",
                "🇰🇷 韩国节点",
                "🔧 手动切换",
            ],
        },
        {
            "name": "🎮 游戏平台",
            "type": "select",
            "proxies": [
                "DIRECT",
                "🚀 节点选择",
                "🇺🇲 美国节点",
                "🇭🇰 香港节点",
                "🇨🇳 台湾节点",
                "🇯🇵 日本节点",
                "🇰🇷 韩国节点",
                "🔧 手动切换",
            ],
        },
        {"name": "🎶 网易音乐", "type": "select", "proxies": ["DIRECT", "🚀 节点选择", "♻️ 自动选择"]},
        {"name": "🎯 全球直连", "type": "select", "proxies": ["DIRECT", "🚀 节点选择", "♻️ 自动选择"]},
        {"name": "🛑 广告拦截", "type": "select", "proxies": ["REJECT", "DIRECT"]},
        {"name": "🍃 应用净化", "type": "select", "proxies": ["REJECT", "DIRECT"]},
        {"name": "🆎 AdBlock", "type": "select", "proxies": ["REJECT", "DIRECT"]},
        {"name": "🛡️ 隐私防护", "type": "select", "proxies": ["REJECT", "DIRECT"]},
        {
            "name": "🐟 漏网之鱼",
            "type": "select",
            "proxies": [
                "🚀 节点选择",
                "🧱 快速破墙",
                "♻️ 自动选择",
                "DIRECT",
                "🇭🇰 香港节点",
                "🇨🇳 台湾节点",
                "🇯🇵 日本节点",
                "🇺🇲 美国节点",
                "🇰🇷 韩国节点",
                "🔧 手动切换",
            ],
        },
        {
            "name": "🇭🇰 香港节点",
            "type": "url-test",
            "url": "http://www.gstatic.com/generate_204",
            "interval": 300,
            "proxies": [],
        },
        {
            "name": "🇨🇳 台湾节点",
            "type": "url-test",
            "url": "http://www.gstatic.com/generate_204",
            "interval": 300,
            "proxies": [],
        },
        {
            "name": "🇺🇲 美国节点",
            "type": "url-test",
            "url": "http://www.gstatic.com/generate_204",
            "interval": 300,
            "proxies": [],
        },
        {
            "name": "🇯🇵 日本节点",
            "type": "url-test",
            "url": "http://www.gstatic.com/generate_204",
            "interval": 300,
            "proxies": [],
        },
        {
            "name": "🇰🇷 韩国节点",
            "type": "url-test",
            "url": "http://www.gstatic.com/generate_204",
            "interval": 300,
            "proxies": [],
        },
    ]
    await save_config(config)
    logging.info("refresh clash config successful")


if __name__ == "__main__":
    logging.basicConfig(
        filename="refresh_clash_config.log",
        level=logging.INFO,
        format="[%(levelname)s] %(asctime)s - %(message)s",
    )

    loop = asyncio.get_event_loop()
    loop.run_until_complete(register_requests())
    loop.run_until_complete(refresh_clash_config())
    loop.run_until_complete(close_requests())
