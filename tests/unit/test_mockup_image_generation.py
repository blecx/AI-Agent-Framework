from pathlib import Path

import pytest

from agents.tooling.mockup_image_generation import generate_issue_mockup_artifacts
from agents.tooling.openai_images_client import OpenAIImagesGenerateParams


class _FakeOpenAIImagesClient:
    def __init__(self, payload: bytes):
        self._payload = payload
        self.calls = []

    def generate_png_bytes(
        self,
        prompt: str,
        *,
        params: OpenAIImagesGenerateParams | None = None,
    ) -> bytes:
        self.calls.append({"prompt": prompt, "params": params})
        return self._payload


def test_generate_issue_mockup_artifacts_missing_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = generate_issue_mockup_artifacts(
        481,
        prompt="a mock UI",
        base_dir=tmp_path,
    )
    assert result.ok is False
    assert "OPENAI_API_KEY" in result.message


def test_generate_issue_mockup_artifacts_writes_files(tmp_path: Path):
    fake_png = b"\x89PNG\r\n\x1a\nFAKE"
    fake_client = _FakeOpenAIImagesClient(fake_png)

    result = generate_issue_mockup_artifacts(
        481,
        prompt="a mock UI",
        image_count=2,
        base_dir=tmp_path,
        openai_client=fake_client,
    )

    out_dir = tmp_path / "issue-481"
    assert result.ok is True
    assert result.output_dir == out_dir
    assert (out_dir / "mockup-001.png").exists()
    assert (out_dir / "mockup-002.png").exists()
    assert (out_dir / "index.html").exists()
    assert len(result.image_paths) == 2
    assert len(fake_client.calls) == 2
