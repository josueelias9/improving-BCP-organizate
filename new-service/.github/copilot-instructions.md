
This project will folow the principles of Clean Architecture as defined by Robert C. Martin:

The Clean Architecture
- Frameworks & Drivers (UI, Database, Web, external interfaces, etc.)
- Interface Adapters (Controllers, Presenters, Gateways)
- Application Business Rules (Use Cases)
- Enterprise Business Rules (Entities, Domain Models)

The Dependencies Rule
- Source code dependencies must point only inward, toward higher-level policies.


Nothing in an inner circle can know anything at all about something in an outer circle. In particular, the name of something declared in an outer circle must not be mentioned by the code in an inner circle. That includes functions, classes, variables, or any other software entity.


https://www.youtube.com/watch?v=C7MRkqP5NRI