import * as vscode from "vscode";
import { FdocCli } from "../cli";
import { DocumentItem } from "../tree";
import { git, statusLines } from "../git";
import { resolveDocTarget } from "../target";
import { gitOutput } from "../output";

/** Stage the document folder, prompt for a message, commit, and optionally push. */
export async function commitDocument(cli: FdocCli, item: DocumentItem | vscode.Uri | undefined) {
  const target = await resolveDocTarget(cli, item);
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

  const channel = gitOutput();
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
