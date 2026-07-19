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

# === ИНИЦИАЛИЗАЦИЯ SESSION STATE ===
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "job_description" not in st.session_state:
    st.session_state.job_description = ""
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

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

# === КНОПКА ПРИМЕРА ===
if st.button("📝 Заполнить пример", use_container_width=True):
    example_resume = "Python-разработчик, 3 года опыта.\nРазработка REST API на FastAPI, работа с PostgreSQL и Redis.\nОпыт работы с Docker, CI/CD (GitLab CI).\nЗнание SQL, REST, ООП, паттернов проектирования.\nАнглийский — B2 (Upper-Intermediate)."
    example_job = "Senior Python Developer\nТребования:\n- 5+ лет опыта на Python\n- Опыт с Django или FastAPI\n- Знание PostgreSQL, MongoDB\n- Docker, Kubernetes\n- Опыт менторинга junior-разработчиков\n- Английский C1"
    st.session_state.resume_text = example_resume
    st.session_state.job_description = example_job
    st.rerun()

# === ВВОД ДАННЫХ ===
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Ваше резюме")
    uploaded_file = st.file_uploader("Загрузите PDF-файл (необязательно)", type=["pdf"])
    
    if uploaded_file is not None:
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            pdf_text = " ".join([page.extract_text() for page in pdf_reader.pages])
            st.session_state.resume_text = pdf_text
            st.success(f"✅ PDF успешно прочитан ({len(pdf_reader.pages)} стр.)")
        except Exception as e:
            st.error(f"Не удалось прочитать PDF: {e}")
    
    resume_text = st.text_area(
        "Или вставьте текст резюме вручную...",
        value=st.session_state.resume_text,
        height=250,
        placeholder="Опыт работы, навыки, образование...",
        key="resume_area"
    )
    st.session_state.resume_text = resume_text

with col2:
    st.subheader("🎯 Описание вакансии")
    job_description = st.text_area(
        "Вставьте текст вакансии...",
        value=st.session_state.job_description,
        height=300,
        placeholder="Требования, обязанности, стек технологий...",
        key="job_area"
    )
    st.session_state.job_description = job_description

# === КНОПКА АНАЛИЗА ===
if st.button("🚀 Провести анализ", type="primary", use_container_width=True):
    if not st.session_state.resume_text.strip() or not st.session_state.job_description.strip():
        st.warning("Пожалуйста, заполните оба поля!")
    else:
        prompt_text = "Ты — эксперт HR и технический рекрутер.\n"
        prompt_text += "Проанализируй резюме кандидата и описание вакансии.\n\n"
        prompt_text += "РЕЗЮМЕ:\n" + st.session_state.resume_text + "\n\n"
        prompt_text += "ВАКАНСИЯ:\n" + st.session_state.job_description + "\n\n"
        prompt_text += "Ответ СТРОГО в формате Markdown:\n"
        prompt_text += "1. **📊 Match-рейтинг**: 0-100% + краткий вердикт.\n"
        prompt_text += "2. **✅ Сильные стороны**\n"
        prompt_text += "3. **⚠️ Зоны роста**\n"
        prompt_text += "4. **🎤 Топ-5 вопросов для интервью** с подсказками\n"
        prompt_text += "5. **💡 3 совета по адаптации резюме**"

        with st.spinner("ИИ анализирует данные..."):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "Ты полезный AI-ассистент. Отвечай структурированно, используй эмодзи."
                        },
                        {
                            "role": "user",
                            "content": prompt_text
                        }
                    ],
                    temperature=0.3,
                    max_tokens=2048
                )
                st.session_state.analysis_result = response.choices[0].message.content
            except Exception as e:
                st.error(f"Ошибка API: {e}")

# === ВЫВОД РЕЗУЛЬТАТА ===
if st.session_state.analysis_result:
    st.divider()
    st.subheader("📝 Результат анализа")
    st.markdown(st.session_state.analysis_result)
    
    st.download_button(
        label="📥 Скачать анализ (Markdown)",
        data=st.session_state.analysis_result,
        file_name="career_analysis.md",
        mime="text/markdown",
        use_container_width=True
    )
