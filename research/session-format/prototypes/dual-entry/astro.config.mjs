import { defineConfig } from 'astro/config';

// Base path can be overridden for GitHub Pages deployment (#9).
// For local dev use '/'. For repo-root GitHub Pages use '/experience-pack/'.
const rawBase = process.env.ASTRO_BASE || '/';
const base = rawBase.replace(/\/$/, '') + '/';

export default defineConfig({
  output: 'static',
  base,
  site: 'https://li-yongqvan.github.io',
  trailingSlash: 'ignore',
});
