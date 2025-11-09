import { create } from "zustand";
import axios from "axios";

interface ExecutionStep {
  step: number;
  line: number;
  type: string;
  description: string;
  value: string | null;
  variables: Record<string, any>;
  output: string;
}

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

  // Step-by-step execution
  executionSteps: ExecutionStep[];
  currentStepIndex: number;
  isExecuting: boolean;
  executeStepByStep: () => Promise<void>;
  setCurrentStep: (index: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  resetExecution: () => void;
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

interface StepByStepResponse {
  json_execution: string;
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
      if (data.remaining_calls !== undefined) {
        alert(`Fixes remaining this hour: ${data.remaining_calls}`);
      }
      if (data.has_errors) {
        set({
          hasErrors: true,
          pseudocode: data.corrected_code,
          errors: data.errors_found,
          explanation: data.explanation,
        });
        alert("Errors found in pseudocode.");
      } else {
        set({ hasErrors: false });
        alert("No syntax errors found.");
      }
    } catch (err) {
      console.error(err);
      // @ts-ignore
      if (err.response?.status === 429) {
        // @ts-ignore
        alert(err.response.data.detail);
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
        alert(
          `Image uploaded successfully!\nUploads remaining this hour: ${data.remaining_calls}`
        );
      }

      console.log("OCR result:", data);
    } catch (err) {
      console.error("OCR error:", err);
      alert("Failed to extract pseudocode from image");
    } finally {
      set({ isOcrLoading: false });
    }
  },

  // Step-by-step execution
  executionSteps: [],
  currentStepIndex: 0,
  isExecuting: false,

  executeStepByStep: async () => {
    const { pseudocode } = get();

    if (!pseudocode.trim()) {
      alert("Please enter some pseudocode first!");
      return;
    }

    set({ isExecuting: true });

    try {
      console.log("Sending pseudocode:", pseudocode);

      const response = await axios.post<StepByStepResponse>(
        "http://localhost:8000/sbs",
        { pseudocode }
      );

      console.log("Response received:", response.data);

      const steps: ExecutionStep[] = response.data.json_execution;
      console.log("Parsed steps:", steps);

      set({
        executionSteps: steps,
        currentStepIndex: 0,
        isExecuting: false,
      });
    } catch (error: any) {
      console.error("Step-by-step execution error:", error);
      console.error("Error response:", error.response?.data);
      console.error("Error status:", error.response?.status);

      const errorMsg = error.response?.data?.detail || error.message || "Unknown error";
      alert(`Error executing step-by-step:\n${errorMsg}\n\nCheck console for details.`);
      set({ isExecuting: false });
    }
  },

  setCurrentStep: (index) => set({ currentStepIndex: index }),

  nextStep: () =>
    set((state) => ({
      currentStepIndex: Math.min(
        state.currentStepIndex + 1,
        state.executionSteps.length - 1
      ),
    })),

  prevStep: () =>
    set((state) => ({
      currentStepIndex: Math.max(state.currentStepIndex - 1, 0),
    })),

  resetExecution: () => set({ executionSteps: [], currentStepIndex: 0 }),
}));