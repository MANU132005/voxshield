/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: '#2F4156',
          50: '#f4f6f8',
          100: '#e5eaef',
          200: '#ccd6e0',
          300: '#a7bacc',
          400: '#7c99b3',
          500: '#5c7d9c',
          600: '#476582',
          700: '#3a516b',
          800: '#2F4156', // Primary Navy
          900: '#263546',
          950: '#19232f',
        },
        teal: {
          DEFAULT: '#567C8D',
          50: '#f3f7f9',
          100: '#e4edf1',
          200: '#cbdee5',
          300: '#a6c6d3',
          400: '#7ba7bb',
          500: '#567C8D', // Primary Teal
          600: '#476878',
          700: '#3c5563',
          800: '#344752',
          900: '#2f3d46',
          950: '#1c262c',
        },
        skyblue: {
          DEFAULT: '#C8D9E6',
          50: '#f7fafc',
          100: '#eff4f9',
          200: '#e1ebf3',
          300: '#C8D9E6', // Primary Sky Blue
          400: '#a8c2d7',
          500: '#8baac5',
        },
        beige: {
          DEFAULT: '#F5F2EB',
          50: '#fdfcfb',
          100: '#FAF8F5',
          200: '#F5F2EB', // Primary Beige Background
          300: '#ede7da',
          400: '#ded4c0',
          500: '#cbbda3',
        },
        background: '#F5F2EB',
        surface: '#FFFFFF',
        'surface-subtle': '#EEF3F8',
        'surface-hover': '#F7FAF9',
        border: '#C8D9E6',
        primary: {
          50: '#F5F2EB',
          100: '#C8D9E6',
          500: '#567C8D',
          600: '#2F4156',
          700: '#19232f',
        },
        shield: {
          safe: '#15803d',
          suspicious: '#b45309',
          danger: '#b91c1c',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 2px 10px -2px rgba(47, 65, 86, 0.06), 0 1px 4px -1px rgba(47, 65, 86, 0.04)',
        'card-hover': '0 8px 20px -4px rgba(47, 65, 86, 0.1), 0 3px 8px -2px rgba(47, 65, 86, 0.06)',
        'elevated': '0 12px 28px -6px rgba(47, 65, 86, 0.12), 0 4px 12px -2px rgba(47, 65, 86, 0.08)',
      }
    },
  },
  plugins: [],
}
