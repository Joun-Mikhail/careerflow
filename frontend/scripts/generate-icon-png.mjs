/**
 * Generate 1024×1024 icon.png and 2732×2732 splash.png from favicon.svg
 * without requiring Chrome. Uses pngjs (already in devDependencies).
 */
import { writeFileSync, mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { PNG } from 'pngjs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ASSETS = resolve(__dirname, '../public/native-assets');

const BRAND = { r: 0x4f, g: 0x46, b: 0xe5 };
const WHITE = { r: 255, g: 255, b: 255 };
const SCALE = 32; // favicon viewBox is 32×32

function insideRoundedRect(x, y, w, h, r) {
  if (x < r && y < r) return (x - r) ** 2 + (y - r) ** 2 <= r ** 2;
  if (x >= w - r && y < r) return (x - (w - r)) ** 2 + (y - r) ** 2 <= r ** 2;
  if (x < r && y >= h - r) return (x - r) ** 2 + (y - (h - r)) ** 2 <= r ** 2;
  if (x >= w - r && y >= h - r) return (x - (w - r)) ** 2 + (y - (h - r)) ** 2 <= r ** 2;
  return x >= 0 && x < w && y >= 0 && y < h;
}

function distToSegment(px, py, x1, y1, x2, y2) {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const len2 = dx * dx + dy * dy;
  if (len2 === 0) return Math.hypot(px - x1, py - y1);
  let t = ((px - x1) * dx + (py - y1) * dy) / len2;
  t = Math.max(0, Math.min(1, t));
  return Math.hypot(px - (x1 + t * dx), py - (y1 + t * dy));
}

/** Polyline from favicon.svg path, scaled to `size`. */
function chartStroke(size) {
  const s = size / 32;
  const stroke = 2.4 * s;
  const pts = [
    [9, 20.5],
    [14, 11],
    [17.5, 17],
    [20, 13],
    [24, 20.5],
  ].map(([x, y]) => [x * s, y * s]);

  const segments = [];
  for (let i = 0; i < pts.length - 1; i++) {
    segments.push([pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]]);
  }
  return { segments, stroke };
}

function drawIcon(size) {
  const png = new PNG({ width: size, height: size });
  const radius = (8 / 32) * size;
  const { segments, stroke } = chartStroke(size);
  const circles = [
    [14, 11],
    [24, 20.5],
  ].map(([x, y]) => ({ cx: (x / 32) * size, cy: (y / 32) * size, r: (1.6 / 32) * size }));

  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const idx = (size * y + x) << 2;
      if (!insideRoundedRect(x, y, size, size, radius)) {
        png.data[idx + 3] = 0;
        continue;
      }

      let isWhite = false;
      for (const [x1, y1, x2, y2] of segments) {
        if (distToSegment(x + 0.5, y + 0.5, x1, y1, x2, y2) <= stroke / 2) {
          isWhite = true;
          break;
        }
      }
      if (!isWhite) {
        for (const c of circles) {
          if (Math.hypot(x + 0.5 - c.cx, y + 0.5 - c.cy) <= c.r) {
            isWhite = true;
            break;
          }
        }
      }

      const c = isWhite ? WHITE : BRAND;
      png.data[idx] = c.r;
      png.data[idx + 1] = c.g;
      png.data[idx + 2] = c.b;
      png.data[idx + 3] = 255;
    }
  }
  return png;
}

function drawSplash(size) {
  const png = new PNG({ width: size, height: size });
  const iconSize = Math.round(size * 512 / 2732);
  const icon = drawIcon(iconSize);
  const offset = Math.floor((size - iconSize) / 2);

  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const idx = (size * y + x) << 2;
      const ix = x - offset;
      const iy = y - offset;
      if (ix >= 0 && ix < iconSize && iy >= 0 && iy < iconSize) {
        const iidx = (iconSize * iy + ix) << 2;
        png.data[idx] = icon.data[iidx];
        png.data[idx + 1] = icon.data[iidx + 1];
        png.data[idx + 2] = icon.data[iidx + 2];
        png.data[idx + 3] = icon.data[iidx + 3];
      } else {
        png.data[idx] = BRAND.r;
        png.data[idx + 1] = BRAND.g;
        png.data[idx + 2] = BRAND.b;
        png.data[idx + 3] = 255;
      }
    }
  }
  return png;
}

mkdirSync(ASSETS, { recursive: true });
writeFileSync(resolve(ASSETS, 'icon.png'), PNG.sync.write(drawIcon(1024)));
writeFileSync(resolve(ASSETS, 'splash.png'), PNG.sync.write(drawSplash(2732)));
console.log('Wrote public/native-assets/icon.png (1024×1024)');
console.log('Wrote public/native-assets/splash.png (2732×2732)');
