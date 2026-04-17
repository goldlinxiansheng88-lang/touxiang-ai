/** 深度合并 locale 片段到英文底稿（未覆盖的键仍用英文）。场景/风格展示请用 t(key, apiFallback)，勿用 te() 判断。 */
export function deepMerge<T extends Record<string, unknown>>(base: T, patch: Partial<T> | Record<string, unknown>): T {
  const out = { ...base } as Record<string, unknown>;
  for (const key of Object.keys(patch)) {
    const pv = (patch as Record<string, unknown>)[key];
    const bv = out[key];
    if (Array.isArray(pv)) {
      out[key] = pv;
      continue;
    }
    if (
      pv &&
      typeof pv === "object" &&
      bv &&
      typeof bv === "object" &&
      !Array.isArray(bv)
    ) {
      out[key] = deepMerge(bv as Record<string, unknown>, pv as Record<string, unknown>);
    } else if (pv !== undefined) {
      out[key] = pv;
    }
  }
  return out as T;
}
