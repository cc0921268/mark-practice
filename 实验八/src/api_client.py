"""JSON-over-HTTP client with bounded timeout, retry and readable errors."""

import json
import time
import urllib.error
import urllib.request
from urllib.parse import urlsplit


class ApiError(RuntimeError):
    pass


class InvalidResponseError(ApiError):
    pass


def call_model(url: str, payload: dict, *, timeout: float = 0.5, retries: int = 2,
               backoff: float = 0.05, on_attempt=None) -> dict:
    """POST JSON; retry transient HTTP/network failures, reject invalid JSON/fields."""
    if urlsplit(url).scheme not in {"http", "https"}:
        raise ApiError("仅允许 HTTP(S) 地址；禁止通过 file:// 读取本地文件")
    if retries < 0:
        raise ValueError("retries cannot be negative")
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    last = None
    for attempt in range(1, retries + 2):
        request = urllib.request.Request(url, data=body, method="POST",
                                         headers={"Content-Type": "application/json; charset=utf-8"})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read()
                status = response.status
            if status != 200:
                raise ApiError(f"HTTP {status}")
            try:
                result = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise InvalidResponseError("API 返回的 JSON 无法解析。") from exc
            if not isinstance(result, dict) or not isinstance(result.get("result"), dict):
                raise InvalidResponseError("API JSON 缺少 result 对象。")
            if on_attempt:
                on_attempt({"attempt": attempt, "status": "success", "http_status": status})
            return result["result"]
        except urllib.error.HTTPError as exc:
            last = f"HTTP {exc.code}"
            retryable = exc.code >= 500 or exc.code == 429
            exc.close()
        except (urllib.error.URLError, TimeoutError) as exc:
            last = f"连接或超时：{exc}"
            retryable = True
        except ApiError:
            if on_attempt:
                on_attempt({"attempt": attempt, "status": "invalid_response"})
            raise
        if on_attempt:
            on_attempt({"attempt": attempt, "status": "retry" if retryable and attempt <= retries else "failed", "reason": last})
        if not retryable or attempt > retries:
            raise ApiError(f"API 调用失败，已尝试 {attempt} 次：{last}")
        time.sleep(backoff * attempt)
    raise ApiError(last or "API 调用失败。")

