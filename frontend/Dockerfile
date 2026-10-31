# Build with: docker build --build-arg BACKEND_URL=https://<api> frontend
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG BACKEND_URL
ENV BACKEND_URL=$BACKEND_URL
RUN if [ "$NODE_ENV" = "production" ] && [ -z "$BACKEND_URL" ]; then \
      echo "ERROR: BACKEND_URL build argument is required when building for production." && exit 1; \
    fi
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
EXPOSE 3000
CMD ["node", "server.js"]
