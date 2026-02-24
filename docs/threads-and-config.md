# Threads and configuration

## Related API

- [`CodexClient`](api/client.md#codex_app_server_client.client.CodexClient)
- [`ThreadHandle`](api/client.md#codex_app_server_client.client.ThreadHandle)
- [`ThreadConfig`](api/models.md#codex_app_server_client.models.ThreadConfig)
- [`TurnOverrides`](api/models.md#codex_app_server_client.models.TurnOverrides)

## Scope boundaries

- [`CodexClient`](api/client.md#codex_app_server_client.client.CodexClient): connection/session scope
- [`ThreadHandle`](api/client.md#codex_app_server_client.client.ThreadHandle) + [`ThreadConfig`](api/models.md#codex_app_server_client.models.ThreadConfig): thread scope
- [`TurnOverrides`](api/models.md#codex_app_server_client.models.TurnOverrides): per-turn scope

## `UNSET` vs `None`

- `UNSET`: omit field from request payload
- `None`: send explicit JSON `null` (where allowed by protocol)

```python
from codex_app_server_client import ThreadConfig, UNSET

cfg = ThreadConfig(
    model=UNSET,
    developer_instructions=None,
)
```

## Thread lifecycle

High-level methods:

- [`start_thread(config=None)`](api/client.md#codex_app_server_client.client.CodexClient.start_thread)
- [`resume_thread(thread_id, overrides=None)`](api/client.md#codex_app_server_client.client.CodexClient.resume_thread)
- [`fork_thread(thread_id, overrides=None)`](api/client.md#codex_app_server_client.client.CodexClient.fork_thread)
- [`read_thread(thread_id, include_turns=True)`](api/client.md#codex_app_server_client.client.CodexClient.read_thread)
- [`list_threads(...)`](api/client.md#codex_app_server_client.client.CodexClient.list_threads)
- [`set_thread_name(...)`](api/client.md#codex_app_server_client.client.CodexClient.set_thread_name)
- [`archive_thread(...)`](api/client.md#codex_app_server_client.client.CodexClient.archive_thread) / [`unarchive_thread(...)`](api/client.md#codex_app_server_client.client.CodexClient.unarchive_thread)
- [`compact_thread(...)`](api/client.md#codex_app_server_client.client.CodexClient.compact_thread)
- [`rollback_thread(...)`](api/client.md#codex_app_server_client.client.CodexClient.rollback_thread)

[`ThreadHandle`](api/client.md#codex_app_server_client.client.ThreadHandle) wraps these operations for one thread id.

## Setting model/cwd/instructions

Thread-level defaults belong on thread methods (`thread/start`, `thread/resume`, `thread/fork`).
Per-turn changes belong in [`TurnOverrides`](api/models.md#codex_app_server_client.models.TurnOverrides).

For persistent thread behavior:

```python
thread = await client.start_thread(
    ThreadConfig(
        cwd=".",
        base_instructions="Be concise",
        developer_instructions="Focus on correctness",
        model="gpt-5.3-codex",
    )
)
```
