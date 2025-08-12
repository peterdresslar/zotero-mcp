from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional

import requests

from .config import get_bridge_endpoint, get_bridge_token
from .errors import WriteBridgeUnavailable, WriteBridgeAuthError


class WriteBridgeClient:
    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None, timeout: float = 5.0):
        self.base_url = base_url or get_bridge_endpoint()
        self.token = token or get_bridge_token()
        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.token:
            headers["X-ZMCP-Token"] = self.token
        return headers

    def health(self) -> Dict[str, Any]:
        try:
            resp = requests.get(f"{self.base_url}/health", headers=self._headers(), timeout=self.timeout)
        except requests.exceptions.RequestException as e:
            raise WriteBridgeUnavailable(str(e))
        if resp.status_code == 401:
            raise WriteBridgeAuthError("bridge requires token or token invalid")
        if resp.status_code >= 400:
            raise WriteBridgeUnavailable(f"health error: {resp.status_code} {resp.text}")
        return resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {"raw": resp.text}

    def init_token(self, token: str) -> bool:
        try:
            resp = requests.post(
                f"{self.base_url}/init",
                json={"token": token},
                headers={"Accept": "application/json"},
                timeout=self.timeout,
            )
        except requests.exceptions.RequestException as e:
            raise WriteBridgeUnavailable(str(e))
        if resp.status_code >= 400:
            return False
        data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
        return bool(data.get("ok", resp.ok))

    def tag(self, item_key: str, add: Optional[list[str]] = None, remove: Optional[list[str]] = None, batch_id: Optional[str] = None) -> Dict[str, Any]:
        payload = {"itemKey": item_key, "add": add or [], "remove": remove or []}
        if batch_id:
            payload["batchId"] = batch_id
        try:
            resp = requests.post(f"{self.base_url}/tag", json=payload, headers=self._headers(), timeout=self.timeout)
        except requests.exceptions.RequestException as e:
            raise WriteBridgeUnavailable(str(e))
        if resp.status_code == 401:
            raise WriteBridgeAuthError("token invalid or missing")
        if resp.status_code >= 400:
            raise WriteBridgeUnavailable(f"tag error: {resp.status_code} {resp.text}")
        return resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {"raw": resp.text}

    def note(self, item_key: str, content: str, mode: str = "upsert", marker: Optional[str] = None) -> Dict[str, Any]:
        payload = {"itemKey": item_key, "content": content, "mode": mode}
        if marker:
            payload["marker"] = marker
        try:
            resp = requests.post(f"{self.base_url}/note", json=payload, headers=self._headers(), timeout=self.timeout)
        except requests.exceptions.RequestException as e:
            raise WriteBridgeUnavailable(str(e))
        if resp.status_code == 401:
            raise WriteBridgeAuthError("token invalid or missing")
        if resp.status_code >= 400:
            raise WriteBridgeUnavailable(f"note error: {resp.status_code} {resp.text}")
        return resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {"raw": resp.text}
