FROM node:latest as build

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

ARG API_URL
ENV VITE_API_URL $API_URL
RUN npm run build

FROM nginx:alpine as run

WORKDIR /usr/share/nginx/html

RUN rm -rf ./*

COPY --from=build /app/dist .

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
