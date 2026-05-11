import * as fs from "fs";
import * as path from "path";
import * as vscode from "vscode";
import { FdocCli } from "./cli";
import { listDocuments } from "./documents";
import { readManifest } from "./manifest";
import { findRepoRoot } from "./workspace";

export class DocumentItem extends vscode.TreeItem {
  constructor(
    public readonly docName: string,
    public readonly repoRoot: string,
    description?: string,
  ) {
    super(docName, vscode.TreeItemCollapsibleState.None);
    this.contextValue = "document";
    this.iconPath = new vscode.ThemeIcon("file-text");
    this.description = description;
    const docDir = path.join(repoRoot, docName);
    this.resourceUri = vscode.Uri.file(docDir);
    const tex = path.join(docDir, `${docName}.tex`);
    if (fs.existsSync(tex)) {
      this.command = {
        command: "vscode.open",
        title: "Open",
        arguments: [vscode.Uri.file(tex)],
      };
    }
    this.tooltip = docDir;
  }
}

export class DocumentsTreeProvider implements vscode.TreeDataProvider<DocumentItem> {
  private readonly _onDidChangeTreeData = new vscode.EventEmitter<DocumentItem | undefined>();
  readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  constructor(private readonly cli: FdocCli) {}

  refresh(): void {
    this._onDidChangeTreeData.fire(undefined);
  }

  getTreeItem(element: DocumentItem): vscode.TreeItem {
    return element;
  }

  async getChildren(): Promise<DocumentItem[]> {
    const folders = vscode.workspace.workspaceFolders ?? [];
    const items: DocumentItem[] = [];
    for (const folder of folders) {
      const root = findRepoRoot(folder);
      if (!root) continue;
      const docs = await listDocuments(this.cli, root);
      for (const doc of docs) {
        items.push(new DocumentItem(doc, root, describeDoc(root, doc)));
      }
    }
    return items;
  }
}

function describeDoc(root: string, doc: string): string | undefined {
  const summary = readManifest(path.join(root, doc));
  if (!summary) return undefined;
  const parts: string[] = [];
  if (summary.id) parts.push(summary.id);
  if (summary.revision) parts.push(`rev ${summary.revision}${summary.draft ? " (draft)" : ""}`);
  return parts.join(" · ") || undefined;
}
