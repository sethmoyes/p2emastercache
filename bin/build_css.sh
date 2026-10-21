#!/bin/bash
# Rebuild avtools/web/static/css/app.css after changing classes in templates, JS
# or Python. Needs Node; the compiled file is committed, so deploys don't.
cd "$( dirname "${BASH_SOURCE[0]}" )/.."
npx --yes --registry https://registry.npmjs.org tailwindcss@3.4.17 -c avtools/web/tailwind/tailwind.config.js \
    -i avtools/web/tailwind/input.css -o avtools/web/static/css/app.css --minify
