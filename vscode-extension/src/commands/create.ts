import * as vscode from "vscode";
import { FdocCli } from "../cli";
import { listProjects } from "../documents";
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

  const idChoice = await vscode.window.showQuickPick(
    [
      {
        label: "Auto-assign from AppSheet",
        value: "sync",
        description: "Pick a project; fdoc will reserve a Document No",
      },
      { label: "Enter ID manually", value: "manual", description: "FD-DC-LTX-#####" },
      { label: "Skip (use placeholder)", value: "skip", description: "FD-DC-LTX-?????" },
    ],
    { placeHolder: "How should the document ID be assigned?" },
  );
  if (!idChoice) return;

  let documentId: string | undefined;
  let projectName: string | undefined;

  if (idChoice.value === "manual") {
    const entered = await vscode.window.showInputBox({
      prompt: "Document ID",
      placeHolder: "FD-DC-LTX-00001",
      validateInput: (v) =>
        /^FD-DC-LTX-\d{5}$/.test(v.trim()) ? undefined : "Format: FD-DC-LTX-#####.",
    });
    if (entered === undefined) return;
    documentId = entered.trim();
  } else if (idChoice.value === "sync") {
    projectName = await pickProject(cli, root);
    if (!projectName) return;
  }

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
  if (documentId) args.push("--id", documentId);
  if (!useManifest.value) args.push("--no-manifest");

  if (projectName) {
    args.push("--sync", "--project", projectName);
  } else {
    args.push("--no-sync");
  }

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

async function pickProject(cli: FdocCli, root: string): Promise<string | undefined> {
  const projects = await vscode.window.withProgress(
    { location: vscode.ProgressLocation.Notification, title: "Loading AppSheet projects…" },
    () => listProjects(cli, root),
  );

  if (projects === null) {
    const choice = await vscode.window.showErrorMessage(
      "Couldn't load AppSheet projects. Check ~/.fdocrc has appsheet_api_key set.",
      "Open settings",
      "Type project name",
    );
    if (choice === "Open settings") {
      await vscode.commands.executeCommand("workbench.action.openSettings", "fdoc");
    } else if (choice === "Type project name") {
      return await vscode.window.showInputBox({
        prompt: "Project name (must match AppSheet exactly)",
        ignoreFocusOut: true,
      });
    }
    return undefined;
  }

  if (projects.length === 0) {
    vscode.window.showWarningMessage("AppSheet returned no active projects.");
    return undefined;
  }

  return await vscode.window.showQuickPick(projects, {
    placeHolder: "Select an AppSheet project",
    ignoreFocusOut: true,
  });
}

function parseCreatedFolder(stdout: string): string | undefined {
  const match = stdout.match(/Successfully created '([^']+)'/);
  return match ? match[1] : undefined;
}
