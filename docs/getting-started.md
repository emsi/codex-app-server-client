# Getting started

## Requirements

- Python `>=3.12`
- `uv`
- `codex app-server` available in `PATH` (for stdio mode)

## Install

```bash
uv sync
```

Canonical import path is `codex_app_server_sdk`.

Legacy alias: `codex_app_server_sdk` remains available for backward compatibility.

## Minimal stdio example

```python
import asyncio
from codex_app_server_sdk import CodexClient


async def main() -> None:
    async with CodexClient.connect_stdio() as client:
        result = await client.chat_once("Hello from Python")
        print(result.final_text)


asyncio.run(main())
```

## Minimal websocket example

```python
import asyncio
from codex_app_server_sdk import CodexClient


async def main() -> None:
    async with CodexClient.connect_websocket(
        url="ws://127.0.0.1:8765",
    ) as client:
        result = await client.chat_once("Hello over websocket")
        print(result.final_text)


asyncio.run(main())
```

## Explicit initialize handshake

[`chat_once(...)`](api/client.md#codex_app_server_sdk.client.CodexClient.chat_once) and [`chat(...)`](api/client.md#codex_app_server_sdk.client.CodexClient.chat) initialize automatically, but you can initialize
early to fail fast or inspect server metadata.

```python
init = await client.initialize()
print(init.protocol_version, init.server_info)
```
