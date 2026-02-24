#!/usr/bin/env python3
"""Resume an existing thread id and continue the conversation."""

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
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--transport",
        choices=["stdio", "websocket"],
        default="stdio",
        help="Transport mode.",
    )
    parser.add_argument("--thread-id", required=True, help="Existing thread id.")
    parser.add_argument(
        "--prompt",
        default="Continue from where we left off and summarize next steps.",
        help="Prompt to send on resumed thread.",
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
        "--cwd",
        default=None,
        help="Optional thread cwd override on resume.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Optional model override on resume.",
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

            _log(args, f"resuming thread_id={args.thread_id}...")
            thread = await client.resume_thread(
                args.thread_id,
                overrides=ThreadConfig(cwd=args.cwd, model=args.model),
            )
            _log(args, f"resumed thread_id={thread.thread_id}")

            _log(args, f"sending prompt={args.prompt!r}")
            result = await thread.chat_once(args.prompt)
            _log(
                args,
                f"turn complete thread_id={result.thread_id} turn_id={result.turn_id}",
            )
            print(f"[thread:{thread.thread_id}] {result.final_text}")
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
