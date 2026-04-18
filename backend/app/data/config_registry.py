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
    "彩虹屁大模型（文案）": "文案能力依赖 Claude API Key；未配置则彩虹屁相关能力不可用。",
    "图片生成大模型": "头像 / 风格图依赖 API Key 与根地址；未配置则无法出图。",
    "存储配置": "生成结果需写入对象存储；Access/Secret/桶/区域为主流程必填项。",
    "支付与会员": "Stripe / Lemon Squeezy / USDT 任选配置；任一填好即可在前台展示对应收款方式。",
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
    # —— 彩虹屁大模型（文案）——
    ConfigEntry(
        key="claude_api_key",
        label="Claude API Key",
        description="Anthropic：用于生成 aura 解读、彩虹屁文案等（与图片模型分开配置）。",
        group="彩虹屁大模型（文案）",
        is_secret=True,
        required=True,
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
        description="如 Replicate OpenAPI 前缀 https://api.replicate.com/v1",
        group="图片生成大模型",
        is_secret=False,
        default="https://api.replicate.com/v1",
        required=True,
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
    "claude_api_key": "API Key",
    "image_api_key": "API Key",
    "image_api_endpoint": "API 根 URL",
    "s3_access_key": "Access Key",
    "s3_secret_key": "Secret Key",
    "s3_bucket_name": "存储桶名称",
    "s3_region": "Region 代码",
    "stripe_secret_key": "Secret Key（sk_…）",
    "stripe_webhook_secret": "Webhook 密钥（whsec_…）",
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
