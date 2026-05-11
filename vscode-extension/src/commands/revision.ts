import * as vscode from "vscode";
import { FdocCli } from "../cli";
import { DocumentItem } from "../tree";
import { hasUncommittedChanges } from "../git";
import { resolveDocTarget } from "../target";

export async function revLock(
  cli: FdocCli,
  item: DocumentItem | vscode.Uri | undefined,
  refresh: () => void,
) {
  const target = await resolveDocTarget(cli, item);
  if (!target) return;

  if (await hasUncommittedChanges(target.root, target.docName)) {
    const proceed = await vscode.window.showWarningMessage(
      `${target.docName} has uncommitted changes. Lock anyway?`,
      "Cancel",
      "Lock anyway",
    );
    if (proceed !== "Lock anyway") return;
  }

  const defaultPush = vscode.workspace
    .getConfiguration("fdoc")
    .get<boolean>("defaultPushOnLock", false);

  const choices: vscode.QuickPickItem[] = [
    { label: "Lock", description: "Set draft=false, commit, tag" },
    { label: "Lock and push", description: "Lock + git push --follow-tags" },
    { label: "Lock, push, and advance", description: "Lock, push, then bump to next revision" },
  ];

  const action = await vscode.window.showQuickPick(choices, {
    placeHolder: defaultPush ? "Default: push enabled" : "Choose lock action",
  });
  if (!action) return;

  const args = ["rev", "lock", target.docName, "--no-sync"];
  if (action.label !== "Lock") args.push("--push");
  if (action.label === "Lock, push, and advance") args.push("--next");

  const result = await cli.run({
    cwd: target.root,
    args,
    title: `Locking ${target.docName}`,
  });
  if (result.code === 0) {
    refresh();
    vscode.window.showInformationMessage(`Locked ${target.docName}.`);
  }
}

export async function revNext(
  cli: FdocCli,
  item: DocumentItem | vscode.Uri | undefined,
  refresh: () => void,
) {
  const target = await resolveDocTarget(cli, item);
  if (!target) return;

  const result = await cli.run({
    cwd: target.root,
    args: ["rev", "next", target.docName],
    title: `Advancing revision of ${target.docName}`,
  });
  if (result.code === 0) {
    refresh();
    vscode.window.showInformationMessage(
      `Advanced revision for ${target.docName}. Review the manifest and commit when ready.`,
    );
  }
}

export async function syncRevision(cli: FdocCli, item: DocumentItem | vscode.Uri | undefined) {
  const target = await resolveDocTarget(cli, item);
  if (!target) return;
  const result = await cli.run({
    cwd: target.root,
    args: ["rev", "lock", target.docName, "--sync"],
    title: `Syncing ${target.docName} with AppSheet`,
  });
  if (result.code !== 0) {
    vscode.window.showErrorMessage(
      "AppSheet sync failed. Ensure ~/.fdocrc has appsheet_api_key set and the project is configured.",
    );
  }
}
