import * as cp from "child_process";
import * as vscode from "vscode";

export interface RunOptions {
  cwd: string;
  args: string[];
  title?: string;
  showOutput?: boolean;
  env?: NodeJS.ProcessEnv;
}

export interface RunResult {
  code: number;
  stdout: string;
  stderr: string;
}

export class FdocCli {
  constructor(private readonly output: vscode.OutputChannel) {}

  private cliPath(): string {
    return vscode.workspace.getConfiguration("fdoc").get<string>("cliPath", "fdoc");
  }

  /** Capture stdout/stderr without streaming. Used for `fdoc list` etc. */
  async capture(opts: RunOptions): Promise<RunResult> {
    return new Promise((resolve, reject) => {
      const child = cp.spawn(this.cliPath(), opts.args, {
        cwd: opts.cwd,
        env: { ...process.env, ...(opts.env ?? {}) },
        shell: false,
      });
      let stdout = "";
      let stderr = "";
      child.stdout.on("data", (d) => (stdout += d.toString()));
      child.stderr.on("data", (d) => (stderr += d.toString()));
      child.on("error", (err) => reject(err));
      child.on("close", (code) => resolve({ code: code ?? -1, stdout, stderr }));
    });
  }

  /**
   * Stream output to the channel and surface progress in the status bar.
   * Returns the exit code; non-zero throws after surfacing an error toast.
   */
  async run(opts: RunOptions): Promise<RunResult> {
    const title = opts.title ?? `fdoc ${opts.args.join(" ")}`;
    if (opts.showOutput !== false) {
      this.output.show(true);
    }
    this.output.appendLine(`\n$ ${this.cliPath()} ${opts.args.join(" ")}`);
    this.output.appendLine(`  (cwd: ${opts.cwd})`);

    return vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title,
        cancellable: true,
      },
      (_progress, token) =>
        new Promise<RunResult>((resolve, reject) => {
          const child = cp.spawn(this.cliPath(), opts.args, {
            cwd: opts.cwd,
            env: { ...process.env, ...(opts.env ?? {}) },
            shell: false,
          });
          let stdout = "";
          let stderr = "";

          token.onCancellationRequested(() => child.kill("SIGTERM"));

          child.stdout.on("data", (d) => {
            const s = d.toString();
            stdout += s;
            this.output.append(s);
          });
          child.stderr.on("data", (d) => {
            const s = d.toString();
            stderr += s;
            this.output.append(s);
          });
          child.on("error", (err) => {
            if ((err as NodeJS.ErrnoException).code === "ENOENT") {
              this.surfaceMissingCli();
            }
            reject(err);
          });
          child.on("close", (code) => {
            const result: RunResult = { code: code ?? -1, stdout, stderr };
            if (result.code !== 0) {
              this.output.appendLine(`\n[exit ${result.code}]`);
            }
            resolve(result);
          });
        }),
    );
  }

  private surfaceMissingCli() {
    const python = vscode.workspace.getConfiguration("fdoc").get<string>("python", "python3");
    const installCmd = `pipx install git+ssh://git@github.com/Fiddlie/latex-tools.git#subdirectory=cli`;
    vscode.window
      .showErrorMessage(
        `fdoc executable not found. Install it with pipx, or set the "fdoc.cliPath" setting.`,
        "Copy install command",
        "Open settings",
      )
      .then((choice) => {
        if (choice === "Copy install command") {
          vscode.env.clipboard.writeText(installCmd);
        } else if (choice === "Open settings") {
          vscode.commands.executeCommand("workbench.action.openSettings", "fdoc.cliPath");
        }
      });
    this.output.appendLine(
      `\nfdoc not found. Try: ${python} -m pipx install git+ssh://git@github.com/Fiddlie/latex-tools.git#subdirectory=cli`,
    );
  }
}
