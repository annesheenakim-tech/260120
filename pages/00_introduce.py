import streamlit as st

st.set_page_config(page_title="자기소개", page_icon="👋", layout="centered")

# ✅ 여기만 필요하면 바꿔도 됨 (그대로 둬도 바로 동작)
NAME = "Shinah Kim"
ONE_LINER = "안녕하세요! 반갑습니다 🙂"
INTRO = (
    "저는 사람의 마음과 행동을 이해하는 심리·뇌과학 관점과 "
    "비즈니스 관점을 연결해, 실제로 작동하는 아이디어를 만드는 걸 좋아해요."
)

# 외부 이미지 URL(추가 파일 없이 streamlit.io에서 바로 표시됨)
PHOTO_URL = "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=900&q=80"

st.title("👋 자기소개")

col1, col2 = st.columns([1, 2], vertical_alignment="center")

with col1:
    st.image(PHOTO_URL, use_container_width=True)

with col2:
    st.subheader(NAME)
    st.write(ONE_LINER)
    st.write(INTRO)

st.divider()

st.subheader("짧은 인사")
st.success("오늘도 좋은 하루 보내요! 여기까지 와준 것만으로도 이미 멋진 시작이에요.")

st.subheader("키워드")
st.write("🧠 정서·자기조절 · 📈 전략/마케팅 · 🚀 MVP 제작 · ✨ 웰빙/디지털 헬스")

st.subheader("연락")
c1, c2, c3 = st.columns(3)
with c1:
    st.link_button("Email", "mailto:hello@example.com")
with c2:
    st.link_button("GitHub", "https://github.com/")
with c3:
    st.link_button("LinkedIn", "https://www.linkedin.com/")

st.caption("© 2026 · Built with Streamlit")
