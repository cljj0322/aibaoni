# 阶段1：构建
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build-only

# 阶段2：Nginx 托管
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
# nginx 配置通过 docker-compose volume 挂载
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
