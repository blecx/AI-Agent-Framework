import base64

from agents.tooling.openai_images_client import (
    OpenAIImagesGenerateParams,
    generate_mock_image,
)


class _FakeImages:
    def __init__(self):
        self.last_generate_kwargs = None

    def generate(self, **kwargs):
        self.last_generate_kwargs = kwargs
        payload = base64.b64encode(b"fake-png-bytes").decode("utf-8")
        return {"data": [{"b64_json": payload}]}


class _FakeOpenAI:
    def __init__(self):
        self.images = _FakeImages()


def test_generate_mock_image_missing_key_returns_failure(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = generate_mock_image("a prompt")

    assert result.ok is False
    assert result.message
    assert "OPENAI_API_KEY" in result.message


def test_generate_mock_image_uses_gpt_image_1_and_returns_payload():
    fake = _FakeOpenAI()

    result = generate_mock_image("a prompt", openai_client=fake)

    assert result.ok is True
    assert result.b64_json
    assert result.png_bytes == b"fake-png-bytes"

    # Verify parameters passed to OpenAI
    assert fake.images.last_generate_kwargs["model"] == OpenAIImagesGenerateParams.model
    assert fake.images.last_generate_kwargs["response_format"] == OpenAIImagesGenerateParams.response_format


def test_generate_mock_image_allows_overriding_params():
    fake = _FakeOpenAI()

    params = OpenAIImagesGenerateParams(model="gpt-image-1", size="512x512")
    result = generate_mock_image("a prompt", openai_client=fake, params=params)

    assert result.ok is True
    assert fake.images.last_generate_kwargs["size"] == "512x512"
