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
