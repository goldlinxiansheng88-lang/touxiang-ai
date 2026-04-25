/**
 * 与 backend/app/data/config_registry.py 保持同步。
 * 当 GET /api/meta/config-registry 不可用时用于渲染分类，避免页面空白。
 */
import type { ConfigRegistrySchemaItem } from "@/api/client";

export const ADMIN_GROUP_ORDER: string[] = [
  "数据库与 API 基础",
  "彩虹屁大模型（文案）",
  "图片生成大模型",
  "存储配置",
  "支付与会员",
  "登录与 OAuth",
  "管理后台",
  "业务参数",
];

/** 左侧栏「配置」子菜单用的短标题，与 ADMIN_GROUP_ORDER 一一对应 */
export const CONFIG_SIDEBAR_SHORT_LABELS: Record<string, string> = {
  "数据库与 API 基础": "数据库",
  "彩虹屁大模型（文案）": "彩虹屁模型",
  图片生成大模型: "生图大模型",
  存储配置: "存储配置",
  支付与会员: "支付配置",
  "登录与 OAuth": "登录",
  管理后台: "管理后台",
  业务参数: "其他",
};

/** 与页内分类卡片 id 一致，供侧栏 #hash 跳转 */
/** 支持「连接」检测的配置 key，须与后端 connection_tests.TESTABLE_KEYS 一致 */
export const CONFIG_TESTABLE_KEYS: ReadonlySet<string> = new Set([
  "database_url",
  "redis_url",
  "encryption_key",
  "public_base_url",
  "frontend_url",
  "claude_api_key",
  "aura_llm_provider",
  "gemini_api_key",
  "deepseek_api_key",
  "image_api_key",
  "image_api_endpoint",
  "fal_key",
  "flux_img2img_model_id",
  "s3_access_key",
  "s3_secret_key",
  "s3_bucket_name",
  "s3_region",
  "stripe_secret_key",
  "lemon_squeezy_api_key",
  "usdt_receive_address",
]);

export function configGroupAnchorId(groupId: string): string {
  const bytes = new TextEncoder().encode(groupId);
  let binary = "";
  for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i]!);
  const b64 = btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  return `cfg-${b64}`;
}

/** 与 backend app/data/config_registry.py VALUE_KIND_LABELS 同步；schema 不可用时合并行仍显示填写类型 */
/** 与 backend ConfigEntry.required 一致；schema 不可用时合并行仍显示必填/选填 */
/** 与 backend ConfigEntry.required 一致：主流程可跑通（含彩虹屁、生图、S3、管理口令） */
const CONFIG_REQUIRED_KEYS = new Set<string>([
  "database_url",
  "redis_url",
  "encryption_key",
  "public_base_url",
  "frontend_url",
  "image_api_key",
  "image_api_endpoint",
  "s3_access_key",
  "s3_secret_key",
  "s3_bucket_name",
  "s3_region",
  "admin_password",
]);

export function configItemRequired(key: string): boolean {
  return CONFIG_REQUIRED_KEYS.has(key);
}

export const CONFIG_VALUE_KIND_BY_KEY: Record<string, string> = {
  database_url: "整段连接串（postgresql://…）",
  redis_url: "整段连接串（redis://…）",
  encryption_key: "Fernet 主密钥",
  public_base_url: "HTTPS 根地址",
  frontend_url: "HTTPS 根地址",
  cors_allowed_origins: "多个 HTTPS Origin（逗号分隔）",
  cors_allow_origin_regex: "正则（Origin 匹配）",
  cors_enable_vercel_preview_regex: "true 或 false",
  aura_llm_provider: "claude / gemini / deepseek",
  claude_api_key: "API Key",
  gemini_api_key: "API Key",
  deepseek_api_key: "API Key",
  image_api_key: "API Key",
  image_api_endpoint: "API 根 URL",
  fal_key: "Fal API Key（FAL_KEY）",
  flux_img2img_model_id: "fal 模型 endpoint",
  s3_access_key: "Access Key",
  s3_secret_key: "Secret Key",
  s3_bucket_name: "存储桶名称",
  s3_region: "Region 代码",
  stripe_secret_key: "Secret Key（sk_…）",
  stripe_webhook_secret: "Webhook 密钥（whsec_…）",
  creem_api_key: "API Key（x-api-key）",
  creem_product_id: "商品 ID（prod_…）",
  creem_webhook_secret: "Webhook HMAC 密钥",
  creem_api_base_url: "HTTPS API 根地址",
  lemon_squeezy_api_key: "API Key（Bearer）",
  lemon_squeezy_store_id: "数字 ID",
  lemon_squeezy_variant_id: "变体 ID",
  lemon_squeezy_webhook_secret: "Webhook 签名串",
  usdt_receive_address: "链上地址",
  usdt_network: "网络名称",
  checkout_amount_usd: "美元金额（数字）",
  checkout_amount_usdt: "USDT 数量（数字）",
  pricing_subscription_url: "HTTPS 完整链接",
  pricing_credits_pack_url: "HTTPS 完整链接",
  commission_default_rate: "比例 0～1",
  google_oauth_client_id: "Client ID",
  google_oauth_client_secret: "Client Secret",
  microsoft_oauth_client_id: "Client ID",
  microsoft_oauth_client_secret: "Client Secret",
  admin_email: "邮箱地址",
  admin_password: "口令",
  free_daily_limit: "正整数",
};

export const ADMIN_GROUP_HINTS: Record<string, string> = {
  "数据库与 API 基础":
    "数据库连接、Redis、主密钥可在下方直接填写。若 PostgreSQL 尚未连通，保存时会先写入 backend/.env 并尝试在本进程内用新串建连；试连成功后再保存一次，其余项会写入配置库。仍失败请看 /health/db。",
  "彩虹屁大模型（文案）":
    "选择 Claude / Gemini / DeepSeek 之一并填写对应 Key；未配置所选模型密钥时使用内置占位文案。",
  图片生成大模型:
    "生图：配置 Fal API Key（FAL_KEY）后 Worker 调用 fal 上 FLUX.1 img2img；上传图 URL 须公网可访问。未配置则仍为占位模糊预览。",
  存储配置: "生成结果需写入对象存储；Access/Secret/桶/区域为主流程必填项。",
  支付与会员:
    "Stripe / Creem / Lemon Squeezy / USDT 任选配置；任一填好即可在前台展示对应收款方式。另可填「定价页 · 订阅链接 / 积分包链接」，用于 /pricing 页面对外跳转。",
  "登录与 OAuth": "第三方登录（Google / Microsoft）相关参数。填入对应 Client ID/Secret 后即可启用。",
  管理后台: "左侧栏「管理密码」与 ADMIN_PASSWORD 一致，用于调用管理接口。",
  业务参数: "免费次数、运营策略相关数值。",
};

export function getFallbackConfigRegistry(): {
  groups: { id: string; label: string; hint: string }[];
  items: ConfigRegistrySchemaItem[];
} {
  const groups = ADMIN_GROUP_ORDER.map((id) => ({
    id,
    label: id,
    hint: ADMIN_GROUP_HINTS[id] ?? "",
  }));

  const itemsRaw: Omit<ConfigRegistrySchemaItem, "required">[] = [
    {
      key: "database_url",
      label: "PostgreSQL",
      group: "数据库与 API 基础",
      description:
        "整段连接串（postgresql://…）。若当前尚无法连库，仍可在此保存：将先同步到 backend/.env 并试连；试连成功后再保存一次即可写入其余项。",
      readonly: false,
      is_secret: true,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.database_url,
    },
    {
      key: "redis_url",
      label: "Redis",
      group: "数据库与 API 基础",
      description: "整段 Redis 地址（redis://…）；保存后写入配置库与 .env。",
      readonly: false,
      is_secret: false,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.redis_url,
    },
    {
      key: "encryption_key",
      label: "Fernet 加密主密钥",
      group: "数据库与 API 基础",
      description: "保存后写入配置库与 .env；修改后建议重启 API。",
      readonly: false,
      is_secret: true,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.encryption_key,
    },
    {
      key: "public_base_url",
      label: "后端 API 公网根地址",
      group: "数据库与 API 基础",
      description: "拼上传图片、Webhook 等绝对 URL，如 https://api.xxx.com",
      readonly: false,
      is_secret: false,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.public_base_url,
    },
    {
      key: "frontend_url",
      label: "前端站点根地址",
      group: "数据库与 API 基础",
      description: "Stripe 支付完成回跳、用户可见链接，如 https://app.xxx.com",
      readonly: false,
      is_secret: false,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.frontend_url,
    },
    {
      key: "cors_allowed_origins",
      label: "CORS 允许的浏览器 Origin（逗号分隔）",
      group: "数据库与 API 基础",
      description:
        "前后端分离部署时必填：填写浏览器地址栏的 Origin（scheme://host，不要带路径），多个用英文逗号分隔。示例：https://app.vercel.app,https://preview.vercel.app",
      readonly: false,
      is_secret: false,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.cors_allowed_origins,
    },
    {
      key: "cors_allow_origin_regex",
      label: "CORS 允许的 Origin 正则（可选）",
      group: "数据库与 API 基础",
      description:
        "用于 Vercel Preview 等多变子域。留空则默认启用内置规则：`https://*.vercel.app`（多级子域，HTTPS only）+（若 FRONTEND_URL / PUBLIC_BASE_URL 为 https）对应精确 Origin。也可用 cors_enable_vercel_preview_regex=false 关闭默认规则。",
      readonly: false,
      is_secret: false,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.cors_allow_origin_regex,
    },
    {
      key: "cors_enable_vercel_preview_regex",
      label: "启用 Vercel 预览域名 CORS 正则（默认开）",
      group: "数据库与 API 基础",
      description:
        "默认 true：放行 `https://*.vercel.app`，并在 https 场景下把 FRONTEND_URL / PUBLIC_BASE_URL 的域名并入正则。更复杂场景请填 cors_allow_origin_regex 覆盖默认，或继续用 cors_allowed_origins 精确列出。",
      readonly: false,
      is_secret: false,
      default: "true",
      value_kind: CONFIG_VALUE_KIND_BY_KEY.cors_enable_vercel_preview_regex,
    },
    {
      key: "aura_llm_provider",
      label: "彩虹屁文案模型",
      group: "彩虹屁大模型（文案）",
      description: "三选一：claude、gemini、deepseek（小写）。决定使用哪把 API Key 生成解读文案。",
      readonly: false,
      is_secret: false,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.aura_llm_provider,
    },
    {
      key: "claude_api_key",
      label: "Claude API Key",
      group: "彩虹屁大模型（文案）",
      description: "Anthropic：当上方选择 claude 时必填。",
      readonly: false,
      is_secret: true,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.claude_api_key,
    },
    {
      key: "gemini_api_key",
      label: "Gemini API Key",
      group: "彩虹屁大模型（文案）",
      description: "Google AI Studio / Gemini：当上方选择 gemini 时必填。",
      readonly: false,
      is_secret: true,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.gemini_api_key,
    },
    {
      key: "deepseek_api_key",
      label: "DeepSeek API Key",
      group: "彩虹屁大模型（文案）",
      description: "DeepSeek OpenAI 兼容接口：当上方选择 deepseek 时必填。",
      readonly: false,
      is_secret: true,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.deepseek_api_key,
    },
    {
      key: "image_api_key",
      label: "图像生成 API Key",
      group: "图片生成大模型",
      description: "Replicate / SDXL 等图像推理服务的密钥。",
      readonly: false,
      is_secret: true,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.image_api_key,
    },
    {
      key: "image_api_endpoint",
      label: "图像 API 根地址",
      group: "图片生成大模型",
      description: "如 Replicate OpenAPI 前缀 https://api.replicate.com/v1（与 Fal 可并行配置）。",
      readonly: false,
      is_secret: false,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.image_api_endpoint,
    },
    {
      key: "fal_key",
      label: "Fal.ai API Key（FAL_KEY）",
      group: "图片生成大模型",
      description:
        "fal.ai Dashboard 创建；Worker 用于 FLUX img2img。也可仅用服务器环境变量 FAL_KEY。上传图须能被 fal 拉取（public_base_url 可公网访问）。",
      readonly: false,
      is_secret: true,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.fal_key,
    },
    {
      key: "flux_img2img_model_id",
      label: "FLUX img2img 模型 ID",
      group: "图片生成大模型",
      description: "默认 fal-ai/flux/dev/image-to-image（FLUX.1 [dev] image-to-image）。",
      readonly: false,
      is_secret: false,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.flux_img2img_model_id,
    },
    {
      key: "s3_access_key",
      label: "对象存储 Access Key",
      group: "存储配置",
      description: "生成结果图、缩略图存放（S3 兼容）。",
      readonly: false,
      is_secret: true,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.s3_access_key,
    },
    {
      key: "s3_secret_key",
      label: "对象存储 Secret Key",
      group: "存储配置",
      description: "与上配对。",
      readonly: false,
      is_secret: true,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.s3_secret_key,
    },
    {
      key: "s3_bucket_name",
      label: "存储桶名称",
      group: "存储配置",
      description: "Bucket 名。",
      readonly: false,
      is_secret: false,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.s3_bucket_name,
    },
    {
      key: "s3_region",
      label: "区域 Region",
      group: "存储配置",
      description: "如 us-east-1。",
      readonly: false,
      is_secret: false,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.s3_region,
    },
    {
      key: "stripe_secret_key",
      label: "Stripe Secret Key",
      group: "支付与会员",
      description: "sk_live_… / sk_test_…",
      readonly: false,
      is_secret: true,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.stripe_secret_key,
    },
    {
      key: "stripe_webhook_secret",
      label: "Stripe Webhook 签名密钥",
      group: "支付与会员",
      description: "Dashboard → Webhooks → Signing secret。",
      readonly: false,
      is_secret: true,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.stripe_webhook_secret,
    },
    {
      key: "lemon_squeezy_api_key",
      label: "Lemon Squeezy API Key",
      group: "支付与会员",
      description: "Settings → API → 创建 API Key（Bearer）。",
      readonly: false,
      is_secret: true,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.lemon_squeezy_api_key,
    },
    {
      key: "lemon_squeezy_store_id",
      label: "Lemon Squeezy Store ID",
      group: "支付与会员",
      description: "商店数字 ID（Dashboard URL 或 API 中可见）。",
      readonly: false,
      is_secret: false,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.lemon_squeezy_store_id,
    },
    {
      key: "lemon_squeezy_variant_id",
      label: "Lemon Squeezy Variant ID",
      group: "支付与会员",
      description: "单次解锁对应的商品变体 ID。",
      readonly: false,
      is_secret: false,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.lemon_squeezy_variant_id,
    },
    {
      key: "lemon_squeezy_webhook_secret",
      label: "Lemon Squeezy Webhook 签名密钥",
      group: "支付与会员",
      description: "创建 Webhook 时填写的 Signing secret；回调 URL 填 /api/webhooks/lemon-squeezy。",
      readonly: false,
      is_secret: true,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.lemon_squeezy_webhook_secret,
    },
    {
      key: "usdt_receive_address",
      label: "USDT 收款地址",
      group: "支付与会员",
      description: "链上收款地址（如 TRC20）；到账后在订单页确认收款。",
      readonly: false,
      is_secret: false,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.usdt_receive_address,
    },
    {
      key: "usdt_network",
      label: "USDT 网络",
      group: "支付与会员",
      description: "如 TRC20、ERC20。",
      readonly: false,
      is_secret: false,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.usdt_network,
    },
    {
      key: "checkout_amount_usd",
      label: "单次解锁价格 (USD)",
      group: "支付与会员",
      description: "用户付费解锁高清等，单位美元，如 2.99。",
      readonly: false,
      is_secret: false,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.checkout_amount_usd,
    },
    {
      key: "checkout_amount_usdt",
      label: "USDT 应付数量",
      group: "支付与会员",
      description: "链上转账应付 USDT 数量；未填则默认与 USD 金额相同。",
      readonly: false,
      is_secret: false,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.checkout_amount_usdt,
    },
    {
      key: "pricing_subscription_url",
      label: "定价页 · 订阅链接",
      group: "支付与会员",
      description: "完整 HTTPS URL；前台 /pricing 展示「订阅」外链。留空则隐藏。",
      readonly: false,
      is_secret: false,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.pricing_subscription_url,
    },
    {
      key: "pricing_credits_pack_url",
      label: "定价页 · 积分包链接",
      group: "支付与会员",
      description: "完整 HTTPS URL；前台 /pricing 展示「积分包」外链。留空则隐藏。",
      readonly: false,
      is_secret: false,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.pricing_credits_pack_url,
    },
    {
      key: "commission_default_rate",
      label: "分销默认佣金比例",
      group: "支付与会员",
      description: "0～1 小数，如 0.30 表示 30%。",
      readonly: false,
      is_secret: false,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.commission_default_rate,
    },
    {
      key: "google_oauth_client_id",
      label: "Google OAuth Client ID",
      group: "登录与 OAuth",
      description: "Google 登录用。来自 Google Cloud Console OAuth 2.0 客户端（Web application）。",
      readonly: false,
      is_secret: false,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.google_oauth_client_id,
    },
    {
      key: "google_oauth_client_secret",
      label: "Google OAuth Client Secret",
      group: "登录与 OAuth",
      description: "Google 登录用。与 Client ID 配对。",
      readonly: false,
      is_secret: true,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.google_oauth_client_secret,
    },
    {
      key: "microsoft_oauth_client_id",
      label: "Microsoft OAuth Client ID",
      group: "登录与 OAuth",
      description: "微软登录用。来自 Azure App Registration（Application (client) ID）。",
      readonly: false,
      is_secret: false,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.microsoft_oauth_client_id,
    },
    {
      key: "microsoft_oauth_client_secret",
      label: "Microsoft OAuth Client Secret",
      group: "登录与 OAuth",
      description: "微软登录用。与 Client ID 配对。",
      readonly: false,
      is_secret: true,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.microsoft_oauth_client_secret,
    },
    {
      key: "admin_email",
      label: "管理员联系邮箱",
      group: "管理后台",
      description: "展示/对账用。",
      readonly: false,
      is_secret: false,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.admin_email,
    },
    {
      key: "admin_password",
      label: "管理后台口令",
      group: "管理后台",
      description: "与页面顶部「管理令牌」相同；对应环境变量 ADMIN_PASSWORD。",
      readonly: false,
      is_secret: true,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.admin_password,
    },
    {
      key: "free_daily_limit",
      label: "免费用户每日生成次数",
      group: "业务参数",
      description: "整数，防刷。",
      readonly: false,
      is_secret: false,
      value_kind: CONFIG_VALUE_KIND_BY_KEY.free_daily_limit,
    },
  ];

  const items: ConfigRegistrySchemaItem[] = itemsRaw.map((it) => ({
    ...it,
    required: configItemRequired(it.key),
  }));

  return { groups, items };
}
