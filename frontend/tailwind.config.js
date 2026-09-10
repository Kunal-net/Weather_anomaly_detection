/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        normal: "#10b981",
        watch: "#f59e0b",
        high: "#f97316",
        critical: "#ef4444",
        command: {
          900: "#0b0f19",
          800: "#0f172a",
          700: "#1e293b",
          600: "#334155",
        },
      },
    },
  },
  plugins: [],
}
