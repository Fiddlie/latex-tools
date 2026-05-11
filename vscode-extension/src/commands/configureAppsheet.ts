import * as fs from "fs";
import * as os from "os";
import * as path from "path";
import * as vscode from "vscode";

const RC_PATH = path.join(os.homedir(), ".fdocrc");

export async function configureAppsheet() {
  const existing = await readRc();
  const currentMasked = existing.appsheet_api_key
    ? `${existing.appsheet_api_key.slice(0, 4)}…${existing.appsheet_api_key.slice(-2)}`
    : "(none)";

  const apiKey = await vscode.window.showInputBox({
    prompt: `AppSheet API access key (current: ${currentMasked})`,
    placeHolder: "Paste from AppSheet > Settings > Integrations > IN: from cloud services",
    password: true,
    ignoreFocusOut: true,
    validateInput: (v) => (v.trim().length === 0 ? "API key is required." : undefined),
  });
  if (!apiKey) return;

  const appId = await vscode.window.showInputBox({
    prompt: "AppSheet app ID (leave blank to keep current / use default)",
    value: existing.appsheet_app_id ?? "",
    ignoreFocusOut: true,
  });
  if (appId === undefined) return;

  const next: Record<string, string> = { ...existing, appsheet_api_key: apiKey.trim() };
  if (appId.trim()) {
    next.appsheet_app_id = appId.trim();
  } else {
    delete next.appsheet_app_id;
  }

  await writeRc(next);
  vscode.window.showInformationMessage(
    `Saved AppSheet credentials to ~/.fdocrc.`,
    "Open ~/.fdocrc",
  ).then((c) => {
    if (c === "Open ~/.fdocrc") {
      vscode.commands.executeCommand("vscode.open", vscode.Uri.file(RC_PATH));
    }
  });
}

interface Rc {
  appsheet_api_key?: string;
  appsheet_app_id?: string;
  [key: string]: string | undefined;
}

async function readRc(): Promise<Rc> {
  if (!fs.existsSync(RC_PATH)) return {};
  const text = fs.readFileSync(RC_PATH, "utf8");
  const out: Rc = {};
  for (const line of text.split("\n")) {
    const match = line.match(/^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?:"([^"]*)"|'([^']*)'|([^\n]+?))\s*$/);
    if (match) {
      out[match[1]] = (match[2] ?? match[3] ?? match[4] ?? "").trim();
    }
  }
  return out;
}

async function writeRc(rc: Rc) {
  // Preserve unrelated keys by reading raw and rewriting only known ones.
  const lines: string[] = [];
  const seen = new Set<string>();
  if (fs.existsSync(RC_PATH)) {
    for (const line of fs.readFileSync(RC_PATH, "utf8").split("\n")) {
      const match = line.match(/^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:/);
      if (match && match[1] in rc) {
        seen.add(match[1]);
        const value = rc[match[1]];
        if (value !== undefined) lines.push(`${match[1]}: "${value}"`);
      } else {
        lines.push(line);
      }
    }
  }
  for (const [key, value] of Object.entries(rc)) {
    if (!seen.has(key) && value !== undefined) {
      lines.push(`${key}: "${value}"`);
    }
  }
  while (lines.length && lines[lines.length - 1].trim() === "") lines.pop();
  fs.writeFileSync(RC_PATH, lines.join("\n") + "\n", { mode: 0o600 });
}
