import http.client
import socket
from typing import Optional, Tuple
from .config import config


def request_processor(
    host: str,
    method: str,
    url: str,
    headers: dict,
    payload: Optional[str] = None,
    port: Optional[int] = None,
    timeout: int = config.default_timeout,
    response_headers: bool = False,
    force_https: bool = False,
) -> Tuple:
    """
    Synchronous HTTP/HTTPS request processor
    """

    use_https = (
        force_https
        or config.env_name in {"PROD", "TRIAL"}
        or (config.env_name == "STG")
    )

    ConnectionCls = (
        http.client.HTTPSConnection if use_https else http.client.HTTPConnection
    )

    try:
        connection = ConnectionCls(
            host,
            port,
            timeout=timeout,
        )

        connection.request(method, url, body=payload, headers=headers)
        response = connection.getresponse()

        body = response.read()
        resp_headers = response.getheaders()
        status = response.status

    except (socket.timeout, ConnectionError, OSError) as exc:
        print(f"❌ Request to {host}:{port}{url} failed: {exc}")
        raise RuntimeError(f"Request failed: {exc}") from exc

    finally:
        try:
            connection.close()
        except Exception:
            pass

    if response_headers:
        return body.decode("utf-8", errors="replace"), resp_headers, status

    return body.decode("utf-8", errors="replace"), status
