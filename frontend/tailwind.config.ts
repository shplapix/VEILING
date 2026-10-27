import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "acid-lime": "#D2F824",
        "electric-blue": "#0052FF",
        "carbon-pitch": "#111112",
        "gallery-canvas": "#F4F5F8",
        "pure-white": "#FFFFFF",
        "hairline-border": "#E5E7EB",
        "muted-steel": "#71717A",
      },
      fontFamily: {
        sans: ["'Plus Jakarta Sans'", "-apple-system", "sans-serif"],
        mono: ["'JetBrains Mono'", "ui-monospace", "monospace"],
      },
      letterSpacing: {
        wordmark: "0.35em",
        hero: "-0.035em",
        kicker: "0.12em",
      },
      borderRadius: {
        none: "0px",
      },
    },
  },
  plugins: [],
};

export default config;
