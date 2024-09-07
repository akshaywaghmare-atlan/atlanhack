// https://nuxt.com/docs/api/configuration/nuxt-config
import { defineNuxtConfig } from 'nuxt/config'
import { resolve } from 'path'

export default defineNuxtConfig({
    compatibilityDate: '2024-04-03',
    devtools: { enabled: true },
    css: [
        // '~/assets/css/main.css',
        // '~/application-ui-sdk/src/styles/custom.css',
        './assets/css/main.css',
        '~/application-ui-sdk/src/style.css'
    ],
    target: 'static',
    // other configurations...
    generate: {
        fallback: true // This creates a 404.html file
    },
    postcss: {
        plugins: {
        tailwindcss: {},
        autoprefixer: {},
        },
    },
    modules: ['@nuxtjs/tailwindcss'],
    modulesDir: ['node_modules', 'frontend/sdk/node_modules'],
    vite: {
        resolve: {
        alias: {
            'treeselectjs': resolve(__dirname, 'node_modules/treeselectjs')
        }
        },
        optimizeDeps: {
        include: ['treeselectjs']
        }
    },
    build: {
        transpile: ['treeselectjs', 'frontend/application-ui-sdk']
    },
})
