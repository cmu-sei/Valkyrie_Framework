import yaml
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from routers import searches, application, datasources, results


def load_conf(path="../bh_web/beacon_huntress/src/config/config.conf"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

app = FastAPI(title="Beacon Huntress API")

# Custom OpenAPI metadata
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        version="1.0.0",
        title=app.title, 
        description="API endpoints for beacon hunting.",
        routes=app.routes,
    )
    schema["info"]["contact"] = {
        "name": "The Valkyrie Team at CMU SEI",
        "url": "https://sei.cmu.edu/",
        "email": "info@sei.cmu.edu"
    }
    schema["info"]["license"] = {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
    schema["info"]["termsOfService"] = "https://sei.cmu.edu/terms"
    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi

@app.on_event("startup")
def load_config_once():
    app.state.config = load_conf()
    print(app.state.config)

app.include_router(application.router)
# app.include_router(datasources.router)
app.include_router(searches.router)
app.include_router(results.router)
