import * as vscode from "vscode";
import { FdocCli } from "../cli";
import { activeWorkspaceFolder, findRepoRoot, pickWorkspaceFolder } from "../workspace";

const DOC_TYPES = [
  { label: "datasheet", description: "Product data sheet" },
  { label: "requirements", description: "Requirements specification" },
];

const TEMPLATES = [
  { label: "default", description: "Standard template" },
  { label: "empty", description: "Minimal scaffold" },
];

export async function createDocument(cli: FdocCli, refresh: () => void): Promise<void> {
  const folder = activeWorkspaceFolder() ?? (await pickWorkspaceFolder());
  if (!folder) return;
  const root = findRepoRoot(folder);
  if (!root) {
    vscode.window.showErrorMessage(
      "This workspace doesn't look like a Fiddlie docs repository (no latex-tools submodule found).",
    );
    return;
  }

  const doctype = await vscode.window.showQuickPick(DOC_TYPES, {
    placeHolder: "Document type",
  });
  if (!doctype) return;

  const title = await vscode.window.showInputBox({
    prompt: "Document title",
    placeHolder: "e.g. ACME Power Module PM-500",
  });
  if (title === undefined) return;

  const documentId = await vscode.window.showInputBox({
    prompt: "Document ID (leave blank to auto-assign)",
    placeHolder: "FD-DC-LTX-00001",
    validateInput: (v) =>
      !v || /^FD-DC-LTX-\d{5}$/.test(v.trim())
        ? undefined
        : "Format: FD-DC-LTX-##### (or leave blank).",
  });
  if (documentId === undefined) return;

  const template = await vscode.window.showQuickPick(TEMPLATES, {
    placeHolder: "Template variant",
  });
  if (!template) return;

  const useManifest = await vscode.window.showQuickPick(
    [
      { label: "Use manifest.yaml", value: true, description: "Recommended" },
      { label: "No manifest (inline metadata)", value: false },
    ],
    { placeHolder: "Manifest mode" },
  );
  if (!useManifest) return;

  const args = ["create", doctype.label, "--template", template.label];
  if (title.trim()) args.push("--title", title.trim());
  if (documentId.trim()) args.push("--id", documentId.trim());
  if (!useManifest.value) args.push("--no-manifest");
  // Avoid the CLI's interactive AppSheet project picker — let users opt in via .fdocrc.
  args.push("--no-sync");

  const result = await cli.run({
    cwd: root,
    args,
    title: `Creating ${doctype.label}`,
  });

  if (result.code === 0) {
    refresh();
    const folderName = parseCreatedFolder(result.stdout);
    if (folderName) {
      const tex = vscode.Uri.file(`${root}/${folderName}/${folderName}.tex`);
      try {
        await vscode.window.showTextDocument(tex);
      } catch {
        // tex file naming may differ; ignore
      }
    }
  } else {
    vscode.window.showErrorMessage(`fdoc create failed (exit ${result.code}).`);
  }
}

function parseCreatedFolder(stdout: string): string | undefined {
  const match = stdout.match(/Successfully created '([^']+)'/);
  return match ? match[1] : undefined;
}
