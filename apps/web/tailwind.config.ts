import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#162033",
        slate: "#5a6880",
        edge: "#d7deea",
        mist: "#f4f7fb",
        canvas: "#eef3f8",
        signal: "#0f766e",
        alert: "#b45309",
        accent: "#1d4ed8"
      },
      boxShadow: {
        panel: "0 18px 40px rgba(22, 32, 51, 0.08)"
      },
      backgroundImage: {
        "dashboard-grid":
          "radial-gradient(circle at top left, rgba(15, 118, 110, 0.12), transparent 28%), radial-gradient(circle at top right, rgba(29, 78, 216, 0.08), transparent 24%)"
      }
    }
  },
  plugins: []
};

export default config;

