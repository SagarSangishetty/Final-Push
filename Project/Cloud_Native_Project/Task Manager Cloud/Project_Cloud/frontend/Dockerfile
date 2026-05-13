# -------- Stage 1 : Builder --------
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# -------- Stage 2 : Runtime --------
FROM nginx:alpine AS runtime

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Create required directories
RUN mkdir -p /var/cache/nginx \
    /var/run \
    /var/log/nginx \
    /etc/nginx/conf.d \
    /tmp

# Override main nginx.conf with pid pointing to /tmp
RUN printf 'pid /tmp/nginx.pid;\nevents { worker_connections 1024; }\nhttp { include /etc/nginx/conf.d/*.conf; }\n' \
    > /etc/nginx/nginx.conf

# Copy app and config
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Fix permissions
RUN chown -R appuser:appgroup \
    /var/cache/nginx \
    /var/run \
    /var/log/nginx \
    /etc/nginx \
    /usr/share/nginx/html \
    /tmp

USER appuser

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]