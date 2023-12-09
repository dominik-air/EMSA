# Frontend

## Installation guide

1. Get [node.js](https://nodejs.org/en/download/current)

   It is recommend to use a node.js (and npm) version manager such as [nodist](https://github.com/nullivex/nodist)

2. Get [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)

3. Install dependencies

   `cd emsa-ui && npm install`

4. Run the apps

   `npm run dev`

## Development guide

### Adding packages

`npm install <package_name>`

### Linter

`npm run lint`

### Formatting

`npm run format`

### Unit tests

`npm run test`

### Mocking the backend's API

`node api-mock/server.cjs`

## Deployment guide

### Building the image

Replace the API_URL's value with the backend's URL.

`docker build --build-arg API_URL=http://localhost:8000 -t emsa-ui:latest .`

