import asyncio
from datetime import timedelta
from re import search
from typing import List, Tuple

import yaml
from loguru import logger
from pydantic import BaseModel

from components import redis
from components.config import async_load_yaml_config
from components.monitor import monitor
from components.requests import close_requests, get, register_requests
from components.retry import retry
from setting import setting


class Proxies(BaseModel):
    proxies: List[dict]
    proxy_names: List[str]
    proxy_names_of_high_speed_special_line: List[str]
    proxy_names_of_hk_node: List[str]
    proxy_names_of_us_node: List[str]
    proxy_names_of_jp_node: List[str]
    proxy_names_of_kr_node: List[str]
    proxy_names_of_tw_node: List[str]


def node_name_matches_country(node_name: str) -> Tuple:  # noqa: C901
    if search(r"(AR|阿根廷)", node_name):
        return f"🇦🇷 {node_name}", "AR"
    if search(r"(AT|奥地利|维也纳)", node_name):
        return f"🇦🇹 {node_name}", "AT"
    if search(r"(AU|Australia|Sydney|澳大利亚|悉尼)", node_name):
        return f"🇦🇺 {node_name}", "AU"
    if search(r"(BE|比利时)", node_name):
        return f"🇧🇪 {node_name}", "BE"
    if search(r"(BR|Brazil|巴西|圣保罗)", node_name):
        return f"🇧🇷 {node_name}", "BR"
    if search(r"(CA|Canada|加拿大|蒙特利尔|温哥华|楓葉|枫叶)", node_name):
        return f"🇨🇦 {node_name}", "CA"
    if search(r"(CH|瑞士|苏黎世)", node_name):
        return f"🇨🇭 {node_name}", "CH"
    if search(r"(DE|Germany|德国|法兰克福|德)", node_name):
        return f"🇩🇪 {node_name}", "DE"
    if search(r"(DK|丹麦)", node_name):
        return f"🇩🇰 {node_name}", "DK"
    if search(r"(ES|西班牙)", node_name):
        return f"🇪🇸 {node_name}", "ES"
    if search(r"EU", node_name):
        return f"🇪🇺 {node_name}", "EU"
    if search(r"(FI|Finland|芬兰|赫尔辛基)", node_name):
        return f"🇫🇮 {node_name}", "FI"
    if search(r"(FR|France|法国|巴黎)", node_name):
        return f"🇫🇷 {node_name}", "FR"
    if search(r"(UK|England|UnitedKingdom|英国|英|伦敦)", node_name):
        return f"🇬🇧 {node_name}", "UK"
    if search(r"(HK|HongKong|香港|深港|沪港|呼港|HKT|HKBN|HGC|WTT|CMI|穗港|京港|港)", node_name):
        return f"🇭🇰 {node_name}", "HK"
    if search(r"(ID|Indonesia|印尼|印度尼西亚|雅加达)", node_name):
        return f"🇮🇩 {node_name}", "ID"
    if search(r"(IE|Ireland|爱尔兰|都柏林)", node_name):
        return f"🇮🇪 {node_name}", "IE"
    if search(r"(IN|India|印度|孟买)", node_name):
        return f"🇮🇳 {node_name}", "IN"
    if search(r"(IT|Italy|意大利|米兰)", node_name):
        return f"🇮🇹 {node_name}", "IT"
    if search(r"(JP|Japan|日本|东京|大阪|埼玉|沪日|穗日|川日|中日|泉日|杭日)", node_name):
        return f"🇯🇵 {node_name}", "JP"
    if search(r"(KP|朝鲜)", node_name):
        return f"🇰🇵 {node_name}", "KP"
    if search(r"(KR|Korea|KOR|韩国|首尔|韩|韓)", node_name):
        return f"🇰🇷 {node_name}", "KR"
    if search(r"(MO|Macao|澳门|CTM)", node_name):
        return f"🇲🇴 {node_name}", "MO"
    if search(r"(MY|Malaysia|马来西亚)", node_name):
        return f"🇲🇾 {node_name}", "MY"
    if search(r"(NL|Netherlands|荷兰|阿姆斯特丹)", node_name):
        return f"🇳🇱 {node_name}", "NL"
    if search(r"(PH|Philippines|菲律宾)", node_name):
        return f"🇵🇭 {node_name}", "PH"
    if search(r"(RO|罗马尼亚)", node_name):
        return f"🇷🇴 {node_name}", "RO"
    if search(r"(RU|Russia|俄罗斯|伯力|莫斯科|圣彼得堡|西伯利亚|新西伯利亚|京俄|杭俄)", node_name):
        return f"🇷🇺 {node_name}", "RU"
    if search(r"(SA|沙特|迪拜)", node_name):
        return f"🇸🇦 {node_name}", "SA"
    if search(r"(SE|Sweden)", node_name):
        return f"🇸🇪 {node_name}", "SE"
    if search(r"(SG|Singapore|新加坡|狮城|沪新|京新|泉新|穗新|深新|杭新)", node_name):
        return f"🇸🇬 {node_name}", "SG"
    if search(r"(TH|Thailand|泰国|曼谷)", node_name):
        return f"🇹🇭 {node_name}", "TH"
    if search(r"(TR|Turkey|土耳其|伊斯坦布尔)", node_name):
        return f"🇹🇷 {node_name}", "TR"
    if search(r"(PK|Pakistan|巴基斯坦)", node_name):
        return f"🇵🇰 {node_name}", "PK"
    if search(
        r"(US|America|UnitedStates|美国|美|京美|波特兰|达拉斯|俄勒冈|凤凰城|费利蒙|硅谷|拉斯维加斯|洛杉矶|圣何塞|圣克拉拉|西雅图|芝加哥|沪美)",  # noqa: E501
        node_name,
    ):
        return f"🇺🇲 {node_name}", "US"
    if search(r"(VN|越南)", node_name):
        return f"🇻🇳 {node_name}", "VN"
    if search(r"(ZA|南非)", node_name):
        return f"🇿🇦 {node_name}", "ZA"
    if search(r"(TW|Taiwan|台湾|台北|台中|新北|彰化|CHT|台|HINET)", node_name):
        return f"🇨🇳 {node_name}", "TW"
    if search(r"(CN|China|回国|中国|江苏|北京|上海|广州|深圳|杭州|常州|徐州|青岛|宁波|镇江|back)", node_name):
        return f"🇨🇳 {node_name}", "CN"

    raise ValueError(f"clash 地区匹配失败 -> {node_name}")


@retry(retries=5)
async def get_clash_proxies() -> Proxies:
    proxy_names = []
    proxy_names_of_high_speed_special_line = []
    proxy_names_of_hk_node = []
    proxy_names_of_us_node = []
    proxy_names_of_jp_node = []
    proxy_names_of_kr_node = []
    proxy_names_of_tw_node = []

    rsp = await get(setting.clash)
    assert rsp.ok, f"clash 订阅获取失败, {rsp.status_code}"

    rdb = redis.client()
    user_info = rsp.headers.get("subscription-userinfo")
    if user_info is not None:
        logger.info("subscription user info: {}", user_info)
        await rdb.set("subscription:user:info", user_info, ex=timedelta(hours=1))

    proxies: List[dict] = yaml.safe_load(rsp.text).get("proxies", [])
    for proxy in proxies:
        try:
            node_name, country = node_name_matches_country(proxy["name"])
        except ValueError as e:
            logger.warning(e)
            continue

        node_name = node_name.replace("中继", "中转")
        node_name = node_name.replace("AIA", "腾讯内网")
        proxy["name"] = node_name
        proxy_names.append(node_name)
        if country == "HK":
            if "专线" in node_name or "腾讯内网" in node_name:
                proxy_names_of_high_speed_special_line.append(node_name)
            proxy_names_of_hk_node.append(node_name)
        # elif country == "SG":
        #     if "专线" in node_name or "腾讯内网" in node_name:
        #         proxy_names_of_high_speed_special_line.append(node_name)
        elif country == "US":
            proxy_names_of_us_node.append(node_name)
        elif country == "JP":
            proxy_names_of_jp_node.append(node_name)
        elif country == "KR":
            proxy_names_of_kr_node.append(node_name)
        elif country == "TW":
            proxy_names_of_tw_node.append(node_name)

    return Proxies(
        proxies=proxies,
        proxy_names=proxy_names,
        proxy_names_of_high_speed_special_line=proxy_names_of_high_speed_special_line,
        proxy_names_of_hk_node=proxy_names_of_hk_node,
        proxy_names_of_us_node=proxy_names_of_us_node,
        proxy_names_of_jp_node=proxy_names_of_jp_node,
        proxy_names_of_kr_node=proxy_names_of_kr_node,
        proxy_names_of_tw_node=proxy_names_of_tw_node,
    )


@monitor
async def refresh_clash_subscription():
    logger.info("start refreshing the subscription of clash")
    proxies = await get_clash_proxies()
    clash = await async_load_yaml_config("../config/clash.yaml")

    clash["proxies"] = proxies.proxies
    clash["proxy-groups"][1]["proxies"].extend(proxies.proxy_names)
    clash["proxy-groups"][2]["proxies"].extend(proxies.proxy_names_of_high_speed_special_line)
    clash["proxy-groups"][3]["proxies"].extend(proxies.proxy_names)
    clash["proxy-groups"][4]["proxies"].extend(proxies.proxy_names)
    clash["proxy-groups"][5]["proxies"].extend(proxies.proxy_names)

    clash["proxy-groups"][25]["proxies"].extend(proxies.proxy_names_of_hk_node)
    clash["proxy-groups"][26]["proxies"].extend(proxies.proxy_names_of_tw_node)
    clash["proxy-groups"][27]["proxies"].extend(proxies.proxy_names_of_us_node)
    clash["proxy-groups"][28]["proxies"].extend(proxies.proxy_names_of_jp_node)
    clash["proxy-groups"][29]["proxies"].extend(proxies.proxy_names_of_kr_node)

    clash_yaml = yaml.safe_dump(clash, allow_unicode=True, width=800, sort_keys=False)
    rdb = redis.client()
    await rdb.set("subscription:clash", clash_yaml, ex=timedelta(hours=1))
    logger.info("refresh clash subscription successful")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(redis.register_redis())
    loop.run_until_complete(register_requests())
    loop.run_until_complete(refresh_clash_subscription())
    loop.run_until_complete(close_requests())
