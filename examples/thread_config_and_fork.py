#!/usr/bin/env python3
"""Advanced thread configuration + fork example with stdio/websocket transport."""

from __future__ import annotations

import argparse
import asyncio
import os
import shlex
import sys

from codex_app_server_client import (
    CodexClient,
    CodexProtocolError,
    CodexTimeoutError,
    CodexTransportError,
    ThreadConfig,
    TurnOverrides,
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
        help="Websocket URL (used when --transport websocket).",
    )
    parser.add_argument(
        "--token",
        default=os.getenv("CODEX_APP_SERVER_TOKEN"),
        help="Optional websocket bearer token.",
    )
    parser.add_argument(
        "--cwd",
        default=".",
        help="Thread working directory.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Optional model id for the initial thread.",
    )
    parser.add_argument(
        "--base-instructions",
        default="Be concise and precise.",
        help="Thread base instructions.",
    )
    parser.add_argument(
        "--developer-instructions",
        default="Prefer actionable suggestions.",
        help="Thread developer instructions.",
    )
    parser.add_argument(
        "--prompt",
        default="Summarize what this repository appears to do.",
        help="Prompt for the original thread.",
    )
    parser.add_argument(
        "--fork-prompt",
        default="Now focus on test strategy and suggest 3 concrete test cases.",
        help="Prompt for the forked thread.",
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

    command = shlex.split(args.cmd)
    return CodexClient.connect_stdio(command=command)


def _log(args: argparse.Namespace, message: str) -> None:
    if not args.quiet:
        print(f"[meta] {message}")


async def run(args: argparse.Namespace) -> int:
    try:
        _log(args, f"transport={args.transport} connecting...")
        async with _build_client(args) as client:
            init = await client.initialize()
            _log(args, f"initialized protocol_version={init.protocol_version or 'unknown'}")

            _log(args, "starting thread...")
            thread = await client.start_thread(
                ThreadConfig(
                    cwd=args.cwd,
                    base_instructions=args.base_instructions,
                    developer_instructions=args.developer_instructions,
                    model=args.model,
                )
            )
            _log(args, f"started thread_id={thread.thread_id}")

            _log(args, "sending original prompt...")
            first = await thread.chat_once(args.prompt)
            _log(
                args,
                f"turn complete thread_id={first.thread_id} turn_id={first.turn_id}",
            )
            print(f"[thread:{thread.thread_id}] {first.final_text}")

            _log(args, "updating thread defaults...")
            await thread.update_defaults(
                ThreadConfig(
                    developer_instructions="Prioritize safety and edge cases.",
                )
            )

            _log(args, "forking thread...")
            forked = await thread.fork(
                overrides=ThreadConfig(
                    developer_instructions="Focus only on testing concerns.",
                )
            )
            _log(args, f"forked parent={thread.thread_id} forked={forked.thread_id}")

            _log(args, "streaming forked turn steps...")
            async for step in forked.chat(
                args.fork_prompt,
                turn_overrides=TurnOverrides(effort="low"),
            ):
                text = (step.text or "").strip()
                print(f"[{step.step_type}] {text}")
            _log(args, "forked turn completed")

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
    args = parse_args()
    raise SystemExit(asyncio.run(run(args)))


if __name__ == "__main__":
    main()
