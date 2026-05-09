import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#172033",
        graphite: "#3f4654",
        muted: "#6b7280",
        line: "#d9dee7",
        cloud: "#f4f6f8",
        paper: "#fbfbf8",
        forest: "#0f6b4f",
        teal: "#0f766e",
        gold: "#b7791f",
        brick: "#b53d2d",
        sky: "#2563eb"
      },
      boxShadow: {
        panel: "0 18px 42px rgba(23, 32, 51, 0.09)",
        crisp: "0 1px 0 rgba(23, 32, 51, 0.08)"
      }
    }
  },
  plugins: []
};

export default config;
