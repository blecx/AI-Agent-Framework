"""Unit tests for artifact media type inference helper."""

from apps.api.routers.artifacts import _infer_media_type


def test_infer_uses_extension_guess_when_available():
    media_type = _infer_media_type("report.md", b"plain text")
    assert media_type == "text/markdown"


def test_infer_png_signature():
    media_type = _infer_media_type("blob", b"\x89PNG\r\n\x1a\n" + b"x" * 8)
    assert media_type == "image/png"


def test_infer_jpeg_signature():
    media_type = _infer_media_type("blob", b"\xff\xd8\xff" + b"x" * 8)
    assert media_type == "image/jpeg"


def test_infer_gif_signature():
    media_type = _infer_media_type("blob", b"GIF89a" + b"x" * 8)
    assert media_type == "image/gif"


def test_infer_webp_signature():
    media_type = _infer_media_type("blob", b"RIFF1234WEBP" + b"x" * 4)
    assert media_type == "image/webp"


def test_infer_octet_stream_for_null_byte_text():
    media_type = _infer_media_type("blob", b"abc\x00def")
    assert media_type == "application/octet-stream"


def test_infer_csv_by_content_sniffing():
    media_type = _infer_media_type("blob", b"a,b,c\n1,2,3\n")
    assert media_type == "text/csv"


def test_infer_markdown_by_content_markers():
    media_type = _infer_media_type("blob", b"# Header\n\n- one\n")
    assert media_type == "text/markdown"


def test_infer_plain_text_fallback():
    media_type = _infer_media_type("blob", b"just normal words")
    assert media_type == "text/plain"


def test_infer_octet_stream_for_non_utf8_content():
    media_type = _infer_media_type("blob", b"\xff\xfe\xfd")
    assert media_type == "application/octet-stream"
