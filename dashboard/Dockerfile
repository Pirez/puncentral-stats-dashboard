# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Accept build arguments for Vite environment variables
# These are passed from Railway service variables
ARG VITE_API_URL
ARG VITE_API_TOKEN
ARG VITE_TEST_VARIABLE
ARG VITE_AUTH_PASSWORD

# Make them available as environment variables during build
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_API_TOKEN=$VITE_API_TOKEN
ENV VITE_TEST_VARIABLE=$VITE_TEST_VARIABLE
ENV VITE_AUTH_PASSWORD=$VITE_AUTH_PASSWORD

# Build the application
# Vite will replace import.meta.env.VITE_* with actual values at build time
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install production dependencies (serve for static hosting)
RUN npm ci --only=production

# Copy built assets from builder
COPY --from=builder /app/dist ./dist

# Expose port (Railway will set PORT env var)
EXPOSE 3000

# Use serve to host static files - more reliable than vite preview
CMD sh -c "npx serve -s dist -l ${PORT:-3000}"
