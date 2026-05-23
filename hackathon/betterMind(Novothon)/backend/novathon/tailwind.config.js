/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    fontFamily: {
      'heading': ['Ubuntu', 'sans-serif'],
    },
    extend: {
      gradientColorStops: {
        'custom-start': '#FF0000', // Start color
        'custom-end': '#0000FF',  // End color
      },
      colors: {
        'primary': '#89C0E9',
        'secondary': '#217AB4',
        'third': '#02182B',
        'secondary2': '#E2E2E2',
        'border-grey': '#D4D7E3',
        'box-grey': '#F7FBFF',
        'deep-secondary': '#3E6D8C'
      },
      boxShadow: {
        'white': '0 0 5px rgba(120, 120, 120, 0.2)',  // Custom white shadow
      }
    },
  },
  plugins: [],
}

