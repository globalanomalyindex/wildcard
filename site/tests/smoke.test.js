import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "..");

test("scaffold: fonts and tokens exist", () => {
  assert.ok(readFileSync(join(root, "fonts/Karrik-Regular.otf")).length > 1000);
  const css = readFileSync(join(root, "css/tokens.css"), "utf8");
  assert.match(css, /--periwinkle: #77a0e4/);
});
