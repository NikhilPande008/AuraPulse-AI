# Build with: docker build --build-arg BACKEND_URL=https://<api> frontend
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG BACKEND_URL
ARG ALLOW_LOCAL_BACKEND=false
RUN if [ -z "$BACKEND_URL" ] && [ "$ALLOW_LOCAL_BACKEND" != "true" ]; then \
      echo "ERROR: pass --build-arg BACKEND_URL=https://<api>"; exit 1; fi
ENV BACKEND_URL=$BACKEND_URL
ENV BUILD_STANDALONE=true
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV HOSTNAME=0.0.0.0
ENV PORT=3000
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
EXPOSE 3000
CMD ["node", "server.js"]
