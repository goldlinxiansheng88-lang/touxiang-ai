/** 分项/通用配置：输入框右侧竖条（必填红 / 选填灰），与标签小徽章一致 */

export const FIELD_ACCENT_REQUIRED = "border-r-[3px] border-r-rose-500";
export const FIELD_ACCENT_OPTIONAL = "border-r-[3px] border-r-stone-300";

export function fieldAccentClass(required: boolean): string {
  return required ? FIELD_ACCENT_REQUIRED : FIELD_ACCENT_OPTIONAL;
}
