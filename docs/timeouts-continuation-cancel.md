# Timeouts, continuation, cancel

## Related API

- [`CodexClient.chat_once(...)`](api/client.md#codex_app_server_client.client.CodexClient.chat_once)
- [`CodexClient.chat(...)`](api/client.md#codex_app_server_client.client.CodexClient.chat)
- [`CodexTurnInactiveError`](api/errors.md#codex_app_server_client.errors.CodexTurnInactiveError)
- [`ChatContinuation`](api/models.md#codex_app_server_client.models.ChatContinuation)
- [`CodexClient.cancel(...)`](api/client.md#codex_app_server_client.client.CodexClient.cancel)

## Request timeout vs inactivity timeout

- request timeout: JSON-RPC request/response envelope timeout
- inactivity timeout: per-turn "no new matching events" timeout

`turn_timeout` is intentionally not used.

## Continuation flow

When a turn goes inactive, APIs raise [`CodexTurnInactiveError`](api/errors.md#codex_app_server_client.errors.CodexTurnInactiveError) with a
[`continuation`](api/models.md#codex_app_server_client.models.ChatContinuation) token.

```python
continuation = None
while True:
    try:
        if continuation is None:
            result = await client.chat_once("Do a long task")
        else:
            result = await client.chat_once(continuation=continuation)
        break
    except CodexTurnInactiveError as exc:
        continuation = exc.continuation
```

Continuation is tied to in-memory session state in the same client instance.

## Continuation constraints

When `continuation=...` is used, do not pass:

- `text`
- `thread_id`
- `user`
- `metadata`
- `thread_config`
- `turn_overrides`

## Cancel semantics

Use `cancel(continuation)` to interrupt a running turn and drain unread data.

```python
cancelled = await client.cancel(exc.continuation)
print(cancelled.was_interrupted, len(cancelled.steps), len(cancelled.raw_events))
```

[`cancel(...)`](api/client.md#codex_app_server_client.client.CodexClient.cancel) cleans internal turn state so the thread can be reused safely.
