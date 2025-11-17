/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./**/*.{html,js}"],
  theme: {
    extend: {
      colors: {
        'instagram-purple': '#833AB4',
        'instagram-pink': '#C13584',
        'instagram-red': '#E1306C',
        'instagram-orange': '#F56040',
        'instagram-yellow': '#FCAF45',
        'light-bg': '#fafafa',
        'card-bg': '#ffffff',
        'text-dark': '#262626',
        'text-light': '#8e8e8e',
        'border-color': '#dbdbdb',
      },
      backgroundImage: {
        'instagram-gradient': 'linear-gradient(45deg, #833AB4, #C13584, #E1306C, #FD1D1D, #F56040, #F77737, #FCAF45)',
      },
      boxShadow: {
        'light': '0 2px 10px rgba(0,0,0,0.08)',
        'medium': '0 4px 12px rgba(0,0,0,0.12)',
        'heavy': '0 5px 25px rgba(0,0,0,0.15)',
      },
      animation: {
        'fadeIn': 'fadeIn 0.5s ease-in',
        'modalFadeIn': 'modalFadeIn 0.3s ease-out',
        'slideIn': 'slideIn 0.3s ease-out',
        'slideOut': 'slideOut 0.3s ease-in',
      },
      keyframes: {
        fadeIn: {
          from: { opacity: 0, transform: 'translateY(20px)' },
          to: { opacity: 1, transform: 'translateY(0)' },
        },
        modalFadeIn: {
          from: { opacity: 0, transform: 'scale(0.9) translateY(-20px)' },
          to: { opacity: 1, transform: 'scale(1) translateY(0)' },
        },
        slideIn: {
          from: { transform: 'translateX(100%)', opacity: 0 },
          to: { transform: 'translateX(0)', opacity: 1 },
        },
        slideOut: {
          from: { transform: 'translateX(0)', opacity: 1 },
          to: { transform: 'translateX(100%)', opacity: 0 },
        },
      }
    }
  },
  plugins: [],
}