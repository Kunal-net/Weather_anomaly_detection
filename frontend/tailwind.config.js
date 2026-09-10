/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Space Grotesk', 'Geist', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        carbon: {
          950: '#060913',
          900: '#0b0f19',
          850: '#0f172a',
          800: '#141c2c',
          700: '#1e293b',
        },
        border: '#1e293b',
        normal: '#10b981',
        watch: '#f59e0b',
        high: '#f97316',
        critical: '#ef4444',
        telemetry: '#06b6d4',
        severity: {
          normal: '#10b981',
          watch: '#f59e0b',
          high: '#f97316',
          critical: '#ef4444',
        },
        aurora: {
          indigo: '#6366f1',
          cyan: '#06b6d4',
          violet: '#8b5cf6',
          crimson: '#ef4444',
        },
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px) rotate(0deg)' },
          '50%': { transform: 'translateY(-8px) rotate(1.5deg)' },
        },
        aurora: {
          '0%, 100%': { opacity: '0.45', transform: 'scale(1) translate(0px, 0px)' },
          '33%': { opacity: '0.65', transform: 'scale(1.15) translate(30px, -20px)' },
          '66%': { opacity: '0.5', transform: 'scale(0.9) translate(-20px, 25px)' },
        },
        'radar-sonar': {
          '0%': { transform: 'scale(0.9)', opacity: '0.8' },
          '70%': { transform: 'scale(2.2)', opacity: '0.1' },
          '100%': { transform: 'scale(2.6)', opacity: '0' },
        },
        'radar-sweep': {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        'pulse-glow': {
          '0%, 100%': { opacity: '1', filter: 'drop-shadow(0 0 12px currentColor)' },
          '50%': { opacity: '0.6', filter: 'drop-shadow(0 0 4px currentColor)' },
        },
        'heat-wave': {
          '0%, 100%': { transform: 'scaleY(1) skewX(0deg)' },
          '50%': { transform: 'scaleY(1.15) skewX(4deg)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      animation: {
        float: 'float 5s ease-in-out infinite',
        'float-slow': 'float 8s ease-in-out infinite',
        aurora: 'aurora 14s ease-in-out infinite',
        'radar-sonar': 'radar-sonar 2.4s cubic-bezier(0, 0.2, 0.8, 1) infinite',
        'radar-sweep': 'radar-sweep 4s linear infinite',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'heat-wave': 'heat-wave 2s ease-in-out infinite',
        shimmer: 'shimmer 4s linear infinite',
        'spin-slow': 'spin 20s linear infinite',
      },
    },
  },
  plugins: [],
}

