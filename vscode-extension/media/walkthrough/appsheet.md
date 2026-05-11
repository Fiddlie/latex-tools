## Connect to AppSheet (optional)

Configure AppSheet so fdoc can auto-assign document IDs and sync revisions to the Fiddlie tracker.

1. In AppSheet, open **Settings → Integrations → IN: from cloud services** and copy your **Application Access Key**.
2. In VS Code, run **fdoc: Configure AppSheet Credentials** from the Command Palette and paste the key.

You only need to do this once per machine — the key is stored in `~/.fdocrc`.

If you skip this step, `fdoc create` will still work; it just uses a placeholder ID (`FD-DC-LTX-?????`) that you can edit later.
