import random
import streamlit as st

st.set_page_config(page_title="영어 이름 추천기", page_icon="🪪", layout="centered")

# -----------------------------
# 데이터: 이름 풀(예시)
# - 실제 서비스에선 JSON/DB로 분리 추천
# -----------------------------
NAME_POOL = {
    # 에너지/이미지 기반
    "calm": {
        "neutral": ["Avery", "Rowan", "Sage", "Morgan", "Quinn", "Blake", "Taylor"],
        "female":  ["Serena", "Luna", "Iris", "Clara", "Evelyn", "Noelle", "Celine"],
        "male":    ["Ethan", "Noah", "Leo", "Julian", "Miles", "Adrian", "Caleb"],
    },
    "bright": {
        "neutral": ["Sunny", "Skyler", "Harper", "Emerson", "Reese", "Jordan", "Riley"],
        "female":  ["Chloe", "Zoe", "Mia", "Lily", "Ella", "Sophie", "Nina"],
        "male":    ["Jack", "Ryan", "Luke", "Owen", "Kai", "Logan", "Aiden"],
    },
    "strong": {
        "neutral": ["Parker", "Cameron", "Drew", "Casey", "Reagan", "Hayden", "Bailey"],
        "female":  ["Vera", "Athena", "Valerie", "Hazel", "Freya", "Scarlett", "Brielle"],
        "male":    ["Max", "Alexander", "Hunter", "Lucas", "Nolan", "Victor", "Damian"],
    },
    "warm": {
        "neutral": ["Jamie", "Charlie", "Sam", "Alex", "Robin", "Shawn", "Lee"],
        "female":  ["Amelia", "Grace", "Hannah", "Emma", "Olivia", "Elena", "Lucy"],
        "male":    ["Henry", "Ben", "James", "William", "Daniel", "Theo", "Matthew"],
    },
    "intellectual": {
        "neutral": ["Ellis", "Alden", "Arden", "Remy", "Finley", "Frankie", "Noel"],
        "female":  ["Ivy", "Audrey", "Cora", "Ada", "Violet", "Sylvia", "Marina"],
        "male":    ["Felix", "Arthur", "Elliot", "Silas", "Isaac", "Hugo", "Theo"],
    },
    "artsy": {
        "neutral": ["River", "Indigo", "Phoenix", "Kai", "Nova", "Wren", "Marley"],
        "female":  ["Aria", "Isla", "Willow", "Aurora", "Daisy", "Jade", "Sienna"],
        "male":    ["Jasper", "Milo", "Ezra", "Asher", "Leo", "Finn", "Theo"],
    },
    "classic": {
        "neutral": ["Jordan", "Taylor", "Casey", "Alex", "Jamie", "Morgan", "Cameron"],
        "female":  ["Elizabeth", "Katherine", "Victoria", "Charlotte", "Caroline", "Jane", "Anna"],
        "male":    ["Michael", "Christopher", "Andrew", "Nicholas", "Jonathan", "Thomas", "Benjamin"],
    },
    "modern": {
        "neutral": ["Avery", "Riley", "Quinn", "Emerson", "Harper", "Logan", "Rowan"],
        "female":  ["Ava", "Mila", "Layla", "Harper", "Nova", "Hazel", "Isla"],
        "male":    ["Liam", "Mason", "Ethan", "Noah", "Aiden", "Lucas", "Wyatt"],
    },
}

# 이름별 발음 힌트(원하면 계속 확장)
PRON_HINT = {
    "Avery": "에이-버리",
    "Rowan": "로-언",
    "Sage": "세이지",
    "Quinn": "퀸",
    "Serena": "서-리나",
    "Julian": "줄리언",
    "Chloe": "클로이",
    "Zoe": "조이",
    "Felix": "필릭스",
    "Arthur": "아서",
    "Aurora": "오-로라",
    "Jasper": "재스퍼",
    "Liam": "리엄",
    "Wyatt": "와이엇",
}

# 성격 키워드 → 추천 태그 매핑
KEYWORD_TO_TAGS = {
    "차분": ["calm"],
    "조용": ["calm"],
    "따뜻": ["warm"],
    "친절": ["warm"],
    "밝": ["bright"],
    "긍정": ["bright"],
    "리더": ["strong"],
    "강단": ["strong"],
    "똑똑": ["intellectual"],
    "논리": ["intellectual"],
    "분석": ["intellectual"],
    "감성": ["artsy", "warm"],
    "창의": ["artsy"],
    "예술": ["artsy"],
    "클래식": ["classic"],
    "전통": ["classic"],
    "모던": ["modern"],
    "세련": ["modern"],
}

ALL_TAGS = list(NAME_POOL.keys())
GENDER_MAP = {"선택 안 함(중성 포함)": "neutral", "여성": "female", "남성": "male"}

def extract_tags(text: str) -> list[str]:
    text = (text or "").strip()
    if not text:
        return []
    hits = []
    for kw, tags in KEYWORD_TO_TAGS.items():
        if kw in text:
            hits.extend(tags)
    # 중복 제거 + 순서 유지
    seen = set()
    out = []
    for t in hits:
        if t not in seen:
            out.append(t)
            seen.add(t)
    return out

def score_name(name: str, prefer_short: bool, prefer_unique: bool) -> float:
    """
    아주 단순한 가점 로직:
    - 짧은 이름 선호: 글자 수가 짧을수록 가점
    - 유니크 선호: 흔한 느낌(클래식/초보자용)보다 특별 느낌에 가점 (대략적)
    """
    s = 0.0
    if prefer_short:
        s += max(0, 8 - len(name)) * 0.2  # 짧을수록 점수↑
    if prefer_unique:
        # 대충 "classic"스러운 매우 흔한 이름들은 약간 감점 (완벽하지 않음)
        common = {"Michael", "Christopher", "Andrew", "Thomas", "Elizabeth", "Jane", "Anna"}
        if name in common:
            s -= 1.0
        else:
            s += 0.6
    return s

def pick_names(tags: list[str], gender_key: str, n: int, prefer_short: bool, prefer_unique: bool) -> list[dict]:
    # 태그가 없으면 전체에서 추천
    candidate_tags = tags if tags else ALL_TAGS

    candidates = []
    for t in candidate_tags:
        # 성별 선택이 "neutral"이면: neutral만 쓰면 선택폭이 너무 좁아질 수 있어
        # 그래서 neutral 선택 시에는 neutral + (female/male 일부)도 섞어줌 (앱 취지에 맞게 조정 가능)
        if gender_key == "neutral":
            pool = NAME_POOL[t]["neutral"] + NAME_POOL[t]["female"] + NAME_POOL[t]["male"]
        else:
            pool = NAME_POOL[t][gender_key] + NAME_POOL[t]["neutral"]
        for nm in pool:
            candidates.append((t, nm))

    # 중복 제거(태그만 다르게 같은 이름 들어갈 수 있음)
    seen = set()
    unique_candidates = []
    for t, nm in candidates:
        if nm not in seen:
            unique_candidates.append((t, nm))
            seen.add(nm)

    # 점수화 후 상위권에서 랜덤하게 뽑기
    scored = []
    for t, nm in unique_candidates:
        scored.append((t, nm, score_name(nm, prefer_short, prefer_unique)))

    scored.sort(key=lambda x: x[2], reverse=True)

    # 상위 pool_size개에서 랜덤 샘플링 (항상 같지 않게)
    pool_size = min(len(scored), max(n * 6, 20))
    top = scored[:pool_size]
    random.shuffle(top)

    results = top[:n]
    out = []
    for t, nm, sc in results:
        out.append({
            "name": nm,
            "tag": t,
            "why": tag_to_reason(t),
            "pron": PRON_HINT.get(nm, "발음 힌트 준비중"),
        })
    return out

def tag_to_reason(tag: str) -> str:
    reasons = {
        "calm": "차분하고 안정적인 인상을 주는 톤",
        "bright": "밝고 경쾌한 에너지의 톤",
        "strong": "자신감 있고 단단한 인상의 톤",
        "warm": "친근하고 따뜻한 분위기의 톤",
        "intellectual": "지적이고 신뢰감 있는 느낌의 톤",
        "artsy": "감각적이고 유니크한 분위기의 톤",
        "classic": "전통적이고 격식 있는 클래식 톤",
        "modern": "세련되고 트렌디한 모던 톤",
    }
    return reasons.get(tag, "선택한 성격/톤과 어울리는 느낌")

# -----------------------------
# UI
# -----------------------------
st.title("🪪 성격 기반 영어 이름 추천")
st.caption("성격 키워드/원하는 분위기를 적으면, 어울리는 영어 이름 후보와 이유를 추천해줘요.")

with st.sidebar:
    st.header("설정")
    n = st.slider("추천 개수", 3, 20, 8)
    gender_label = st.selectbox("이름 성별 톤", list(GENDER_MAP.keys()), index=0, key="gender")
    prefer_short = st.toggle("짧고 부르기 쉬운 이름 선호", value=True)
    prefer_unique = st.toggle("유니크한 이름 선호", value=False)
    show_pron = st.toggle("발음 힌트 표시", value=True)
    show_tag = st.toggle("분위기 태그 표시", value=True)

st.subheader("1) 성격/분위기 입력")
text = st.text_area(
    "예: 차분하고 지적인데 따뜻한 느낌 / 밝고 사교적인 느낌 / 세련되고 모던한 느낌",
    height=80,
    key="personality_text",
)

st.subheader("2) 스타일 선택(선택)")
style = st.multiselect(
    "원하는 분위기 태그를 직접 고를 수도 있어요(선택).",
    options=ALL_TAGS,
    default=[],
)

# 자동 추출 태그
auto_tags = extract_tags(text)
merged_tags = []
# 사용자 선택 style 우선, 없으면 auto 사용, 둘 다 있으면 합치기
if style:
    merged_tags = style
elif auto_tags:
    merged_tags = auto_tags
else:
    merged_tags = []

st.write("인식된 분위기 태그:", merged_tags if merged_tags else "입력 기반 자동/수동 태그가 없어서 전체에서 추천할게요.")

st.markdown("---")
if st.button("이름 추천 받기", type="primary"):
    gender_key = GENDER_MAP[gender_label]
    results = pick_names(merged_tags, gender_key, n, prefer_short, prefer_unique)

    st.subheader("추천 결과")
    for i, r in enumerate(results, start=1):
        cols = st.columns([1, 3])
        with cols[0]:
            st.markdown(f"### {i}. {r['name']}")
        with cols[1]:
            lines = [f"- 이유: {r['why']}"]
            if show_tag:
                lines.append(f"- 태그: {r['tag']}")
            if show_pron:
                lines.append(f"- 발음: {r['pron']}")
            st.markdown("\n".join(lines))

    st.markdown("---")
    st.subheader("추가 커스터마이즈 팁")
    st.markdown(
        "- **성(Last name)** 이나 **한국 이름 발음**과의 어울림까지 맞추면 만족도가 확 올라가요.\n"
        "- 예: 성이 Kim이면 K로 시작하는 이름은 발음 리듬이 강해질 수 있어서, 부드러운 이름과 균형을 맞추는 방식도 좋아요."
    )

else:
    st.info("성격/분위기를 입력하고 ‘이름 추천 받기’를 눌러봐요.")
