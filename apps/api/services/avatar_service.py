"""Avatar inference utilities.

This module provides lightweight helpers for enriching API responses with avatar
URLs based on known identifier patterns (email, GitHub username).
"""

from __future__ import annotations

import hashlib
import re
from typing import Optional
from urllib.parse import quote


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_GITHUB_USERNAME_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")


def infer_owner_avatar_url(owner: Optional[str]) -> Optional[str]:
    """Infer an avatar URL for an owner identifier.

    Rules (minimal and deterministic):
    - If the owner looks like an email address, return a Gravatar identicon URL.
    - If the owner looks like a GitHub username, return a GitHub profile PNG URL.
    - Otherwise return None.
    """

    if not owner:
        return None

    owner = owner.strip()
    if not owner:
        return None

    if _EMAIL_RE.match(owner):
        digest = hashlib.md5(owner.lower().encode("utf-8")).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?d=identicon"

    if _GITHUB_USERNAME_RE.match(owner):
        return f"https://github.com/{quote(owner)}.png"

    return None
