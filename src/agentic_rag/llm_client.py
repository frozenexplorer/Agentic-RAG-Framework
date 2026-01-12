from __future__ import annotations

import os
from openai import OpenAI
from .config import get_settings

def get_client() -> OpenAI:
    s = get_settings()

    if s.provider == "openai":
        # LM Studio (or any OpenAI-compatible server) can be used by setting OPENAI_BASE_URL
        base_url = os.getenv("OPENAI_BASE_URL", "").strip() or None
        return OpenAI(api_key=s.openai_api_key, base_url=base_url)

    # Azure OpenAI (v1 endpoint)
    return OpenAI(api_key=s.azure_api_key, base_url=s.azure_base_url)

