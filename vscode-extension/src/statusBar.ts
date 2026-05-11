import * as path from "path";
import * as vscode from "vscode";
import { docContext } from "./workspace";
import { readManifest } from "./manifest";

/**
 * Status bar item that shows the current document, its revision, and a
 * "DRAFT" tag when the manifest's draft flag is true. Clicking the item
 * runs `fdoc.build`.
 */
export class FdocStatusBar implements vscode.Disposable {
  private readonly item: vscode.StatusBarItem;
  private readonly disposables: vscode.Disposable[] = [];

  constructor() {
    this.item = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    this.item.command = "fdoc.build";
    this.disposables.push(
      this.item,
      vscode.window.onDidChangeActiveTextEditor(() => this.update()),
      vscode.workspace.onDidSaveTextDocument((doc) => {
        if (doc.fileName.endsWith("manifest.yaml")) this.update();
      }),
    );
    this.update();
  }

  /** Public re-render hook (e.g. after `fdoc rev next` mutates a manifest). */
  refresh(): void {
    this.update();
  }

  private update(): void {
    const editor = vscode.window.activeTextEditor;
    const ctx = editor ? docContext(editor.document.uri) : undefined;
    if (!ctx) {
      this.item.hide();
      return;
    }
    const summary = readManifest(path.join(ctx.root, ctx.docName));
    const parts: string[] = [`$(book) ${ctx.docName}`];
    if (summary?.revision) parts.push(`rev ${summary.revision}`);
    if (summary?.draft) parts.push("DRAFT");
    this.item.text = parts.join(" · ");
    const tooltip = new vscode.MarkdownString();
    tooltip.appendMarkdown(`**${summary?.title ?? ctx.docName}**\n\n`);
    if (summary?.id) tooltip.appendMarkdown(`ID: \`${summary.id}\`\n\n`);
    if (summary?.revision) {
      tooltip.appendMarkdown(
        `Revision: \`${summary.revision}\`${summary.draft ? " (draft)" : ""}\n\n`,
      );
    }
    tooltip.appendMarkdown(`Click to build.`);
    this.item.tooltip = tooltip;
    this.item.show();
  }

  dispose(): void {
    for (const d of this.disposables) d.dispose();
  }
}
