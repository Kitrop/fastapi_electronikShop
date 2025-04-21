from redis import Redis
from functools import wraps
import json
from typing import Any, Callable, Optional
import os

from app.utils.logger import logger

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

redis_client = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)

def cache(ttl: int = 300):
    """
    Декоратор для кэширования результатов функций
    :param ttl: время жизни кэша в секундах
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Создаем ключ кэша на основе аргументов функции
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Пытаемся получить данные из кэша
            cached_data = redis_client.get(cache_key)
            if cached_data:
                logger.info(f"Cache hit for key: {cache_key}")
                return json.loads(cached_data)
            
            # Если данных нет в кэше, выполняем функцию
            logger.info(f"Cache miss for key: {cache_key}")
            result = await func(*args, **kwargs)
            
            # Сохраняем результат в кэш
            redis_client.setex(
                cache_key,
                ttl,
                json.dumps(result)
            )
            
            return result
        return wrapper
    return decorator

def invalidate_cache(pattern: str) -> None:
    """
    Удаляет ключи кэша по шаблону
    :param pattern: шаблон для поиска ключей
    """
    keys = redis_client.keys(pattern)
    if keys:
        redis_client.delete(*keys)
        logger.info(f"Invalidated cache keys matching pattern: {pattern}") 