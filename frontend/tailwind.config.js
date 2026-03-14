/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        approve: '#22c55e',
        investigate: '#f59e0b',
        escalate: '#ef4444',
        pine: '#1a56db',
      },
    },
  },
  plugins: [],
}
