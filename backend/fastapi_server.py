from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import requests
from datetime import datetime

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2:3b"
MODEL_NAME = os.getenv("OLLAMA_MODEL", DEFAULT_MODEL)

class TripRequest(BaseModel):
    origin: str
    destination: str
    start_date: str
    end_date: str
    interests: list[str]
    pace: str

def build_itinerary_prompt(trip: TripRequest) -> str:
    interests_str = ", ".join(trip.interests)
    start = datetime.fromisoformat(trip.start_date)
    end = datetime.fromisoformat(trip.end_date)
    num_days = (end - start).days + 1
    if num_days < 1:
        num_days = 1  
    if num_days == 1:
        day_rule = (
            "Chuyến đi chỉ diễn ra trong **1 ngày**. "
            "Hãy tạo lịch trình cho **duy nhất Ngày 1** (không được tạo Ngày 2, Ngày 3...)."
        )
    else:
        day_rule = (
            f"Chuyến đi kéo dài **{num_days} ngày**. "
            f"Hãy tạo lịch trình từ **Ngày 1** đến **Ngày {num_days}**, "
            "không được thêm hoặc bớt ngày."
        )
    prompt = f"""
Bạn là một trợ lý du lịch thông minh, **trả lời hoàn toàn bằng tiếng Việt**.
Thông tin chuyến đi:
- Điểm xuất phát: {trip.origin}
- Điểm đến: {trip.destination}
- Thời gian: từ {trip.start_date} đến {trip.end_date} (tổng cộng {num_days} ngày)
- Sở thích: {interests_str}
- Nhịp độ chuyến đi: {trip.pace} (relaxed = thư thả, normal = bình thường, tight = dày đặc)
{day_rule}
Yêu cầu:
- Lập lịch trình chi tiết theo từng ngày.
- Mỗi ngày phải có 3 phần: **Buổi sáng**, **Buổi chiều**, **Buổi tối**.
- Ở MỖI phần (sáng/chiều/tối), hãy viết 3–5 gạch đầu dòng.
- Mỗi gạch đầu dòng phải có **giờ + hoạt động**, ví dụ: `8:00 – Ăn sáng tại quán phở nổi tiếng gần khách sạn`.
- Nội dung ngắn gọn, thực tế, phù hợp với sở thích đã cho.
- Định dạng bằng Markdown:
  - `## Ngày 1: ...`
  - `### Buổi sáng`
  - `- 8:00 – ...`
  - `### Buổi chiều`
  - `### Buổi tối`
Quan trọng:
- **Chỉ dùng tiếng Việt**, xưng “bạn” với người dùng.
- Không giải thích thêm về cách bạn suy nghĩ, chỉ in ra lịch trình hoàn chỉnh.
"""
    return prompt
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"hello": "world"}

@app.post("/itinerary")
async def itinerary(trip: TripRequest):
    prompt = build_itinerary_prompt(trip)
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
    }
    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=300)
        r.raise_for_status()
        data = r.json()
        return {"ok": True, "itinerary": data.get("response", "")}
    except Exception as e:
        return {"ok": False, "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
