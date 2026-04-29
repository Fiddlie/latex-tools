import * as fs from "fs";
import * as path from "path";
import * as vscode from "vscode";
import { FdocCli } from "./cli";
import { listDocuments } from "./documents";
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
  const manifest = path.join(root, doc, "manifest.yaml");
  if (!fs.existsSync(manifest)) return undefined;
  try {
    const content = fs.readFileSync(manifest, "utf8");
    const id = content.match(/^\s*id:\s*["']?([^"'\n]+)/m)?.[1]?.trim();
    const rev = content.match(/^\s*number:\s*["']?([^"'\n]+)/m)?.[1]?.trim();
    const draft = /draft:\s*true/i.test(content);
    const parts: string[] = [];
    if (id) parts.push(id);
    if (rev) parts.push(`rev ${rev}${draft ? " (draft)" : ""}`);
    return parts.join(" · ") || undefined;
  } catch {
    return undefined;
  }
}
