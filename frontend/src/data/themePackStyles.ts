/**
 * 主题包风格列表：数据来自 themePacks.catalog.json（与后端 theme_pack_data 同源）。
 */
import type { StyleItem } from "@/types/aura";

import catalog from "./themePacks.catalog.json";
import { stylePrefixForExplorePack } from "./packCodes";

type CatalogRow = {
  nameEn: string;
  nameZh: string;
  subEn: string;
  subZh: string;
  prompt: string;
  proof: string;
  image?: string;
  thumb?: number;
};

function buildAll(): StyleItem[] {
  const thumbs = (catalog as { thumbs?: string[] }).thumbs ?? [];
  const packs = catalog.packs as Record<string, CatalogRow[]>;
  const rows: StyleItem[] = [];
  for (const [code, items] of Object.entries(packs)) {
    items.forEach((item, i) => {
      const idx = i + 1;
      const id = `tp_${code}_${String(idx).padStart(2, "0")}`;
      let url = (item.image ?? "").trim();
      if (!url && thumbs.length) {
        const ti = (((item.thumb as number) ?? 0) % thumbs.length + thumbs.length) % thumbs.length;
        url = thumbs[ti] ?? "";
      }
      if (!url) {
        // 与 styleVisuals 默认人像参数一致；catalog 正常生成时不应走到此分支
        url =
          "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&w=400&h=600&fit=crop&q=85";
      }
      rows.push({
        id,
        display_name: item.nameEn,
        subtitle: item.subEn,
        social_proof: item.proof,
        thumbnail_url: url,
      });
    });
  }
  return rows;
}

export const ALL_THEME_PACK_STYLE_ITEMS: StyleItem[] = buildAll();

export function stylesForExplorePackId(packId: string): StyleItem[] {
  const prefix = stylePrefixForExplorePack(packId);
  if (!prefix) return [];
  return ALL_THEME_PACK_STYLE_ITEMS.filter((s) => s.id.startsWith(`tp_${prefix}_`));
}
