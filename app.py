import streamlit as st
from groq import Groq
import os

# Настройка страницы
st.set_page_config(page_title="AI Career Coach", page_icon="??", layout="wide")

# Безопасное получение ключа: сначала из секретов Streamlit, потом из переменных окружения
api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("? Ошибка: API-ключ Groq не найден. Проверьте настройки Secret в Streamlit Cloud.")
    st.stop()

client = Groq(api_key=api_key)

st.title("?? ИИ-Карьерный Консультант")
st.markdown("Вставьте текст резюме и описание вакансии, чтобы получить мгновенный разбор от ИИ.")

with st.sidebar:
    st.header("?? Настройки")
    model = st.selectbox("Модель ИИ", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    st.caption("Powered by Groq & Streamlit")

col1, col2 = st.columns(2)

with col1:
    st.subheader("?? Ваше резюме")
    resume_text = st.text_area("Вставьте текст резюме...", height=300, placeholder="Опыт работы, навыки, образование...")

with col2:
    st.subheader("?? Описание вакансии")
    job_description = st.text_area("Вставьте текст вакансии...", height=300, placeholder="Требования, обязанности, стек технологий...")

if st.button("?? Провести анализ", type="primary", use_container_width=True):
    if not resume_text.strip() or not job_description.strip():
        st.warning("Пожалуйста, заполните оба поля!")
    else:
        prompt = f"""
        Ты — эксперт HR и технический рекрутер. 
        Проанализируй резюме кандидата и описание вакансии.
        
        РЕЗЮМЕ:
        {resume_text}
        
        ВАКАНСИЯ:
        {job_description}
        
        Ответ СТРОГО в формате Markdown:
        1. **?? Match-рейтинг**: 0-100% + краткий вердикт.
        2. **? Сильные стороны**
        3. **?? Зоны роста**
        4. **?? Топ-5 вопросов для интервью** с подсказками
        5. **?? 3 совета по адаптации резюме**
        """
        
        with st.spinner("ИИ анализирует данные (это займет пару секунд)..."):
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "Ты полезный AI-ассистент. Отвечай структурированно, используй эмодзи."},
                        {"role": "user", "content": prompt}
                    ],
                    model=model,
                    temperature=0.3,
                    max_tokens=2048,
                )
                result = chat_completion.choices[0].message.content
                st.divider()
                st.subheader("?? Результат анализа")
                st.markdown(result)
            except Exception as e:
                st.error(f"? Ошибка API: {e}")