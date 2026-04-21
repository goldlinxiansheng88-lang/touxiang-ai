import type { Scene } from "@/types/aura";

/** 首页「探索包」标签：与顶栏场景重复时由 filter 剔除 */
export type ExplorePackItem = {
  id: string;
  emoji: string;
  /** vue-i18n 键，如 home.explorePacks.couples */
  labelKey: string;
  /** 配置里若已有该场景 id，则不展示（语义与顶栏分类重复） */
  dedupeBySceneId?: string;
};

/** 与参考图一致的两行共 14 项；顶栏已有场景通过 filter 去重（同 emoji / 绑定场景 id） */
export const EXPLORE_PACK_SEED: ExplorePackItem[] = [
  { id: "couples", emoji: "👩‍❤️‍👨", labelKey: "home.explorePacks.couples" },
  { id: "cartoon", emoji: "🐱", labelKey: "home.explorePacks.cartoon" },
  { id: "anime", emoji: "👧", labelKey: "home.explorePacks.anime" },
  { id: "retro", emoji: "📺", labelKey: "home.explorePacks.retro" },
  { id: "artwork", emoji: "🖼️", labelKey: "home.explorePacks.artwork" },
  { id: "movies", emoji: "🍿", labelKey: "home.explorePacks.movies" },
  { id: "games", emoji: "🎮", labelKey: "home.explorePacks.games" },
  { id: "love", emoji: "💖", labelKey: "home.explorePacks.love" },
  { id: "lifestyle", emoji: "🎉", labelKey: "home.explorePacks.lifestyle" },
  { id: "transport", emoji: "🏎️", labelKey: "home.explorePacks.transport" },
  { id: "stories", emoji: "🏰", labelKey: "home.explorePacks.stories" },
  { id: "dream", emoji: "🌟", labelKey: "home.explorePacks.dream" },
  { id: "sport", emoji: "🏃", labelKey: "home.explorePacks.sport" },
  { id: "joy", emoji: "😆", labelKey: "home.explorePacks.joy" },
];

export function filterExplorePacks(scenes: Scene[]): ExplorePackItem[] {
  const sceneIds = new Set(scenes.map((s) => s.id));
  const sceneIcons = new Set(scenes.map((s) => s.icon.trim()));
  return EXPLORE_PACK_SEED.filter((p) => {
    if (p.dedupeBySceneId && sceneIds.has(p.dedupeBySceneId)) return false;
    if (sceneIcons.has(p.emoji.trim())) return false;
    return true;
  });
}
