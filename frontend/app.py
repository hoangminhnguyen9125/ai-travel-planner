import streamlit as st
import requests
from datetime import date

st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide",
)
st.title("✈️ AI Travel Planner")

if "history" not in st.session_state:
    st.session_state.history = []          
if "last_itinerary" not in st.session_state:
    st.session_state.last_itinerary = ""

st.sidebar.header("Backend status")
base_url = st.sidebar.text_input(
    "Base URL:",
    value="http://localhost:8000",
    help="Địa chỉ FastAPI backend (mặc định là localhost:8000)",
)
backend_ok = False
if base_url:
    try:
        r = requests.get(base_url, timeout=3)
        if r.status_code == 200:
            backend_ok = True
    except Exception:
        backend_ok = False

st.sidebar.checkbox("Backend online", value=backend_ok, disabled=True)
col_left, col_right = st.columns([1, 1.4])
with col_left:
    st.subheader("Thông tin chuyến đi")
    origin = st.text_input("Điểm xuất phát (origin)", value="Ho Chi Minh City")
    destination = st.text_input("Điểm đến (destination)", value="Da Nang")
    today = date.today()
    start_date = st.date_input(
        "Ngày bắt đầu",
        value=today,
        min_value=today,          
        key="start_date",
    )
    end_date = st.date_input(
        "Ngày kết thúc",
        value=start_date,
        min_value=start_date,     
        key="end_date",
    )
  
    interests_raw = st.text_input(
        "Sở thích",
        value="food, nature",
    )
    interests_list = [x.strip() for x in interests_raw.split(",") if x.strip()]
    pace = st.radio(
        "Nhịp độ ",
        options=["relaxed", "normal", "tight"],
        index=1,
        horizontal=False,
    )
    st.markdown("### ")
    if st.button("Tạo lịch trình"):
        if not backend_ok:
            st.error("Backend hiện không online. Hãy kiểm tra FastAPI server (cổng 8000).")
        elif start_date < today:
            st.error("Ngày bắt đầu không được nhỏ hơn hôm nay.")
        elif end_date < start_date:
            st.error("Ngày kết thúc phải lớn hơn hoặc bằng ngày bắt đầu.")
        else:
            payload = {
                "origin": origin,
                "destination": destination,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "interests": interests_list,
                "pace": pace,
            }
            st.info("Đang gọi AI, vui lòng chờ...")
            try:
                r = requests.post(f"{base_url}/itinerary", json=payload, timeout=600)
                r.raise_for_status()
                data = r.json()
            except Exception as e:
                st.error(f"Lỗi khi gọi backend: {e}")
            else:
                if data.get("ok"):
                    itinerary = data.get("itinerary", "")
                    if not itinerary:
                        st.warning("Backend trả về rỗng.")
                    else:
                        st.session_state.last_itinerary = itinerary
                        summary = (
                            f"{origin} → {destination} "
                            f"({start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')}) "
                            f"– {pace}"
                        )
                        st.session_state.history.insert(
                            0,
                            {
                                "summary": summary,
                                "payload": payload,
                                "itinerary": itinerary,
                            },
                        )
                        st.success("Đã tạo lịch trình mới thành công!")
                else:
                    st.error(f"Backend trả về lỗi: {data.get('error', 'Không rõ nguyên nhân')}")

with col_right:
    st.subheader("Lịch sử các chuyến trước")
    history = st.session_state.history
    if not history:
        st.write("Chưa có lịch sử.")
    else:
        for i, item in enumerate(history):
            if isinstance(item, dict) and "trip" in item:
                trip = item["trip"]
                itinerary = item.get("itinerary", "")
            elif isinstance(item, dict) and "payload" in item:
                trip = item["payload"]
                itinerary = item.get("itinerary", "")
            else:
                trip = item if isinstance(item, dict) else {}
                itinerary = item.get("itinerary", "") if isinstance(item, dict) else str(item)
            origin      = trip.get("origin", "Unknown")
            destination = trip.get("destination", "Unknown")
            start_date  = trip.get("start_date", "?")
            end_date    = trip.get("end_date", "?")

            label = f"{origin} -> {destination} ({start_date} -> {end_date})"
            with st.expander(label):
                st.markdown(itinerary or "_Không có dữ liệu lịch trình_")
