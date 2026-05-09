FROM node:20-alpine

WORKDIR /app

COPY package*.json .
RUN npm ci

COPY . .

ARG BACKEND_URL
ARG API_SECRET
ENV BACKEND_URL=$BACKEND_URL
ENV API_SECRET=$API_SECRET

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]