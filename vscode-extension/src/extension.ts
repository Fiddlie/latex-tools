import * as vscode from "vscode";
import { FdocCli } from "./cli";
import { DocumentsTreeProvider, DocumentItem } from "./tree";
import { initRepo } from "./commands/init";
import { createDocument } from "./commands/create";
import {
  buildDocument,
  openManifest,
  openPdf,
  revealInOS,
} from "./commands/build";
import { buildAll } from "./commands/buildAll";
import { revLock, revNext, syncRevision } from "./commands/revision";
import { pushRepo, updateSubmodule } from "./commands/push";
import { pullRepo } from "./commands/pull";
import { commitDocument } from "./commands/commit";
import { configureAppsheet } from "./commands/configureAppsheet";
import { docContext, findRepoRoot } from "./workspace";
import { FdocStatusBar } from "./statusBar";
import { FdocDecorationProvider } from "./decorations";
import { checkSubmoduleFreshness } from "./updateNudge";

export function activate(context: vscode.ExtensionContext) {
  const output = vscode.window.createOutputChannel("fdoc");
  const cli = new FdocCli(output);
  const tree = new DocumentsTreeProvider(cli);
  const statusBar = new FdocStatusBar();
  const decorations = new FdocDecorationProvider();

  const refreshTree = () => {
    tree.refresh();
    statusBar.refresh();
  };

  // Watch manifests so the tree, status bar, and decorations pick up changes.
  const watcher = vscode.workspace.createFileSystemWatcher("**/manifest.yaml");
  watcher.onDidChange(refreshTree);
  watcher.onDidCreate(refreshTree);
  watcher.onDidDelete(refreshTree);

  const setContextKeys = () => {
    const folders = vscode.workspace.workspaceFolders ?? [];
    const hasRepo = folders.some((f) => findRepoRoot(f));
    vscode.commands.executeCommand("setContext", "fdoc.hasRepo", hasRepo);
    const editor = vscode.window.activeTextEditor;
    const inDoc = editor ? !!docContext(editor.document.uri) : false;
    vscode.commands.executeCommand("setContext", "fdoc.editorInDoc", inDoc);
  };
  setContextKeys();

  context.subscriptions.push(
    output,
    watcher,
    statusBar,
    decorations,
    vscode.window.registerFileDecorationProvider(decorations),
    vscode.window.registerTreeDataProvider("fdoc.documents", tree),
    vscode.window.onDidChangeActiveTextEditor(setContextKeys),
    vscode.workspace.onDidChangeWorkspaceFolders(() => {
      setContextKeys();
      refreshTree();
    }),
    vscode.commands.registerCommand("fdoc.refresh", refreshTree),
    vscode.commands.registerCommand("fdoc.init", () => initRepo(cli)),
    vscode.commands.registerCommand("fdoc.create", () => createDocument(cli, refreshTree)),
    vscode.commands.registerCommand("fdoc.build", (item?: DocumentItem | vscode.Uri) =>
      buildDocument(cli, item),
    ),
    vscode.commands.registerCommand("fdoc.buildClean", (item?: DocumentItem | vscode.Uri) =>
      buildDocument(cli, item, { clean: true }),
    ),
    vscode.commands.registerCommand("fdoc.buildAll", () => buildAll(cli)),
    vscode.commands.registerCommand("fdoc.openPdf", (item?: DocumentItem | vscode.Uri) =>
      openPdf(cli, item),
    ),
    vscode.commands.registerCommand("fdoc.openManifest", (item?: DocumentItem | vscode.Uri) =>
      openManifest(cli, item),
    ),
    vscode.commands.registerCommand("fdoc.revealInOS", (item?: DocumentItem | vscode.Uri) =>
      revealInOS(cli, item),
    ),
    vscode.commands.registerCommand("fdoc.revLock", (item?: DocumentItem | vscode.Uri) =>
      revLock(cli, item, refreshTree),
    ),
    vscode.commands.registerCommand("fdoc.revNext", (item?: DocumentItem | vscode.Uri) =>
      revNext(cli, item, refreshTree),
    ),
    vscode.commands.registerCommand("fdoc.syncRevision", (item?: DocumentItem | vscode.Uri) =>
      syncRevision(cli, item),
    ),
    vscode.commands.registerCommand("fdoc.push", () => pushRepo(cli)),
    vscode.commands.registerCommand("fdoc.pull", () => pullRepo()),
    vscode.commands.registerCommand("fdoc.update", () => updateSubmodule(cli)),
    vscode.commands.registerCommand("fdoc.commitDocument", (item?: DocumentItem | vscode.Uri) =>
      commitDocument(cli, item),
    ),
    vscode.commands.registerCommand("fdoc.configureAppsheet", () => configureAppsheet()),
    vscode.commands.registerCommand("fdoc.openWalkthrough", () =>
      vscode.commands.executeCommand(
        "workbench.action.openWalkthrough",
        "fiddlie.fdoc#fdoc.setup",
        false,
      ),
    ),
  );

  if (vscode.workspace.getConfiguration("fdoc").get<boolean>("checkSubmoduleUpdates", true)) {
    // Fire and forget; failures are silent inside the helper.
    checkSubmoduleFreshness(context, cli);
  }
}

export function deactivate() {
  /* noop */
}
