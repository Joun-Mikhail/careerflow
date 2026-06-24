# Install landing page

The canonical source for `https://app.careerflow.app/install` — a single
trusted page that points visitors at the right install path for their device
(App Store on iOS, Google Play on Android, PWA install everywhere else).

## How it ships

The frontend's `prebuild` script copies `landing/` into
`frontend/public/install/`, so the production build deploys the landing page
alongside the SPA at the `/install` path. The frontend's `vercel.json` has a
dedicated rewrite that bypasses the SPA fallback for this path.

To preview locally:

```bash
cd frontend
npm run build
npm run preview
# open http://localhost:4173/install
```

## Updating store URLs

Edit the `APPSTORE_URL` and `PLAYSTORE_URL` constants at the top of the inline
`<script>` block in [`index.html`](./index.html) once real listings exist.
Until then they point at placeholder IDs that 404 — the PWA install path still
works.
