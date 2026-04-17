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
        pass

def check_and_record_cost(input_tokens: int, output_tokens: int):
    today = time.strftime("%Y-%m-%d")
    budget = settings.daily_budget_usd
    
    # Tính chi phí estimate (ví dụ giá gpt-4o-mini)
    cost = (input_tokens / 1000) * 0.00015 + (output_tokens / 1000) * 0.0006
    
    if redis_client:
        cost_key = f"daily_cost:{today}"
        
        # Increment cost và kiểm tra budget
        current_cost = redis_client.get(cost_key)
        current_cost = float(current_cost) if current_cost else 0.0
        
        if current_cost >= budget:
            raise HTTPException(503, "Daily budget exhausted. Try tomorrow.")
            
        redis_client.incrbyfloat(cost_key, cost)
        redis_client.expire(cost_key, 86400 * 2) # Giữ log 2 ngày
    else:
        # Fallback logic in case of no redis (for testing)
        pass
