export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        serif: ['"Playfair Display"', 'Georgia', 'serif'],
        sans: ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'sans-serif'],
        display: ['"Playfair Display"', 'Georgia', 'serif'],
      },
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
          900: '#9a3412',
          950: '#5e2a00',
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
          900: '#9a3412',
          tint: '#984800',
        },
        gourmet: {
          surface: '#f9f9f9',
          'surface-lowest': '#ffffff',
          'surface-low': '#f3f3f3',
          'surface-container': '#eeeeee',
          'surface-high': '#e8e8e8',
          'surface-highest': '#e2e2e2',
          'on-surface': '#1a1c1c',
          'on-surface-variant': '#574236',
          outline: '#8b7264',
          'outline-variant': '#dec1b0',
        },
        veg: {
          DEFAULT: '#1b6d01',
          container: '#63b549',
          dark: '#0c4200',
          bg: '#f0fdf4',
          border: '#bbf7d0',
        },
        nonveg: {
          DEFAULT: '#991b1b',
          container: '#f87171',
          dark: '#450a0a',
          bg: '#fef2f2',
          border: '#fecaca',
        }
      },
      borderRadius: {
        '2xl': '1.5rem', // 24px primary organic radius
        '3xl': '2rem',   // 32px container radius
        'xl': '1rem',    // 16px secondary radius
        'full': '9999px',
      },
      boxShadow: {
        gourmet: '0 16px 40px -10px rgba(32, 16, 0, 0.08)',
        'gourmet-hover': '0 24px 50px -12px rgba(252, 128, 25, 0.22)',
        glow: '0 16px 40px rgba(252, 128, 25, 0.28)',
        soft: '0 20px 60px rgba(15, 23, 42, 0.08)',
        glass: '0 8px 32px 0 rgba(0, 0, 0, 0.06)',
      },
      animation: {
        float: 'float 6s ease-in-out infinite',
        pulsefast: 'pulse 1.2s ease-in-out infinite',
        shimmer: 'shimmer 2s linear infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-6px)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        }
      }
    }
  },
  plugins: []
}
