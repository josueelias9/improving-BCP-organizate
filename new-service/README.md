# How to use this container

- Althought the Dockerfile have the `poetry install` instruction, this is applied in another directory. Since we are going to act as developer, we neer to install the dependancies in the workspace

```sh
poetry install
poetry env info
```

- select the created Python environment

![alt text](image-1.png)

- press `F5` to start FastApi service

```sh
# optional:
# PYTHONPATH="." poetry run fastapi run app/main.py 
```

- run the streamlit frontend

```sh
cd src/Aframework
poetry run streamlit run app.py
```

- be sure you have downloaded the file to analyze in you download directory (in Windows)
- go to `./REST/README.md` and read the file
- go to `./REST/case 1.http` and replace `@fileName = EECC062026_05628441.PDF` with the name of the file you want to analize. Then, apply the endpoints in order
- go to `localhost:8501` and start updating the transactions
- save the latest changes with `./REST/case 1.http` - export transactions

### other options

```sh
vulture .
```

```sh
poetry run black .
```
