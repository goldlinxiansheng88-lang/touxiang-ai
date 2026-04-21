/** 渐变（图片加载失败时兜底）+ 风格参考：商用可用人像（Unsplash License） */

import { ALL_THEME_PACK_STYLE_ITEMS } from "@/data/themePackStyles";

const U = "https://images.unsplash.com";
const q = "auto=format&w=400&h=600&fit=crop&q=85";

/**
 * 每张均为「人物为主体」的竖版裁切，气质与附录 A 风格对应。
 * 许可：https://unsplash.com/license — 可免费用于含商业在内的用途（无需付费；建议保留摄影师信息于关于页）。
 * 若需 100% 自有肖像权：替换为自生成图或签约模特素材，并改成本地 / CDN URL。
 */
const THUMB_MAP: Record<string, string> = {
  /** GHIBLI：柔光、鲜花、清透肤色 — 梦幻人像 */
  GHIBLI: `${U}/photo-1534528741775-53994a69daeb?${q}`,
  /** PIXAR：高饱和棚拍、明快立体光 — 类 3D 渲染亲和力 */
  PIXAR: `${U}/photo-1507003211169-0a1dd7228f2d?${q}`,
  /** OIL_PAINTING：侧光、强明暗 — 油画式立体塑形 */
  OIL_PAINTING: `${U}/photo-1506794778202-cad84cf45f1d?${q}`,
  /** CYBERPUNK：霓虹侧光人像 — 夜景街头灯色 */
  CYBERPUNK: `${U}/photo-1533619043865-1c2e2f32ff2f?${q}`,
  /** SHONEN_ANIME：拳击姿态、紧绷对抗感 — 力量感人像 */
  SHONEN_ANIME: `${U}/photo-1627262899263-839fe9307c00?${q}`,
  /** VAMP_ROMANTIC：暗调皮草/晚宴 glamour 人像 */
  VAMP_ROMANTIC: `${U}/photo-1531746020798-e6953c6e8e04?${q}`,
  /** GLITCHY_GLAM：高饱和多色背景 — 前卫编辑/彩妆人像 */
  GLITCHY_GLAM: `${U}/photo-1529626455594-4ff0802cfb7e?${q}`,
  /** POETCORE：沙发阅读、安静神态 — Dark academia 人像 */
  POETCORE: `${U}/photo-1635098996118-1ae0b325024e?${q}`,
  /** EXTRA_CELESTIAL：纯色戏剧光人像 — 「星感」棚拍气质 */
  EXTRA_CELESTIAL: `${U}/photo-1494790108377-be9c29b29330?${q}`,
  /** GLAMORATTI：礼服、高光肤质 — 红毯/权力感人像 */
  GLAMORATTI: `${U}/photo-1524504388940-b1c1722653e1?${q}`,
  /** COTTAGECORE：油菜花田、草帽户外人像 — 田园金调 */
  COTTAGECORE: `${U}/photo-1612821997318-bbe0e3b6813b?${q}`,
  /** SOFT_GRUNGE：街拍、松弛神态 — 颗粒与褪色感人像 */
  SOFT_GRUNGE: `${U}/photo-1515886657613-9f3515b0c78f?${q}`,
  /** WHIMSIGOTHIC：创意妆面/神态 — 神秘气质人像 */
  WHIMSIGOTHIC: `${U}/photo-1487412720507-e7ab37603c6f?${q}`,
  /** Y2K：粉绿撞色裙装、墨镜 — 千禧 glossy 时装人像 */
  Y2K: `${U}/photo-1617690032703-f991ed0e0ee6?${q}`,
  /** VINTAGE_POLAROID：暖调、略褪色 — 复古胶片感人像 */
  VINTAGE_POLAROID: `${U}/photo-1544723795-3fb6469f5b39?${q}`,
};

const THEME_PACK_THUMB_BY_ID: Record<string, string> = Object.fromEntries(
  ALL_THEME_PACK_STYLE_ITEMS.map((s) => [s.id, s.thumbnail_url]),
);

export function styleThumbUrl(id: string): string {
  return THEME_PACK_THUMB_BY_ID[id] ?? THUMB_MAP[id] ?? THUMB_MAP.GHIBLI;
}

export const STYLE_GRADIENTS: Record<string, string> = {
  GHIBLI: "linear-gradient(155deg, #c5e3c8 0%, #eef6ef 45%, #9ec9a8 100%)",
  PIXAR: "linear-gradient(145deg, #ffe0b2 0%, #fff8e7 50%, #ffcc80 100%)",
  OIL_PAINTING: "linear-gradient(160deg, #d7ccc8 0%, #efebe9 50%, #a1887f 100%)",
  CYBERPUNK: "linear-gradient(135deg, #311b92 0%, #4a148c 40%, #00e5ff 100%)",
  SHONEN_ANIME: "linear-gradient(145deg, #ff7043 0%, #ffccbc 50%, #d32f2f 100%)",
  VAMP_ROMANTIC: "linear-gradient(160deg, #1a0a12 0%, #4a1942 50%, #880e4f 100%)",
  GLITCHY_GLAM: "linear-gradient(125deg, #ff00cc 0%, #00ffcc 50%, #330033 100%)",
  POETCORE: "linear-gradient(160deg, #3e2723 0%, #5d4037 45%, #8d6e63 100%)",
  EXTRA_CELESTIAL: "linear-gradient(145deg, #1a237e 0%, #5c6bc0 40%, #e1bee7 100%)",
  GLAMORATTI: "linear-gradient(155deg, #fce4ec 0%, #f8bbd9 40%, #ad1457 100%)",
  COTTAGECORE: "linear-gradient(160deg, #fff9c4 0%, #dce775 50%, #827717 100%)",
  SOFT_GRUNGE: "linear-gradient(145deg, #424242 0%, #757575 40%, #bdbdbd 100%)",
  WHIMSIGOTHIC: "linear-gradient(160deg, #311432 0%, #6a1b9a 50%, #ce93d8 100%)",
  Y2K: "linear-gradient(135deg, #eceff1 0%, #b0bec5 40%, #cfd8dc 100%)",
  VINTAGE_POLAROID: "linear-gradient(160deg, #efebe9 0%, #d7ccc8 50%, #bcaaa4 100%)",
};

/** 主题包风格无单独色板时用稳定哈希轮换 */
const TP_GRADIENT_POOL = [
  "linear-gradient(155deg, #fce4ec 0%, #f8bbd0 45%, #c2185b 100%)",
  "linear-gradient(150deg, #e3f2fd 0%, #90caf9 50%, #0d47a1 100%)",
  "linear-gradient(160deg, #fff8e1 0%, #ffe082 50%, #ff6f00 100%)",
  "linear-gradient(145deg, #ede7f6 0%, #b39ddb 50%, #4527a0 100%)",
  "linear-gradient(158deg, #e8f5e9 0%, #a5d6a7 50%, #1b5e20 100%)",
  "linear-gradient(150deg, #fce4ec 0%, #f48fb1 50%, #880e4f 100%)",
  "linear-gradient(160deg, #eceff1 0%, #cfd8dc 50%, #37474f 100%)",
  "linear-gradient(155deg, #fff3e0 0%, #ffcc80 50%, #e65100 100%)",
  "linear-gradient(160deg, #e0f7fa 0%, #4dd0e1 50%, #006064 100%)",
  "linear-gradient(150deg, #f3e5f5 0%, #ce93d8 50%, #4a148c 100%)",
  "linear-gradient(158deg, #efebe9 0%, #bcaaa4 50%, #3e2723 100%)",
  "linear-gradient(155deg, #e8eaf6 0%, #9fa8da 50%, #1a237e 100%)",
];

function hashStyleId(s: string): number {
  let h = 0;
  for (let i = 0; i < s.length; i += 1) h = (h * 31 + s.charCodeAt(i)) | 0;
  return Math.abs(h);
}

const FALLBACK = "linear-gradient(160deg, #f5f0eb 0%, #e8ddd4 100%)";

export function styleGradient(id: string): string {
  if (STYLE_GRADIENTS[id]) return STYLE_GRADIENTS[id];
  if (id.startsWith("tp_")) return TP_GRADIENT_POOL[hashStyleId(id) % TP_GRADIENT_POOL.length];
  return FALLBACK;
}
