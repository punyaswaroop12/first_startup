# UnitDispatch

UnitDispatch is a rental-property maintenance vendor marketplace for landlords, small property managers, and real estate investors.

## Run locally

```bash
npm install
npm --prefix apps/vendor-match-pro run dev
```

Open `http://127.0.0.1:3010`.

## Build checks

```bash
npm --prefix apps/vendor-match-pro run lint
npm --prefix apps/vendor-match-pro run typecheck
npm --prefix apps/vendor-match-pro run build
```

## Vercel deployment

1. Push the repo to GitHub.
2. Import the repo into Vercel.
3. Set the root directory to `apps/vendor-match-pro`.
4. Framework preset: `Next.js`.
5. Build command: `npm run build`.
6. Leave output directory blank.
7. Add environment variables from `.env.example` if needed.
8. Add your custom domain in Project Settings -> Domains.

## Domain setup

Use `useunitdispatch.com` as the primary domain for the cleanest startup landing page.

Typical DNS records:

- Apex/root `useunitdispatch.com`: `A` record to Vercel's IP shown in the dashboard
- `www.useunitdispatch.com`: `CNAME` record to the target shown by Vercel

Always copy the exact records Vercel shows in Project Settings -> Domains.
