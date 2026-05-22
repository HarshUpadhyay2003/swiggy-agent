export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        swiggy: {
          50: '#fff7ed',
          100: '#ffedd5',
          200: '#fed7aa',
          300: '#fdba74',
          400: '#fb923c',
          500: '#fc8019',
          600: '#f97316',
          700: '#ea580c',
          800: '#c2410c',
          900: '#9a3412'
        },
        brand: {
          50: '#fff7ed',
          100: '#ffedd5',
          200: '#fed7aa',
          300: '#fdba74',
          400: '#fb923c',
          500: '#fc8019',
          600: '#f97316',
          700: '#ea580c',
          800: '#c2410c',
          900: '#9a3412'
        }
      },
      boxShadow: {
        glow: '0 20px 55px rgba(252, 128, 25, 0.16)',
        soft: '0 20px 60px rgba(15, 23, 42, 0.08)'
      },
      animation: {
        float: 'float 6s ease-in-out infinite',
        pulsefast: 'pulse 1.2s ease-in-out infinite'
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-6px)' }
        }
      }
    }
  },
  plugins: []
}
