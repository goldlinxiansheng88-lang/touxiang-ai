"""集中登记所有可配置项（对应原 .env / Settings），供后台展示与播种。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ConfigEntry:
    key: str
    label: str
    description: str
    group: str
    is_secret: bool
    readonly: bool = False
    default: str = ""
    # True = 核心业务可运行所需（含彩虹屁/生图/存储等）；False = 支付、展示、有内置默认等
    required: bool = False


# 顺序即后台分组与展示顺序（业务向命名，便于运营理解）
GROUP_ORDER: tuple[str, ...] = (
    "数据库与 API 基础",
    "彩虹屁大模型（文案）",
    "图片生成大模型",
    "存储配置",
    "支付与会员",
    "管理后台",
    "业务参数",
)

# 每组一句说明，展示在后台分组标题下
GROUP_HINTS: dict[str, str] = {
    "数据库与 API 基础": (
        "数据库、Redis、主密钥可先在本页保存。若当前进程连不上 PostgreSQL，会先把这三项写入 backend/.env，"
        "并尝试用新连接串在本进程内重建连接池；试连成功后请再保存一次，即可把其余项写入配置库。"
        "连接串勿留占位符；仍失败请打开 /health/db 看具体错误。独立 Celery 等进程若单独读 .env，修改后需各自重启。"
    ),
    "彩虹屁大模型（文案）": (
        "在「彩虹屁文案模型」中选 Claude / Gemini / DeepSeek 之一，并填写对应 API Key。"
        "未配置所选模型的密钥时，将使用内置占位文案。"
    ),
    "图片生成大模型": (
        "生图：在后台填写 Fal API Key（或环境变量 FAL_KEY）后，Worker 会调用 fal 上 "
        "FLUX.1 img2img（默认 fal-ai/flux/dev/image-to-image）。上传图 URL 须对公网可访问（public_base_url）。"
        "未配置 Fal 时仍走本地占位模糊预览。"
    ),
    "存储配置": "生成结果需写入对象存储；Access/Secret/桶/区域为主流程必填项。",
    "支付与会员": "Stripe / Creem / Lemon Squeezy / USDT 任选配置；任一填好即可在前台展示对应收款方式。",
    "管理后台": "左侧栏「管理密码」与 ADMIN_PASSWORD 一致，用于调用管理接口。",
    "业务参数": "免费次数、运营策略相关数值。",
}

CONFIG_ENTRIES: tuple[ConfigEntry, ...] = (
    # —— 数据库与 API 基础 ——
    ConfigEntry(
        key="database_url",
        label="PostgreSQL",
        description="整段连接串（postgresql://…），与云平台「Direct connection」或自建库一致；保存后写入配置库并同步 backend/.env，本 API 进程会按新串重建连接池。若当前尚无法连库，仍可在此保存：将先同步到 backend/.env 并试连；试连成功后再保存一次即可写入其余项。",
        group="数据库与 API 基础",
        is_secret=True,
        readonly=False,
        required=True,
    ),
    ConfigEntry(
        key="redis_url",
        label="Redis",
        description="整段地址（redis:// 或 rediss://…）；保存后写入配置库与 .env。Worker 使用 Redis 时修改后也需重启。",
        group="数据库与 API 基础",
        is_secret=False,
        readonly=False,
        required=True,
    ),
    ConfigEntry(
        key="encryption_key",
        label="Fernet 加密主密钥",
        description="用于加密库中其它敏感配置。保存后写入配置库与 .env；修改后建议重启 API。",
        group="数据库与 API 基础",
        is_secret=True,
        readonly=False,
        required=True,
    ),
    ConfigEntry(
        key="public_base_url",
        label="后端 API 公网根地址",
        description="拼上传图片、Webhook 等绝对 URL，如 https://api.xxx.com",
        group="数据库与 API 基础",
        is_secret=False,
        required=True,
    ),
    ConfigEntry(
        key="frontend_url",
        label="前端站点根地址",
        description="Stripe 支付完成回跳、用户可见链接，如 https://app.xxx.com",
        group="数据库与 API 基础",
        is_secret=False,
        required=True,
    ),
    ConfigEntry(
        key="cors_allowed_origins",
        label="CORS 允许的浏览器 Origin（逗号分隔）",
        description=(
            "前后端分离部署时必须配置：浏览器 Origin 形如 https://app.xxx.com（不要带路径）。"
            "前端 axios 使用 withCredentials=true 时，后端不能使用 Access-Control-Allow-Origin: *。"
        ),
        group="数据库与 API 基础",
        is_secret=False,
        readonly=False,
        required=False,
    ),
    ConfigEntry(
        key="cors_allow_origin_regex",
        label="CORS 允许的 Origin 正则（可选）",
        description=(
            "用于 Vercel Preview 等多变子域：填写 Python/JS 风格的正则（不要带引号）。"
            "留空时默认启用 `https://*.vercel.app` 规则（可用 cors_enable_vercel_preview_regex=false 关闭）。"
        ),
        group="数据库与 API 基础",
        is_secret=False,
        readonly=False,
        required=False,
    ),
    ConfigEntry(
        key="cors_enable_vercel_preview_regex",
        label="启用 Vercel 预览域名 CORS 正则（默认开）",
        description="默认开启：放行 `https://*.vercel.app`（HTTPS only）。若你有自定义前端域名，请优先用 cors_allowed_origins 精确列出。",
        group="数据库与 API 基础",
        is_secret=False,
        readonly=False,
        default="true",
        required=False,
    ),
    # —— 彩虹屁大模型（文案）——
    ConfigEntry(
        key="aura_llm_provider",
        label="彩虹屁文案模型",
        description="三选一：claude（Anthropic）、gemini（Google AI Studio）、deepseek（DeepSeek）。决定下方哪把 Key 生效。",
        group="彩虹屁大模型（文案）",
        is_secret=False,
        default="claude",
        required=False,
    ),
    ConfigEntry(
        key="claude_api_key",
        label="Claude API Key",
        description="Anthropic：当「彩虹屁文案模型」为 claude 时使用。",
        group="彩虹屁大模型（文案）",
        is_secret=True,
        required=False,
    ),
    ConfigEntry(
        key="gemini_api_key",
        label="Gemini API Key",
        description="Google AI Studio / Gemini API Key；当「彩虹屁文案模型」为 gemini 时使用。",
        group="彩虹屁大模型（文案）",
        is_secret=True,
        required=False,
    ),
    ConfigEntry(
        key="deepseek_api_key",
        label="DeepSeek API Key",
        description="DeepSeek OpenAI 兼容接口；当「彩虹屁文案模型」为 deepseek 时使用。",
        group="彩虹屁大模型（文案）",
        is_secret=True,
        required=False,
    ),
    # —— 图片生成大模型 ——
    ConfigEntry(
        key="image_api_key",
        label="图像生成 API Key",
        description="Replicate / SDXL 等图像推理服务的密钥。",
        group="图片生成大模型",
        is_secret=True,
        required=True,
    ),
    ConfigEntry(
        key="image_api_endpoint",
        label="图像 API 根地址",
        description="如 Replicate OpenAPI 前缀 https://api.replicate.com/v1（与 Fal 并行：未用 Replicate 可保留默认）。",
        group="图片生成大模型",
        is_secret=False,
        default="https://api.replicate.com/v1",
        required=True,
    ),
    ConfigEntry(
        key="fal_key",
        label="Fal.ai API Key（FAL_KEY）",
        description="fal.ai Dashboard 创建；Worker 用于 FLUX img2img。也可不设此项，仅在服务器环境变量中配置 FAL_KEY。",
        group="图片生成大模型",
        is_secret=True,
        required=False,
    ),
    ConfigEntry(
        key="flux_img2img_model_id",
        label="FLUX img2img 模型 ID",
        description="默认 fal-ai/flux/dev/image-to-image（FLUX.1 [dev] image-to-image）。勿随意更改除非迁移新 endpoint。",
        group="图片生成大模型",
        is_secret=False,
        default="fal-ai/flux/dev/image-to-image",
        required=False,
    ),
    # —— 存储配置 ——
    ConfigEntry(
        key="s3_access_key",
        label="对象存储 Access Key",
        description="生成结果图、缩略图存放（S3 兼容）。",
        group="存储配置",
        is_secret=True,
        required=True,
    ),
    ConfigEntry(
        key="s3_secret_key",
        label="对象存储 Secret Key",
        description="与上配对。",
        group="存储配置",
        is_secret=True,
        required=True,
    ),
    ConfigEntry(
        key="s3_bucket_name",
        label="存储桶名称",
        description="Bucket 名。",
        group="存储配置",
        is_secret=False,
        required=True,
    ),
    ConfigEntry(
        key="s3_region",
        label="区域 Region",
        description="如 us-east-1。",
        group="存储配置",
        is_secret=False,
        default="us-east-1",
        required=True,
    ),
    ConfigEntry(
        key="s3_endpoint_url",
        label="对象存储 Endpoint URL",
        description="S3 兼容 endpoint（R2 形如 https://<accountid>.r2.cloudflarestorage.com）。",
        group="存储配置",
        is_secret=False,
        required=True,
    ),
    ConfigEntry(
        key="s3_public_base_url",
        label="对象存储公网访问前缀",
        description="对外可访问的 URL 前缀（建议绑定自定义域名），如 https://img.yourdomain.com/bucket-or-prefix（末尾不带 /）。",
        group="存储配置",
        is_secret=False,
        required=True,
    ),
    # —— 支付与会员 ——
    ConfigEntry(
        key="stripe_secret_key",
        label="Stripe Secret Key",
        description="sk_live_… / sk_test_…",
        group="支付与会员",
        is_secret=True,
    ),
    ConfigEntry(
        key="stripe_webhook_secret",
        label="Stripe Webhook 签名密钥",
        description="Dashboard → Webhooks → Signing secret。",
        group="支付与会员",
        is_secret=True,
    ),
    ConfigEntry(
        key="creem_api_key",
        label="Creem API Key",
        description="Creem Dashboard → Settings → API Keys；请求头 x-api-key。",
        group="支付与会员",
        is_secret=True,
    ),
    ConfigEntry(
        key="creem_product_id",
        label="Creem 商品 ID",
        description="Dashboard → Products 中商品的 ID（如 prod_…）；Checkout 金额以该商品定价为准。",
        group="支付与会员",
        is_secret=False,
    ),
    ConfigEntry(
        key="creem_webhook_secret",
        label="Creem Webhook 签名密钥",
        description="Dashboard → Developers → Webhooks 中复制的 secret；用于 /api/webhooks/creem 校验 creem-signature（HMAC-SHA256）。",
        group="支付与会员",
        is_secret=True,
    ),
    ConfigEntry(
        key="creem_api_base_url",
        label="Creem API 根地址",
        description="生产默认 https://api.creem.io；沙盒可用 https://test-api.creem.io。",
        group="支付与会员",
        is_secret=False,
        default="https://api.creem.io",
    ),
    ConfigEntry(
        key="lemon_squeezy_api_key",
        label="Lemon Squeezy API Key",
        description="Settings → API → 创建 API Key（Bearer）。",
        group="支付与会员",
        is_secret=True,
    ),
    ConfigEntry(
        key="lemon_squeezy_store_id",
        label="Lemon Squeezy Store ID",
        description="商店数字 ID（Dashboard URL 或 API 中可见）。",
        group="支付与会员",
        is_secret=False,
    ),
    ConfigEntry(
        key="lemon_squeezy_variant_id",
        label="Lemon Squeezy Variant ID",
        description="单次解锁对应的商品变体 ID；价格可与下方 USD 金额一致或在后台用 custom_price 覆盖。",
        group="支付与会员",
        is_secret=False,
    ),
    ConfigEntry(
        key="lemon_squeezy_webhook_secret",
        label="Lemon Squeezy Webhook 签名密钥",
        description="创建 Webhook 时填写的 Signing secret；用于 /api/webhooks/lemon-squeezy 验签。",
        group="支付与会员",
        is_secret=True,
    ),
    ConfigEntry(
        key="usdt_receive_address",
        label="USDT 收款地址",
        description="链上收款地址（如 TRC20）；填写后前台显示 USDT 支付。到账需管理员在订单页「确认收款」。",
        group="支付与会员",
        is_secret=False,
    ),
    ConfigEntry(
        key="usdt_network",
        label="USDT 网络",
        description="如 TRC20、ERC20，展示给用户。",
        group="支付与会员",
        is_secret=False,
        default="TRC20",
    ),
    ConfigEntry(
        key="checkout_amount_usd",
        label="单次解锁价格 (USD)",
        description="用户付费解锁高清等，单位美元，如 2.99。",
        group="支付与会员",
        is_secret=False,
        default="2.99",
    ),
    ConfigEntry(
        key="checkout_amount_usdt",
        label="USDT 应付数量",
        description="链上转账应付 USDT 数量（可与美元标价分开设置）；未填则默认与 USD 金额相同。",
        group="支付与会员",
        is_secret=False,
        default="2.99",
    ),
    ConfigEntry(
        key="commission_default_rate",
        label="分销默认佣金比例",
        description="0～1 小数，如 0.30 表示 30%。",
        group="支付与会员",
        is_secret=False,
        default="0.30",
    ),
    # —— 管理后台 ——
    ConfigEntry(
        key="admin_email",
        label="管理员联系邮箱",
        description="展示/对账用。",
        group="管理后台",
        is_secret=False,
    ),
    ConfigEntry(
        key="admin_password",
        label="管理后台口令",
        description="与页面顶部「管理令牌」相同；对应环境变量 ADMIN_PASSWORD。",
        group="管理后台",
        is_secret=True,
        required=True,
    ),
    # —— 业务参数 ——
    ConfigEntry(
        key="free_daily_limit",
        label="免费用户每日生成次数",
        description="整数，防刷。",
        group="业务参数",
        is_secret=False,
        default="3",
    ),
)

# 后台表单「填写类型」提示（与前端 CONFIG_VALUE_KIND_BY_KEY 语义一致）
VALUE_KIND_LABELS: dict[str, str] = {
    "database_url": "整段连接串（postgresql://…）",
    "redis_url": "整段连接串（redis://…）",
    "encryption_key": "Fernet 主密钥",
    "public_base_url": "HTTPS 根地址",
    "frontend_url": "HTTPS 根地址",
    "cors_allowed_origins": "多个 HTTPS Origin（逗号分隔）",
    "cors_allow_origin_regex": "正则（Origin 匹配）",
    "cors_enable_vercel_preview_regex": "true | false",
    "aura_llm_provider": "claude | gemini | deepseek",
    "claude_api_key": "API Key",
    "gemini_api_key": "API Key",
    "deepseek_api_key": "API Key",
    "image_api_key": "API Key",
    "image_api_endpoint": "API 根 URL",
    "fal_key": "Fal API Key（FAL_KEY）",
    "flux_img2img_model_id": "fal 模型 endpoint 名",
    "s3_access_key": "Access Key",
    "s3_secret_key": "Secret Key",
    "s3_bucket_name": "存储桶名称",
    "s3_region": "Region 代码",
    "s3_endpoint_url": "HTTPS Endpoint URL",
    "s3_public_base_url": "公网 URL 前缀",
    "stripe_secret_key": "Secret Key（sk_…）",
    "stripe_webhook_secret": "Webhook 密钥（whsec_…）",
    "creem_api_key": "API Key（x-api-key）",
    "creem_product_id": "商品 ID（prod_…）",
    "creem_webhook_secret": "Webhook HMAC 密钥",
    "creem_api_base_url": "HTTPS API 根地址",
    "lemon_squeezy_api_key": "API Key（Bearer）",
    "lemon_squeezy_store_id": "数字 ID",
    "lemon_squeezy_variant_id": "变体 ID",
    "lemon_squeezy_webhook_secret": "Webhook 签名串",
    "usdt_receive_address": "链上地址",
    "usdt_network": "网络名称",
    "checkout_amount_usd": "美元金额（数字）",
    "checkout_amount_usdt": "USDT 数量（数字）",
    "commission_default_rate": "比例 0～1",
    "admin_email": "邮箱地址",
    "admin_password": "口令",
    "free_daily_limit": "正整数",
}


def entry_by_key(key: str) -> ConfigEntry | None:
    for e in CONFIG_ENTRIES:
        if e.key == key:
            return e
    return None


def should_encrypt_on_write(key: str) -> bool:
    # 主密钥与基础设施连接串：明文存库并同步 .env，避免无密钥时无法写入或启动期循环依赖
    if key in ("encryption_key", "database_url", "redis_url"):
        return False
    e = entry_by_key(key)
    if e:
        return e.is_secret and not e.readonly
    return any(s in key.lower() for s in ("key", "secret", "password"))
