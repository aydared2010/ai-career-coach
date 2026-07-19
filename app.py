import streamlit as st
from groq import Groq
import os
import PyPDF2

# === НАСТРОЙКА СТРАНИЦЫ ===
st.set_page_config(page_title="AI Career Coach", page_icon="💼", layout="wide")

# === ПОДКЛЮЧЕНИЕ К GROQ ===
api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("Ошибка: API-ключ Groq не найден.")
    st.stop()
client = Groq(api_key=api_key)

# === ЗАГОЛОВОК ===
st.title("💼 ИИ-Карьерный Консультант")
st.markdown("Загрузите резюме и описание вакансии для мгновенного анализа от ИИ.")

# === БОКОВАЯ ПАНЕЛЬ ===
with st.sidebar:
    st.header("⚙️ Настройки")
    model = st.selectbox("Модель ИИ", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    st.divider()
    st.caption("✨ Новые возможности:")
    st.caption("• Загрузка PDF-резюме")
    st.caption("• Примеры для быстрого старта")
    st.caption("• Экспорт результата")
    st.caption("Powered by Groq & Streamlit")

# === ВВОД ДАННЫХ ===
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Ваше резюме")
    
    # УЛУЧШЕНИЕ 1: Загрузка PDF
    uploaded_file = st.file_uploader("Загрузите PDF-файл (необязательно)", type=["pdf"])
    
    if uploaded_file is not None:
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            resume_text = " ".join([page.extract_text() for page in pdf_reader.pages])
            st.success(f"✅ PDF успешно прочитан ({len(pdf_reader.pages)} стр.)")
            st.text_area("Извлеченный текст:", resume_text, height=200)
        except Exception as e:
            st.error(f"Не удалось прочитать PDF: {e}")
            resume_text = ""
    else:
        resume_text = st.text_area("Или вставьте текст резюме вручную...", height=250, placeholder="Опыт работы, навыки, образование...")

with col2:
    st.subheader("🎯 Описание вакансии")
    job_description = st.text_area("Вставьте текст вакансии...", height=300, placeholder="Требования, обязанности, стек технологий...")

# === КНОПКИ УПРАВЛЕНИЯ ===
btn_col1, btn_col2, btn_col3 = st.columns(3)

with btn_col1:
    # УЛУЧШЕНИЕ 2: Заполнить пример
    if st.button("📝 Заполнить пример", use_container_width=True):
        st.session_state.resume = """Python-разработчик, 3 года опыта.
Разработка REST API на FastAPI, работа с PostgreSQL и Redis.
Опыт работы с Docker, CI/CD (GitLab CI).
Знание SQL, REST, ООП, паттернов проектирования.
Английский — B2 (Upper-Intermediate)."""
        st.session_state.job = """Senior Python Developer
Требования:
- 5+ лет опыта на Python
- Опыт с Django или FastAPI
- Знание PostgreSQL, MongoDB
- Docker, Kubernetes
- Опыт менторинга junior-разработчиков
- Английский C1"""
        st.rerun()

# Применяем примеры из session_state
if "resume" in st.session_state and not resume_text:
    resume_text = st.session_state.resume
if "job" in st.session_state and not job_description:
    job_description = st.session_state.job

with btn_col2:
    analyze_clicked = st.button("🚀 Провести анализ", type="primary", use_container_width=True)

# === ЛОГИКА АНАЛИЗА ===
result = None
if analyze_clicked:
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
        1. **📊 Match-рейтинг**: 0-100% + краткий вердикт.
        2. **✅ Сильные стороны**
        3. **⚠️ Зоны роста**
        4. **🎤 Топ-5 вопросов для интервью** с подсказками
        5. **💡 3 совета по адаптации резюме**
        """

        with st.spinner("ИИ анализирует данные..."):
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
            except Exception as e:
                st.error(f"Ошибка API: {e}")

# === ВЫВОД РЕЗУЛЬТАТА ===
if result:
    st.divider()
    st.subheader("📝 Результат анализа")
    st.markdown(result)
    
    # УЛУЧШЕНИЕ 3: Кнопка скачивания
    st.download_button(
        label="📥 Скачать анализ (Markdown)",
        data=result,
        file_name="career_analysis.md",
        mime="text/markdown",
        use_container_width=True
    )
