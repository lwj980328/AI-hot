import { format, formatDistanceToNow } from "date-fns";
import { zhCN } from "date-fns/locale";

/** 格式化日期时间 */
export function formatDateTime(dateStr: string): string {
  return format(new Date(dateStr), "yyyy-MM-dd HH:mm:ss", { locale: zhCN });
}

/** 格式化相对时间 */
export function formatRelativeTime(dateStr: string): string {
  return formatDistanceToNow(new Date(dateStr), { addSuffix: true, locale: zhCN });
}

/** 截断文本 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + "...";
}
