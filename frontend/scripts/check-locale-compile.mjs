/**
 * Fail CI if any vue-i18n message fails compilation (e.g. unescaped @ in "you@example.com").
 * Mirrors merged bundles in src/locales/index.ts (en / zh-CN / ja / ko / zh-TW).
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { createI18n } from "vue-i18n";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");

function deepMerge(base, patch) {
  const out = { ...base };
  for (const key of Object.keys(patch)) {
    const pv = patch[key];
    const bv = out[key];
    if (Array.isArray(pv)) {
      out[key] = pv;
      continue;
    }
    if (pv && typeof pv === "object" && bv && typeof bv === "object" && !Array.isArray(bv)) {
      out[key] = deepMerge(bv, pv);
    } else if (pv !== undefined) {
      out[key] = pv;
    }
  }
  return out;
}

function readJson(rel) {
  return JSON.parse(fs.readFileSync(path.join(root, rel), "utf8"));
}

function buildPackStyles(pick) {
  const catalog = readJson("src/data/themePacks.catalog.json");
  const packs = catalog.packs;
  const out = {};
  for (const [code, items] of Object.entries(packs)) {
    items.forEach((item, i) => {
      const sid = `tp_${code}_${String(i + 1).padStart(2, "0")}`;
      const name = pick === "zh" ? item.nameZh : item.nameEn;
      out[sid] = { name, proof: item.proof };
    });
  }
  return { packStyles: out };
}

function walkKeys(node, prefix, onLeaf) {
  if (typeof node === "string") {
    onLeaf(prefix);
    return;
  }
  if (!node || typeof node !== "object" || Array.isArray(node)) return;
  for (const [k, v] of Object.entries(node)) {
    const p = prefix ? `${prefix}.${k}` : k;
    walkKeys(v, p, onLeaf);
  }
}

const enBase = readJson("src/locales/en.base.json");
const zhCNBase = readJson("src/locales/zh-CN.base.json");
const zhCNAdmin = readJson("src/locales/zh-CN.admin.json");
const jaPartial = readJson("src/locales/ja.json");
const koPartial = readJson("src/locales/ko.json");
const zhTWPartial = readJson("src/locales/zh-TW.json");

const enJson = deepMerge(deepMerge(enBase, zhCNAdmin), buildPackStyles("en"));
const zhCN = deepMerge(deepMerge(zhCNBase, zhCNAdmin), buildPackStyles("zh"));
const ja = deepMerge(enJson, jaPartial);
const ko = deepMerge(enJson, koPartial);
const zhTW = deepMerge(deepMerge(enJson, buildPackStyles("zh")), zhTWPartial);

const bundles = { en: enJson, "zh-CN": zhCN, ja, ko, "zh-TW": zhTW };

let failed = false;
for (const [loc, bundle] of Object.entries(bundles)) {
  const i18n = createI18n({ legacy: false, locale: loc, messages: { [loc]: bundle } });
  const g = i18n.global;
  const buf = [];
  const origErr = console.error;
  const origWarn = console.warn;
  console.error = (...args) => {
    buf.push(args.join(" "));
  };
  console.warn = () => {};
  walkKeys(bundle, "", (keyPath) => {
    g.locale.value = loc;
    g.t(keyPath);
  });
  console.error = origErr;
  console.warn = origWarn;
  const bad = buf.filter((l) => l.includes("Invalid linked") || l.includes("Unexpected empty linked"));
  if (bad.length) {
    failed = true;
    console.error(`\n[${loc}] message compile problems (first ${Math.min(8, bad.length)} lines):`);
    bad.slice(0, 8).forEach((l) => console.error(l));
  }
}

if (failed) process.exit(1);
console.log("locale vue-i18n compile check: OK");
