"use client";

import { useState, UIEvent, useEffect } from "react";
import { notebookStyle, postItStyle, textAreaPostItStyle } from "@/constants";
import { Camera } from "lucide-react";
import ActionButton from "@/components/ActionButton";
import { useAppStore } from "@/store/app";
import OCRModal from "./ui/OCRModal";
import { useWSStore } from "@/store/ws";

const PseudocodePostIt: React.FC = () => {
  const [scrollPosition, setScrollPosition] = useState(0);
  const [isOcrOpen, setIsOcrOpen] = useState(false);
  const { isSwapped } = useAppStore();
  const { sendUpdate, lastMessage, isOwner } = useWSStore();

  const pseudocode = useAppStore((state) => state.pseudocode);
  const setPseudocode = useAppStore((state) => state.setPseudocode);

  const handleScroll = (e: UIEvent<HTMLTextAreaElement>) =>
    setScrollPosition(e.currentTarget.scrollTop);

  const handleCameraClick = () => {
    setIsOcrOpen(true);
  };

  return (
    <div className={postItStyle(true)}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-3xl font-black text-black">PSEUDOCODE</h2>
      </div>
      <div className="relative">
        <textarea
          style={notebookStyle(scrollPosition)}
          onScroll={handleScroll}
          className={textAreaPostItStyle}
          placeholder="Write or paste your pseudocode here..."
          value={pseudocode}
          onChange={(e) => setPseudocode(e.target.value)}
        />{" "}
        {!isSwapped && (
          <div className="absolute bottom-4 right-4">
            <ActionButton
              icon={<Camera className="h-5 w-5 text-black" />}
              color="bg-pink-400"
              pixels={4}
              onClick={handleCameraClick}
            />
          </div>
        )}
      </div>
      <OCRModal isOpen={isOcrOpen} onClose={() => setIsOcrOpen(false)} />
    </div>
  );
};

export default PseudocodePostIt;
