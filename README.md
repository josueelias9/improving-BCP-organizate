# Start project
- Build images

```sh
docker compose build
docker compose up -d
```

- create tables and populare with data

```sh
docker exec new-service-container ./scripts/prestart.sh
```

- go to the `new-service/REST client.http` file and execute the endpoints
