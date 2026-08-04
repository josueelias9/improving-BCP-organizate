# develop

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

### other options

```sh
vulture .
```

```sh
poetry run black .
```
