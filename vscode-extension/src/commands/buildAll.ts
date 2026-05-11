import * as vscode from "vscode";
import { FdocCli } from "../cli";
import { listDocuments } from "../documents";
import { activeWorkspaceFolder, findRepoRoot, pickWorkspaceFolder } from "../workspace";

export async function buildAll(cli: FdocCli) {
  const folder = activeWorkspaceFolder() ?? (await pickWorkspaceFolder());
  if (!folder) return;
  const root = findRepoRoot(folder);
  if (!root) {
    vscode.window.showErrorMessage("Not in a Fiddlie documentation repository.");
    return;
  }

  const docs = await listDocuments(cli, root);
  if (docs.length === 0) {
    vscode.window.showInformationMessage("No documents found.");
    return;
  }

  const failed: string[] = [];
  for (const doc of docs) {
    const result = await cli.run({
      cwd: root,
      args: ["build", doc],
      title: `Building ${doc}`,
    });
    if (result.code !== 0) failed.push(doc);
  }

  if (failed.length === 0) {
    vscode.window.showInformationMessage(`Built all ${docs.length} document(s).`);
  } else {
    vscode.window.showWarningMessage(
      `Built ${docs.length - failed.length}/${docs.length}. Failed: ${failed.join(", ")}.`,
    );
  }
}
