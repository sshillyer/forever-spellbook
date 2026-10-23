// Builds dist/index.html: the page template with data.json and icons.json inlined.
// No dependencies. Usage: node scripts/build.mjs
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const read = (p) => readFileSync(join(root, p), 'utf8');

// Minify the JSON and make it safe to sit inside a <script> tag.
const inline = (p) => JSON.stringify(JSON.parse(read(p))).replace(/<\//g, '<\\/');

const template = read('src/index.template.html');
if (!template.includes('__DATA__') || !template.includes('__ICONS__')) {
  throw new Error('Template is missing the __DATA__ or __ICONS__ placeholder');
}

const data = JSON.parse(read('data/data.json'));
const html = template
  .replace('__DATA__', () => inline('data/data.json'))
  .replace('__ICONS__', () => inline('data/icons.json'));

// GitHub Pages serves a full document, so wrap the page content in one.
const doc = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="WoW Forever spellbook, talent calculator and action bar planner.">
<style>:root{color-scheme:light}body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
</head>
<body>
${html}
</body>
</html>
`;

mkdirSync(join(root, 'dist'), { recursive: true });
writeFileSync(join(root, 'dist/index.html'), doc);
const classes = Object.keys(data.classes).length;
console.log(`Built dist/index.html (${(doc.length / 1024).toFixed(0)} KB, ${classes} classes, data pulled ${data.meta.pulled})`);
