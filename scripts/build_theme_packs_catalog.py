#!/usr/bin/env python3
"""生成 themePacks.catalog.json：各探索分类独立 15 组名称 / 副标题 / prompt；每条配图为 Unsplash 人像 URL，全站 210 条互不重复。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "frontend" / "src" / "data" / "themePacks.catalog.json"

PROOFS = ["🔥", "⭐", "✨", "💫", "🌟"]

sys.path.insert(0, str(ROOT / "scripts"))
from theme_pack_photo_slugs import slugs_by_pack  # noqa: E402

_PREVIEW_Q = "auto=format&w=400&h=600&fit=crop&q=85"


def portrait_preview_url(photo_slug: str) -> str:
    """Unsplash 竖版人像裁切，与 frontend styleVisuals 主站缩略图参数一致。"""
    return f"https://images.unsplash.com/photo-{photo_slug}?{_PREVIEW_Q}"


def pack_rows(*items: tuple[str, str, str, str, str]) -> list[dict]:
    out: list[dict] = []
    for i, it in enumerate(items):
        name_en, name_zh, sub_en, sub_zh, prompt = it
        out.append(
            {
                "nameEn": name_en,
                "nameZh": name_zh,
                "subEn": sub_en,
                "subZh": sub_zh,
                "prompt": prompt,
                "proof": PROOFS[i % len(PROOFS)],
            }
        )
    return out


# 每包 15 条：名称 / 副标题 / prompt 均贴合该分类，不与其他包共用模板词
PACKS_DATA: dict[str, list[dict]] = {
    "co": pack_rows(
        ("Silhouette Vows", "逆光誓约", "Sunset rim light", "日落轮廓光", "romantic couple silhouette at golden hour, emotional closeness, cinematic rim light"),
        ("Chinese Bridal Xiuhe", "中式秀禾", "Traditional red palette", "传统红金配色", "couple in Chinese xiùhé wedding attire, ornate embroidery, soft studio light"),
        ("Korean Light Gown", "韩式轻婚纱", "Airy tulle", "轻盈薄纱", "K-style pre-wedding couple, pastel tulle, clean beauty lighting"),
        ("Seaside Dusk", "海边暮色", "Ocean breeze", "海风与浪色", "couple on shoreline at blue hour, wind in hair, teal-orange grade"),
        ("Neon City Night", "都市霓虹夜", "Rain reflections", "雨后路面反光", "couple under city neon, shallow depth, urban romance"),
        ("Film Home Date", "胶片居家约会", "Grain & warmth", "颗粒暖调", "couple in sunlit apartment, 35mm film grain, candid intimacy"),
        ("Snow Lantern Walk", "雪地点灯漫步", "Cold sparkle", "冷色高光", "couple in winter street with lanterns, breath vapor, soft bokeh"),
        ("Café Window Gaze", "咖啡馆对视", "Steam & glass", "玻璃与蒸汽", "couple across café table, window reflections, cozy palette"),
        ("Forest Ceremony", "森系婚礼", "Dappled green", "斑驳绿意", "couple in pine forest clearing, dappled sunlight, organic tones"),
        ("Retro HK Glam", "复古港风双", "Teal & amber", "青橙港味", "couple in 90s Hong Kong film look, teal shadows, amber highlights"),
        ("Church Stained Light", "教堂彩窗光", "Volumetric shafts", "体积光束", "couple in chapel with stained glass color cast, solemn romance"),
        ("Campsite Firelight", "露营篝火夜", "Ember glow", "余烬暖脸", "couple by tent and campfire, low key warm fill, adventure mood"),
        ("Travel Street Snap", "旅行街拍", "Motion hints", "轻微动感", "couple walking busy market abroad, documentary framing, vivid colors"),
        ("Slow Morning Home", "居家晨间", "Sheer curtains", "纱帘柔光", "couple in bedhead morning light, linen sheets, tender calm"),
        ("Garden Pavilion", "园林画境", "Misty rockery", "假山薄雾", "couple in classical Chinese garden, mist, jade-green palette"),
    ),
    "ca": pack_rows(
        ("3D Chibi Pop", "3D Q版萌态", "Soft SSS", "次表面散射", "stylized 3D chibi portrait, soft subsurface scattering, candy colors"),
        ("Cel Anime Clean", "赛璐璐清透", "Hard edge light", "硬边光", "classic cel-shaded anime portrait, crisp line art, flat color blocks"),
        ("US Comic Bold", "美漫粗线张力", "Halftone dots", "网点纸感", "American comic ink portrait, bold outlines, halftone shading"),
        ("Rubber Hose Retro", "橡皮管复古", "Bouncy limbs", "夸张肢体", "1930s rubber hose cartoon style portrait, bendy exaggeration"),
        ("Watercolor Storybook", "水彩绘本", "Bleeding edges", "晕染边缘", "children's book watercolor portrait, soft pigment blooms"),
        ("Claymation Feel", "黏土定格感", "Thumbprint texture", "指纹肌理", "stop-motion clay look portrait, tactile surface, warm key"),
        ("Pixel RPG Sprite", "像素RPG立绘", "Limited palette", "限制调色板", "16-bit RPG portrait sprite upscale, crisp pixels, fantasy frame"),
        ("Sticker Flat", "贴纸扁平风", "Bold outline", "粗描边", "kawaii sticker aesthetic portrait, thick white outline, pastel flats"),
        ("Disney Fairytale", "童话公主光", "Prismatic flare", "棱镜光斑", "fairytale princess cartoon lighting, magical sparkles"),
        ("Pixar-ish 3D", "皮克斯式立体", "Big eyes", "大眼睛", "friendly 3D cartoon portrait, expressive eyes, soft global illumination"),
        ("Vaporwave Toon", "蒸汽波卡通", "Chrome & grid", "铬与网格", "vaporwave cartoon bust, chrome highlights, retro grid horizon"),
        ("Neon Outline Toon", "霓虹勾线卡通", "Bloom edges", "发光边", "neon outline cartoon portrait, dark background, electric hues"),
        ("Paper Cut Layers", "剪纸叠层", "Shadow depth", "层叠阴影", "layered paper cut-out style portrait, craft texture, pop colors"),
        ("Doodle Kawaii", "简笔萌系", "Loose lines", "松线稿", "hand-drawn doodle kawaii portrait, imperfect charm, bright fills"),
        ("Flash Web Retro", "FLASH网页复古", "Vector UI", "矢量界面", "early-2000s flash cartoon avatar vibe, vector UI accents"),
    ),
    "an": pack_rows(
        ("Shonen Split Light", "少年漫分叉光", "Hard shadow", "硬阴影", "shonen anime portrait, dramatic split lighting, intense gaze"),
        ("Makoto Sky Air", "新海诚空气感", "Lens flare", "镜头眩光", "anime portrait with vast sky, atmospheric perspective, subtle flare"),
        ("Otome Soft Bloom", "乙女柔光 bloom", "Rose haze", "玫瑰雾", "otome game style portrait, soft bloom, romantic eyelashes"),
        ("Mecha Pilot Rim", "机战驾驶舱边光", "HUD tint", "HUD 色偏", "mecha pilot anime portrait, cockpit rim light, cool sci-fi UI"),
        ("Kyoto Animation Skin", "京阿尼式肤色", "Pastel room", "淡彩室内", "slice-of-life anime portrait, delicate skin tones, warm room"),
        ("Dark Isekai", "暗黑异世界", "Purple mist", "紫雾", "dark fantasy isekai portrait, glowing sigils, moody contrast"),
        ("Healing Watercolor Anime", "治愈水彩上色", "Paper tooth", "纸纹", "gentle watercolor anime portrait, soft edges, pastoral calm"),
        ("Battle Shonen Spark", "热血高光星火", "Speed lines", "速度线", "battle anime portrait, motion lines, hot highlights"),
        ("Chibi Two-Head", "Q版二头身", "Oversize head", "大头比", "super-deformed chibi anime portrait, cute proportions, sparkle eyes"),
        ("Shojo Petal Shower", "少女漫花瓣雨", "Pastel petals", "粉瓣", "shojo manga portrait, falling petals, dreamy backlight"),
        ("Cybernetic Edge", "赛博义体边缘光", "Chrome skin lines", "金属肌理线", "cyberpunk anime portrait, chrome body lines, magenta rim"),
        ("Demon Slayer Texture", "炭笔鬼灭肌理", "Paper grain", "纸颗粒", "dark shonen ink texture portrait, hatching, ember sparks"),
        ("Retro OVA Grain", "复古OVA颗粒", "VHS noise", "VHS 噪点", "1980s OVA anime portrait, film grain, muted vintage grade"),
        ("Star Sigil Magic", "星阵魔法背景", "Constellation", "星座连线", "magical girl anime portrait, star circle background, glow"),
        ("Poolside School Arc", "泳池校季光影", "Caustics", "焦散水纹", "school anime portrait by pool, caustic light patterns, summer"),
    ),
    "re": pack_rows(
        ("80s Synth Portrait", "80年代合成器肖像", "Neon grid", "霓虹网格", "1980s retro portrait, synthwave grid, magenta-cyan glow"),
        ("VHS Tracking Mood", "VHS 跟踪线情绪", "Chromatic drift", "色偏漂移", "VHS artifact portrait, tracking errors, nostalgic blur"),
        ("Polaroid 1978", "1978 拍立得", "Warm fade", "暖褪色", "1970s polaroid portrait, cream whites, burnt orange shadows"),
        ("CRT Scanline Studio", "CRT 扫描线棚拍", "Phosphor green", "磷绿偏色", "CRT monitor aesthetic portrait, subtle scanlines, green cast"),
        ("Disco Ball Glitter", "迪斯科球碎光", "Silver spark", "银碎闪", "disco era portrait, glitter makeup, mirror ball specks"),
        ("Cassette Boombox", "卡带收音机街头", "Teal shadow", "青阴影", "80s street portrait with boombox, oversized jacket, teal grade"),
        ("Arcade Neon", "街机霓虹肖像", "Coin-op glow", "投币机光", "arcade neon portrait, cabinet reflections on face, saturated"),
        ("Drive-In Dusk", "汽车影院暮色", "Car chrome", "车身镀铬", "1950s drive-in retro portrait, chrome bumper reflections, dusk sky"),
        ("Newsprint Halftone", "报纸网点人像", "Mono press", "单色印刷", "vintage newspaper halftone portrait, rough ink dots"),
        ("Super 8 Home Movie", "超8家庭电影", "Warm jitter", "暖抖动感", "super 8 film portrait, handheld micro-jitter, sun flares"),
        ("Floppy Disk Office", "软盘办公室复古", "Beige PC", "米色微机", "90s office retro portrait, beige CRT, floppy disk props"),
        ("Roller Rink Pink", "轮滑场粉紫", "Floor gloss", "地板高光", "roller disco retro portrait, glossy floor reflections, pink fog"),
        ("Mall Food Court", "商场美食广场", "Fluorescent flat", "荧光灯平光", "90s mall portrait, food court lighting, nostalgic flatness"),
        ("Blockbuster Friday", "租片店周五夜", "Shelf bokeh", "货架虚化", "video rental store retro portrait, shelf bokeh, jacket collar"),
        ("Denim Double Denim", "丹宁双牛仔", "Indigo fade", "靛蓝褪色", "all-denim 90s portrait, double denim fashion, washed indigo"),
    ),
    "ar": pack_rows(
        ("Oil Impasto", "油画厚涂", "Palette knife", "刮刀肌理", "oil painting portrait, heavy impasto, visible brush ridges"),
        ("Renaissance Chiaroscuro", "文艺复兴明暗", "Deep shadow", "深暗部", "Renaissance portrait lighting, strong chiaroscuro, sfumato"),
        ("Watercolor Bleed", "水彩晕染", "Wet edge", "湿边", "fine art watercolor portrait, pigment bleeding, cold press texture"),
        ("Charcoal Academic", "素描学院派", "Smudge dust", "炭粉", "academic charcoal portrait, smudged shadows, atelier paper"),
        ("Marble Sculpture", "大理石雕塑感", "Cold spec", "冷高光", "sculptural marble bust look portrait, cold specular, museum"),
        ("Ukiyo-e Flat", "浮世绘平涂", "Flat pattern", "平面纹样", "ukiyo-e inspired portrait, flat color planes, woodblock texture"),
        ("Art Nouveau Curve", "新艺术曲线", "Gold filigree", "金卷草", "Art Nouveau portrait, sinuous lines, gold filigree frame hint"),
        ("Cubist Facets", "立体派切面", "Fractured plane", "破碎体面", "cubist inspired portrait, fractured planes, muted palette"),
        ("Impressionist Garden", "印象派花园光", "Broken color", "并置纯色", "Monet-like impressionist portrait in garden light, dabs"),
        ("Surreal Soft", "超现实柔焦", "Floating objects", "悬浮物", "surrealist portrait, soft focus, subtle impossible props"),
        ("Ink Wash Minimal", "水墨极简", "Negative space", "留白", "Chinese ink wash portrait, minimal strokes, generous negative space"),
        ("Pastel Chalk", "粉彩粉笔", "Paper grain", "纸颗粒", "soft pastel chalk portrait, dusty pigment, toothy paper"),
        ("Gouache Matte", "水粉哑光", "Flat shape", "平涂块面", "matte gouache illustration portrait, crisp shapes, poster feel"),
        ("Gold Leaf Icon", "金箔圣像感", "Halos", "光晕", "byzantine icon inspired portrait, gold leaf accents, sacred symmetry"),
        ("Digital Matte Painting", "数字绘景", "Epic vista", "远景史诗", "matte-painting style portrait with painted vista backdrop"),
    ),
    "mo": pack_rows(
        ("Noir Key Light", "黑色电影主光", "Venetian blind", "百叶窗影", "film noir portrait, venetian blind shadows, high contrast"),
        ("Epic Wide Anamorphic", "史诗变形宽银幕", "Lens flare", "变形眩光", "cinematic anamorphic portrait, letterbox mood, flares"),
        ("Teal Orange Blockbuster", "青橙大片调色", "Explosion rim", "爆炸轮廓光", "Hollywood blockbuster grade portrait, teal shadows"),
        ("Indie 16mm Grain", "独立16mm颗粒", "Natural skin", "自然肤色", "16mm indie film portrait, visible grain, honest skin"),
        ("Sci-Fi Bridge", "科幻舰桥蓝光", "Cool fill", "冷填充", "sci-fi movie portrait on starship bridge, cool ambient, rim"),
        ("Period Candlelit", "古装烛光", "Warm flicker", "暖闪烁", "period drama portrait, candlelight flicker, velvet costume"),
        ("Horror Cold Fill", "惊悚冷填充", "Under-eye hollow", "眼下凹陷", "horror film portrait, cold side fill, unsettling calm"),
        ("Rom-Com Golden Hour", "爱情喜剧黄金时刻", "Soft flare", "柔眩光", "romantic comedy portrait, golden hour park, soft flare"),
        ("Action Rain Night", "动作雨夜霓虹", "Wet skin", "湿皮肤高光", "action movie portrait in rain, neon reflections on wet skin"),
        ("Western Dust Haze", "西部尘雾", "Low sun", "低阳", "western film portrait, dust particles, rim lit hat brim"),
        ("Musical Spotlight", "音乐剧追光", "Stage smoke", "舞台烟", "musical film portrait, single spotlight, theatrical smoke"),
        ("Heist Vault Green", "劫案金库绿", "Fluorescent sick", "病态荧光", "heist movie portrait, sickly green vault fluorescents"),
        ("Space Opera Nebula", "太空歌剧星云", "Cosmic rim", "宇宙轮廓光", "space opera portrait, nebula backdrop, cosmic rim light"),
        ("Biopic Soft Window", "传记片窗光", "Quiet dignity", "沉静尊严", "biopic portrait, soft window light, understated wardrobe"),
        ("Documentary Available Light", "纪录自然光", "Truth palette", "真实肤色", "documentary portrait, available light, honest grade"),
    ),
    "ga": pack_rows(
        ("JRPG Hero Key", "JRPG 英雄主光", "Rim sword glint", "剑刃反光", "JRPG hero portrait, rim light, subtle armor glints"),
        ("FPS Tactical Helmet", "战术头盔面光", "HUD reflection", "HUD 反射", "tactical FPS portrait, helmet visor reflections, grit"),
        ("Open World Golden", "开放世界黄金时刻", "Vista haze", "远景薄雾", "open-world RPG portrait, golden hour vista, adventure"),
        ("Fighting Game Impact", "格斗游戏冲击", "Speed trail", "速度拖影", "fighting game portrait, impact freeze, motion trails"),
        ("Visual Novel Soft", "视觉小说柔焦", "Cherry petals", "樱花瓣", "visual novel CG portrait, soft bloom, cherry blossom"),
        ("Stealth Cold Moon", "潜行冷月", "Blue fill", "蓝填充", "stealth game portrait, moonlit rooftop, cold blue fill"),
        ("Racing Helmet Glare", "赛车头盔眩光", "Carbon fiber", "碳纤维", "racing game portrait, helmet visor streak glare, carbon suit"),
        ("Pixel Souls Gloom", "像素魂系阴郁", "Fog vignette", "雾暗角", "dark fantasy game portrait, heavy fog vignette, torch rim"),
        ("MOBA Splash Art", "MOBA 宣发立绘", "Rim explosion", "轮廓爆发光", "MOBA splash art portrait, explosive rim, saturated"),
        ("Cozy Farming Sim", "种田模拟治愈", "Pastel noon", "粉彩正午", "cozy farming sim portrait, pastel noon, straw hat"),
        ("Cyberpunk HUD Face", "赛博HUD映脸", "Cyan magenta", "青洋红", "cyberpunk game portrait, HUD reflections on cheeks"),
        ("Horror Game Flashlight", "恐怖手电底光", "Harsh upward", "硬底光", "survival horror portrait, flashlight underlight, dread"),
        ("RTS Commander Map", "RTS 指挥官地图光", "Table projection", "桌面投影", "RTS commander portrait, holographic map glow on face"),
        ("Gacha SSR Sparkle", "抽卡SSR闪", "Prismatic bokeh", "棱镜焦外", "gacha SSR reveal portrait, prismatic sparkles, luxury"),
        ("Sandbox Voxel", "沙盒体素风", "Chunky light", "块状光", "voxel sandbox game portrait, chunky voxel shading, playful"),
    ),
    "lo": pack_rows(
        ("First Date Shy", "初次约会腼腆", "Cafe blush", "咖啡馆脸红", "shy first-date portrait, warm café light, soft blush"),
        ("Long Distance Letter", "异地恋书信光", "Desk lamp", "台灯暖光", "romantic letter-writing portrait, desk lamp pool, longing"),
        ("Proposal Ring Bokeh", "求婚戒指焦外", "Spark highlights", "碎高光", "proposal moment portrait, ring bokeh, emotional eyes"),
        ("Anniversary Candle", "纪念日烛光", "Twin flames", "双烛芯", "anniversary dinner portrait, twin candles, intimate table"),
        ("Wedding Aisle Glow", "婚礼通道柔光", "Veil bloom", "头纱 bloom", "wedding aisle portrait, soft veil bloom, pastel flowers"),
        ("Rainy Umbrella Share", "雨天共伞", "Wet reflections", "湿路反光", "couple sharing umbrella portrait, rainy street reflections"),
        ("Slow Dance Sparkle", "慢舞碎光", "Disco ball micro", "微迪斯科球", "slow dance portrait, micro glitter lights on skin"),
        ("Morning Coffee Kiss", "晨间咖啡吻", "Steam curl", "蒸汽卷曲", "morning kitchen portrait, steam curl, gentle kiss pose"),
        ("Polaroid Love Note", "拍立得情书", "White frame", "白框", "polaroid-style love portrait, handwritten note prop, vintage"),
        ("Sunset Rooftop Hug", "天台日落拥抱", "City bokeh", "城市虚化", "rooftop hug portrait at sunset, city bokeh, wind"),
        ("Beach Heart Trace", "沙滩心形痕", "Footprints", "脚印", "beach romance portrait, traced heart in sand, turquoise sea"),
        ("Snowflake On Nose", "鼻尖雪花", "Cold pink cheeks", "冷粉颊", "winter playful portrait, snowflake on nose, laughter"),
        ("Train Window Goodbye", "车窗告别", "Glass streak", "玻璃水痕", "emotional train window goodbye portrait, rain streaks"),
        ("Balcony String Lights", "阳台串灯", "Warm LEDs", "暖LED", "balcony date portrait, string lights bokeh, cozy knit"),
        ("Forehead Touch Calm", "额间相依", "Soft wrap", "柔包裹光", "calm forehead-to-forehead portrait, soft wrap light, trust"),
    ),
    "li": pack_rows(
        ("Sunday Brunch Table", "周日早午餐桌", "Natural window", "自然窗光", "lifestyle brunch portrait, natural window, ceramics"),
        ("Yoga Mat Morning", "瑜伽垫晨光", "Pastel mat", "淡色垫", "wellness lifestyle portrait, morning yoga mat, soft sun"),
        ("Plant Parent Corner", "绿植角落地", "Leaf shadow", "叶影", "plant parent lifestyle portrait, monstera shadows, calm"),
        ("Coffee Shop Remote", "咖啡馆远程办公", "Laptop glow", "笔电微光", "digital nomad portrait, laptop glow on face, latte"),
        ("Farmer Market Tote", "农夫市集帆布袋", "Busy color", "缤纷色彩", "farmer's market lifestyle portrait, tote bag, produce color"),
        ("Minimalist Bedroom", "极简卧室", "White linen", "白亚麻", "minimal bedroom lifestyle portrait, white linen, airy"),
        ("City Bike Commute", "城市单车通勤", "Motion blur bg", "背景动感", "bike commute lifestyle portrait, motion blur street"),
        ("Skincare Mirror Routine", "护肤镜前日常", "Ring light soft", "环形灯柔光", "skincare routine portrait, ring light softness"),
        ("Bookstore Aisle", "书店过道", "Warm tungsten", "暖钨丝", "bookstore lifestyle portrait, warm tungsten stacks, glasses"),
        ("Kitchen Cook Steam", "厨房烹饪蒸汽", "Overhead practical", "顶光实用", "cooking lifestyle portrait, steam wisps, overhead"),
        ("Hiking Trail Midday", "徒步正午山径", "Hat brim shade", "帽檐阴影", "hiking lifestyle portrait, hat brim shade, trail dust"),
        ("Record Listening Night", "黑胶夜听", "Lamp pool", "台灯光区", "vinyl listening lifestyle portrait, warm lamp pool, cozy"),
        ("Beach Volleyball Tan", "沙滩排球日晒", "Hard sun", "硬阳光", "active beach lifestyle portrait, sporty tan, sand sparkle"),
        ("Pottery Studio Clay", "陶艺工作室", "Dust motes", "尘粒光束", "pottery studio lifestyle portrait, clay hands, dust motes"),
        ("Rainy Reading Nook", "雨天阅读角", "Blanket wrap", "毯子包裹", "cozy reading nook portrait, rainy window, blanket wrap"),
    ),
    "tr": pack_rows(
        ("Night Train Berth", "夜行列车铺位", "Blue cabin", "蓝车厢", "night train portrait, blue cabin light, travel solitude"),
        ("Vintage Convertible", "复古敞篷公路", "Wind hair", "风吹发", "road trip portrait in vintage convertible, golden highway"),
        ("Airport Gate Wait", "机场登机口等待", "Cool terminal", "冷航站楼", "airport gate portrait, cool terminal fluorescents, luggage"),
        ("Subway Motion Blur", "地铁动感模糊", "Neon streak", "霓虹拖影", "subway portrait with motion blur streaks, urban rush"),
        ("Ferry Deck Wind", "渡轮甲板大风", "Sea spray", "飞沫", "ferry deck portrait, strong wind, sea spray backlight"),
        ("Scooter City Rain", "踏板车雨城", "Wet visor", "湿面罩", "scooter commuter portrait in rain, wet visor reflections"),
        ("SUV Desert Dune", "越野沙丘", "Heat shimmer", "热浪", "SUV desert portrait, heat shimmer, burnt sienna dunes"),
        ("Bicycle Golden Alley", "单车金色巷弄", "Long shadow", "长影", "bicycle portrait in golden alley, long shadow, Europe vibe"),
        ("Harbor Sail Sunset", "港湾帆影日落", "Mast lines", "桅杆线", "sailboat harbor portrait at sunset, mast lines, warm haze"),
        ("Cable Car Mist", "缆车穿雾", "Soft fog", "柔雾", "cable car portrait through mist, soft fog, mountain silhouette"),
        ("Red Eye Flight", "红眼航班", "Dim cabin", "暗舱", "red-eye flight portrait, dim cabin, tired glam"),
        ("Motorcycle Leather Rim", "摩托皮衣轮廓光", "Chrome bounce", "镀铬反光", "motorcycle portrait, leather jacket, chrome bounce"),
        ("Electric Bus Teal", "电动巴士青绿", "Clean futurism", "干净未来感", "electric bus stop portrait, teal futurism, glass"),
        ("Helicopter Pad Wind", "停机坪大风", "Rotor blur", "旋翼模糊", "helipad portrait, rotor blur overhead, heroic rim"),
        ("Spaceport Gate", "太空港登机口", "Cool sci-fi", "冷科幻", "sci-fi spaceport portrait, cool gate lights, travel wonder"),
    ),
    "st": pack_rows(
        ("Medieval Castle Torch", "中世纪城堡火把", "Warm flicker", "暖闪烁", "medieval tale portrait, torch flicker, stone hall"),
        ("Wandering Knight Mist", "迷雾游侠", "Cape silhouette", "斗篷剪影", "knight errant portrait in mist, cape silhouette"),
        ("Fairy Tale Forest Path", "童话森林小径", "Fireflies", "萤火虫", "fairy tale portrait on forest path, fireflies, moon"),
        ("Ocean Tale Storm", "海洋传说风暴", "Salt spray", "盐雾", "sea story portrait, stormy horizon, salt spray on skin"),
        ("Space Odyssey Portal", "太空奥德赛门", "Star rim", "星光轮廓", "sci-fi odyssey portrait near glowing portal, star rim"),
        ("Detective Foggy Street", "侦探雾街", "Fedora shadow", "礼帽影", "noir detective story portrait, foggy street, fedora"),
        ("Samurai Dawn Duel", "武士黎明对决", "Cold steel glint", "冷钢闪", "samurai story portrait at dawn, steel glint, tension"),
        ("Lost City Jungle Vine", "失落城藤蔓", "Moss light", "苔藓光", "lost city explorer portrait, jungle vines, dappled moss"),
        ("Steampunk Gear Light", "蒸汽朋克齿轮光", "Brass bounce", "黄铜反光", "steampunk story portrait, gear shadows, brass bounce"),
        ("Post Apocalyptic Dust", "末世风沙", "Goggle tan", "护目镜晒痕", "post-apocalyptic survivor portrait, dust storm, goggles"),
        ("Victorian Séance", "维多利亚降灵会", "Candle smoke", "烛烟", "Victorian séance story portrait, candle smoke, mystery"),
        ("Pirate Deck Sunset", "海盗甲板日落", "Rope texture", "绳结肌理", "pirate tale portrait on deck at sunset, rope texture"),
        ("Cyber Oracle Neon", "赛博神谕霓虹", "Hologram face map", "全息面纹", "cyber oracle portrait, hologram lines on face"),
        ("Desert Caravan Silk", "沙漠商队丝绸", "Sand glitter", "沙粒闪", "caravan tale portrait, silk scarves, glittering sand"),
        ("Library Prophecy Scroll", "图书馆预言卷轴", "Dust beam", "尘束光", "library prophecy portrait, dust beam, ancient scroll"),
    ),
    "dr": pack_rows(
        ("Cloud Nine Soft", "九霄软云", "Pastel cumulus", "淡积云", "dream portrait floating in soft clouds, pastel cumulus"),
        ("Moon Bath Silver", "月光浴银调", "Cool halo", "冷光晕", "moonlit dream portrait, silver halo, serene expression"),
        ("Underwater Drift", "水下漂浮梦", "Caustic ribbons", "焦散带", "underwater dream portrait, caustic light ribbons, hair float"),
        ("Butterfly Garden Trance", "蝶园出神", "Wing bokeh", "蝶翼虚化", "dream portrait in butterfly garden, wing-shaped bokeh"),
        ("Northern Lights Face", "极光映脸", "Green curtain", "绿色幕", "aurora dream portrait, green aurora curtain on face map"),
        ("Starry Eyelid Glitter", "眼睑星尘闪", "Micro stars", "微星点", "dreamy portrait with glitter stars on eyelids, macro soft"),
        ("Mirage Heat Wave", "热浪蜃景", "Ripple air", "空气波纹", "desert mirage dream portrait, heat shimmer, surreal horizon"),
        ("Paper Moon Studio", "纸月亮影棚", "Cutout prop", "剪纸道具", "surreal paper moon prop portrait, studio whimsy"),
        ("Crystal Cave Prism", "水晶洞棱镜", "Rainbow caustics", "彩虹焦散", "crystal cave dream portrait, rainbow caustics on skin"),
        ("Sleep Paralysis Soft", "梦魇柔化版", "Gentle shadow", "柔和阴影", "softened sleep paralysis art portrait, gentle shadow"),
        ("Lucid Doorway Light", "清醒梦门口光", "Tungsten spill", "钨丝溢出", "lucid dream portrait at glowing doorway, warm spill"),
        ("Feather Bed Descent", "羽毛床坠落感", "Slow shutter", "慢门", "dream descent portrait among feathers, slow shutter blur"),
        ("Opal Haze Portrait", "蛋白石雾人像", "Iridescent skin", "虹彩肤", "opal haze dream portrait, iridescent skin highlights"),
        ("Milk Bath Stars", "牛奶浴星屑", "Macro bubbles", "微气泡", "milk bath dream portrait, floating star glitter, macro"),
        ("Rainbow Fog Silhouette", "彩虹雾剪影", "Edge glow", "边缘光", "silhouette in rainbow fog dream portrait, edge glow"),
    ),
    "sp": pack_rows(
        ("Track Spike Start", "田径起跑钉鞋", "Low sun rake", "低阳侧刷", "track athlete portrait at blocks, low sun rake, grit"),
        ("Basketball Arena Sweat", "篮球馆汗光", "Overhead spots", "顶光点阵", "basketball portrait under arena spots, sweat sheen"),
        ("Swim Goggle Chrome", "泳镜镀铬反光", "Pool caustics", "泳池焦散", "swimmer portrait, chrome goggles, pool caustics on skin"),
        ("Climbing Chalk Dust", "攀岩镁粉尘", "Grip texture", "抓握肌理", "climber portrait, chalk dust cloud, cliff rim light"),
        ("Tennis Court Harsh Noon", "网球场正午硬光", "Crisp shadow", "清晰影", "tennis portrait at noon, harsh crisp shadow, sweat"),
        ("Boxing Ring Rope Rim", "拳台围绳轮廓光", "Red corner", "红角", "boxing portrait in ring, rope rim light, red corner"),
        ("Soccer Field Mud", "足球场泥点", "Green cast", "绿色环境光", "soccer portrait with mud splatter, green field cast"),
        ("Yoga Inversion Glow", "瑜伽倒立光", "Studio gradient", "棚渐变", "yoga inversion portrait, studio gradient backdrop, calm"),
        ("Marathon Rain Poncho", "马拉松雨披", "Neon bib", "荧光号码", "marathon runner portrait in rain, neon bib, motion"),
        ("Skate Park Golden", "滑板公园金色时刻", "Long lens comp", "长焦压缩", "skate portrait at golden hour, compression, flare"),
        ("Ski Goggle Mountain", "滑雪镜雪山", "Cold air crisp", "冷空气清晰", "ski portrait, goggle reflection of peaks, crisp cold"),
        ("Rowing Crew Dawn", "赛艇队黎明", "Water texture", "水纹", "rowing crew portrait at dawn, water texture, synchronized"),
        ("Gym Deadlift Chalk", "健身房硬拉镁粉", "Industrial light", "工业风灯", "gym deadlift portrait, chalk puff, industrial lamps"),
        ("Surf Golden Curl", "冲浪金色卷浪", "Spray backlight", "浪花逆光", "surfer portrait inside curling wave, spray backlight"),
        ("Fencing Blade Spark", "击剑剑尖火花", "Dark strip", "暗剑道", "fencing portrait, blade spark hint, dark piste strip"),
    ),
    "jo": pack_rows(
        ("Big Laugh Sunflare", "大笑阳光眩光", "Lens bloom", "镜头 bloom", "joyful big laugh portrait, sunflare bloom, park"),
        ("Confetti Pop Moment", "纸屑迸发瞬间", "Color chips", "彩色碎片", "confetti pop celebration portrait, color chips on hair"),
        ("Bubble Gum Pink", "泡泡糖粉调", "Playful crop", "俏皮构图", "playful bubble gum portrait, pink grade, cheek puff"),
        ("Birthday Cake Candle", "生日蛋糕烛光", "Warm cheeks", "暖颊", "birthday joy portrait, candle glow on cheeks, frosting"),
        ("Water Balloon Freeze", "水球冻结瞬间", "Splash crown", "水花冠", "water balloon burst portrait frozen, splash crown"),
        ("Dog Park Genuine Smile", "狗公园真诚笑", "Golden fur bokeh", "金毛虚化", "dog park joy portrait with pet, golden bokeh"),
        ("Rollercoaster Scream", "过山车尖叫", "Wind cheeks", "风鼓脸颊", "rollercoaster scream portrait, wind-blown cheeks, thrill"),
        ("Splash Fight Summer", "夏日泼水战", "Water sparkles", "水珠闪", "summer splash fight portrait, water sparkles, laughter"),
        ("Karaoke Neon Joy", "KTV霓虹欢乐", "RGB face", "RGB 映脸", "karaoke joy portrait, neon RGB on face, mic prop"),
        ("Snow Angel Grin", "雪地天使笑", "Sky blue contrast", "天蓝对比", "snow angel joy portrait, sky blue contrast, grin"),
        ("Paint War Color", "彩粉大战", "Powder cloud", "粉雾", "color powder festival portrait, powder cloud, vibrant skin"),
        ("Fairground Cotton Candy", "游乐场棉花糖", "Pastel spin", "粉彩旋转", "fairground joy portrait, cotton candy pastel spin"),
        ("Jump Trampoline Blue", "蹦床跃起蓝天", "Wide angle stretch", "广角拉伸", "trampoline jump portrait, blue sky stretch"),
        ("Beach Cartwheel Sand", "沙滩侧手翻", "Sand spray", "沙粒飞溅", "beach cartwheel joy portrait, sand spray, sun"),
        ("Group Hug Stack", "叠罗汉拥抱", "Warm tangle", "暖交织", "group hug stack portrait, warm tangled arms, smiles"),
    ),
}


def attach_unique_images(packs: dict[str, list[dict]]) -> dict[str, list[dict]]:
    """每条写入唯一 image：真实人像（Unsplash），按包语义分桶，全站 210 条互不重复。"""
    by_pack = slugs_by_pack()
    out: dict[str, list[dict]] = {}
    for code, rows in packs.items():
        slugs = by_pack[code]
        if len(slugs) != len(rows):
            raise ValueError(f"pack {code}: slug count {len(slugs)} != row count {len(rows)}")
        fixed = []
        for i, r in enumerate(rows):
            item = {**r, "image": portrait_preview_url(slugs[i])}
            fixed.append(item)
        out[code] = fixed
    return out


def main() -> None:
    packs = attach_unique_images(PACKS_DATA)
    doc = {"packs": packs}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} ({sum(len(v) for v in packs.values())} styles)")


if __name__ == "__main__":
    main()
