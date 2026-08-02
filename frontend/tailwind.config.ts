import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{vue,ts}'],
  theme: {
    extend: {
      colors: {
        mandrong: {
          bg: '#0E100F',
          surface: '#171B18',
          text: '#F5F1EA',
          muted: '#A9A399',
          line: '#2D342F',
          primary: '#74D4B3',
          primaryHover: '#5EC7A1',
          warning: '#F4C542',
          danger: '#FF6B5F',
        },
      },
    },
  },
  plugins: [],
} satisfies Config
