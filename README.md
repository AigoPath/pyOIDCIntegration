# RationAI OAuth Receiver Auth

The Auth class implements JWT-based authorization for FastAPI services, that receive incoming requests from authorized users or services. The tokens contain an `aud` (audience) claim and the receiving service needs to check if itself is set as audience (e.g. "org.empaia.global.jes" or "org.empaia.reference_center_1.id_mapper").

## Code Checks

Check your code before committing.

* always format code with `black` and `isort`
* check code quality using `pycodestyle` and `pylint`

```bash
poetry shell
```

```bash
black .
isort .
pycodestyle *.py
pylint *.py
```
