import logging
from enum import unique
from http.cookies import SimpleCookie
from typing import Mapping, Optional, Union
from uuid import UUID, uuid4

import ujson as ujson
from aiohttp import ClientResponse, ClientSession, ClientTimeout, TCPConnector
from aiohttp.typedefs import LooseCookies, LooseHeaders
from multidict import CIMultiDictProxy
from yarl import URL

from components.enum import StrEnum
from components.getsetter import GetSetTer

pool = GetSetTer()


@unique
class Method(StrEnum):
    get = "get"
    post = "post"
    put = "put"
    patch = "patch"
    delete = "delete"


class Response:
    def __init__(
        self,
        r_id: UUID,
        url: URL,
        status_code: int,
        headers: CIMultiDictProxy[str],
        cookies: SimpleCookie,
        content: bytes,
        text: str,
    ):
        self.__r_id = r_id
        self.__url: URL = url
        self.__status_code = status_code
        self.__headers = headers
        self.__cookies = cookies
        self.__content = content
        self.__text: str = text

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"<Response({self.r_id}) [{self.status_code}]>"

    def __bool__(self):
        return self.ok

    def __nonzero__(self):
        return self.ok

    @property
    def r_id(self) -> UUID:
        return self.__r_id

    @property
    def url(self) -> URL:
        return self.__url

    @property
    def ok(self) -> bool:
        return self.status_code < 400

    @property
    def status_code(self) -> int:
        return self.__status_code

    @property
    def headers(self) -> CIMultiDictProxy[str]:
        return self.__headers

    @property
    def cookies(self) -> SimpleCookie:
        return self.__cookies

    @property
    def content(self) -> bytes:
        return self.__content

    @property
    def text(self) -> str:
        return self.__text

    def json(self) -> Union[list, dict]:
        return ujson.loads(self.text)


async def register_requests():
    pool.val = TCPConnector(limit_per_host=3, keepalive_timeout=15)


async def close_requests():
    await pool.val.close()


async def request(
    method: str,
    url: str,
    params: Optional[Mapping[str, str]] = None,
    data: Optional[dict] = None,
    json: Optional[dict] = None,
    headers: Optional[LooseHeaders] = None,
    cookies: Optional[LooseCookies] = None,
    *args,
    **kwargs,
) -> Response:
    r_id = uuid4()
    logging.info("%s request(%s), url: %s, params: %s, data: %s, json: %s", method, r_id, url, params, data, json)
    async with ClientSession(connector=pool.val, timeout=ClientTimeout(total=30), connector_owner=False) as session:
        async with getattr(session, method)(
            url,
            params=params,
            data=data,
            json=json,
            headers=headers,
            cookies=cookies,
            *args,
            **kwargs,
        ) as response:
            response: ClientResponse
            content = await response.read()
            text = await response.text()

            rsp = Response(
                r_id=r_id,
                url=response.url,
                status_code=response.status,
                headers=response.headers,
                cookies=response.cookies,
                content=content,
                text=text,
            )

            if not rsp.ok:
                logging.warning("%s, text: %s", rsp, rsp.text)

            return rsp


# noinspection DuplicatedCode
async def get(
    url: str,
    params: Optional[Mapping[str, str]] = None,
    data: Optional[dict] = None,
    json: Optional[dict] = None,
    headers: Optional[LooseHeaders] = None,
    cookies: Optional[LooseCookies] = None,
    *args,
    **kwargs,
) -> Response:
    return await request(
        Method.get,
        url,
        params=params,
        data=data,
        json=json,
        headers=headers,
        cookies=cookies,
        *args,
        **kwargs,
    )


# noinspection DuplicatedCode
async def post(
    url: str,
    params: Optional[Mapping[str, str]] = None,
    data: Optional[dict] = None,
    json: Optional[dict] = None,
    headers: Optional[LooseHeaders] = None,
    cookies: Optional[LooseCookies] = None,
    *args,
    **kwargs,
) -> Response:
    return await request(
        Method.post,
        url,
        params=params,
        data=data,
        json=json,
        headers=headers,
        cookies=cookies,
        *args,
        **kwargs,
    )


# noinspection DuplicatedCode
async def put(
    url: str,
    params: Optional[Mapping[str, str]] = None,
    data: Optional[dict] = None,
    json: Optional[dict] = None,
    headers: Optional[LooseHeaders] = None,
    cookies: Optional[LooseCookies] = None,
    *args,
    **kwargs,
) -> Response:
    return await request(
        Method.put,
        url,
        params=params,
        data=data,
        json=json,
        headers=headers,
        cookies=cookies,
        *args,
        **kwargs,
    )


# noinspection DuplicatedCode
async def patch(
    url: str,
    params: Optional[Mapping[str, str]] = None,
    data: Optional[dict] = None,
    json: Optional[dict] = None,
    headers: Optional[LooseHeaders] = None,
    cookies: Optional[LooseCookies] = None,
    *args,
    **kwargs,
) -> Response:
    return await request(
        Method.patch,
        url,
        params=params,
        data=data,
        json=json,
        headers=headers,
        cookies=cookies,
        *args,
        **kwargs,
    )


# noinspection DuplicatedCode
async def delete(
    url: str,
    params: Optional[Mapping[str, str]] = None,
    data: Optional[dict] = None,
    json: Optional[dict] = None,
    headers: Optional[LooseHeaders] = None,
    cookies: Optional[LooseCookies] = None,
    *args,
    **kwargs,
) -> Response:
    return await request(
        Method.delete,
        url,
        params=params,
        data=data,
        json=json,
        headers=headers,
        cookies=cookies,
        *args,
        **kwargs,
    )
