import * as cp from "child_process";

export interface GitResult {
  code: number;
  stdout: string;
  stderr: string;
}

export function git(cwd: string, args: string[]): Promise<GitResult> {
  return new Promise((resolve, reject) => {
    const child = cp.spawn("git", args, { cwd, shell: false });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (d) => (stdout += d.toString()));
    child.stderr.on("data", (d) => (stderr += d.toString()));
    child.on("error", reject);
    child.on("close", (code) => resolve({ code: code ?? -1, stdout, stderr }));
  });
}

export async function hasUncommittedChanges(cwd: string, scope?: string): Promise<boolean> {
  const args = ["status", "--porcelain"];
  if (scope) args.push("--", scope);
  const r = await git(cwd, args);
  return r.code === 0 && r.stdout.trim().length > 0;
}

export async function statusLines(cwd: string, scope?: string): Promise<string[]> {
  const args = ["status", "--porcelain"];
  if (scope) args.push("--", scope);
  const r = await git(cwd, args);
  if (r.code !== 0) return [];
  return r.stdout.split("\n").filter((l) => l.length > 0);
}
