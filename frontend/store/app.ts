import { create } from "zustand";
import axios from "axios";

interface AppState {
  pseudocode: string;
  cppCode: string;
  setPseudocode: (code: string) => void;
  setCppCode: (code: string) => void;
  pseudocodeToCpp: () => Promise<void>;
  cppToPseudocode: () => Promise<void>;
  isSwapped: boolean;
  toggleSwap: () => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  pseudocode: "",
  cppCode: "",
  setCppCode: (code) => set({ cppCode: code }),
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

  cppToPseudocode: async () => {
    const { cppCode } = get();
    try {
      const response = await axios.post("http://127.0.0.1:8000/ctp", {
        cpp_code: cppCode,
      });
      set({ pseudocode: response.data.pseudocode });
    } catch (error: any) {
      console.error(error);
      alert(
        "There is a mistake in the cpp code. Please check it and try again."
      );
    }
  },

  isSwapped: false,
  toggleSwap: () => set((state) => ({ isSwapped: !state.isSwapped })),
}));
