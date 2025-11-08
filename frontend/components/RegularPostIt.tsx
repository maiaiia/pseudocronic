"use client";

import { postItStyle, textAreaPostItStyle } from "@/constants";
import React from "react";
import { useAppStore } from "@/store/app";

const RegularPostIt = () => {
  const cppCode = useAppStore((state) => state.cppCode);

  return (
    <div className={postItStyle(false)}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-3xl font-black text-black">C++</h2>
      </div>
      <textarea
        className={`${textAreaPostItStyle} p-4`}
        placeholder="Your C++ code will appear here..."
        value={cppCode}
      />
    </div>
  );
};

export default RegularPostIt;
