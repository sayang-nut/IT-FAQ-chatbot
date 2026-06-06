# app/llm.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

SYSTEM_ROLE = """Bạn là IT Support Assistant thân thiện của công ty.
Nhiệm vụ: trả lời câu hỏi IT của nhân viên dựa HOÀN TOÀN vào tài liệu nội bộ được cung cấp.
Quy tắc:
- Chỉ dùng thông tin trong phần [TÀI LIỆU NỘI BỘ], không tự bịa thêm.
- Trả lời ngắn gọn, rõ ràng, thân thiện.
- Nếu tài liệu không đủ thông tin, hướng dẫn liên hệ IT Helpdesk ext. 100.
- Trả lời bằng cùng ngôn ngữ với câu hỏi (Việt hoặc Anh)."""

def build_prompt(user_question: str, relevant_docs: list[dict]) -> str:
    if not relevant_docs:
        context = "Không tìm thấy tài liệu liên quan."
    else:
        context_parts = []
        for doc in relevant_docs:
            item = doc["item"]
            context_parts.append(
                f"[{item['category']}] {item['question']}\n→ {item['answer']}"
            )
        context = "\n\n".join(context_parts)

    return f"""{SYSTEM_ROLE}

[TÀI LIỆU NỘI BỘ]
{context}

[CÂU HỎI CỦA NHÂN VIÊN]
{user_question}

[TRẢ LỜI]"""


def generate_answer(user_question: str, relevant_docs: list[dict]) -> str:
    # Nếu không có doc nào → trả lời mặc định, không gọi API
    if not relevant_docs:
        return (
            "Xin lỗi, tôi không tìm thấy thông tin phù hợp trong tài liệu nội bộ. "
            "Vui lòng liên hệ IT Helpdesk trực tiếp:\n"
            "📞 Ext. 100\n📧 it-support@company.com"
        )

    prompt = build_prompt(user_question, relevant_docs)

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[LLM] Gemini error: {e}")
        return (
            "Hệ thống AI tạm thời gặp sự cố. "
            "Vui lòng liên hệ IT Helpdesk: Ext. 100."
        )