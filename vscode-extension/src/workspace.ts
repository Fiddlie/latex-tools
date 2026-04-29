import * as fs from "fs";
import * as path from "path";
import * as vscode from "vscode";

/**
 * Find the documentation repo root for a workspace folder.
 * A repo root contains a `latex-tools/classes` subdirectory (submodule),
 * or is itself the latex-tools repo (has both `classes/` and `packages/`).
 */
export function findRepoRoot(folder: vscode.WorkspaceFolder | undefined): string | undefined {
  if (!folder) return undefined;
  const root = folder.uri.fsPath;
  if (
    fs.existsSync(path.join(root, "latex-tools", "classes")) ||
    (fs.existsSync(path.join(root, "classes")) && fs.existsSync(path.join(root, "packages")))
  ) {
    return root;
  }
  return undefined;
}

/** Return the active workspace folder, falling back to the first one. */
export function activeWorkspaceFolder(): vscode.WorkspaceFolder | undefined {
  const editor = vscode.window.activeTextEditor;
  if (editor) {
    const folder = vscode.workspace.getWorkspaceFolder(editor.document.uri);
    if (folder) return folder;
  }
  return vscode.workspace.workspaceFolders?.[0];
}

/** Quickpick a workspace folder when more than one is open. */
export async function pickWorkspaceFolder(): Promise<vscode.WorkspaceFolder | undefined> {
  const folders = vscode.workspace.workspaceFolders ?? [];
  if (folders.length === 0) {
    vscode.window.showErrorMessage("Open a folder first.");
    return undefined;
  }
  if (folders.length === 1) return folders[0];
  const picked = await vscode.window.showWorkspaceFolderPick({
    placeHolder: "Select the documentation repository",
  });
  return picked;
}
