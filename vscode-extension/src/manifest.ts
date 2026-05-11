import * as fs from "fs";
import * as path from "path";

export interface ManifestSummary {
  id?: string;
  revision?: string;
  draft: boolean;
  title?: string;
}

/**
 * Lightweight manifest reader. We deliberately avoid pulling in a YAML
 * dependency — the manifest format is small and stable, so a regex pass
 * is enough for what we need (status bar text, tree descriptions).
 */
export function readManifest(docDir: string): ManifestSummary | undefined {
  const file = path.join(docDir, "manifest.yaml");
  if (!fs.existsSync(file)) return undefined;
  let text: string;
  try {
    text = fs.readFileSync(file, "utf8");
  } catch {
    return undefined;
  }
  return {
    id: extractScalar(text, "id"),
    revision: extractScalar(text, "current"),
    draft: /draft:\s*true/i.test(text),
    title: extractScalar(text, "title"),
  };
}

function extractScalar(text: string, key: string): string | undefined {
  const re = new RegExp(`^\\s*${key}:\\s*(?:"([^"]*)"|'([^']*)'|([^\\n]+))`, "m");
  const m = text.match(re);
  if (!m) return undefined;
  return (m[1] ?? m[2] ?? m[3] ?? "").trim() || undefined;
}
