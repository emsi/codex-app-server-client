#!/usr/bin/env python3
"""Run two thread handles over one client connection."""

from __future__ import annotations

import argparse
import asyncio
import os
import shlex
import sys

from codex_app_server_sdk import (
    CodexClient,
    CodexProtocolError,
    CodexTimeoutError,
    CodexTransportError,
    ThreadConfig,
    ThreadHandle,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--transport",
        choices=["stdio", "websocket"],
        default="stdio",
        help="Transport mode.",
    )
    parser.add_argument(
        "--cmd",
        default="codex app-server",
        help="Stdio app-server command.",
    )
    parser.add_argument(
        "--url",
        default=os.getenv("CODEX_APP_SERVER_WS_URL", "ws://127.0.0.1:8765"),
        help="Websocket URL.",
    )
    parser.add_argument(
        "--token",
        default=os.getenv("CODEX_APP_SERVER_TOKEN"),
        help="Optional websocket token.",
    )
    parser.add_argument(
        "--prompt-a",
        default="Analyze likely architecture in 3 bullets.",
        help="Prompt for thread A.",
    )
    parser.add_argument(
        "--prompt-b",
        default="Suggest a minimal test plan in 3 bullets.",
        help="Prompt for thread B.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress lifecycle progress logs.",
    )
    return parser.parse_args()


def _build_client(args: argparse.Namespace) -> CodexClient:
    if args.transport == "websocket":
        return CodexClient.connect_websocket(url=args.url, token=args.token)
    return CodexClient.connect_stdio(command=shlex.split(args.cmd))


def _log(args: argparse.Namespace, message: str) -> None:
    if not args.quiet:
        print(f"[meta] {message}")


async def run(args: argparse.Namespace) -> int:
    try:
        _log(args, f"transport={args.transport} connecting...")
        async with _build_client(args) as client:
            init = await client.initialize()
            _log(args, f"initialized protocol_version={init.protocol_version or 'unknown'}")

            _log(args, "starting thread A...")
            thread_a = await client.start_thread(
                ThreadConfig(
                    developer_instructions="Focus on architecture.",
                )
            )
            _log(args, f"started thread A id={thread_a.thread_id}")

            _log(args, "starting thread B...")
            thread_b = await client.start_thread(
                ThreadConfig(
                    developer_instructions="Focus on tests.",
                )
            )
            _log(args, f"started thread B id={thread_b.thread_id}")

            async def _run_one(name: str, handle: ThreadHandle, prompt: str) -> None:
                thread_id = handle.thread_id
                _log(args, f"[{name}] using thread_id={thread_id}...")
                _log(args, f"[{name}] sending prompt={prompt!r}")
                result = await handle.chat_once(prompt)
                _log(
                    args,
                    f"[{name}] turn complete thread_id={result.thread_id} turn_id={result.turn_id}",
                )
                print(f"[{name}:{result.thread_id}] {result.final_text}")

            await asyncio.gather(
                _run_one("A", thread_a, args.prompt_a),
                _run_one("B", thread_b, args.prompt_b),
            )
            _log(args, "all concurrent thread turns completed")

        return 0
    except CodexTimeoutError as exc:
        print(f"[error] timeout: {exc}", file=sys.stderr)
        return 2
    except CodexProtocolError as exc:
        details = f" code={exc.code}" if exc.code is not None else ""
        print(f"[error] protocol:{details} {exc}", file=sys.stderr)
        return 3
    except CodexTransportError as exc:
        print(f"[error] transport: {exc}", file=sys.stderr)
        return 4


def main() -> None:
    raise SystemExit(asyncio.run(run(parse_args())))


if __name__ == "__main__":
    main()
