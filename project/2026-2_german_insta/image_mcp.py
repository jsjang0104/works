"""FLUX image generation through the Space's actual MCP SSE endpoint."""

import asyncio
import base64
import binascii
import json
from collections.abc import Callable
from datetime import timedelta
from io import BytesIO
from urllib.parse import urlparse

import httpx
from PIL import Image

import settings

MAX_IMAGE_BYTES = 25 * 1024 * 1024


class ImageGenerationError(RuntimeError):
    pass


def _validate(data: bytes) -> bytes:
    if not data or len(data) > MAX_IMAGE_BYTES:
        raise ImageGenerationError("이미지 파일 크기가 올바르지 않습니다.")
    try:
        with Image.open(BytesIO(data)) as image:
            image.verify()
    except Exception as error:
        raise ImageGenerationError(
            "서버 응답이 읽을 수 있는 이미지가 아닙니다."
        ) from error
    return data


def _decode(encoded: str) -> bytes:
    try:
        return _validate(base64.b64decode(encoded, validate=True))
    except (ValueError, binascii.Error) as error:
        raise ImageGenerationError(
            "이미지의 base64 응답이 올바르지 않습니다."
        ) from error


def _download(url: str) -> bytes:
    if url.startswith("data:image/") and ";base64," in url:
        return _decode(url.split(";base64,", 1)[1])
    if urlparse(url).scheme != "https":
        raise ImageGenerationError("이미지 다운로드 주소는 HTTPS여야 합니다.")
    # Downloads use no authentication headers: never forward the HF token to a returned URL.
    try:
        with httpx.stream("GET", url, timeout=30, follow_redirects=True) as response:
            response.raise_for_status()
            chunks, total = [], 0
            for chunk in response.iter_bytes():
                total += len(chunk)
                if total > MAX_IMAGE_BYTES:
                    raise ImageGenerationError(
                        "이미지가 다운로드 크기 제한을 초과했습니다."
                    )
                chunks.append(chunk)
        return _validate(b"".join(chunks))
    except httpx.HTTPError as error:
        raise ImageGenerationError(
            "생성된 이미지를 다운로드하지 못했습니다."
        ) from error


def _find_url(value) -> str | None:
    if isinstance(value, dict):
        for key in ("url", "uri"):
            url = value.get(key)
            if isinstance(url, str) and url.startswith(("https://", "data:image/")):
                return url
        for item in value.values():
            if isinstance(item, (dict, list)):
                found = _find_url(item)
                if found:
                    return found
    elif isinstance(value, list):
        for item in value:
            found = _find_url(item)
            if found:
                return found
    return None


def extract_image(result, download: Callable | None = None) -> bytes:
    download = download or _download
    payload = (
        result.model_dump(by_alias=True) if hasattr(result, "model_dump") else result
    )
    if not isinstance(payload, dict):
        raise ImageGenerationError("MCP 응답 형식을 해석할 수 없습니다.")
    if payload.get("isError"):
        # Remote error details may echo authorization headers or other credentials.
        raise ImageGenerationError(
            "HF MCP 이미지 생성에 실패했습니다. "
            "HF 로그인과 Space 상태·할당량을 확인하거나 잠시 후 다시 시도해 주세요."
        )
    candidates = []
    for block in payload.get("content", []):
        if block.get("type") == "image":
            return _decode(block.get("data", ""))
        if block.get("type") == "resource":
            resource = block.get("resource", {})
            if resource.get("mimeType", "").startswith("image/") and resource.get(
                "blob"
            ):
                return _decode(resource["blob"])
            candidates.append(resource)
            text = resource.get("text")
        else:
            candidates.append(block)
            text = block.get("text")
        if isinstance(text, str):
            try:
                candidates.append(json.loads(text))
            except ValueError:
                pass
    if payload.get("structuredContent"):
        candidates.append(payload["structuredContent"])
    for candidate in candidates:
        url = _find_url(candidate)
        if url:
            return _validate(download(url))
    raise ImageGenerationError(
        "MCP 응답에서 이미지 데이터나 다운로드 URL을 찾지 못했습니다."
    )


async def _call_tool(prompt: str):
    from huggingface_hub import get_token
    from mcp import ClientSession
    from mcp.client.sse import sse_client

    token = get_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    timeout = settings.MCP_TIMEOUT_SECONDS
    async with (
        asyncio.timeout(timeout),
        sse_client(
            settings.MCP_URL, headers=headers, timeout=20, sse_read_timeout=timeout
        ) as streams,
        ClientSession(
            *streams, read_timeout_seconds=timedelta(seconds=timeout)
        ) as session,
    ):
        await session.initialize()
        listing = await session.list_tools()
        if settings.MCP_TOOL not in {tool.name for tool in listing.tools}:
            raise ImageGenerationError("설정된 이미지 생성 도구가 Space에 없습니다.")
        return await session.call_tool(
            settings.MCP_TOOL,
            {
                "prompt": prompt,
                "seed": 42,
                "randomize_seed": True,
                "width": 1024,
                "height": 768,
                "num_inference_steps": 4,
            },
        )


def generate_image(prompt: str) -> bytes:
    try:
        return extract_image(asyncio.run(_call_tool(prompt)))
    except ImageGenerationError:
        raise
    except TimeoutError as error:
        raise ImageGenerationError(
            "HF MCP 응답 시간이 초과되었습니다. 잠시 후 다시 시도해 주세요."
        ) from error
    except Exception as error:
        raise ImageGenerationError(
            "HF MCP에 연결하거나 생성 도구를 호출하지 못했습니다. "
            "네트워크, HF 로그인 및 Space 할당량을 확인해 주세요."
        ) from error
