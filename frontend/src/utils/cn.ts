import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/** 合并 className，支持条件和 TailwindCSS 去重 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
