import * as vscode from "vscode";
import { FdocCli } from "../cli";
import { DocumentItem } from "../tree";
import { listDocuments } from "../documents";
import { activeWorkspaceFolder, findRepoRoot, pickWorkspaceFolder } from "../workspace";
import { git, statusLines } from "../git";

/** Stage the document folder, prompt for a message, commit, and optionally push. */
export async function commitDocument(cli: FdocCli, item: DocumentItem | undefined) {
  const target = await resolveTarget(cli, item);
  if (!target) return;

  const lines = await statusLines(target.root, target.docName);
  if (lines.length === 0) {
    vscode.window.showInformationMessage(`${target.docName} has no changes to commit.`);
    return;
  }

  const summary = lines.slice(0, 8).join("\n") + (lines.length > 8 ? "\n…" : "");
  const message = await vscode.window.showInputBox({
    prompt: `Commit message for ${target.docName}`,
    placeHolder: "Describe what changed",
    ignoreFocusOut: true,
    value: `Update ${target.docName}`,
    validateInput: (v) => (v.trim().length > 0 ? undefined : "Message is required."),
  });
  if (!message) return;

  const push = await vscode.window.showQuickPick(
    [
      { label: "Commit", value: false },
      { label: "Commit and push", value: true },
    ],
    { placeHolder: `${lines.length} change(s) in ${target.docName}/` },
  );
  if (!push) return;

  const channel = vscode.window.createOutputChannel("fdoc git");
  channel.show(true);
  channel.appendLine(`Changes:\n${summary}\n`);

  const add = await git(target.root, ["add", "--", target.docName]);
  channel.append(add.stdout);
  channel.append(add.stderr);
  if (add.code !== 0) {
    vscode.window.showErrorMessage("git add failed.");
    return;
  }

  const commit = await git(target.root, ["commit", "-m", message]);
  channel.append(commit.stdout);
  channel.append(commit.stderr);
  if (commit.code !== 0) {
    vscode.window.showErrorMessage("git commit failed.");
    return;
  }

  if (push.value) {
    const pushResult = await git(target.root, ["push", "--follow-tags"]);
    channel.append(pushResult.stdout);
    channel.append(pushResult.stderr);
    if (pushResult.code !== 0) {
      vscode.window.showErrorMessage("git push failed.");
      return;
    }
  }

  vscode.window.showInformationMessage(
    push.value ? `Committed and pushed ${target.docName}.` : `Committed ${target.docName}.`,
  );
}

async function resolveTarget(
  cli: FdocCli,
  item: DocumentItem | undefined,
): Promise<{ root: string; docName: string } | undefined> {
  if (item) return { root: item.repoRoot, docName: item.docName };
  const folder = activeWorkspaceFolder() ?? (await pickWorkspaceFolder());
  if (!folder) return undefined;
  const root = findRepoRoot(folder);
  if (!root) {
    vscode.window.showErrorMessage("Not in a Fiddlie documentation repository.");
    return undefined;
  }
  const docs = await listDocuments(cli, root);
  if (docs.length === 0) {
    vscode.window.showInformationMessage("No documents found.");
    return undefined;
  }
  const picked = await vscode.window.showQuickPick(docs, { placeHolder: "Select a document" });
  if (!picked) return undefined;
  return { root, docName: picked };
}
