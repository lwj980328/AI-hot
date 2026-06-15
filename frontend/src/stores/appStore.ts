import { create } from "zustand";

/** 应用状态 */
interface AppState {
  /** 侧边栏是否展开（移动端） */
  sidebarOpen: boolean;
  /** 当前选中的任务 ID */
  selectedTaskId: string | null;
  /** 当前选中的报告 ID */
  selectedReportId: string | null;
}

/** 应用 Actions */
interface AppActions {
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setSelectedTaskId: (id: string | null) => void;
  setSelectedReportId: (id: string | null) => void;
}

/** 应用 Store */
export const useAppStore = create<AppState & AppActions>((set) => ({
  sidebarOpen: false,
  selectedTaskId: null,
  selectedReportId: null,

  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setSelectedTaskId: (id) => set({ selectedTaskId: id }),
  setSelectedReportId: (id) => set({ selectedReportId: id }),
}));
