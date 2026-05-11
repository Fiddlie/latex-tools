import * as fs from "fs";
import * as path from "path";
import * as vscode from "vscode";
import { FdocCli } from "./cli";
import { git } from "./git";
import { findRepoRoot } from "./workspace";

const NUDGE_DISMISSED_KEY = "fdoc.updateNudgeDismissedFor";
const CHECK_INTERVAL_MS = 1000 * 60 * 60 * 24; // once per day per repo

/**
 * On activation (and once per day per repo), fetch the latex-tools
 * submodule's remote and notify the user when their pinned commit is
 * behind. Lets the user run `fdoc update` from the toast.
 */
export async function checkSubmoduleFreshness(
  context: vscode.ExtensionContext,
  cli: FdocCli,
): Promise<void> {
  for (const folder of vscode.workspace.workspaceFolders ?? []) {
    const root = findRepoRoot(folder);
    if (!root) continue;
    const submodule = path.join(root, "latex-tools");
    if (!fs.existsSync(path.join(submodule, ".git")) && !fs.existsSync(path.join(submodule, "HEAD"))) {
      continue;
    }

    const stateKey = `${NUDGE_DISMISSED_KEY}:${root}`;
    const lastShown = context.globalState.get<number>(stateKey, 0);
    if (Date.now() - lastShown < CHECK_INTERVAL_MS) continue;

    // Fetch silently in the submodule so we have up-to-date remote refs.
    const fetched = await git(submodule, ["fetch", "--quiet"]);
    if (fetched.code !== 0) continue;

    const head = await git(submodule, ["rev-parse", "HEAD"]);
    const branch = await git(submodule, ["symbolic-ref", "--short", "refs/remotes/origin/HEAD"]);
    const remoteRef = branch.code === 0 ? branch.stdout.trim() : "origin/main";

    const remote = await git(submodule, ["rev-parse", remoteRef]);
    if (head.code !== 0 || remote.code !== 0) continue;
    if (head.stdout.trim() === remote.stdout.trim()) continue;

    const behind = await git(submodule, [
      "rev-list",
      "--count",
      `${head.stdout.trim()}..${remote.stdout.trim()}`,
    ]);
    const n = behind.code === 0 ? parseInt(behind.stdout.trim(), 10) : 0;
    if (!n) continue;

    const choice = await vscode.window.showInformationMessage(
      `latex-tools is ${n} commit${n === 1 ? "" : "s"} behind ${remoteRef}.`,
      "Update now",
      "Remind me later",
      "Don't ask for this repo",
    );

    if (choice === "Update now") {
      await cli.run({ cwd: root, args: ["update"], title: "Updating latex-tools" });
      context.globalState.update(stateKey, Date.now());
    } else if (choice === "Don't ask for this repo") {
      context.globalState.update(stateKey, Number.MAX_SAFE_INTEGER);
    } else {
      context.globalState.update(stateKey, Date.now());
    }
  }
}
