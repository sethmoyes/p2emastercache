// Build: bin/build_css.sh (writes avtools/web/static/css/app.css)
module.exports = {
  content: [
    './avtools/web/templates/**/*.html',
    './avtools/web/static/js/**/*.js',
    './avtools/web/*.py',
  ],
  theme: { extend: {} },
  plugins: [],
};
