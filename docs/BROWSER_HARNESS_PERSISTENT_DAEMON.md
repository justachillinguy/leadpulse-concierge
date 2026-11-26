# Keeping Chrome Remote Debugging Authorized Without Repeated Prompts

Chrome 144+ (`chrome://inspect/#remote-debugging`) prompts **"Allow remote debugging?"** once per new CDP WebSocket connection to the default profile.

If the `browser-harness` daemon dies between commands (for example, when a command session exits and cleans up child processes), the next command starts a new daemon and triggers a new Chrome permission prompt.

## Recommended Fixes (Sanctioned)

### Option A — Persistent Daemon (Keep Logged-In Personal Profile)
Start the `browser-harness` daemon once as a persistent background daemon so all subsequent commands reuse the **same** CDP connection (Chrome asks at most once per Chrome restart):

```powershell
& "C:\Users\to-go\AppData\Roaming\uv\tools\browser-harness\Scripts\python.exe" -m browser_harness.daemon
```

Verify with:
```powershell
& "C:\Users\to-go\.local\bin\browser-harness.exe" --doctor
```
Both `[ok] daemon alive` and `[ok] active browser connections — 1` should be green.

### Option B — Dedicated Automation Chrome Profile (Zero Prompts Across Restarts)
Per `browser_harness/daemon.py`, launching a dedicated Chrome instance on a non-default profile avoids Chrome 144's per-connection Allow dialog:

```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9333 --user-data-dir="C:\Users\to-go\chrome-debug-profile"
```
Then set:
```powershell
$env:BU_CDP_URL = "http://127.0.0.1:9333"
```
