"use client";

import { postItStyle, textAreaPostItStyle } from "@/constants";
import React from "react";

const RegularPostIt = () => {
  return (
    <div className={postItStyle(false)}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-3xl font-black text-black">C++</h2>
      </div>
      <textarea
        className={`${textAreaPostItStyle} p-4`}
        placeholder="Your C++ code will appear here..."
      />
    </div>
  );
};

export default RegularPostIt;
