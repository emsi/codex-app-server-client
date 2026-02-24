# Protocol mapping

High-level methods map to JSON-RPC methods as follows.

| High-level API | JSON-RPC method |
| --- | --- |
| [`initialize(...)`](api/client.md#codex_app_server_client.client.CodexClient.initialize) | `initialize` |
| [`start_thread(...)`](api/client.md#codex_app_server_client.client.CodexClient.start_thread) | `thread/start` |
| [`resume_thread(...)`](api/client.md#codex_app_server_client.client.CodexClient.resume_thread) | `thread/resume` |
| [`fork_thread(...)`](api/client.md#codex_app_server_client.client.CodexClient.fork_thread) | `thread/fork` |
| [`set_thread_name(...)`](api/client.md#codex_app_server_client.client.CodexClient.set_thread_name) | `thread/name/set` |
| [`archive_thread(...)`](api/client.md#codex_app_server_client.client.CodexClient.archive_thread) | `thread/archive` |
| [`unarchive_thread(...)`](api/client.md#codex_app_server_client.client.CodexClient.unarchive_thread) | `thread/unarchive` |
| [`compact_thread(...)`](api/client.md#codex_app_server_client.client.CodexClient.compact_thread) | `thread/compact/start` |
| [`rollback_thread(...)`](api/client.md#codex_app_server_client.client.CodexClient.rollback_thread) | `thread/rollback` |
| [`read_thread(...)`](api/client.md#codex_app_server_client.client.CodexClient.read_thread) | `thread/read` |
| [`list_threads(...)`](api/client.md#codex_app_server_client.client.CodexClient.list_threads) | `thread/list` |
| [`chat_once(...)`](api/client.md#codex_app_server_client.client.CodexClient.chat_once) / [`chat(...)`](api/client.md#codex_app_server_client.client.CodexClient.chat) turn start path | `turn/start` |
| [`interrupt_turn(...)`](api/client.md#codex_app_server_client.client.CodexClient.interrupt_turn) / [`cancel(...)`](api/client.md#codex_app_server_client.client.CodexClient.cancel) | `turn/interrupt` |
| [`steer_turn(...)`](api/client.md#codex_app_server_client.client.CodexClient.steer_turn) | `turn/steer` |
| [`start_review(...)`](api/client.md#codex_app_server_client.client.CodexClient.start_review) | `review/start` |
| [`list_models(...)`](api/client.md#codex_app_server_client.client.CodexClient.list_models) | `model/list` |
| [`exec_command(...)`](api/client.md#codex_app_server_client.client.CodexClient.exec_command) | `command/exec` |
| [`read_config(...)`](api/client.md#codex_app_server_client.client.CodexClient.read_config) | `config/read` |
| [`read_config_requirements(...)`](api/client.md#codex_app_server_client.client.CodexClient.read_config_requirements) | `configRequirements/read` |
| [`write_config_value(...)`](api/client.md#codex_app_server_client.client.CodexClient.write_config_value) | `config/value/write` |
| [`batch_write_config(...)`](api/client.md#codex_app_server_client.client.CodexClient.batch_write_config) | `config/batchWrite` |

## Notification handling

- step extraction is based on `item/completed`
- turn completion/failure uses supported aliases (`turn/completed`, `turn/failed`, etc.)
- transport-level receive loop routes responses vs notifications
