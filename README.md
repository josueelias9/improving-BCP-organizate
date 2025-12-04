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

## stop processess

```sh
docker compose down
```

## TODO

```txt
- [ ] do not show transactions's uuid in the frontend. Instead, show only the order of the transaction
- [ ] create a unique identifier for transaction
- [ ] store pdf file
- [ ] implement logic to diferenciate between credit and debit pdf files
- [ ]
```