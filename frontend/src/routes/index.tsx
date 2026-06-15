import { createBrowserRouter } from "react-router-dom";
import { AppLayout } from "@/components/layout/AppLayout";
import { DashboardPage } from "@/pages/dashboard/DashboardPage";
import { ResearchPage } from "@/pages/research/ResearchPage";
import { ReportListPage } from "@/pages/reports/ReportListPage";
import { SettingsPage } from "@/pages/settings/SettingsPage";

/** 路由配置 */
export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      {
        index: true,
        element: <DashboardPage />,
      },
      {
        path: "research",
        element: <ResearchPage />,
      },
      {
        path: "reports",
        element: <ReportListPage />,
      },
      {
        path: "settings",
        element: <SettingsPage />,
      },
    ],
  },
]);
