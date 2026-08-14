import { defineConfig } from 'astro/config';

// Base path can be overridden for GitHub Pages deployment (#9).
// For local dev use '/'. For repo-root GitHub Pages use '/-2/'.
const base = process.env.ASTRO_BASE || '/';

export default defineConfig({
  output: 'static',
  base,
  site: 'https://li-yongqvan.github.io',
  trailingSlash: 'ignore',
});
