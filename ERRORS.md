# ERRORS.md

## [2026-02-13 15:33] - Shutdown RuntimeError

- **Type**: Runtime
- **Severity**: Low
- **File**: `main.py`
- **Agent**: Tien Nghich
- **Root Cause**: Trying to send a Telegram message in `post_shutdown` hook when the `HTTPXRequest` is already closed/uninitialized.
- **Error Message**: `RuntimeError('This HTTPXRequest is not initialized!')`
- **Fix Applied**: Removed the `send_message` call from `post_shutdown`. Only logging is performed.
- **Status**: Fixed
