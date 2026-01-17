from __future__ import annotations

import os
from openai import OpenAI, AsyncOpenAI
from .config import get_settings

def get_client() -> OpenAI:
    s = get_settings()

    if s.provider == "openai":
        return OpenAI(api_key=s.openai_api_key, base_url=s.openai_base_url)

    # Azure OpenAI (v1 endpoint)
    return OpenAI(api_key=s.azure_api_key, base_url=s.azure_base_url)


def get_async_client() -> AsyncOpenAI:
    s = get_settings()

    if s.provider == "openai":
        return AsyncOpenAI(api_key=s.openai_api_key, base_url=s.openai_base_url)

    # Azure OpenAI (v1 endpoint)
    return AsyncOpenAI(api_key=s.azure_api_key, base_url=s.azure_base_url)

