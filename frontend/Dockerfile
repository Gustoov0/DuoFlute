# ---------- Etapa "dev": servidor de desenvolvimento (Vite) com recarga automática ----------
FROM node:22-alpine AS dev
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
EXPOSE 80
CMD ["npm", "run", "dev"]

# ---------- Etapa "build": gera os arquivos estáticos otimizados ----------
FROM dev AS build
RUN npm run build

# ---------- Etapa "prod": Nginx servindo só os arquivos prontos (imagem final padrão) ----------
FROM nginx:1.27-alpine AS prod
COPY nginx.spa.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80