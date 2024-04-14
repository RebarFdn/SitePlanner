/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "../siteplan/**/*.{py, js}",
    "../templates/**/*.{html, js}",
    "node_modules/preline/dist/*.js",
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('preline/plugin'),
  ],
}

