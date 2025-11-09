"use client";

import React, { useState } from "react";
import { X } from "lucide-react";
import { useAppStore } from "@/store/app";

interface OCRModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const OCRModal: React.FC<OCRModalProps> = ({ isOpen, onClose }) => {
  const [file, setFile] = useState<File | null>(null);
  const ocrUploadImage = useAppStore((state) => state.ocrUploadImage);
  const isLoading = useAppStore((state) => state.isOcrLoading);

  if (!isOpen) return null;

  const handleUpload = async () => {
    if (!file) return alert("Select an image first!");
    await ocrUploadImage(file);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-yellow-400 border-4 border-black shadow-[6px_6px_0px_black] rounded-2xl p-6 w-[400px] flex flex-col gap-4">
        <div className="flex justify-between items-center">
          <h2 className="font-black text-black text-lg">
            Upload Pseudocode Image
          </h2>
          <button onClick={onClose}>
            <X className="h-6 w-6 text-black" />
          </button>
        </div>

        <input
          type="file"
          accept="image/*"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="border-4 border-black rounded-xl p-2 bg-white"
        />

        <button
          onClick={handleUpload}
          className="bg-green-400 text-black font-bold border-4 border-black shadow-[4px_4px_0px_black] p-3 rounded-xl disabled:bg-gray-400"
          disabled={isLoading}
        >
          {isLoading ? "Processing..." : "Extract Pseudocode"}
        </button>
      </div>
    </div>
  );
};

export default OCRModal;
