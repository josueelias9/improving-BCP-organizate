# Alternative to "BCP Organizate"

This project is meant to replace the BCP-Organizate app that was removed by BCP. 

The idea on the feature is to integrate this with other banks and currency platform.s

# How to use

This project is highly integrated with vs code. Thus, you can take advantage of the dev container features to start upgrading the code.

Start dev container and follow [README file](new-service/README.md) inside it

![alt text](image.png)



## project architecture

Example with db 

```mermaid
sequenceDiagram
    box rgb(141, 173, 241) external layer
    participant FastAPI
    participant DbDocument
    end
    
    box rgb(248, 131, 131) application layer
    participant DocumentUseCase
    end
    
    FastAPI->>DocumentUseCase: DTORequest
    DbDocument<<->>DocumentUseCase: DocumentEntity
    DocumentUseCase->>FastAPI: DTOResponse
```


in general, this is the pattern we are using for this project:

```mermaid
sequenceDiagram
    box rgb(141, 173, 241) frameworks and drivers layer
    participant FastAPI
    participant Driver
    end

    box rgb(127, 176, 134) FastAPI routes
    participant route
    end

    box rgb(248, 131, 131) application layer
    participant UseCase
    end
    
    FastAPI->>route: 
    route->>UseCase: creates DTORequest
    Driver<<->>UseCase: Entities and primitives
    UseCase->>route: DTOResponse
    route->>FastAPI: 

```


The original architecture: For this project the `Interface Adapters` layer was removed to take advantage of FastAPI and swagger. the idea was to use the DTO directly in the routes to generate the documentation automatically, otherwise, and aditional layer of DTO (FastAPI DTO) would have been required.

```mermaid
sequenceDiagram
    box rgb(141, 173, 241) frameworks & drivers
    participant Framework
    participant Driver
    end

    box rgb(127, 176, 134) Interface Adapters 
    participant Controller
    participant Presenter
    end
    
    box rgb(248, 131, 131) application
    participant UseCase
    end
    
    Framework->>Controller: calls the controller
    Controller->>UseCase: DTORequest
    Driver<<->>UseCase: Entities and primitives
    UseCase->>Presenter: DTOResponse
    Presenter->>Framework: adapt data
    
```

## future integration

The idea is instead of using a pdf, use an API directly to consume information form BCP directly.

https://www.viabcp.com/empresas/open-economy



```
docker compose down db -v
docker compose up db -d
docker compose up new-service-init --build
```



```
./scripts/enc.sh encrypt
SOPS_AGE_KEY_FILE=../key.txt ./scripts/enc.sh decrypt
```


```mermaid

flowchart LR


parser --> file_extension
parser --> read_file
parser --> get_transactions
parser --> get_initial_day
parser --> get_final_day/remove
parser --> get_balance
parser --> get_account

```