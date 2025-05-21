import uvicorn
from fastapi import Request
from app.core.config import settings
from app.core.app import get_app
from logger import setup_logger

logger = setup_logging()

if __name__ == '__main__':
    app = get_app(name='Transaction Service')
    
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url}")
        try:
            response = await call_next(request)
            logger.info(f"Response: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            raise

    uvicorn.run(app, host=settings.app.app_host, port=settings.app.app_port)