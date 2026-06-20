# syntax=docker/dockerfile:1
# ---------------------------------------------------------------------------
# CareerFlow frontend image: build the SPA, then serve it with Nginx.
# ---------------------------------------------------------------------------
FROM node:20-alpine AS build

WORKDIR /app

# Install dependencies first for layer caching. Use a lockfile when present.
COPY package.json package-lock.json* ./
RUN npm install

COPY . .
RUN npm run build

# ---------------------------------------------------------------------------
FROM nginx:1.27-alpine AS runtime

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
