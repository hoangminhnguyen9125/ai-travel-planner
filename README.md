# AI Travel Planner
AI Travel Planner using **FastAPI + Streamlit + Ollama**  
Ứng dụng tạo lịch trình du lịch bằng AI, chạy hoàn toàn **local** trên máy người dùng .

## 1. Chức năng
- Nhập:
  - Điểm xuất phát
  - Điểm đến 
  - Ngày bắt đầu / ngày kết thúc
  - Sở thích (food, nature, museums, shopping,…)
  - Nhịp độ chuyến đi: `relaxed`, `normal`, `tight`
- AI sẽ tạo:
  - Lịch trình chi tiết từng ngày
  - Lịch sử các chuyến đi trước sẽ được lưu lạilại
  - Có thể bấm vào từng mục trong “Lịch sử các chuyến trước” để xem lại chi tiết

## 2. Cách chạy chương trình
- Đã cài đặt python và ollama
- Trên Anaconda Prompt (hoặc terminal) chạy: pip install -r requirements.txt
- Tải model của ollama trên Anaconda Prompt (hoặc terminal) chạy : ollama pull llama3.2:3b
 ( Mặc định chương trình dùng model llama3.2:3b vì nhẹ)
- Nếu người dùng dùng model khác (ví dụ llama3) thì trước khi chạy backend cần chạy: set OLLAMA_MODEL=llama3
- Trên Anaconda Prompt (hoặc terminal) chạy: python backend/fastapi_server.py
- Mở Anaconda Prompt (hoặc terminal) mới, không đóng cái cũ ở trên 
- Trên Anaconda Prompt (hoặc terminal) mới, chạy: streamlit run frontend/app.py