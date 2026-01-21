"""
Custom Exception Handlers for User-Friendly Error Messages

These handlers catch common errors and return friendly messages
instead of technical stack traces to users.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.logger import get_logger
import traceback

logger = get_logger()

class ChatbotException(Exception):
    """Base exception for chatbot-specific errors"""
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class RAGException(ChatbotException):
    """Exception for RAG system errors"""
    def __init__(self, message: str = "Error en el sistema de búsqueda", details: dict = None):
        super().__init__(message, status_code=500, details=details)

class LLMException(ChatbotException):
    """Exception for LLM service errors"""
    def __init__(self, message: str = "Error al generar respuesta", details: dict = None):
        super().__init__(message, status_code=500, details=details)

class DatabaseException(ChatbotException):
    """Exception for database errors"""
    def __init__(self, message: str = "Error de base de datos", details: dict = None):
        super().__init__(message, status_code=500, details=details)

class CacheException(ChatbotException):
    """Exception for cache errors"""
    def __init__(self, message: str = "Error en caché", details: dict = None):
        super().__init__(message, status_code=500, details=details)

async def chatbot_exception_handler(request: Request, exc: ChatbotException):
    """Handler for custom chatbot exceptions"""
    logger.error(f"ChatbotException: {exc.message}", extra={"details": exc.details})
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "type": exc.__class__.__name__,
            "details": exc.details
        }
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handler for HTTP exceptions with friendly messages"""
    
    # Map status codes to user-friendly messages
    friendly_messages = {
        400: "La solicitud contiene datos inválidos. Por favor, verifica tu consulta.",
        401: "Se requiere autenticación para acceder a este recurso.",
        403: "No tienes permiso para acceder a este recurso.",
        404: "El recurso solicitado no fue encontrado.",
        405: "Método no permitido para este recurso.",
        422: "Los datos enviados no son válidos.",
        429: "Has excedido el límite de peticiones. Por favor, espera un momento.",
        500: "Ocurrió un error interno. Estamos trabajando para solucionarlo.",
        502: "Servicio temporalmente no disponible. Por favor, intenta más tarde.",
        503: "El servicio está en mantenimiento. Por favor, intenta más tarde.",
        504: "El servicio tardó demasiado en responder. Por favor, intenta nuevamente."
    }
    
    message = friendly_messages.get(exc.status_code, exc.detail)
    
    logger.warning(
        f"HTTP {exc.status_code}: {exc.detail}",
        extra={
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": message,
            "status_code": exc.status_code
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler for request validation errors"""
    
    # Extract validation errors
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        f"Validation error: {len(errors)} field(s)",
        extra={"errors": errors}
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "message": "Los datos enviados no son válidos. Por favor, verifica los campos.",
            "validation_errors": errors
        }
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """Handler for unhandled exceptions"""
    
    # Log full stack trace
    error_trace = traceback.format_exc()
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "trace": error_trace
        }
    )
    
    # Determine if this is a known error type
    error_message = "Lo siento, ocurrió un error inesperado. "
    
    if "connection" in str(exc).lower():
        error_message += "Hubo un problema de conexión con el servicio. Por favor, intenta nuevamente."
    elif "timeout" in str(exc).lower():
        error_message += "La operación tardó demasiado tiempo. Por favor, intenta con una consulta más simple."
    elif "api" in str(exc).lower() and "key" in str(exc).lower():
        error_message += "Hay un problema con la configuración del servicio. Por favor, contacta al administrador."
    else:
        error_message += "Estamos trabajando para solucionarlo."
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": error_message,
            "type": "InternalServerError"
        }
    )

# Service-specific helper functions
def handle_service_error(service_name: str, error: Exception) -> ChatbotException:
    """
    Convert service errors to user-friendly exceptions
    
    Args:
        service_name: Name of the service (e.g., "Pinecone", "OpenAI", "Redis")
        error: The original exception
    
    Returns:
        ChatbotException: User-friendly exception
    """
    error_str = str(error).lower()
    
    # API Key errors
    if "api" in error_str and "key" in error_str:
        return ChatbotException(
            message=f"Error de configuración en {service_name}. Por favor, contacta al administrador.",
            status_code=500,
            details={"service": service_name, "type": "api_key_error"}
        )
    
    # Connection errors
    if "connection" in error_str or "connect" in error_str:
        return ChatbotException(
            message=f"No se pudo conectar con {service_name}. Por favor, intenta más tarde.",
            status_code=503,
            details={"service": service_name, "type": "connection_error"}
        )
    
    # Timeout errors
    if "timeout" in error_str:
        return ChatbotException(
            message=f"{service_name} tardó demasiado en responder. Por favor, intenta nuevamente.",
            status_code=504,
            details={"service": service_name, "type": "timeout_error"}
        )
    
    # Rate limit errors
    if "rate" in error_str and "limit" in error_str:
        return ChatbotException(
            message="Has alcanzado el límite de uso del servicio. Por favor, espera un momento.",
            status_code=429,
            details={"service": service_name, "type": "rate_limit_error"}
        )
    
    # Generic service error
    return ChatbotException(
        message=f"Error en {service_name}. Por favor, intenta más tarde.",
        status_code=500,
        details={"service": service_name, "type": "service_error"}
    )
