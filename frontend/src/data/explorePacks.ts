import type { Scene } from "@/types/aura";

/** 首页「探索包」标签：与顶栏场景重复时由 filter 剔除 */
export type ExplorePackItem = {
  id: string;
  emoji: string;
  /** vue-i18n 键，如 home.explorePacks.couples */
  labelKey: string;
  /** 配置里若已有该场景 id，则不展示（语义与顶栏分类重复） */
  dedupeBySceneId?: string;
  /** 与首页「场景」pill 同一套 id（如 AVATAR），用于主题包分区 */
  primaryScene: string;
};

/** 与参考图一致的两行共 14 项；顶栏已有场景通过 filter 去重（同 emoji / 绑定场景 id） */
export const EXPLORE_PACK_SEED: ExplorePackItem[] = [
  { id: "couples", emoji: "👩‍❤️‍👨", labelKey: "home.explorePacks.couples", primaryScene: "AVATAR" },
  { id: "cartoon", emoji: "🐱", labelKey: "home.explorePacks.cartoon", primaryScene: "AVATAR" },
  { id: "anime", emoji: "👧", labelKey: "home.explorePacks.anime", primaryScene: "AVATAR" },
  { id: "games", emoji: "🎮", labelKey: "home.explorePacks.games", primaryScene: "AVATAR" },
  { id: "dream", emoji: "🌟", labelKey: "home.explorePacks.dream", primaryScene: "WALLPAPER" },
  { id: "retro", emoji: "📺", labelKey: "home.explorePacks.retro", primaryScene: "FASHION" },
  { id: "sport", emoji: "🏃", labelKey: "home.explorePacks.sport", primaryScene: "FASHION" },
  { id: "artwork", emoji: "🖼️", labelKey: "home.explorePacks.artwork", primaryScene: "POSTER" },
  { id: "movies", emoji: "🍿", labelKey: "home.explorePacks.movies", primaryScene: "POSTER" },
  { id: "transport", emoji: "🏎️", labelKey: "home.explorePacks.transport", primaryScene: "TRAVEL" },
  { id: "stories", emoji: "🏰", labelKey: "home.explorePacks.stories", primaryScene: "TRAVEL" },
  { id: "love", emoji: "💖", labelKey: "home.explorePacks.love", primaryScene: "DAILY" },
  { id: "lifestyle", emoji: "🎉", labelKey: "home.explorePacks.lifestyle", primaryScene: "DAILY" },
  { id: "joy", emoji: "😆", labelKey: "home.explorePacks.joy", primaryScene: "DAILY" },
];

/** 按站点场景顺序输出非空分组；未知 primaryScene 排在已知顺序之后 */
export function packsGroupedByScene(
  packs: ExplorePackItem[],
  sceneOrder: string[],
): { sceneId: string; packs: ExplorePackItem[] }[] {
  const map = new Map<string, ExplorePackItem[]>();
  for (const p of packs) {
    const list = map.get(p.primaryScene) ?? [];
    list.push(p);
    map.set(p.primaryScene, list);
  }
  const out: { sceneId: string; packs: ExplorePackItem[] }[] = [];
  for (const id of sceneOrder) {
    const list = map.get(id);
    if (list?.length) out.push({ sceneId: id, packs: list });
  }
  for (const [id, list] of map) {
    if (!sceneOrder.includes(id) && list.length) out.push({ sceneId: id, packs: list });
  }
  return out;
}

export function filterExplorePacks(scenes: Scene[]): ExplorePackItem[] {
  const sceneIds = new Set(scenes.map((s) => s.id));
  const sceneIcons = new Set(scenes.map((s) => s.icon.trim()));
  return EXPLORE_PACK_SEED.filter((p) => {
    if (p.dedupeBySceneId && sceneIds.has(p.dedupeBySceneId)) return false;
    if (sceneIcons.has(p.emoji.trim())) return false;
    return true;
  });
}
