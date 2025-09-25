import type { Config } from "tailwindcss"

export default {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
    "./pages/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        bg: "#0b0f14",
        fg: "#e6f2ff",
        primary: "#5ee7ff",
        accent: "#7c3aed",
        muted: "#0f1620",
        card: "#0c1218",
        border: "rgba(255,255,255,0.08)",
        gray: {
          750: "#374151",
          850: "#1f2937",
          950: "#111827"
        }
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "Segoe UI", "Roboto", "Helvetica", "Arial", "Apple Color Emoji", "Segoe UI Emoji"]
      },
      boxShadow: {
        glow: "0 0 60px rgba(94, 231, 255, 0.25)",
        card: "0 20px 60px rgba(0,0,0,0.45)"
      },
      backgroundImage: {
        "grad-hero": "radial-gradient(1200px 600px at 10% -10%, rgba(124,58,237,0.25), transparent), radial-gradient(900px 500px at 90% -10%, rgba(94,231,255,0.18), transparent), linear-gradient(180deg, #091017 0%, #0b0f14 60%)"
      }
    }
  },
  plugins: []
} satisfies Config
