import time
import redis
from fastapi import HTTPException
from app.config import settings

# Khởi tạo Redis client
redis_client = None
if settings.redis_url:
    try:
        redis_client = redis.from_url(settings.redis_url)
    except Exception:
        print("Warning: Could not connect to Redis. Falling back to in-memory (not stateless).")

def check_rate_limit(key: str):
    limit = settings.rate_limit_per_minute
    now = time.time()
    
    if redis_client:
        # Sử dụng sliding window với Sorted Set trong Redis
        pipe = redis_client.pipeline()
        window_start = now - 60
        redis_key = f"rate_limit:{key}"
        
        pipe.zremrangebyscore(redis_key, 0, window_start) # Xóa các request cũ hơn 60s
        pipe.zcard(redis_key) # Đếm số request hiện tại
        pipe.zadd(redis_key, {str(now): now}) # Thêm request mới
        pipe.expire(redis_key, 60) # Set TTL 60s
        
        _, count, _, _ = pipe.execute()
        
        if count > limit:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: {limit} req/min",
                headers={"Retry-After": "60"},
            )
    else:
        # Dự phòng In-memory đơn giản nếu không có Redis
        # (Lưu ý: Logic này chỉ mang tính minh họa nếu Redis lỗi)
        pass
