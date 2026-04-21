/** 与后端 `public._ASPECT_RATIOS` 一致 */
export const ASPECT_RATIO_VALUES = [
  "auto",
  "1:1",
  "3:4",
  "4:3",
  "16:9",
  "9:16",
  "2:3",
  "3:2",
] as const;

export type AspectRatioValue = (typeof ASPECT_RATIO_VALUES)[number];

export type ImageSpecOption = {
  value: AspectRatioValue;
  /** 示意框宽高比，null 表示 Auto 用通用图符 */
  frame: { w: number; h: number } | null;
};

export const IMAGE_SPEC_OPTIONS: ImageSpecOption[] = [
  { value: "auto", frame: null },
  { value: "1:1", frame: { w: 1, h: 1 } },
  { value: "3:4", frame: { w: 3, h: 4 } },
  { value: "4:3", frame: { w: 4, h: 3 } },
  { value: "16:9", frame: { w: 16, h: 9 } },
  { value: "9:16", frame: { w: 9, h: 16 } },
  { value: "2:3", frame: { w: 2, h: 3 } },
  { value: "3:2", frame: { w: 3, h: 2 } },
];

export function isAspectRatioValue(s: string): s is AspectRatioValue {
  return (ASPECT_RATIO_VALUES as readonly string[]).includes(s);
}
