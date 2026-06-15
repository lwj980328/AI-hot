import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  FlaskConical,
  FileText,
  Settings,
  BrainCircuit,
} from "lucide-react";
import { cn } from "@/utils/cn";

/** 侧边栏菜单项 */
const menuItems = [
  { path: "/", label: "首页", icon: LayoutDashboard },
  { path: "/research", label: "研究", icon: FlaskConical },
  { path: "/reports", label: "报告", icon: FileText },
  { path: "/settings", label: "设置", icon: Settings },
];

/** 侧边栏组件 */
export function Sidebar() {
  return (
    <aside className="hidden w-64 border-r bg-sidebar md:block">
      <div className="flex h-full flex-col">
        {/* Logo */}
        <div className="flex h-16 items-center gap-2 border-b px-6">
          <BrainCircuit className="h-6 w-6 text-primary" />
          <span className="text-lg font-semibold">AI Research OS</span>
        </div>

        {/* 导航菜单 */}
        <nav className="flex-1 space-y-1 p-4">
          {menuItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === "/"}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-sidebar-accent text-sidebar-primary"
                    : "text-sidebar-foreground hover:bg-sidebar-accent"
                )
              }
            >
              <item.icon className="h-5 w-5" />
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* 底部信息 */}
        <div className="border-t p-4">
          <p className="text-xs text-muted-foreground">
            AI Research OS v0.1.0
          </p>
        </div>
      </div>
    </aside>
  );
}
