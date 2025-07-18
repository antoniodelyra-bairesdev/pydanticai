import time
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from .config import settings
from .models.response_models import StatusResponse
from .routers import pdf_router

# Variável para armazenar o tempo de início da aplicação
app_start_time = time.time()

# Constantes
SECONDS_PER_MINUTE = 60


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação."""
    # Startup
    logger.info("Iniciando aplicação PDF to Markdown API")
    logger.info(f"Versão: {settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")

    # Criar diretórios necessários
    Path(settings.temp_dir).mkdir(parents=True, exist_ok=True)
    logger.info(f"Diretório temporário criado: {settings.temp_dir}")

    yield

    # Shutdown
    logger.info("Encerrando aplicação PDF to Markdown API")


# Criar instância da aplicação
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API para conversão de arquivos PDF em formato Markdown usando Docling",
    debug=settings.debug,
    lifespan=lifespan,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(pdf_router.router)


# Handlers de exceção
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler para erros de validação."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Dados de entrada inválidos",
            "error_code": "VALIDATION_ERROR",
            "details": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handler geral para exceções não tratadas."""
    logger.error(f"Erro não tratado: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Erro interno do servidor",
            "error_code": "INTERNAL_ERROR",
            "message": str(exc) if settings.debug else "Erro interno",
        },
    )


@app.get("/", response_model=StatusResponse)
async def root():
    """Endpoint raiz com informações da API."""
    uptime_seconds = time.time() - app_start_time
    uptime_str = f"{uptime_seconds:.0f}s"

    if uptime_seconds > SECONDS_PER_MINUTE:
        minutes = int(uptime_seconds // SECONDS_PER_MINUTE)
        seconds = int(uptime_seconds % SECONDS_PER_MINUTE)
        uptime_str = f"{minutes}m {seconds}s"

    return StatusResponse(status="running", version=settings.app_version, uptime=uptime_str)


@app.get("/health")
async def health_check():
    """Endpoint de health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.app_version,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "docling_pdf.main:app",  # Ajustado para o nome do módulo
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
