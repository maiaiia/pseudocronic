import { create } from "zustand";

interface WSState {
  ws: WebSocket | null;
  roomId: string;
  isOwner: boolean;
  connectToRoom: (roomId: string, owner: boolean) => void;
  sendUpdate: (data: any) => void;
  lastMessage: any;
}

export const useWSStore = create<WSState>((set, get) => ({
  ws: null,
  roomId: "",
  isOwner: false,
  lastMessage: null,

  connectToRoom: (roomId, owner) => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${roomId}`);
    ws.onmessage = (event) => {
      set({ lastMessage: JSON.parse(event.data) });
    };
    set({ ws, roomId, isOwner: owner });
  },

  sendUpdate: (data) => {
    const { ws, isOwner } = get();
    if (ws && isOwner) {
      ws.send(JSON.stringify(data));
    }
  },
}));
