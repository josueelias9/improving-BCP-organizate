# develop

- install dependancies

```sh
poetry install
poetry env info
```

- select the created Python environment

![alt text](image-1.png)

```sh
PYTHONPATH="." poetry run fastapi run app/main.py 
```

```sh
vulture .
```

```sh
python -m black ./app/
```
