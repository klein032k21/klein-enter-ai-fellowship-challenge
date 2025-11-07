/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#000000',
        foreground: '#FFFFFF',
        primary: {
          DEFAULT: '#ffae35',
          foreground: '#000000',
        },
        card: {
          DEFAULT: '#0a0a0a',
          foreground: '#FFFFFF',
        },
        border: '#262626',
        muted: {
          DEFAULT: '#171717',
          foreground: '#a3a3a3',
        },
      },
    },
  },
  plugins: [],
}
