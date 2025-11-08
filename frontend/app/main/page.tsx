"use client";

import { useState } from "react";
import { ArrowRight, Code2, Wrench, Info, PlayCircle } from "lucide-react";
import PseudocodePostIt from "@/components/PseudocodePostIt";
import RegularPostIt from "@/components/RegularPostIt";
import ActionButton from "@/components/ActionButton";
import { useAppStore } from "@/store/app";

const MainPage: React.FC = () => {
  const { isSwapped, toggleSwap, pseudocodeToCpp, cppToPseudocode } =
    useAppStore();

  return (
    <div className="min-h-screen bg-yellow-400">
      <div className="max-w-7xl mx-auto p-8">
        <div className="grid grid-cols-1 lg:grid-cols-13 gap-8 mb-8">
          {isSwapped ? (
            <>
              <RegularPostIt />
              <div className="hidden lg:flex flex-col items-center justify-center lg:col-span-1">
                <ActionButton
                  icon={
                    <ArrowRight
                      className="h-8 w-8 text-black"
                      strokeWidth={3}
                    />
                  }
                  color="bg-orange-400"
                  pixels={6}
                  onClick={toggleSwap}
                  label=""
                  className="rotate-8 p-4"
                />
              </div>
              <PseudocodePostIt />
            </>
          ) : (
            <>
              <PseudocodePostIt />
              <div className="hidden lg:flex flex-col items-center justify-center lg:col-span-1">
                <ActionButton
                  icon={
                    <ArrowRight
                      className="h-8 w-8 text-black"
                      strokeWidth={3}
                    />
                  }
                  color="bg-lime-400"
                  pixels={6}
                  onClick={toggleSwap}
                  label=""
                  className="-rotate-8 p-4"
                />
              </div>
              <RegularPostIt />
            </>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap justify-center gap-6">
          <ActionButton
            label="TRANSLATE"
            icon={<Code2 className="h-6 w-6" />}
            color="bg-blue-400"
            onClick={isSwapped ? cppToPseudocode : pseudocodeToCpp}
          />
          <ActionButton
            label="FIX MY CODE"
            icon={<Wrench className="h-6 w-6" />}
            color="bg-green-400"
          />
          <ActionButton
            label="EXPLAIN ISSUES"
            icon={<Info className="h-6 w-6" />}
            color="bg-amber-400"
          />
          <ActionButton
            label="EXECUTE STEP BY STEP"
            icon={<PlayCircle className="h-6 w-6" />}
            color="bg-purple-400"
          />
        </div>
      </div>
    </div>
  );
};

export default MainPage;
