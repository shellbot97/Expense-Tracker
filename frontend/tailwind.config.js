/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#2563EB',
          hover: '#1D4ED8',
          light: '#EFF6FF',
          subtle: '#DBEAFE',
        },
        secondary: {
          DEFAULT: '#1E1B4B',
          hover: '#312E81',
          light: '#EEF2FF',
        },
        accent: {
          DEFAULT: '#7C3AED',
          light: '#F5F3FF',
        },
        neutral: {
          950: '#0A0A0A',
          800: '#262626',
          600: '#525252',
          400: '#A3A3A3',
          200: '#E5E5E5',
          100: '#F5F5F5',
          50: '#FAFAFA',
        },
        success: {
          DEFAULT: '#15803D',
          light: '#F0FDF4',
        },
        warning: {
          DEFAULT: '#C2410C',
          light: '#FFF7ED',
        },
        error: {
          DEFAULT: '#DC2626',
          light: '#FEF2F2',
        },
        info: {
          DEFAULT: '#0369A1',
          light: '#F0F9FF',
        },
      },
      fontFamily: {
        headline: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        body: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'SF Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
