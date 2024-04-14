/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "../siteplan/**/*.{py, js}",
    "../templates/**/*.{html, js}",
    
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require("rippleui")
  ],
}

