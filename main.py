import streamlit as st
st.title("김신아 첫 웹앱")
st.write('안녕하세요! 반갑습니다!')

import pandas as pd

# ---- 데이터(예시) ----
# 실제 서비스에선 DB/스프레드시트/JSON으로 분리 추천
MBTI_JOBS = {
    "INTJ": [
        {"직업": "전략 컨설턴트", "이유": "복잡한 문제를 구조화하고 장기 전략을 설계하는 데 강점"},
        {"직업": "데이터 사이언티스트", "이유": "가설 기반 분석과 모델링을 즐기는 경향"},
        {"직업": "프로덕트 매니저", "이유": "큰 그림을 그리며 제품 방향성을 설계"},
    ],
    "INTP": [
        {"직업": "연구원(R&D)", "이유": "개념 탐구/이론화/실험 설계에 몰입"},
        {"직업": "소프트웨어 엔지니어", "이유": "논리적 문제 해결과 시스템 설계에 흥미"},
        {"직업": "퀀트/리서처", "이유": "수학적 모델로 현상을 설명하려는 성향"},
    ],
    "ENTJ": [
        {"직업": "사업개발(BD)", "이유": "목표 중심 실행과 협상/의사결정에 강점"},
        {"직업": "영업 리더", "이유": "성과 관리와 조직 드라이브에 능숙"},
        {"직업": "프로젝트 리더/PMO", "이유": "자원 배분과 일정/리스크 관리"},
    ],
    "ENFP": [
        {"직업": "브랜드/마케팅", "이유": "스토리텔링과 아이디어 발산, 사람 중심"},
        {"직업": "콘텐츠 크리에이터", "이유": "표현/기획/커뮤니케이션 에너지"},
        {"직업": "HR(조직문화)", "이유": "사람/동기/관계에 관심이 높음"},
    ],
}

# 누락 MBTI를 위한 기본 추천(예시)
DEFAULT_JOBS = [
    {"직업": "프로젝트 코디네이터", "이유": "협업/조율을 통해 실행력을 키우기 좋음"},
    {"직업": "데이터/리서치 어시스턴트", "이유": "탐색→가설→검증 루틴에 익숙해짐"},
    {"직업": "고객경험(CX) 기획", "이유": "사용자 관찰 기반으로 개선을 만드는 역할"},
]

MBTI_LIST = [
    "ISTJ","ISFJ","INFJ","INTJ",
    "ISTP","ISFP","INFP","INTP",
    "ESTP","ESFP","ENFP","ENTP",
    "ESTJ","ESFJ","ENFJ","ENTJ"
]

# ---- UI ----
st.set_page_config(page_title="MBTI 직업 추천", page_icon="💼", layout="centered")
st.title("💼 MBTI 기반 직업 추천")
st.caption("MBTI는 참고용 성향 지표예요. 관심/역량/경험과 함께 보정해서 쓰면 정확도가 올라가요.")

with st.sidebar:
    st.header("옵션")
    top_n = st.slider("추천 개수", 1, 10, 3)
    show_reason = st.toggle("추천 이유 보기", value=True)

st.subheader("1) MBTI를 선택하세요")
mbti = st.selectbox("MBTI", MBTI_LIST, index=3)

st.subheader("2) 추천 결과")
jobs = MBTI_JOBS.get(mbti, DEFAULT_JOBS)[:top_n]

df = pd.DataFrame(jobs)
if not show_reason and "이유" in df.columns:
    df = df.drop(columns=["이유"])

st.dataframe(df, use_container_width=True)

st.markdown("---")
st.subheader("3) 개인화(간단 버전)")
col1, col2 = st.columns(2)
with col1:
    interest = st.text_input("관심 분야(예: 마케팅, 데이터, 상담, 헬스케어)", "")
with col2:
    strength = st.text_input("강점(예: 분석, 커뮤니케이션, 리더십)", "")

if st.button("개인화 추천 힌트 생성"):
    # 아주 단순한 룰 기반 예시 (서비스화 시 규칙/모델로 고도화)
    hints = []
    if interest:
        hints.append(f"- 관심 분야 **{interest}** 쪽으로 추천 결과를 필터링/재정렬해보세요.")
    if strength:
        hints.append(f"- 강점 **{strength}** 가 잘 쓰이는 직무(예: 기획/PM, 컨설팅, 분석, 영업)를 우선 탐색해보세요.")
    if not hints:
        hints.append("- 관심/강점 입력하면 추천을 더 날카롭게 커스터마이즈할 수 있어요.")
    st.markdown("\n".join(hints))

st.markdown("---")
st.caption("데이터는 예시입니다. MBTI_JOBS를 늘리거나 CSV/DB로 분리하면 서비스 품질이 크게 올라가요.")

