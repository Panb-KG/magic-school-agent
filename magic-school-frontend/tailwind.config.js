/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        magic: {
          primary: '#7C3AED',    // 紫色
          primaryDark: '#5B21B6', // 深紫色
          secondary: '#F59E0B',  // 金色
          accent: '#10B981',     // 绿色
          danger: '#EF4444',     // 红色
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
