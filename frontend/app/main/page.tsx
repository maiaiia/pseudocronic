"use client";

import { ArrowRight, Code2, Wrench, PlayCircle } from "lucide-react";
import { useAppStore } from "@/store/app";
import PseudocodePostIt from "@/components/PseudocodePostIt";
import RegularPostIt from "@/components/RegularPostIt";
import ActionButton from "@/components/ActionButton";

const MainPage: React.FC = () => {
  const {
    isSwapped,
    toggleSwap,
    pseudocodeToCpp,
    cppToPseudocode,
    hasErrors,
    errors,
    explanation,
    checkAndFixCode,
  } = useAppStore();

  return (
    <div className="min-h-screen bg-yellow-400">
      <div className="max-w-7xl mx-auto p-8 space-y-8">
        {/* Textareas */}
        <div className="grid grid-cols-1 lg:grid-cols-13 gap-8">
          {isSwapped ? (
            <>
              <RegularPostIt />
              <div className="hidden lg:flex items-center justify-center lg:col-span-1">
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
              <div className="hidden lg:flex items-center justify-center lg:col-span-1">
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

        {/* Buttons */}
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
            color="bg-red-500"
            onClick={checkAndFixCode}
          />
          <ActionButton
            label="EXECUTE STEP BY STEP"
            icon={<PlayCircle className="h-6 w-6" />}
            color="bg-pink-300"
          />
        </div>

        {/* Error + Explanation cards */}
        {hasErrors && (
          <div className="grid gap-4 mt-6">
            {errors.map((err, i) => (
              <div
                key={i}
                className="bg-red-500 text-black font-semibold shadow-[4px_4px_0px_black] rounded-2xl p-4 border-4 border-black"
              >
                ⚠️ {err}
              </div>
            ))}
            <div className="bg-blue-300 text-black shadow-[4px_4px_0px_black] rounded-2xl p-4 border-4 border-black">
              ℹ️ {explanation}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MainPage;
