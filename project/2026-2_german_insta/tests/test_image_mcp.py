import base64
import importlib
import json
from io import BytesIO

import pytest
from PIL import Image


def subject():
    assert importlib.util.find_spec("image_mcp"), "Implement the MCP image client"
    return importlib.import_module("image_mcp")


def png():
    stream = BytesIO()
    Image.new("RGB", (128, 128), "green").save(stream, "PNG")
    return stream.getvalue()


def test_embedded_image_content_is_decoded():
    mcp = subject()
    data = png()
    result = {
        "content": [
            {"type": "image", "mimeType": "image/png", "data": base64.b64encode(data).decode()}
        ]
    }
    assert mcp.extract_image(result) == data


def test_gradio_json_file_url_is_downloaded():
    mcp = subject()
    data = png()
    result = {
        "content": [
            {
                "type": "text",
                "text": json.dumps(
                    [{"path": "/tmp/gradio/image.png", "url": "https://example.test/image.png"}, 42]
                ),
            }
        ]
    }

    def download(url):
        assert url == "https://example.test/image.png"
        return data

    assert mcp.extract_image(result, download=download) == data


def test_embedded_resource_and_resource_link_are_supported():
    mcp = subject()
    data = png()
    embedded = {
        "content": [
            {
                "type": "resource",
                "resource": {
                    "mimeType": "image/png",
                    "blob": base64.b64encode(data).decode(),
                    "uri": "file:///remote",
                },
            }
        ]
    }
    linked = {
        "content": [
            {
                "type": "resource_link",
                "mimeType": "image/png",
                "uri": "https://example.test/image.png",
            }
        ]
    }
    assert mcp.extract_image(embedded) == data
    assert mcp.extract_image(linked, download=lambda url: data) == data


def test_tool_error_and_invalid_image_are_not_successes():
    mcp = subject()
    for payload in (
        {"isError": True, "content": [{"type": "text", "text": "GPU quota exhausted"}]},
        {"content": [{"type": "image", "mimeType": "image/png", "data": "not base64"}]},
        {"content": [{"type": "text", "text": "Seed: 42"}]},
        {
            "content": [
                {
                    "type": "image",
                    "mimeType": "image/png",
                    "data": base64.b64encode(b"not an image").decode(),
                }
            ]
        },
    ):
        with pytest.raises(mcp.ImageGenerationError):
            mcp.extract_image(payload)


def test_remote_local_path_is_not_read_from_our_filesystem(tmp_path):
    mcp = subject()
    path = tmp_path / "private.png"
    path.write_bytes(png())
    result = {"content": [{"type": "text", "text": json.dumps({"path": str(path)})}]}
    with pytest.raises(mcp.ImageGenerationError):
        mcp.extract_image(result)


def test_remote_error_details_are_not_exposed():
    mcp = subject()
    sentinel = "hf_SYNTHETIC_TEST_SENTINEL"
    payload = {
        "isError": True,
        "content": [{"type": "text", "text": f"Authorization: Bearer {sentinel}"}],
    }
    with pytest.raises(mcp.ImageGenerationError) as caught:
        mcp.extract_image(payload)
    assert sentinel not in str(caught.value)
    assert "Authorization" not in str(caught.value)
    assert "HF MCP" in str(caught.value)
