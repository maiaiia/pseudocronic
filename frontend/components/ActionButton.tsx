"use client";

import React, { ReactNode } from "react";
import { neobrutalistButton } from "@/constants";

interface ActionButtonProps {
  label?: string;
  icon: ReactNode;
  color: string;
  pixels?: number;
  onClick?: () => void;
  className?: string;
}

const ActionButton: React.FC<ActionButtonProps> = ({
  label,
  icon,
  color,
  pixels = 6,
  onClick,
  className = "",
}) => {
  return (
    <button
      type="button" // important to prevent form submission / GET requests
      className={`${className} ${neobrutalistButton(
        pixels
      )} ${color} px-4 py-4 text-lg rounded-none flex items-center justify-center font-bold`}
      onClick={onClick}
    >
      {icon}
      {label && <span className="ml-2">{label}</span>}
    </button>
  );
};

export default ActionButton;
