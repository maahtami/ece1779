# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./

# Use `npm ci` when a lockfile exists for reproducible builds, otherwise fall back to `npm install`
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

COPY . .

# Allow passing the API base URL at build time so create-react-app
# substitutes `process.env.REACT_APP_API_URL` into the static build.
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=${REACT_APP_API_URL:-https://ims-inventory-f25-final.fly.dev/}

RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

RUN npm install -g serve

COPY --from=builder /app/build ./build

EXPOSE 3000

CMD ["serve", "-s", "build", "-l", "3000"]
