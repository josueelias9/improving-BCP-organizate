# Start project

- Build images

```sh
docker compose build
docker compose up -d
```

- create tables and populare with data

```sh
docker exec new-service-container /app/scripts/prestart.sh
```

- go to the `localhost:8000/dashboard/documents`

## stop processes

```sh
docker compose down
```

# debug mode

```sh
docker compose -f docker-compose.yml -f docker-compose.combined.yml up -d
```



averiguar

https://www.viabcp.com/empresas/open-economy