from fastapi import FastAPI

from modules.organizations.router import router as organizations_router
from modules.summary.router import router as summary_router
from modules.filters.router import router as filters_router

app = FastAPI(
    title="OSC Brasil API",
    description="API para consulta e análise de dados das Organizações da Sociedade Civil no Brasil.",
    version="0.1.0",
)

app.include_router(organizations_router)
app.include_router(summary_router)
app.include_router(filters_router)

@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
