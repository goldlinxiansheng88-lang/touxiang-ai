/** 探索包 id → 风格 id 前缀（与后端 theme_pack_data 一致） */
export const EXPLORE_PACK_TO_STYLE_PREFIX: Record<string, string> = {
  couples: "co",
  cartoon: "ca",
  anime: "an",
  retro: "re",
  artwork: "ar",
  movies: "mo",
  games: "ga",
  love: "lo",
  lifestyle: "li",
  transport: "tr",
  stories: "st",
  dream: "dr",
  sport: "sp",
  joy: "jo",
};

export function stylePrefixForExplorePack(packId: string): string | undefined {
  return EXPLORE_PACK_TO_STYLE_PREFIX[packId];
}
