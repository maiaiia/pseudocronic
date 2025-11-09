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
    executeStepByStep,
    executionSteps,
    currentStepIndex,
    nextStep,
    prevStep,
    resetExecution,
    canFix,
    canExecute,
  } = useAppStore();
  const currentStep = executionSteps[currentStepIndex];
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
            color={!isSwapped && canFix ? "bg-red-500" : "bg-gray-400"}
            onClick={!isSwapped && canFix ? checkAndFixCode : undefined}
          />
          <ActionButton
            label="EXECUTE STEP BY STEP"
            icon={<PlayCircle className="h-6 w-6" />}
            color={!isSwapped && canExecute ? "bg-pink-300" : "bg-gray-400"}
            onClick={!isSwapped && canExecute ? executeStepByStep : undefined}
          />
        </div>

        {/* Error + Explanation cards */}
        {hasErrors && (
          <div className="grid gap-4 mt-6 relative">
            <button
              onClick={useAppStore.getState().clearFixInfo}
              className="absolute -top-6 right-0 bg-red-400 border-2 border-black shadow-[2px_2px_0px_black] rounded-lg px-3 py-1 font-bold hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none transition-all"
            >
              ✕
            </button>
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

        {/* Step-by-step execution viewer */}
        {executionSteps.length > 0 && currentStep && (
          <div className="grid gap-4 mt-6">
            {/* Navigation controls */}
            <div className="bg-pink-300 shadow-[4px_4px_0px_black] rounded-2xl p-4 border-4 border-black">
              <div className="flex items-center justify-between mb-4">
                <span className="font-bold text-2xl">
                  Pas {currentStep.step} / {executionSteps.length}
                </span>
                <div className="flex gap-2">
                  <button
                    onClick={resetExecution}
                    className="px-4 py-2 bg-red-400 border-2 border-black shadow-[2px_2px_0px_black] rounded-lg font-bold hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none transition-all"
                  >
                    ✕
                  </button>
                  <button
                    onClick={prevStep}
                    disabled={currentStepIndex === 0}
                    className="px-4 py-2 bg-yellow-400 border-2 border-black shadow-[2px_2px_0px_black] rounded-lg font-bold disabled:opacity-50 disabled:cursor-not-allowed hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none transition-all"
                  >
                    ←
                  </button>
                  <button
                    onClick={nextStep}
                    disabled={currentStepIndex === executionSteps.length - 1}
                    className="px-4 py-2 bg-lime-400 border-2 border-black shadow-[2px_2px_0px_black] rounded-lg font-bold disabled:opacity-50 disabled:cursor-not-allowed hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none transition-all"
                  >
                    →
                  </button>
                </div>
              </div>
              <div className="text-lg font-semibold">
                📍 Linia {currentStep.line} | {currentStep.type}
              </div>
            </div>

            {/* Step description */}
            <div className="bg-blue-300 shadow-[4px_4px_0px_black] rounded-2xl p-4 border-4 border-black">
              <div className="font-bold mb-2">Execuție:</div>
              {currentStep.description}
              {currentStep.value && (
                <div className="mt-2">
                  <span className="font-bold">Valoare:</span>{" "}
                  {currentStep.value}
                </div>
              )}
            </div>

            {/* Variables */}
            {Object.keys(currentStep.variables).length > 0 && (
              <div className="bg-green-300 shadow-[4px_4px_0px_black] rounded-2xl p-4 border-4 border-black">
                <div className="font-bold mb-2">Variabile:</div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {Object.entries(currentStep.variables).map(([key, value]) => (
                    <div
                      key={key}
                      className="bg-white border-2 border-black rounded-lg p-2 font-mono"
                    >
                      <span className="font-bold">{key}:</span> {String(value)}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Output */}
            {currentStep.output && (
              <div className="bg-purple-300 shadow-[4px_4px_0px_black] rounded-2xl p-4 border-4 border-black">
                <div className="font-bold mb-2">Output:</div>
                <pre className="bg-black text-green-400 p-3 rounded-lg font-mono text-sm overflow-auto">
                  {currentStep.output}
                </pre>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MainPage;
