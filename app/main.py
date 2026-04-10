from fastapi import FastAPI
from app.api.v1.endpoints import parse, health
from app.core.exceptions import ParsingError
from fastapi.responses import JSONResponse


app = FastAPI(
    title="PDF Parser API",
    description="Сервис для извлечения данных из PDF-реестров и протоколов",
    version="1.0.0"
)


app.include_router(parse.router, prefix="/api/v1", tags=["parse"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])


@app.exception_handler(ParsingError)
async def parsing_error_handler(request, exc):
    return JSONResponse(status_code=422, content={"detail": str(exc)})
