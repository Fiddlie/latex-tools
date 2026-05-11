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

/**
 * Locate the repo root the user is operating on, or show a friendly error.
 * Falls back through: active editor's folder → single workspace folder → quickpick.
 */
export async function ensureRepoRoot(): Promise<string | undefined> {
  const folder = activeWorkspaceFolder() ?? (await pickWorkspaceFolder());
  if (!folder) return undefined;
  const root = findRepoRoot(folder);
  if (!root) {
    vscode.window.showErrorMessage("Not in a Fiddlie documentation repository.");
    return undefined;
  }
  return root;
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

/**
 * Given a file URI inside a doc folder, return its repo root + document name.
 * Returns undefined if the URI isn't under a recognised doc folder.
 *
 * A doc folder is the direct child of the repo root that contains the file.
 */
export function docContext(uri: vscode.Uri | undefined): { root: string; docName: string } | undefined {
  if (!uri || uri.scheme !== "file") return undefined;
  const folder = vscode.workspace.getWorkspaceFolder(uri);
  if (!folder) return undefined;
  const root = findRepoRoot(folder);
  if (!root) return undefined;
  const rel = path.relative(root, uri.fsPath);
  if (rel.startsWith("..") || path.isAbsolute(rel)) return undefined;
  const segments = rel.split(path.sep);
  const docName = segments[0];
  if (!docName) return undefined;
  const docDir = path.join(root, docName);
  if (!fs.existsSync(docDir) || !fs.statSync(docDir).isDirectory()) return undefined;
  // A doc folder has either a manifest.yaml or a `<docName>.tex`.
  if (
    !fs.existsSync(path.join(docDir, "manifest.yaml")) &&
    !fs.existsSync(path.join(docDir, `${docName}.tex`))
  ) {
    return undefined;
  }
  return { root, docName };
}
