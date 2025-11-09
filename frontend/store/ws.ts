import { create } from "zustand";
import { useAppStore } from "./app";

interface WSState {
  ws: WebSocket | null;
  roomId: string;
  isOwner: boolean;
  connectToRoom: (roomId: string, owner: boolean) => void;
  sendUpdate: (data: Partial<AppStateSnapshot>) => void;
  lastMessage: Partial<AppStateSnapshot> | null;
  applyUpdate: (data: Partial<AppStateSnapshot>) => void;
}

interface AppStateSnapshot {
  pseudocode: string;
  cppCode: string;
  hasErrors: boolean;
  errors: string[];
  explanation: string;
  executionSteps: any;
  currentStepIndex: number;
  isSwapped: boolean;
}

export const useWSStore = create<WSState>((set, get) => ({
  ws: null,
  roomId: "",
  isOwner: false,
  lastMessage: null,

  connectToRoom: (roomId, owner) => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${roomId}`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (!get().isOwner) {
        useAppStore.setState((prev) => ({
          pseudocode: data.pseudocode ?? prev.pseudocode,
          cppCode: data.cppCode ?? prev.cppCode,
          isSwapped: data.isSwapped ?? prev.isSwapped,
          executionSteps: data.executionSteps ?? prev.executionSteps,
          currentStepIndex: data.currentStepIndex ?? prev.currentStepIndex,
          hasErrors: data.hasErrors ?? prev.hasErrors,
          errors: data.errors ?? prev.errors,
          explanation: data.explanation ?? prev.explanation,
        }));
      }
    };

    set({ ws, roomId, isOwner: owner });
  },

  sendUpdate: (data) => {
    const { ws, isOwner } = get();
    if (ws && isOwner) {
      ws.send(JSON.stringify(data));
    }
  },

  applyUpdate: (data) => {
    useAppStore.setState((prev) => ({
      pseudocode: data.pseudocode ?? prev.pseudocode,
      cppCode: data.cppCode ?? prev.cppCode,
      hasErrors: data.hasErrors ?? prev.hasErrors,
      errors: data.errors ?? prev.errors,
      explanation: data.explanation ?? prev.explanation,
      executionSteps: data.executionSteps ?? prev.executionSteps,
      currentStepIndex: data.currentStepIndex ?? prev.currentStepIndex,
      isSwapped: data.isSwapped ?? prev.isSwapped,
    }));
  },
}));
