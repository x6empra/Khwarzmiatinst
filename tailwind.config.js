/** @type {import('tailwindcss').Config} */
// Tokens سُحبت من DESIGN_GUIDE.md — لا تعدّل بدون تحديث الدليل.
module.exports = {
  content: [
    './templates/**/*.html',
    './apps/**/templates/**/*.html',
    './apps/**/*.py',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1B2A4E', // كحلي
          light: '#2C4A7C',
          lighter: '#3F66A8',
          lightest: '#5E84C2',
        },
        accent: {
          DEFAULT: '#F39C12', // برتقالي
          dark: '#D68910',
          light: '#F8C471',
        },
        success: {
          DEFAULT: '#27AE60', // أخضر
          dark: '#1E8449',
          light: '#82E0AA',
        },
        neutral: {
          900: '#2C3E50',
          700: '#5D6D7E',
          400: '#BFC9CA',
          100: '#F4F6F7',
          50: '#FFFFFF',
        },
      },
      fontFamily: {
        sans: ['Cairo', 'Inter', 'system-ui', 'sans-serif'],
        ar: ['Cairo', 'sans-serif'],
        en: ['Inter', 'sans-serif'],
      },
      fontSize: {
        xs: '12px',
        sm: '14px',
        base: '16px',
        lg: '18px',
        xl: '24px',
        '2xl': '32px',
        '3xl': '48px',
        '4xl': '64px',
      },
      spacing: {
        1: '4px',
        2: '8px',
        3: '12px',
        4: '16px',
        6: '24px',
        8: '32px',
        12: '48px',
        16: '64px',
      },
      borderRadius: {
        sm: '4px',
        md: '8px',
        lg: '12px',
        xl: '16px',
        full: '9999px',
      },
      boxShadow: {
        sm: '0 1px 2px rgba(27,42,78,0.08)',
        md: '0 4px 8px rgba(27,42,78,0.10)',
        lg: '0 10px 20px rgba(27,42,78,0.12)',
        xl: '0 20px 40px rgba(27,42,78,0.16)',
      },
      ringColor: {
        accent: '#F39C12',
      },
    },
  },
  plugins: [
    require('tailwindcss-rtl'),
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
