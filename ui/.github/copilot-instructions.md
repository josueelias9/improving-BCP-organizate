
This project will folow the principles of Clean Architecture as defined by Robert C. Martin:

The Clean Architecture
- Frameworks & Drivers (UI, Database, Web, external interfaces, etc.)
- Interface Adapters (Controllers, Presenters, Gateways)
- Application Business Rules (Use Cases)
- Enterprise Business Rules (Entities, Domain Models)

The Dependencies Rule
- Source code dependencies must point only inward, toward higher-level policies.


Nothing in an inner circle can know anything at all about something in an outer circle. In particular, the name of something declared in an outer circle must not be mentioned by the code in an inner circle. That includes functions, classes, variables, or any other software entity.


## Which Data Crosses the Boundaries
Typically the data that crosses the boundaries consists of simple data structures. You can use basic structs or simple data transfer objects if you like. Or the data can simply be arguments in function calls. Or you can pack it into a hashmap, or construct it into an object. The important thing is that isolated, simple data structures are passed across the boundaries. We don’t want to cheat and pass Entity objects or database rows. We don’t want the data structures to have any kind of dependency that violates the Dependency Rule.

https://www.youtube.com/watch?v=C7MRkqP5NRI