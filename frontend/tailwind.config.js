/** @type {import('tailwindcss').Config} */

// const sdkTailwindConfig = require('./application-ui-sdk/tailwind.config.js')
const config = require('@atlanhq/application-ui-sdk');

module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,vue,ts}",
    "./layouts/**/*.vue",
    "./pages/**/*.vue",
    "./error.vue",
    "./layouts/**/*.vue",
    "./plugins/**/*.{js,ts}",
    "./nuxt.config.{js,ts}",
    "./app.vue",
    "./node_modules/@atlanhq/**/*.{js,ts}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}