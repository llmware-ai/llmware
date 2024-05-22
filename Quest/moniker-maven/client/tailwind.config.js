module.exports = {
  content: [
    "./public/index.html",
    "./src/*.{js,jsx,ts,tsx}",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: 'class', // or 'media'
  theme: {
    extend: {
      colors: {
        darkTheme: "#2F303A", // Ensure the hex value is correct
      },
    },
  },
  plugins: [],
};
