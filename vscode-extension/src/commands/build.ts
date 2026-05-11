import * as fs from "fs";
import * as path from "path";
import * as vscode from "vscode";
import { FdocCli } from "../cli";
import { DocumentItem } from "../tree";
import { resolveDocTarget } from "../target";

export async function buildDocument(
  cli: FdocCli,
  item: DocumentItem | vscode.Uri | undefined,
  opts: { clean?: boolean } = {},
): Promise<void> {
  const target = await resolveDocTarget(cli, item);
  if (!target) return;

  const args = ["build", target.docName];
  if (opts.clean) args.push("--clean");

  const result = await cli.run({
    cwd: target.root,
    args,
    title: opts.clean ? `Cleaning and building ${target.docName}` : `Building ${target.docName}`,
  });

  if (result.code === 0) {
    const open = await vscode.window.showInformationMessage(
      `Built ${target.docName}.`,
      "Open PDF",
    );
    if (open === "Open PDF") {
      await openPdfFor(target.root, target.docName);
    }
  } else {
    vscode.window.showErrorMessage(`Build failed (exit ${result.code}). See output for details.`);
  }
}

export async function openPdf(
  cli: FdocCli,
  item: DocumentItem | vscode.Uri | undefined,
): Promise<void> {
  const target = await resolveDocTarget(cli, item);
  if (!target) return;
  await openPdfFor(target.root, target.docName);
}

export async function openManifest(
  cli: FdocCli,
  item: DocumentItem | vscode.Uri | undefined,
): Promise<void> {
  const target = await resolveDocTarget(cli, item);
  if (!target) return;
  const manifest = path.join(target.root, target.docName, "manifest.yaml");
  if (!fs.existsSync(manifest)) {
    vscode.window.showWarningMessage(`${target.docName} has no manifest.yaml.`);
    return;
  }
  await vscode.window.showTextDocument(vscode.Uri.file(manifest));
}

export async function revealInOS(
  cli: FdocCli,
  item: DocumentItem | vscode.Uri | undefined,
): Promise<void> {
  const target = await resolveDocTarget(cli, item);
  if (!target) return;
  await vscode.commands.executeCommand(
    "revealFileInOS",
    vscode.Uri.file(path.join(target.root, target.docName)),
  );
}

async function openPdfFor(root: string, docName: string): Promise<void> {
  const docDir = path.join(root, docName);
  const candidates = fs
    .readdirSync(docDir)
    .filter((f) => f.endsWith(".pdf"))
    .map((f) => path.join(docDir, f));
  if (candidates.length === 0) {
    vscode.window.showWarningMessage(`No PDF found in ${docName}/. Build the document first.`);
    return;
  }
  await vscode.commands.executeCommand("latex-workshop.view", vscode.Uri.file(candidates[0]));
}
