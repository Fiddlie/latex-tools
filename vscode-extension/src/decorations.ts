import * as path from "path";
import * as vscode from "vscode";
import { findRepoRoot } from "./workspace";
import { statusLines } from "./git";
import { readManifest } from "./manifest";

/**
 * Decorates document folders with badges:
 *   - "M" if any file under the folder is dirty (uncommitted)
 *   - "D" if the manifest's current revision is still a draft
 *
 * The provider is keyed off the doc folder's URI (which we set on
 * the tree items), so the badges appear in our fdoc Documents view.
 * Built-in Git decorations cover finer-grained file states inside the
 * folder already; this provider gives us a single roll-up at the doc
 * level even when the folder isn't expanded in the Explorer.
 */
export class FdocDecorationProvider
  implements vscode.FileDecorationProvider, vscode.Disposable
{
  private readonly _emitter = new vscode.EventEmitter<vscode.Uri | vscode.Uri[]>();
  readonly onDidChangeFileDecorations = this._emitter.event;

  /** docDir → set of dirty relative paths */
  private dirty = new Map<string, Set<string>>();
  private timer: NodeJS.Timeout | undefined;
  private readonly disposables: vscode.Disposable[] = [];

  constructor() {
    // Only files that can actually affect a doc's git status — typing
    // and tabbing in unsaved buffers doesn't change git's view, only
    // saves do, and only for tracked file types under the repo.
    const watcher = vscode.workspace.createFileSystemWatcher(
      "**/*.{tex,bib,cls,sty,lua,yaml,yml,pdf,png,jpg,jpeg,svg}",
    );
    const refresh = () => this.scheduleRefresh();
    this.disposables.push(
      watcher,
      watcher.onDidChange(refresh),
      watcher.onDidCreate(refresh),
      watcher.onDidDelete(refresh),
      vscode.workspace.onDidChangeWorkspaceFolders(refresh),
    );
    this.scheduleRefresh();
  }

  provideFileDecoration(uri: vscode.Uri): vscode.FileDecoration | undefined {
    if (uri.scheme !== "file") return undefined;
    const folder = vscode.workspace.getWorkspaceFolder(uri);
    if (!folder) return undefined;
    const root = findRepoRoot(folder);
    if (!root) return undefined;
    const docDir = uri.fsPath;
    if (path.dirname(docDir) !== root) return undefined;

    const badges: string[] = [];
    const tooltips: string[] = [];

    if (this.dirty.get(docDir)?.size) {
      badges.push("M");
      tooltips.push("Uncommitted changes");
    }

    const summary = readManifest(docDir);
    if (summary?.draft) {
      badges.push("D");
      tooltips.push("Draft revision");
    }

    if (badges.length === 0) return undefined;

    return {
      badge: badges.slice(0, 2).join(""),
      tooltip: tooltips.join(" · "),
      color: badges.includes("M")
        ? new vscode.ThemeColor("gitDecoration.modifiedResourceForeground")
        : new vscode.ThemeColor("gitDecoration.untrackedResourceForeground"),
      propagate: false,
    };
  }

  private scheduleRefresh(): void {
    if (this.timer) clearTimeout(this.timer);
    this.timer = setTimeout(() => this.refresh().catch(() => undefined), 300);
  }

  private async refresh(): Promise<void> {
    const next = new Map<string, Set<string>>();
    const changed: vscode.Uri[] = [];

    for (const folder of vscode.workspace.workspaceFolders ?? []) {
      const root = findRepoRoot(folder);
      if (!root) continue;
      const lines = await statusLines(root);
      for (const line of lines) {
        // porcelain v1: "XY path" — slice past first 3 chars
        const file = line.slice(3).trim();
        if (!file) continue;
        const seg = file.split("/")[0];
        const docDir = path.join(root, seg);
        let set = next.get(docDir);
        if (!set) {
          set = new Set();
          next.set(docDir, set);
        }
        set.add(file);
      }
    }

    // Compute the diff so we only fire decoration changes for affected URIs.
    const keys = new Set([...this.dirty.keys(), ...next.keys()]);
    for (const docDir of keys) {
      const prev = this.dirty.get(docDir);
      const cur = next.get(docDir);
      const same = prev?.size === cur?.size && [...(prev ?? [])].every((p) => cur?.has(p));
      if (!same) changed.push(vscode.Uri.file(docDir));
    }

    this.dirty = next;
    if (changed.length) this._emitter.fire(changed);
  }

  dispose(): void {
    if (this.timer) clearTimeout(this.timer);
    for (const d of this.disposables) d.dispose();
    this._emitter.dispose();
  }
}
