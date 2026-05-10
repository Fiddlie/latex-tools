import { FdocCli } from "./cli";

/** Run `fdoc list` and return document folder names. */
export async function listDocuments(cli: FdocCli, root: string): Promise<string[]> {
  const r = await cli.capture({ cwd: root, args: ["list"] });
  if (r.code !== 0) return [];
  return r.stdout
    .split("\n")
    .map((l) => l.trim())
    .filter((l) => l.length > 0);
}

/** Run `fdoc projects list` and return project names. Returns null on error. */
export async function listProjects(cli: FdocCli, cwd: string): Promise<string[] | null> {
  const r = await cli.capture({ cwd, args: ["projects", "list"] });
  if (r.code !== 0) return null;
  return r.stdout
    .split("\n")
    .map((l) => l.trim())
    .filter((l) => l.length > 0);
}
