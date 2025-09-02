# app/middleware.py
from __future__ import annotations

import time, uuid, threading
from typing import Dict, Optional, Set

from jose import jwt as jose_jwt
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        rid = uuid.uuid4().hex
        request.state.request_id = rid
        response = await call_next(request)
        response.headers["X-Request-ID"] = rid
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        rate_per_sec: float = 5.0,
        burst: int = 15,
        skip_paths: Optional[Set[str]] = None,
    ) -> None:
        super().__init__(app)
        self.rate = float(rate_per_sec)
        self.capacity = int(burst)
        self.tokens: Dict[str, float] = {}
        self.updated: Dict[str, float] = {}
        self.lock = threading.Lock()
        self.skip_paths = set(skip_paths or set())

    def _key(self, request: Request) -> str:
        # اگر JWT باشد، sub را بدون verify می‌خوانیم تا کلید کاربر محور شود
        auth = request.headers.get("authorization") or ""
        if auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1].strip()
            try:
                claims = jose_jwt.get_unverified_claims(token)
                sub = claims.get("sub")
                if sub:
                    return f"user:{sub}"
            except Exception:
                pass
        try:
            ip = request.client.host
        except Exception:
            ip = "unknown"
        return f"ip:{ip}"

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        path = request.url.path
        if path in self.skip_paths or request.method == "OPTIONS":
            return await call_next(request)

        key = self._key(request)
        now = time.monotonic()
        with self.lock:
            tokens = self.tokens.get(key, float(self.capacity))
            last = self.updated.get(key, now)
            # refill
            tokens = min(self.capacity, tokens + self.rate * (now - last))
            if tokens < 1.0:
                retry_after = max(1, int((1.0 - tokens) / max(self.rate, 0.001)))
                return JSONResponse(
                    {"detail": "Rate limit exceeded"},
                    status_code=429,
                    headers={
                        "Retry-After": str(retry_after),
                        "X-RateLimit-Limit": str(self.capacity),
                        "X-RateLimit-Remaining": str(int(tokens)),
                        "X-RateLimit-Key": key,
                    },
                )
            tokens -= 1.0
            self.tokens[key] = tokens
            self.updated[key] = now

        response = await call_next(request)
        try:
            response.headers["X-RateLimit-Limit"] = str(self.capacity)
            response.headers["X-RateLimit-Remaining"] = str(int(tokens))
        except Exception:
            pass
        return response
