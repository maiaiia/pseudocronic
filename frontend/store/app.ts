import { create } from "zustand";
import axios from "axios";

interface AppState {
  pseudocode: string;
  cppCode: string;
  setPseudocode: (code: string) => void;
  pseudocodeToCpp: () => Promise<void>;
  isSwapped: boolean;
  toggleSwap: () => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  pseudocode: "",
  cppCode: "",
  setPseudocode: (code) => set({ pseudocode: code }),

  pseudocodeToCpp: async () => {
    const { pseudocode } = get();
    try {
      const response = await axios.post("http://127.0.0.1:8000/ptc", {
        pseudocode,
      });
      set({ cppCode: response.data.cpp_code });
    } catch (error: any) {
      console.error(error);
      alert(
        "There is a mistake in the pseudocode. Please check it and try again."
      );
    }
  },

  isSwapped: false,
  toggleSwap: () => set((state) => ({ isSwapped: !state.isSwapped })),
}));
