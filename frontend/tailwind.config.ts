import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: 'class',
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary — 어스/포레스트 계열
        primary: {
          100: "#EAE1BD",
          200: "#D6E8C8",
          300: "#9FBF7F",
          400: "#5E3B1D",
          500: "#18341D",
        },
        // Neutral — 어스/세이지 계열
        warm: {
          100: "#EAE1BD",
          200: "#D6E8C8",
          300: "#9FBF7F",
          600: "#8E8051",
          900: "#011B12",
        },
        // Surface — 말풍선/카드
        surface: {
          ai:     "#D6E8C8",
          user:   "#9FBF7F",
          card:   "#F5F0E0",
          header: "#EAE1BD",
        },
        // Semantic
        status: {
          error:   "#D94F4F",
          success: "#4A9B6F",
          warning: "#E8913A",
          dday:    "#F94224",
        },
      },
      fontFamily: {
        sans: ["Pretendard", "sans-serif"],
      },
    },
  },
  plugins: [],
};
export default config;
