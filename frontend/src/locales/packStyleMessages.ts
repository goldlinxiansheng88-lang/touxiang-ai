/**
 * 主题包风格 i18n：由 themePacks.catalog.json 生成 en / zh-CN 的 packStyles 扁平表。
 */
import catalog from "@/data/themePacks.catalog.json";

export type PackStyleEntry = { name: string; proof: string };

type CatalogRow = {
  nameEn: string;
  nameZh: string;
  proof: string;
};

function buildLocale(pick: "en" | "zh"): Record<string, PackStyleEntry> {
  const packs = catalog.packs as Record<string, CatalogRow[]>;
  const out: Record<string, PackStyleEntry> = {};
  for (const [code, items] of Object.entries(packs)) {
    items.forEach((item, i) => {
      const sid = `tp_${code}_${String(i + 1).padStart(2, "0")}`;
      const name = pick === "zh" ? item.nameZh : item.nameEn;
      out[sid] = { name, proof: item.proof };
    });
  }
  return out;
}

export const PACK_STYLE_I18N = {
  en: buildLocale("en"),
  "zh-CN": buildLocale("zh"),
} as const;
