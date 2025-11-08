import { create } from "zustand";

interface AppState {
  isSwapped: boolean;
  toggleSwap: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  isSwapped: false,
  toggleSwap: () => set((state) => ({ isSwapped: !state.isSwapped })),
}));
