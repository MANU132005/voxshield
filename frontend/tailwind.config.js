/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#090d16',
        surface: '#111827',
        'surface-hover': '#1f2937',
        border: '#1f293d',
        primary: {
          50: '#f0f9ff',
          500: '#0284c7',
          600: '#0284c7',
          700: '#0369a1',
        },
        shield: {
          safe: '#10b981',
          suspicious: '#f59e0b',
          danger: '#ef4444',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
