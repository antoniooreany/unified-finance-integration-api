import json

import httpx
from fastapi import HTTPException
from pydantic import ValidationError

from app.config import settings
from app.schemas import Invoice, ProviderResponse


async def fetch_invoices() -> list[Invoice]:
    url = f"{settings.provider_base_url.rstrip('/')}/api/v1/invoices"
    headers = {"X-API-Key": settings.provider_api_key}

    async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
        try:
            response = await client.get(url, headers=headers)
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            raise HTTPException(status_code=503, detail="Provider unavailable") from e

        if response.status_code == 401:
            raise HTTPException(status_code=500, detail="Provider configuration error")
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            err_headers = {}
            if retry_after and retry_after.isdigit():
                err_headers["Retry-After"] = retry_after
            raise HTTPException(status_code=503, detail="Provider temporarily unavailable", headers=err_headers)
        elif response.status_code == 500 or response.status_code >= 400:
            raise HTTPException(status_code=502, detail="Provider service error")

        try:
            data = response.json()
            if not isinstance(data, dict) or "invoices" not in data:
                raise ValueError("Missing invoices key")
            if not isinstance(data["invoices"], list):
                raise TypeError("invoices must be a list")
            provider_response = ProviderResponse.model_validate(data)
            return provider_response.invoices
        except (json.JSONDecodeError, ValidationError, ValueError, TypeError) as e:
            raise HTTPException(status_code=502, detail="Invalid provider response") from e
