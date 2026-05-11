import * as vscode from "vscode";
import { ensureRepoRoot } from "../workspace";
import { git } from "../git";
import { gitOutput } from "../output";

export async function pullRepo() {
  const root = await ensureRepoRoot();
  if (!root) return;

  const channel = gitOutput();
  channel.show(true);
  channel.appendLine(`\n$ git pull --recurse-submodules`);

  await vscode.window.withProgress(
    {
      location: vscode.ProgressLocation.Notification,
      title: "Pulling from remote",
      cancellable: false,
    },
    async () => {
      const pull = await git(root, ["pull", "--recurse-submodules"]);
      channel.append(pull.stdout);
      channel.append(pull.stderr);
      if (pull.code !== 0) {
        vscode.window.showErrorMessage("git pull failed. See output for details.");
        return;
      }
      const sub = await git(root, ["submodule", "update", "--init", "--recursive"]);
      channel.append(sub.stdout);
      channel.append(sub.stderr);
      vscode.window.showInformationMessage("Pulled latest changes.");
    },
  );
}
