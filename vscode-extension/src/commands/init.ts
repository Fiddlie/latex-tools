import * as path from "path";
import * as vscode from "vscode";
import { FdocCli } from "../cli";

export async function initRepo(cli: FdocCli): Promise<void> {
  const name = await vscode.window.showInputBox({
    prompt: "New documentation repository name",
    placeHolder: "my-product-docs",
    validateInput: (v) =>
      v && /^[A-Za-z0-9._-]+$/.test(v.trim())
        ? undefined
        : "Use letters, numbers, dots, dashes or underscores.",
  });
  if (!name) return;

  const parentUri = await vscode.window.showOpenDialog({
    canSelectFolders: true,
    canSelectFiles: false,
    canSelectMany: false,
    openLabel: "Choose parent directory",
    title: "Where should the new repo be created?",
  });
  if (!parentUri || parentUri.length === 0) return;
  const parent = parentUri[0].fsPath;

  const result = await cli.run({
    cwd: parent,
    args: ["init", name.trim()],
    title: `Initializing ${name}`,
  });

  if (result.code !== 0) {
    vscode.window.showErrorMessage(`fdoc init failed (exit ${result.code}). See output for details.`);
    return;
  }

  const newPath = path.join(parent, name.trim());
  const open = await vscode.window.showInformationMessage(
    `Created ${name}.`,
    "Open in current window",
    "Open in new window",
  );
  if (open) {
    await vscode.commands.executeCommand(
      "vscode.openFolder",
      vscode.Uri.file(newPath),
      open === "Open in new window",
    );
  }
}
