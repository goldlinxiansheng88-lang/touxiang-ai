/** 与后端 GET /api/config 一致；后端不可用时用于本地展示 */
import type { Scene, StyleItem } from "@/types/aura";
import { styleThumbUrl } from "@/data/styleVisuals";

export const FALLBACK_SCENES: Scene[] = [
  { id: "AVATAR", label: "Avatar", icon: "✨", ratio: "1:1" },
  { id: "WALLPAPER", label: "Wallpaper", icon: "📱", ratio: "9:16" },
  { id: "FASHION", label: "Fashion", icon: "👔", ratio: "2:3" },
  { id: "POSTER", label: "Poster", icon: "🎨", ratio: "1:1" },
  { id: "TRAVEL", label: "Travel", icon: "✈️", ratio: "3:2" },
  { id: "DAILY", label: "Daily", icon: "☕", ratio: "4:5" },
];

export const FALLBACK_STYLES: StyleItem[] = [
  { id: "GHIBLI", display_name: "Soft & Dreamy", subtitle: "Ghibli-inspired", social_proof: "🔥 1.2M views", thumbnail_url: styleThumbUrl("GHIBLI") },
  { id: "PIXAR", display_name: "3D Pixar", subtitle: "Pixar CGI", social_proof: "⭐ 900k+", thumbnail_url: styleThumbUrl("PIXAR") },
  { id: "OIL_PAINTING", display_name: "Oil Portrait", subtitle: "Impressionist", social_proof: "🔥 800k views", thumbnail_url: styleThumbUrl("OIL_PAINTING") },
  { id: "CYBERPUNK", display_name: "Neon Edge", subtitle: "Cyberpunk", social_proof: "⭐ 500k+", thumbnail_url: styleThumbUrl("CYBERPUNK") },
  { id: "SHONEN_ANIME", display_name: "Action Anime", subtitle: "Shonen", social_proof: "🔥 600k views", thumbnail_url: styleThumbUrl("SHONEN_ANIME") },
  { id: "VAMP_ROMANTIC", display_name: "Dark Glamour", subtitle: "Romantic goth", social_proof: "⭐ 400k+", thumbnail_url: styleThumbUrl("VAMP_ROMANTIC") },
  { id: "GLITCHY_GLAM", display_name: "Glitch Glam", subtitle: "Avant-garde", social_proof: "🔥 350k views", thumbnail_url: styleThumbUrl("GLITCHY_GLAM") },
  { id: "POETCORE", display_name: "Poetcore", subtitle: "Dark academia", social_proof: "⭐ 300k+", thumbnail_url: styleThumbUrl("POETCORE") },
  { id: "EXTRA_CELESTIAL", display_name: "Cosmic", subtitle: "Holographic", social_proof: "🔥 450k views", thumbnail_url: styleThumbUrl("EXTRA_CELESTIAL") },
  { id: "GLAMORATTI", display_name: "Power Glam", subtitle: "80s power", social_proof: "⭐ 280k+", thumbnail_url: styleThumbUrl("GLAMORATTI") },
  { id: "COTTAGECORE", display_name: "Sunlit Meadow", subtitle: "Cottagecore", social_proof: "🔥 520k views", thumbnail_url: styleThumbUrl("COTTAGECORE") },
  { id: "SOFT_GRUNGE", display_name: "Soft Grunge", subtitle: "90s grunge", social_proof: "⭐ 310k+", thumbnail_url: styleThumbUrl("SOFT_GRUNGE") },
  { id: "WHIMSIGOTHIC", display_name: "Mystic Aura", subtitle: "Whimsigothic", social_proof: "🔥 290k views", thumbnail_url: styleThumbUrl("WHIMSIGOTHIC") },
  { id: "Y2K", display_name: "Y2K Pop", subtitle: "Chrome Y2K", social_proof: "⭐ 410k+", thumbnail_url: styleThumbUrl("Y2K") },
  { id: "VINTAGE_POLAROID", display_name: "Retro Polaroid", subtitle: "1970s warm", social_proof: "🔥 360k views", thumbnail_url: styleThumbUrl("VINTAGE_POLAROID") },
];

export const FALLBACK_PUBLIC_CONFIG = {
  scenes: FALLBACK_SCENES,
  styles: FALLBACK_STYLES,
};
