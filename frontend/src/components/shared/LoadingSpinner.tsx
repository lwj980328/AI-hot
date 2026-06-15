import { Loader2 } from "lucide-react";
import { cn } from "@/utils/cn";

interface LoadingSpinnerProps {
  className?: string;
  size?: number;
}

/** 加载动画组件 */
export function LoadingSpinner({ className, size = 24 }: LoadingSpinnerProps) {
  return <Loader2 className={cn("animate-spin", className)} size={size} />;
}
