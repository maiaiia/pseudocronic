import { create } from "zustand";
import axios from "axios";
import toast from "react-hot-toast";
import { useWSStore } from "./ws";

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

  executionSteps: ExecutionStep[];
  currentStepIndex: number;
  isExecuting: boolean;
  executeStepByStep: () => Promise<void>;
  setCurrentStep: (index: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  resetExecution: () => void;

  canFix: boolean;
  canExecute: boolean;
  setCanFix: (v: boolean) => void;
  setCanExecute: (v: boolean) => void;

  clearFixInfo: () => void;

  problemStatement: string;
  setProblemStatement: (text: string) => void;
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
  json_execution: string; // JSON string from backend
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
      set({
        cppCode: response.data.cpp_code,
        canExecute: true,
        canFix: true,
        hasErrors: false,
      });
    } catch (error: any) {
      toast.error("You pseudocode has errors");
      set({
        hasErrors: true,
        canFix: true,
        canExecute: false,
      });
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
      toast.error(
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
    set({ canFix: false });
    try {
      const res = await axios.post<CorrectionResponse>(
        "http://localhost:8000/api/v1/correction",
        {
          code: pseudocode,
        }
      );
      const data = res.data;

      if (data.remaining_calls !== undefined) {
        toast.success(`Fixes remaining this hour: ${data.remaining_calls}`, {
          icon: "⚠️",
        });
      }

      if (data.has_errors) {
        set({
          hasErrors: true,
          pseudocode: data.corrected_code,
          errors: data.errors_found,
          explanation: data.explanation,
          canFix: false,
        });
        toast.error("Errors found in pseudocode.");
      } else {
        set({ hasErrors: false });
        toast.success("No syntax errors found.");
      }
    } catch (err: any) {
      console.error(err);
      if (err.response?.status === 429) {
        toast.error(err.response.data.detail);
      } else {
        toast.error("Error checking pseudocode.");
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
        toast.error(error.detail);
        return;
      }

      if (!response.ok) throw new Error("OCR upload failed");
      const data: OCRResponse = await response.json();
      set({ pseudocode: data.extracted_text });

      if (data.remaining_calls !== undefined) {
        toast.success(
          `Image uploaded successfully!\nUploads remaining this hour: ${data.remaining_calls}`
        );
      }
    } catch (err) {
      console.error("OCR error:", err);
      toast.error("Failed to extract pseudocode from image");
    } finally {
      set({ isOcrLoading: false });
    }
  },

  executionSteps: [],
  currentStepIndex: 0,
  isExecuting: false,

  executeStepByStep: async () => {
    const { pseudocode } = get();
    if (!pseudocode.trim()) {
      toast.error("Please enter some pseudocode first!", { icon: "⚠️" });
      return;
    }

    set({ isExecuting: true, canExecute: false });

    try {
      console.log("Sending pseudocode");
      const response = await axios.post<StepByStepResponse>(
        "http://localhost:8000/sbs",
        { pseudocode }
      );
      console.log("Response received");

      const steps: ExecutionStep[] =
        typeof response.data.json_execution === "string"
          ? JSON.parse(response.data.json_execution)
          : response.data.json_execution;

      set({
        executionSteps: steps,
        currentStepIndex: 0,
        isExecuting: false,
      });

      // Broadcast steps to spectators
      const wsStore = useWSStore.getState();
      if (wsStore.isOwner) {
        wsStore.sendUpdate({ executionSteps: steps, currentStepIndex: 0 });
      }
    } catch (error: any) {
      console.error("Step-by-step execution error:", error);
      const errorMsg =
        error.response?.data?.detail || error.message || "Unknown error";
      toast.error(`Error executing step-by-step:\n${errorMsg}`);
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

  canFix: false,
  canExecute: false,
  setCanFix: (v) => set({ canFix: v }),
  setCanExecute: (v) => set({ canExecute: v }),

  clearFixInfo: () => set({ hasErrors: false, errors: [], explanation: "" }),

  problemStatement: "",
  setProblemStatement: (stmt: string) => set({ problemStatement: stmt }),
}));
