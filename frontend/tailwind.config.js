/** @type {import('tailwindcss').Config} */

const sdkTailwindConfig = require('./application-ui-sdk/tailwind.config.js')

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
    "./application-ui-sdk/**/*.{js,ts}",
  ],
  theme: {
    extend: {
      ...sdkTailwindConfig.theme.extend,
    },
  },
  plugins: [
    ...sdkTailwindConfig.plugins,
  ],
}