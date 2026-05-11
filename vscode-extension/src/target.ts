import * as vscode from "vscode";
import { FdocCli } from "./cli";
import { DocumentItem } from "./tree";
import { listDocuments } from "./documents";
import { docContext, ensureRepoRoot } from "./workspace";

export interface DocTarget {
  root: string;
  docName: string;
}

/**
 * Resolve a document target from a command argument (tree item or URI),
 * the active editor, or a quickpick over `fdoc list`. The single source
 * of truth for build/lock/commit-style commands.
 */
export async function resolveDocTarget(
  cli: FdocCli,
  arg: DocumentItem | vscode.Uri | undefined,
): Promise<DocTarget | undefined> {
  if (arg instanceof DocumentItem) {
    return { root: arg.repoRoot, docName: arg.docName };
  }
  if (arg instanceof vscode.Uri) {
    const ctx = docContext(arg);
    if (ctx) return ctx;
  }
  const editorCtx = docContext(vscode.window.activeTextEditor?.document.uri);
  if (editorCtx) return editorCtx;
  const root = await ensureRepoRoot();
  if (!root) return undefined;
  const docs = await listDocuments(cli, root);
  if (docs.length === 0) {
    vscode.window.showInformationMessage(
      "No documents found. Create one with fdoc: Create Document.",
    );
    return undefined;
  }
  const picked = await vscode.window.showQuickPick(docs, { placeHolder: "Select a document" });
  if (!picked) return undefined;
  return { root, docName: picked };
}
