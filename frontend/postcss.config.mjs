/** @type {import('postcss-load-config').Config} */
const config = {
  plugins: {
    '@tailwindcss/postcss': {},  // ← Use this instead of 'tailwindcss'
  },
};

export default config;