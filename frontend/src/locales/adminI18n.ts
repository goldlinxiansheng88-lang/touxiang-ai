/** 与后端 / 内置 schema 的分类 id 一致 */
export const ADMIN_GROUP_I18N: Record<string, string> = {
  "数据库与 API 基础": "db",
  "彩虹屁大模型（文案）": "claude",
  图片生成大模型: "image",
  存储配置: "storage",
  支付与会员: "payment",
  管理后台: "adminPanel",
  业务参数: "biz",
};

export function adminGroupPath(id: string, field: "label" | "short" | "hint"): string {
  const slug = ADMIN_GROUP_I18N[id];
  if (!slug) return "";
  return `admin.groups.${slug}.${field}`;
}

export function adminItemField(key: string, field: "label" | "description"): string {
  return `admin.items.${key}.${field}`;
}

export function adminValueKindKey(configKey: string): string {
  return `admin.valueKinds.${configKey}`;
}

export function tr(
  te: (key: string) => boolean,
  t: (key: string, ...args: unknown[]) => string,
  key: string,
  fallback: string,
): string {
  return key && te(key) ? t(key) : fallback;
}
