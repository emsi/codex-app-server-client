#!/usr/bin/env python3
"""Showcase thread/model/config helper APIs over stdio or websocket transport."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import shlex
import sys
from typing import Any

from codex_app_server_client import (
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
        help="Optional websocket bearer token.",
    )
    parser.add_argument(
        "--cwd",
        default=None,
        help="Optional thread cwd.",
    )
    parser.add_argument(
        "--prompt",
        default="Give a 3-bullet summary of what this project does.",
        help="Prompt to send on the started thread.",
    )
    parser.add_argument(
        "--thread-name",
        default="api-showcase-thread",
        help="Name to assign to the started thread.",
    )
    parser.add_argument(
        "--list-limit",
        type=int,
        default=5,
        help="Max threads to fetch via thread/list.",
    )
    parser.add_argument(
        "--models-limit",
        type=int,
        default=5,
        help="Max models to fetch via model/list.",
    )
    parser.add_argument(
        "--archive",
        action="store_true",
        help="Archive the started thread at the end.",
    )
    parser.add_argument(
        "--show-data",
        action="store_true",
        help="Print raw JSON payloads from helper APIs.",
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


def _count_threads(payload: Any) -> int | None:
    if not isinstance(payload, dict):
        return None
    threads = payload.get("threads")
    if isinstance(threads, list):
        return len(threads)
    return None


def _count_models(payload: Any) -> int | None:
    if not isinstance(payload, dict):
        return None
    models = payload.get("models")
    if isinstance(models, list):
        return len(models)
    return None


async def run(args: argparse.Namespace) -> int:
    try:
        _log(args, f"transport={args.transport} connecting...")
        async with _build_client(args) as client:
            init = await client.initialize()
            _log(args, f"initialized protocol_version={init.protocol_version or 'unknown'}")

            thread_cfg = ThreadConfig(cwd=args.cwd) if args.cwd is not None else None
            _log(args, "starting thread...")
            thread = await client.start_thread(thread_cfg)
            _log(args, f"started thread_id={thread.thread_id}")

            _log(args, f"setting thread name={args.thread_name!r}...")
            await thread.set_name(args.thread_name)

            _log(args, "sending prompt...")
            result = await thread.chat_once(args.prompt)
            _log(
                args,
                f"turn complete thread_id={result.thread_id} turn_id={result.turn_id}",
            )
            print(f"[chat] thread_id={result.thread_id} turn_id={result.turn_id}")
            print(result.final_text)

            _log(args, "reading thread snapshot...")
            thread_snapshot = await thread.read(include_turns=False)
            _log(args, "listing threads...")
            threads_page = await client.list_threads(
                limit=args.list_limit,
                sort_key="updated_at",
                sort_direction="desc",
            )
            _log(args, "listing models...")
            models_page = await client.list_models(limit=args.models_limit)
            _log(args, "reading config...")
            config_snapshot = await client.read_config(include_layers=False)

            _log(
                args,
                f"listed_threads={_count_threads(threads_page)} "
                f"listed_models={_count_models(models_page)}",
            )

            if args.archive:
                _log(args, "archiving thread...")
                await thread.archive()
                _log(args, f"archived thread_id={thread.thread_id}")

            if args.show_data:
                print("[thread/read]")
                print(json.dumps(thread_snapshot, indent=2, sort_keys=True))
                print("[thread/list]")
                print(json.dumps(threads_page, indent=2, sort_keys=True))
                print("[model/list]")
                print(json.dumps(models_page, indent=2, sort_keys=True))
                print("[config/read]")
                print(json.dumps(config_snapshot, indent=2, sort_keys=True))
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
