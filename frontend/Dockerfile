# syntax=docker/dockerfile:1.7

FROM node:22-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

ARG VITE_API_BASE_URL=""
ENV VITE_API_BASE_URL="$VITE_API_BASE_URL"
RUN npm run build


FROM nginxinc/nginx-unprivileged:1.30.6-alpine3.24 AS runtime

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=5 \
  CMD ["wget", "--quiet", "--tries=1", "--spider", "http://127.0.0.1:8080/nginx-health"]
