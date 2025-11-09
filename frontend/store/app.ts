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

  hasErrors: boolean;
  errors: string[];
  explanation: string;
  checkAndFixCode: () => Promise<void>;

  isOcrLoading: boolean;
  ocrUploadImage: (file: File) => Promise<void>;
}

interface CorrectionResponse {
  corrected_code: string;
  has_errors: boolean;
  errors_found: string[];
  explanation: string;
  remaining_calls?: number;
}
interface OCRResponse {
  extracted_text: string;
  remaining_calls?: number;

}

export const useAppStore = create<AppState>((set, get) => ({
  pseudocode: "",
  cppCode: "",
  setCppCode: (code) => set({ cppCode: code }),
  setPseudocode: (code) => set({ pseudocode: code }),

  pseudocodeToCpp: async () => {
    const { pseudocode } = get();
    try {
      const response = await axios.post("http://localhost:8000/ptc", {
        pseudocode,
      });
      set({ cppCode: response.data.cpp_code });
    } catch (error: any) {
      set({ hasErrors: true });
      console.error(error);
      alert(
        "There is a mistake in the pseudocode. Please check it and try again."
      );
    }
  },

  cppToPseudocode: async () => {
    const { cppCode } = get();
    try {
      const response = await axios.post("http://localhost:8000/ctp", {
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

  hasErrors: false,
  errors: [],
  explanation: "",

  checkAndFixCode: async () => {
    const { pseudocode } = get();
    try {
      const res = await axios.post<CorrectionResponse>(
        "http://localhost:8000/api/v1/correction",
        { code: pseudocode }
      );
      const data = res.data;
      if (data.remaining_calls !== undefined){
        alert(`Fixes remaining this hour: ${data.remaining_calls}`);
      }
      if (data.has_errors) {
        set({
          hasErrors: true,
          pseudocode: data.corrected_code,
          errors: data.errors_found,
          explanation: data.explanation,
        });
        alert("Errors found in pseudocode. Press Fix My Code to view details.");
      } else {
        set({ hasErrors: false });
        alert("No syntax errors found.");
      }
    } catch (err) {
      console.error(err);
      // @ts-ignore
      if (err.response?.status === 429) {
        // @ts-ignore
        alert(err.response.data.detail)
      } else {
        alert("Error checking pseudocode.");
      }
    }
  },

  isOcrLoading: false,
  ocrUploadImage: async (file: File) => {
    set({ isOcrLoading: true });
    try {
      const formData = new FormData();
      formData.append("image", file);
      const response = await fetch("http://localhost:8000/api/v1/ocr", {
        method: "POST",
        body: formData,
      });

      if (response.status === 429) {
        const error = await response.json();
        alert(error.detail);
        return;
      }

      if (!response.ok) throw new Error("OCR upload failed");
      const data = await response.json();
      set({ pseudocode: data.extracted_text });

      if (data.remaining_calls !== undefined) {
        alert(`Image uploaded successfully!\nUploads remaining this hour: ${data.remaining_calls}`);
      }

      console.log("OCR result:", data);
    } catch (err) {
      console.error("OCR error:", err);
      alert("Failed to extract pseudocode from image");
    } finally {
      set({ isOcrLoading: false });
    }
  },
}));
