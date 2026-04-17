# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. Lộ Hardcoded secrets: Các biến OPENAI_API_KEY và DATABASE_URL (chứa cả credential của PostgreSQL) được gắn cứng ngay trong source code -> rủi ro bảo mật nghiêm trọng; nếu code được push lên GitHub, key sẽ bị quét và bị lạm dụng ngay lập tức. Các thông tin này bắt buộc phải được nạp qua biến môi trường (Environment variables) hoặc các secret manager.
2. Thiếu hệ thống quản lý cấu hình: Các tham số hệ thống như DEBUG = True hay MAX_TOKENS = 500 đang bị hardcode. Khi vận hành hệ thống AI thực tế qua nhiều môi trường (Dev, Staging, Prod), thiết kế này triệt tiêu khả năng thay đổi hành vi của agent nếu không sửa trực tiếp source code. Giải pháp chuẩn là sử dụng các thư viện như pydantic-settings kết hợp file .env.
3. Sử dụng print sai mục đích và rò rỉ secret qua Log: Việc dùng print thay vì thư viện logging chuẩn (như loguru hoặc module logging của Python) khiến hệ thống không thể phân loại log (INFO, WARN, ERROR) khi monitor. Hơn nữa, dòng code print(f"[DEBUG] Using key: {OPENAI_API_KEY}") trực tiếp đẩy secret ra standard output, khiến key bị lưu lại vĩnh viễn trên các hệ thống thu thập log.
4. Không có health check endpoint: Ứng dụng hoàn toàn thiếu một route định tuyến trạng thái (ví dụ /health hoặc /ping). Khi agent được đóng gói chạy dưới dạng container (như Docker) hoặc quản lý bởi các cloud platform, hệ thống điều phối bắt buộc phải gọi endpoint này để kiểm tra xem tiến trình có đang phản hồi không. Nếu không có, hệ thống sẽ không biết để tự động restart khi agent bị crash hoặc treo.
5. Gắn cứng cấu hình khởi chạy mạng (Host, Port, Reload): * host="localhost": Khiến ứng dụng chỉ nhận request nội bộ, không thể giao tiếp ra ngoài (đặc biệt lỗi khi chạy trong container, host bắt buộc phải là 0.0.0.0).

port=8000: Gây xung đột và lỗi deploy trên các nền tảng cloud (như Railway) vì các hệ thống này yêu cầu ứng dụng listen trên một port động được cấp phát qua biến môi trường PORT.

reload=True: Đây là tính năng chỉ dành cho môi trường phát triển (Local/Dev). Nếu để lọt ra production, nó sẽ theo dõi file system liên tục, gây hao tổn tài nguyên nghiêm trọng và rò rỉ bộ nhớ.
...

### Exercise 1.3: Comparison table
### 2. So sánh Basic vs Advanced (12-Factor Compliant Agent)

| Feature | Basic | Advanced | Tại sao quan trọng? |
| :--- | :--- | :--- | :--- |
| **Config** | Hardcode | Env vars (`config.settings`) | Đảm bảo bảo mật thông tin nhạy cảm. Cho phép thay đổi hành vi hệ thống linh hoạt trên đa môi trường mà không cần sửa đổi source code. |
| **Health check** | Không có | Có (`/health`, `/ready`) | Là cơ chế giao tiếp bắt buộc với hệ thống điều phối (Kubernetes, Docker). Giúp tự động nhận diện agent bị treo để restart, hoặc chặn traffic vào agent chưa tải xong. |
| **Logging** | `print()` | Structured JSON (`logging`) | Cho phép phân loại mức độ sự kiện. Định dạng JSON giúp các công cụ (Datadog, ELK) dễ dàng parse, truy vấn và thiết lập cảnh báo tự động. Tránh rò rỉ secret. |
| **Shutdown** | Đột ngột | Graceful (Lifespan, SIGTERM) | Tránh tình trạng mất request khi hệ thống scale down. Cho phép agent có thời gian hoàn tất các request đang xử lý và đóng an toàn kết nối database/API. |
| **Network & Binding** | Cố định (`localhost:8000`, `reload=True`) | Động (`0.0.0.0`, port từ `$PORT`) | `0.0.0.0` bắt buộc để nhận traffic ngoài container. Port động giúp nền tảng Cloud tự động cấp phát không gây xung đột. Tắt `reload` tiết kiệm tài nguyên. |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
### 1. Base image là gì?
Base image được sử dụng trong file là `python:3.11`. Đây là bản phân phối đầy đủ (full distribution) của Python, có dung lượng khá lớn (khoảng 1 GB).

### 2. Working directory là gì?
Working directory (thư mục làm việc mặc định bên trong container) được thiết lập là `/app`. Mọi câu lệnh `COPY`, `RUN`, hay `CMD` phía sau sẽ được thực thi tại thư mục này.

### 3. Tại sao COPY requirements.txt trước?
Thao tác này nhằm tối ưu hóa cơ chế **Docker layer cache**. 

Trong quá trình develop, mã nguồn ứng dụng sẽ thay đổi liên tục, trong khi danh sách các thư viện (`requirements.txt`) ít bị cập nhật hơn. Bằng cách copy `requirements.txt` và chạy `pip install` trước, Docker sẽ lưu lại (cache) layer chứa các thư viện này. Nếu lần build tiếp theo chỉ sửa code (không sửa `requirements.txt`), Docker sẽ sử dụng lại cache cũ thay vì phải tải và cài đặt lại toàn bộ thư viện từ đầu, giúp tiết kiệm tối đa thời gian build.

### 4. CMD vs ENTRYPOINT khác nhau thế nào?

- **CMD (Command):** Định nghĩa lệnh và tham số mặc định khi container khởi chạy. Điểm yếu là nó **rất dễ bị ghi đè** (override). Ví dụ: nếu bạn chạy `docker run <image_name> /bin/bash`, lệnh `/bin/bash` sẽ lập tức thay thế hoàn toàn lệnh `python app.py`.
- **ENTRYPOINT:** Cấu hình container chạy như một file thực thi cố định. Lệnh trong `ENTRYPOINT` **không bị ghi đè** bởi các tham số truyền qua `docker run` (trừ khi cố tình dùng cờ `--entrypoint`). Các tham số từ `docker run` sẽ được tự động nối vào phía sau chuỗi lệnh của `ENTRYPOINT` như những arguments phụ. 

**Best practice:** Thường dùng `ENTRYPOINT` để khai báo tệp thực thi chính (vd: `ENTRYPOINT ["python", "app.py"]`) và dùng `CMD` để truyền các tham số mặc định có thể thay đổi được (vd: `CMD ["--port", "8000"]`).

### Exercise 2.3: Image size comparison
- Develop: 424 MB
- Production: 56.6 MB
- Difference: 86.6%

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://your-app.railway.app
- Screenshot: [Link to screenshot in repo]

## Part 4: API Security

### Exercise 4.1-4.3: Test results
[Paste your test outputs]

### Exercise 4.4: Cost guard implementation
[Explain your approach]

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
[Your explanations and test results]