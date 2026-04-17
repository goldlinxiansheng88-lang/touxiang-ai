"""Public scenes + styles for GET /api/config (matches spec + appendix A)."""

SCENES = [
    {"id": "AVATAR", "label": "Avatar", "icon": "👤", "ratio": "1:1"},
    {"id": "WALLPAPER", "label": "Wallpaper", "icon": "📱", "ratio": "9:16"},
    {"id": "FASHION", "label": "Fashion", "icon": "👔", "ratio": "2:3"},
    {"id": "POSTER", "label": "Poster", "icon": "🎨", "ratio": "1:1"},
    {"id": "TRAVEL", "label": "Travel", "icon": "✈️", "ratio": "3:2"},
    {"id": "DAILY", "label": "Daily", "icon": "☕", "ratio": "4:5"},
]

# 与前端一致：Unsplash 可商用人像（竖版裁切），见前端 styleVisuals.ts 注释
_U = "https://images.unsplash.com"
_Q = "auto=format&w=400&h=600&fit=crop&q=85"
_THUMB = (
    f"{_U}/photo-1534528741775-53994a69daeb?{_Q}",
    f"{_U}/photo-1507003211169-0a1dd7228f2d?{_Q}",
    f"{_U}/photo-1506794778202-cad84cf45f1d?{_Q}",
    f"{_U}/photo-1533619043865-1c2e2f32ff2f?{_Q}",
    f"{_U}/photo-1627262899263-839fe9307c00?{_Q}",
    f"{_U}/photo-1531746020798-e6953c6e8e04?{_Q}",
    f"{_U}/photo-1529626455594-4ff0802cfb7e?{_Q}",
    f"{_U}/photo-1635098996118-1ae0b325024e?{_Q}",
    f"{_U}/photo-1494790108377-be9c29b29330?{_Q}",
    f"{_U}/photo-1524504388940-b1c1722653e1?{_Q}",
    f"{_U}/photo-1612821997318-bbe0e3b6813b?{_Q}",
    f"{_U}/photo-1515886657613-9f3515b0c78f?{_Q}",
    f"{_U}/photo-1487412720507-e7ab37603c6f?{_Q}",
    f"{_U}/photo-1617690032703-f991ed0e0ee6?{_Q}",
    f"{_U}/photo-1544723795-3fb6469f5b39?{_Q}",
)

STYLES = [
    {
        "id": "GHIBLI",
        "display_name": "Soft & Dreamy",
        "subtitle": "Ghibli-inspired",
        "social_proof": "🔥 1.2M views",
        "thumbnail_url": _THUMB[0],
    },
    {
        "id": "PIXAR",
        "display_name": "3D Pixar",
        "subtitle": "Pixar CGI",
        "social_proof": "⭐ 900k+",
        "thumbnail_url": _THUMB[1],
    },
    {
        "id": "OIL_PAINTING",
        "display_name": "Oil Portrait",
        "subtitle": "Impressionist",
        "social_proof": "🔥 800k views",
        "thumbnail_url": _THUMB[2],
    },
    {
        "id": "CYBERPUNK",
        "display_name": "Neon Edge",
        "subtitle": "Cyberpunk",
        "social_proof": "⭐ 500k+",
        "thumbnail_url": _THUMB[3],
    },
    {
        "id": "SHONEN_ANIME",
        "display_name": "Action Anime",
        "subtitle": "Shonen",
        "social_proof": "🔥 600k views",
        "thumbnail_url": _THUMB[4],
    },
    {
        "id": "VAMP_ROMANTIC",
        "display_name": "Dark Glamour",
        "subtitle": "Romantic goth",
        "social_proof": "⭐ 400k+",
        "thumbnail_url": _THUMB[5],
    },
    {
        "id": "GLITCHY_GLAM",
        "display_name": "Glitch Glam",
        "subtitle": "Avant-garde",
        "social_proof": "🔥 350k views",
        "thumbnail_url": _THUMB[6],
    },
    {
        "id": "POETCORE",
        "display_name": "Poetcore",
        "subtitle": "Dark academia",
        "social_proof": "⭐ 300k+",
        "thumbnail_url": _THUMB[7],
    },
    {
        "id": "EXTRA_CELESTIAL",
        "display_name": "Cosmic",
        "subtitle": "Holographic",
        "social_proof": "🔥 450k views",
        "thumbnail_url": _THUMB[8],
    },
    {
        "id": "GLAMORATTI",
        "display_name": "Power Glam",
        "subtitle": "80s power",
        "social_proof": "⭐ 280k+",
        "thumbnail_url": _THUMB[9],
    },
    {
        "id": "COTTAGECORE",
        "display_name": "Sunlit Meadow",
        "subtitle": "Cottagecore",
        "social_proof": "🔥 520k views",
        "thumbnail_url": _THUMB[10],
    },
    {
        "id": "SOFT_GRUNGE",
        "display_name": "Soft Grunge",
        "subtitle": "90s grunge",
        "social_proof": "⭐ 310k+",
        "thumbnail_url": _THUMB[11],
    },
    {
        "id": "WHIMSIGOTHIC",
        "display_name": "Mystic Aura",
        "subtitle": "Whimsigothic",
        "social_proof": "🔥 290k views",
        "thumbnail_url": _THUMB[12],
    },
    {
        "id": "Y2K",
        "display_name": "Y2K Pop",
        "subtitle": "Chrome Y2K",
        "social_proof": "⭐ 410k+",
        "thumbnail_url": _THUMB[13],
    },
    {
        "id": "VINTAGE_POLAROID",
        "display_name": "Retro Polaroid",
        "subtitle": "1970s warm",
        "social_proof": "🔥 360k views",
        "thumbnail_url": _THUMB[14],
    },
]

STYLE_PARAMS = {
    "GHIBLI": {
        "prompt": "Studio Ghibli style, hand-drawn animation, soft watercolor background, gentle lighting",
        "lora": "GhibliBackground:0.8",
        "color": "sat -10%, temp +200K",
    },
    "PIXAR": {
        "prompt": "Pixar style 3D character, big expressive eyes, smooth CGI skin",
        "lora": "PixarStyle:0.9",
        "color": "sat +15%",
    },
    "OIL_PAINTING": {
        "prompt": "oil painting style, impressionist brushstrokes, visible canvas texture",
        "lora": "OilPainting:0.85",
        "color": "contrast -5%",
    },
    "CYBERPUNK": {
        "prompt": "cyberpunk aesthetic, neon purple and cyan lighting, futuristic city",
        "lora": "CyberpunkNeon:0.9",
        "color": "hue +10°, sat +30%",
    },
    "SHONEN_ANIME": {
        "prompt": "shonen anime style, sharp lines, dramatic shading, vibrant colors",
        "lora": "ShonenStyle:0.8",
        "color": "contrast +20%",
    },
    "VAMP_ROMANTIC": {
        "prompt": "romantic goth aesthetic, smudged kohl smoky eye, candlelit boudoir",
        "lora": "DarkRomance:0.9",
        "color": "shadow +30%",
    },
    "GLITCHY_GLAM": {
        "prompt": "editorial avant-garde makeup, mismatched aesthetic, digital glitch",
        "lora": "GlitchCore:0.7",
        "color": "RGB split",
    },
    "POETCORE": {
        "prompt": "dark academia aesthetic, oversized turtleneck, muted earth tones",
        "lora": "DarkAcademia:0.85",
        "color": "sat -30%, temp -200K",
    },
    "EXTRA_CELESTIAL": {
        "prompt": "holographic sheen, opalescent eyeshadow, cosmic silhouette",
        "lora": "Holographic:0.8",
        "color": "rainbow highlight",
    },
    "GLAMORATTI": {
        "prompt": "80s power dressing, oversized shoulder pads, luxury hotel lobby",
        "lora": "80sGlamour:0.85",
        "color": "contrast +15%",
    },
    "COTTAGECORE": {
        "prompt": "cottagecore aesthetic, wildflower meadow, soft golden hour",
        "lora": "CottagecoreV2:0.8",
        "color": "temp +400K",
    },
    "SOFT_GRUNGE": {
        "prompt": "soft grunge aesthetic, faded band tee, film grain",
        "lora": "Grunge90s:0.85",
        "color": "sat -40%, vignette +30%",
    },
    "WHIMSIGOTHIC": {
        "prompt": "whimsigothic aesthetic, mystical witchy vibes, celestial motifs",
        "lora": "Whimsigothic:0.9",
        "color": "hue -15°",
    },
    "Y2K": {
        "prompt": "Y2K aesthetic, metallic silver, chrome reflections",
        "lora": "Y2KPop:0.8",
        "color": "VHS scanlines",
    },
    "VINTAGE_POLAROID": {
        "prompt": "vintage polaroid photo, faded colors, 1970s warm nostalgic tone",
        "lora": "PolaroidVibe:0.7",
        "color": "polaroid frame",
    },
}
