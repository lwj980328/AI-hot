import { useLocation } from "react-router-dom";
import { BrainCircuit, Menu } from "lucide-react";
import { Button } from "@/components/ui/button";

/** 页面标题映射 */
const pageTitles: Record<string, string> = {
  "/": "Dashboard",
  "/research": "研究工作台",
  "/workflow": "Workflow Monitor",
  "/reports": "研究报告",
  "/settings": "设置",
};

/** 顶部导航栏组件 */
export function Header() {
  const location = useLocation();
  const title = pageTitles[location.pathname] || "AI Research OS";

  return (
    <header className="flex h-16 items-center justify-between border-b px-6">
      <div className="flex items-center gap-4">
        {/* 移动端菜单按钮 */}
        <Button variant="ghost" size="icon" className="md:hidden">
          <Menu className="h-5 w-5" />
        </Button>

        {/* 移动端 Logo */}
        <div className="flex items-center gap-2 md:hidden">
          <BrainCircuit className="h-6 w-6 text-primary" />
          <span className="font-semibold">AI Research OS</span>
        </div>

        {/* 页面标题 */}
        <h1 className="text-lg font-semibold hidden md:block">{title}</h1>
      </div>

      {/* 右侧操作区 */}
      <div className="flex items-center gap-2">
        {/* 后续可添加用户头像、通知等 */}
      </div>
    </header>
  );
}
