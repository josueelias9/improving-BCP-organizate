FROM node:20

WORKDIR /app

COPY . .

WORKDIR /app/nextjs-dashboard

RUN npm install -g pnpm

RUN pnpm i

EXPOSE 3000

CMD ["pnpm", "dev"]