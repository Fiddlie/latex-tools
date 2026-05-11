import * as vscode from "vscode";

let gitChannel: vscode.OutputChannel | undefined;

/** Shared, lazily-created output channel for raw git invocations. */
export function gitOutput(): vscode.OutputChannel {
  if (!gitChannel) {
    gitChannel = vscode.window.createOutputChannel("fdoc git");
  }
  return gitChannel;
}

/** Dispose the shared channel (called from extension deactivate). */
export function disposeOutput(): void {
  gitChannel?.dispose();
  gitChannel = undefined;
}
