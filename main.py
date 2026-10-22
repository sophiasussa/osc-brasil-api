from fastapi import FastAPI

from modules.organizations.router import router as organizations_router


app = FastAPI(
    title="OSC Brasil API",
    description="API para consulta e análise de dados das Organizações da Sociedade Civil no Brasil.",
    version="0.1.0",
)

app.include_router(organizations_router)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
