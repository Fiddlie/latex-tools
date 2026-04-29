import * as vscode from "vscode";
import { FdocCli } from "./cli";
import { DocumentsTreeProvider, DocumentItem } from "./tree";
import { initRepo } from "./commands/init";
import { createDocument } from "./commands/create";
import { buildDocument, openPdf } from "./commands/build";
import { revLock, revNext, syncRevision } from "./commands/revision";
import { pushRepo, updateSubmodule } from "./commands/push";
import { commitDocument } from "./commands/commit";
import { findRepoRoot } from "./workspace";

export function activate(context: vscode.ExtensionContext) {
  const output = vscode.window.createOutputChannel("fdoc");
  const cli = new FdocCli(output);
  const tree = new DocumentsTreeProvider(cli);

  const refreshTree = () => tree.refresh();

  // Watch manifests so the tree picks up revision changes automatically.
  const watcher = vscode.workspace.createFileSystemWatcher("**/manifest.yaml");
  watcher.onDidChange(refreshTree);
  watcher.onDidCreate(refreshTree);
  watcher.onDidDelete(refreshTree);

  // Set context key so the welcome view shows when no repo is detected.
  const updateContext = () => {
    const has = (vscode.workspace.workspaceFolders ?? []).some((f) => findRepoRoot(f));
    vscode.commands.executeCommand("setContext", "fdoc.hasRepo", has);
  };
  updateContext();

  context.subscriptions.push(
    output,
    watcher,
    vscode.window.registerTreeDataProvider("fdoc.documents", tree),
    vscode.workspace.onDidChangeWorkspaceFolders(() => {
      updateContext();
      refreshTree();
    }),
    vscode.commands.registerCommand("fdoc.refresh", refreshTree),
    vscode.commands.registerCommand("fdoc.init", () => initRepo(cli)),
    vscode.commands.registerCommand("fdoc.create", () => createDocument(cli, refreshTree)),
    vscode.commands.registerCommand("fdoc.build", (item?: DocumentItem) =>
      buildDocument(cli, item),
    ),
    vscode.commands.registerCommand("fdoc.buildClean", (item?: DocumentItem) =>
      buildDocument(cli, item, { clean: true }),
    ),
    vscode.commands.registerCommand("fdoc.openPdf", (item?: DocumentItem) => openPdf(cli, item)),
    vscode.commands.registerCommand("fdoc.revLock", (item?: DocumentItem) =>
      revLock(cli, item, refreshTree),
    ),
    vscode.commands.registerCommand("fdoc.revNext", (item?: DocumentItem) =>
      revNext(cli, item, refreshTree),
    ),
    vscode.commands.registerCommand("fdoc.syncRevision", (item?: DocumentItem) =>
      syncRevision(cli, item),
    ),
    vscode.commands.registerCommand("fdoc.push", () => pushRepo(cli)),
    vscode.commands.registerCommand("fdoc.update", () => updateSubmodule(cli)),
    vscode.commands.registerCommand("fdoc.commitDocument", (item?: DocumentItem) =>
      commitDocument(cli, item),
    ),
  );
}

export function deactivate() {
  /* noop */
}
