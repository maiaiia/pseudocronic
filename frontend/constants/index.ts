export const notebookStyle = (scrollPosition: number): React.CSSProperties => {
  const lineHeight = 25.6;
  const lineThickness = 1;
  const offset = scrollPosition % lineHeight;

  return {
    backgroundImage: `repeating-linear-gradient(
      to bottom,
      rgba(0, 0, 0, 0.25) 0px,
      rgba(0, 0, 0, 0.25) ${lineThickness}px,
      transparent ${lineThickness}px,
      transparent ${lineHeight}px
    )`,
    backgroundSize: `100% ${lineHeight}px`,
    backgroundRepeat: "repeat",
    backgroundColor: "#fffefb",
    lineHeight: "1.6",
    paddingLeft: "16px",
    paddingTop: "2px",
    backgroundPositionY: `-${offset}px`,
  };
};

export const postItStyle = (rotate: boolean): string => {
  return `lg:col-span-6 bg-white rounded-none border-4 
  border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] p-6 transform ${
    rotate ? "-rotate-1" : "rotate-1"
  }`;
};

export const textAreaPostItStyle =
  "w-full h-96 resize-none font-mono text-base border-4 border-black rounded-none shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] focus:shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] focus:translate-x-[-2px] focus:translate-y-[-2px] transition-all focus:outline-none";

export const neobrutalistButton = (pixels: number): string =>
  `border-4 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] active:shadow-[0px_0px_0px_0px_rgba(0,0,0,1)] active:translate-x-[${pixels}px] active:translate-y-[${pixels}px] transition-all cursor-pointer`;
