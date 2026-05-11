import * as vscode from "vscode";
import { activeWorkspaceFolder, findRepoRoot, pickWorkspaceFolder } from "../workspace";
import { git } from "../git";

export async function pullRepo() {
  const folder = activeWorkspaceFolder() ?? (await pickWorkspaceFolder());
  if (!folder) return;
  const root = findRepoRoot(folder);
  if (!root) {
    vscode.window.showErrorMessage("Not in a Fiddlie documentation repository.");
    return;
  }

  const channel = getChannel();
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
      // Sync submodule contents in case .gitmodules changed.
      const sub = await git(root, ["submodule", "update", "--init", "--recursive"]);
      channel.append(sub.stdout);
      channel.append(sub.stderr);
      vscode.window.showInformationMessage("Pulled latest changes.");
    },
  );
}

let cached: vscode.OutputChannel | undefined;
function getChannel(): vscode.OutputChannel {
  if (!cached) cached = vscode.window.createOutputChannel("fdoc git");
  return cached;
}
