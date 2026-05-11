import * as vscode from "vscode";
import { findRepoRoot } from "./workspace";
import { git } from "./git";

const NUDGE_KEY = "fdoc.pullBehindDismissedFor";
const CHECK_INTERVAL_MS = 1000 * 60 * 60 * 24;

/**
 * On activation (and once per day per repo), fetch the origin for each
 * documentation repo and notify the user when their current branch is
 * behind its upstream.
 *
 * Triggers `fdoc.pull` from the toast. Authentication is delegated to
 * git's existing credential helpers; we don't ship our own.
 */
export async function checkPullBehind(context: vscode.ExtensionContext): Promise<void> {
  for (const folder of vscode.workspace.workspaceFolders ?? []) {
    const root = findRepoRoot(folder);
    if (!root) continue;

    const branch = await git(root, ["symbolic-ref", "--short", "HEAD"]);
    if (branch.code !== 0) continue;
    const branchName = branch.stdout.trim();

    const upstream = await git(root, [
      "rev-parse",
      "--abbrev-ref",
      `${branchName}@{upstream}`,
    ]);
    if (upstream.code !== 0) continue;
    const upstreamRef = upstream.stdout.trim();

    const stateKey = `${NUDGE_KEY}:${root}:${branchName}`;
    const lastShown = context.globalState.get<number>(stateKey, 0);
    if (Date.now() - lastShown < CHECK_INTERVAL_MS) continue;

    const fetched = await git(root, ["fetch", "--quiet"]);
    if (fetched.code !== 0) continue;

    const counts = await git(root, [
      "rev-list",
      "--left-right",
      "--count",
      `${branchName}...${upstreamRef}`,
    ]);
    if (counts.code !== 0) continue;

    const [ahead, behind] = counts.stdout.trim().split(/\s+/).map((n) => parseInt(n, 10));
    if (!Number.isFinite(behind) || behind === 0) continue;

    const aheadNote = ahead > 0 ? ` (you also have ${ahead} unpushed commit${ahead === 1 ? "" : "s"})` : "";
    const choice = await vscode.window.showInformationMessage(
      `${branchName} is ${behind} commit${behind === 1 ? "" : "s"} behind ${upstreamRef}${aheadNote}.`,
      "Pull now",
      "Remind me later",
      "Don't ask for this branch",
    );

    if (choice === "Pull now") {
      await vscode.commands.executeCommand("fdoc.pull");
      context.globalState.update(stateKey, Date.now());
    } else if (choice === "Don't ask for this branch") {
      context.globalState.update(stateKey, Number.MAX_SAFE_INTEGER);
    } else {
      context.globalState.update(stateKey, Date.now());
    }
  }
}
