"""
Mock LLM — dùng chung cho tất cả ví dụ.
Không cần API key thật. Trả lời giả lập để focus vào deployment concept.
"""
import time
import random


MOCK_RESPONSES = {
    "default": [
        "Chào bạn, tôi là Chuyên gia Tâm lý AI. Tôi luôn sẵn lòng lắng nghe bạn.",
        "Mọi cảm xúc của bạn đều hợp lệ. Hãy cứ thoải mái chia sẻ nhé.",
        "Tôi ở đây để hỗ trợ bạn tìm thấy sự an tĩnh trong tâm trí.",
    ],
    "docker": ["Container là cách đóng gói app để chạy ở mọi nơi. Build once, run anywhere!"],
    "deploy": ["Deployment là quá trình đưa code từ máy bạn lên server để người khác dùng được."],
    "health": ["Agent đang hoạt động bình thường. All hệ thống đều ổn định."],
    "stress": ["Khi bị căng thẳng, hãy thử hít thở sâu và dành 5 phút để thiền định. Bạn đang làm rất tốt rồi."],
    "tâm lý": ["Tâm lý học giúp chúng ta thấu hiểu sâu sắc hơn về hành vi và cảm xúc của chính mình."],
}


def ask(question: str, delay: float = 0.1) -> str:
    """
    Mock LLM call với delay giả lập latency thật.
    """
    time.sleep(delay + random.uniform(0, 0.05))  # simulate API latency

    question_lower = question.lower()
    for keyword, responses in MOCK_RESPONSES.items():
        if keyword in question_lower:
            return random.choice(responses)

    return random.choice(MOCK_RESPONSES["default"])


def ask_stream(question: str):
    """
    Mock streaming response — yield từng token.
    """
    response = ask(question)
    words = response.split()
    for word in words:
        time.sleep(0.05)
        yield word + " "
