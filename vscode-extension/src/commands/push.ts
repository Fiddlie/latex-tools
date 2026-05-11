import * as vscode from "vscode";
import { FdocCli } from "../cli";
import { ensureRepoRoot } from "../workspace";

export async function pushRepo(cli: FdocCli) {
  const root = await ensureRepoRoot();
  if (!root) return;

  const confirm = vscode.workspace.getConfiguration("fdoc").get<boolean>("confirmPush", true);
  if (confirm) {
    const ok = await vscode.window.showWarningMessage(
      "Push commits and revision tags to the remote?",
      { modal: true },
      "Push",
    );
    if (ok !== "Push") return;
  }

  await cli.run({
    cwd: root,
    args: ["push"],
    title: "Pushing to remote",
  });
}

export async function updateSubmodule(cli: FdocCli) {
  const root = await ensureRepoRoot();
  if (!root) return;

  const ref = await vscode.window.showInputBox({
    prompt: "Specific ref (branch, tag, or commit) — leave blank for default branch",
    placeHolder: "main, v1.2.0, ...",
  });
  if (ref === undefined) return;

  const args = ["update"];
  if (ref.trim()) args.push("--ref", ref.trim());

  await cli.run({ cwd: root, args, title: "Updating latex-tools" });
}
