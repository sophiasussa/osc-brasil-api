from fastapi import FastAPI

app = FastAPI(
    title="OSC Brasil API",
    description="API para consulta e análise de dados das Organizações da Sociedade Civil no Brasil.",
    version="0.1.0",
)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
