// Build: bin/web/build_css.sh (writes bin/web/static/css/app.css)
module.exports = {
  content: [
    './bin/web/templates/**/*.html',
    './bin/web/static/js/**/*.js',
    './bin/web/*.py',
  ],
  theme: { extend: {} },
  plugins: [],
};
