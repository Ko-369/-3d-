import assert from "node:assert/strict";
import { access, readFile, readdir } from "node:fs/promises";
import test from "node:test";

const root = new URL("../", import.meta.url);
const expectedIds = ["motherboard", "cpu", "gpu", "memory", "storage", "power", "cooling", "network", "case"];

async function text(path) {
  return readFile(new URL(path, root), "utf8");
}

test("preserves the original interaction density while replacing the topic", async () => {
  const [data, app, viewer] = await Promise.all([
    text("app/lib/anatomy-data.ts"),
    text("app/components/AnatomyApp.tsx"),
    text("app/components/OrganViewer.tsx"),
  ]);

  for (const id of expectedIds) assert.match(data, new RegExp(`id: "${id}"`));
  assert.equal((data.match(/\{ id: "[^"]+", ta:/g) ?? []).length, 35);
  assert.equal((viewer.match(/\{ id: "(?:rotate|zoom|isolate|section|layers|compare|reset)"/g) ?? []).length, 7);
  assert.equal((app.match(/<article(?:\s|>)/g) ?? []).length, 6);
  assert.doesNotMatch(app, /Anatomy Atelier/);
  assert.match(app, /Computer Architecture Lab/);
});

test("ships nine 3D models and five learning visuals per hardware specimen", async () => {
  const models = (await readdir(new URL("public/models/", root))).filter((name) => name.endsWith(".glb"));
  assert.equal(models.length, 9);

  for (const id of expectedIds) {
    await access(new URL(`public/models/${id}.glb`, root));
    const visuals = (await readdir(new URL(`public/hardware/${id}/`, root))).filter((name) => name.endsWith(".webp"));
    assert.deepEqual(visuals.sort(), ["compare.webp", "location.webp", "microscopic.webp", "organ.webp", "thumb.webp"]);
  }
});

test("keeps the twelve-locale architecture", async () => {
  const organLocales = (await readdir(new URL("app/i18n/organs/", root))).filter((name) => name.endsWith(".ts"));
  const uiLocales = (await readdir(new URL("app/i18n/ui/", root))).filter((name) => name.endsWith(".ts"));
  assert.equal(organLocales.length, 12);
  assert.equal(uiLocales.length, 12);
});
