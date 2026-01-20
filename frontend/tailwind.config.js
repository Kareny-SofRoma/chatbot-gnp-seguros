/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#312b66',
          light: '#4a4380',
          dark: '#1f1a45',
        },
        secondary: {
          DEFAULT: '#67528a',
          light: '#8672a6',
          dark: '#4d3a66',
        },
        accent: {
          DEFAULT: '#2b5c96',
          light: '#3d7bb5',
          dark: '#1d4070',
        },
        success: {
          DEFAULT: '#518a7c',
          light: '#6ba596',
          dark: '#3d6860',
        },
        background: {
          DEFAULT: '#e8e8eb',
          light: '#f5f5f7',
          dark: '#d1d1d6',
        },
      },
    },
  },
  plugins: [],
}
