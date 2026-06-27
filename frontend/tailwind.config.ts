import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}", "./lib/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#172033",
        mist: "#f6f8fb",
        line: "#d9e0ea",
        teal: "#0f766e",
        saffron: "#d97706",
        plum: "#7c3aed"
      },
      boxShadow: {
        soft: "0 12px 35px rgba(23, 32, 51, 0.08)"
      }
    }
  },
  plugins: []
};

export default config;
