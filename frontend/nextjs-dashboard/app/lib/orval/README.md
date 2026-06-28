


We are using Orval to autogenerate interfaces based on the openapi documentation created on the FastAPI end (https://orval.dev/docs/installation)

This is the official command:

```sh
docker run --rm -v "$(pwd):/app" -w /app ghcr.io/orval-labs/orval --config ./orval.config.ts
```

However, it seams that there is bug on the script.

As a workaround, I created a dockefile that will ron orval on a separated system. Execute the following commands when you want to update the interaces in the frontend. These commands must be executed at the level of this `README.md` file.

```sh
docker build -t my-orval -f Dockerfile .
docker run --rm -v "$(pwd):/app" -w /app my-orval --config ./orval.config.ts
```