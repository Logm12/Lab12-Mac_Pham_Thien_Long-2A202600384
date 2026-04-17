# Deployment Information

## Public URL
https://lab12-production-5585.up.railway.app

## Platform
Railway

## Test Commands

### Health Check
```bash
curl https://lab12-production-5585.up.railway.app/health
```

### Readiness Check
```bash
curl ttps://lab12-production-5585.up.railway.app/ready
```

### API Test (with authentication)
```bash
curl -X POST ttps://lab12-production-5585.up.railway.app/ask \
  -H "X-API-Key: my-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
```

## Environment Variables Set
- PORT: Port mà ứng dụng listen (mặc định 8080 trên Railway)
- REDIS_URL: Kết nối tới Redis instance (để stateless)
- AGENT_API_KEY: Key bảo mật để truy cập API
- LOG_LEVEL: Mức độ ghi log (INFO/DEBUG)
- DAILY_BUDGET_USD: Hạn mức chi phí mỗi ngày

## Screenshots
- [Deployment dashboard](extras/railway-deployment.png)
- [Service running](extras/railway-deployment-status.png)
- [Test results](extras/API-Security-with-key.png)
