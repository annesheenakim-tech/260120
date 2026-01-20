import random
import re
import streamlit as st

st.set_page_config(page_title="영어 이름 추천기", page_icon="🪪", layout="centered")

# -----------------------------
# 데이터: 이름 풀(예시)
# -----------------------------
NAME_POOL = {
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

VOWELS = set("AEIOUY")

# -----------------------------
# 유틸: 텍스트 → 태그
# -----------------------------
def extract_tags(text: str) -> list[str]:
    text = (text or "").strip()
    if not text:
        return []
    hits = []
    for kw, tags in KEYWORD_TO_TAGS.items():
        if kw in text:
            hits.extend(tags)
    seen = set()
    out = []
    for t in hits:
        if t not in seen:
            out.append(t)
            seen.add(t)
    return out

# -----------------------------
# Last name 기반 발음/리듬 스코어
# -----------------------------
def normalize_name(s: str) -> str:
    """영문자만 남기고 대문자로 정규화."""
    s = (s or "").strip()
    s = re.sub(r"[^A-Za-z]", "", s)
    return s.upper()

def first_letter(s: str) -> str:
    s = normalize_name(s)
    return s[0] if s else ""

def last_letter(s: str) -> str:
    s = normalize_name(s)
    return s[-1] if s else ""

def starts_with_vowel(s: str) -> bool:
    s = normalize_name(s)
    return bool(s) and s[0] in VOWELS

def ends_with_vowel(s: str) -> bool:
    s = normalize_name(s)
    return bool(s) and s[-1] in VOWELS

def consonant_collision_penalty(lastname: str, firstname: str) -> float:
    """
    성 마지막 글자와 이름 첫 글자의 충돌(자음 중복/발음 뭉침) 패널티
    - 같은 글자면 큰 패널티
    - 발음이 비슷한 군(예: C/K/Q, S/Z, T/D 등)이면 중간 패널티
    """
    ln_last = last_letter(lastname)
    fn_first = first_letter(firstname)
    if not ln_last or not fn_first:
        return 0.0

    # 같은 문자면 강한 패널티
    if ln_last == fn_first:
        return 2.0

    # 유사 자음군
    groups = [
        set("CKQ"),
        set("SZ"),
        set("TD"),
        set("PB"),
        set("FV"),
        set("GM"),
        set("LR"),
        set("JW"),
        set("XKS"),  # X는 KS/SZ 계열로 뭉치는 경우가 많아서 완화
    ]
    for g in groups:
        if ln_last in g and fn_first in g:
            return 1.2

    # 끝이 자음이고 시작도 자음이면 약한 패널티(뭉침 가능)
    if (ln_last not in VOWELS) and (fn_first not in VOWELS):
        return 0.4

    return 0.0

def rhythm_bonus(lastname: str, firstname: str) -> float:
    """
    리듬 보너스:
    - (성 끝이 자음, 이름 시작이 모음) → 연결이 부드러워지는 경우 많음
    - (성 끝이 모음, 이름 시작이 자음) → 또렷한 구분
    - (모음-모음) 은 약간 흐릴 수 있어 소폭 감점
    """
    ln_ends_v = ends_with_vowel(lastname)
    fn_starts_v = starts_with_vowel(firstname)

    if (not ln_ends_v) and fn_starts_v:
        return 0.8
    if ln_ends_v and (not fn_starts_v):
        return 0.5
    if ln_ends_v and fn_starts_v:
        return -0.2
    return 0.0

def korean_pron_ease_penalty(firstname: str) -> float:
    """
    한국어 화자에게 발음이 상대적으로 까다로운 패턴에 약한 패널티.
    (완벽한 음운 규칙이 아니라 휴리스틱)
    """
    n = normalize_name(firstname)

    penalty = 0.0
    hard_patterns = [
        "TH", "R", "L", "V", "F", "Z", "X", "Q", "PH", "WR", "DW", "TW", "STR"
    ]
    for p in hard_patterns:
        if p in n:
            penalty += 0.15

    # 너무 길면 기억/호명 난이도↑
    if len(n) >= 10:
        penalty += 0.4
    elif len(n) >= 8:
        penalty += 0.2

    return penalty

# -----------------------------
# 기본 선호 스코어
# -----------------------------
def base_preference_score(name: str, prefer_short: bool, prefer_unique: bool) -> float:
    s = 0.0
    if prefer_short:
        s += max(0, 8 - len(name)) * 0.2  # 짧을수록 가점
    if prefer_unique:
        common = {"MICHAEL", "CHRISTOPHER", "ANDREW", "THOMAS", "ELIZABETH", "JANE", "ANNA"}
        if normalize_name(name) in common:
            s -= 1.0
        else:
            s += 0.6
    return s

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

def total_score(
    firstname: str,
    lastname: str,
    prefer_short: bool,
    prefer_unique: bool,
    avoid_collision: bool,
) -> tuple[float, dict]:
    """
    총점 + 디버그 breakdown 반환
    """
    b = base_preference_score(firstname, prefer_short, prefer_unique)

    coll = consonant_collision_penalty(lastname, firstname) if avoid_collision else 0.0
    rhy = rhythm_bonus(lastname, firstname) if lastname else 0.0
    ease = korean_pron_ease_penalty(firstname)

    # 점수 구성: base + 리듬 - 충돌 - 발음난이도
    score = b + rhy - coll - ease

    detail = {
        "base": round(b, 2),
        "rhythm": round(rhy, 2),
        "collision_penalty": round(coll, 2),
        "pron_ease_penalty": round(ease, 2),
        "total": round(score, 2),
    }
    return score, detail

def build_candidates(tags: list[str], gender_key: str) -> list[tuple[str, str]]:
    candidate_tags = tags if tags else ALL_TAGS
    candidates = []
    for t in candidate_tags:
        if gender_key == "neutral":
            pool = NAME_POOL[t]["neutral"] + NAME_POOL[t]["female"] + NAME_POOL[t]["male"]
        else:
            pool = NAME_POOL[t][gender_key] + NAME_POOL[t]["neutral"]
        for nm in pool:
            candidates.append((t, nm))

    # 이름 중복 제거
    seen = set()
    uniq = []
    for t, nm in candidates:
        key = normalize_name(nm)
        if key not in seen:
            uniq.append((t, nm))
            seen.add(key)
    return uniq

def recommend(
    tags: list[str],
    gender_key: str,
    n: int,
    prefer_short: bool,
    prefer_unique: bool,
    lastname: str,
    avoid_collision: bool,
    strict_filter: bool,
) -> list[dict]:
    candidates = build_candidates(tags, gender_key)

    scored = []
    for t, nm in candidates:
        sc, detail = total_score(nm, lastname, prefer_short, prefer_unique, avoid_collision)

        # 엄격 필터: 충돌 패널티가 큰 애들은 제외
        if strict_filter and detail["collision_penalty"] >= 1.2:
            continue

        scored.append((t, nm, sc, detail))

    scored.sort(key=lambda x: x[2], reverse=True)

    # 상위 풀에서 랜덤성 부여
    pool_size = min(len(scored), max(n * 8, 30))
    top = scored[:pool_size]
    random.shuffle(top)

    results = top[:n]
    out = []
    for t, nm, sc, detail in results:
        out.append({
            "name": nm,
            "tag": t,
            "why": tag_to_reason(t),
            "pron": PRON_HINT.get(nm, "발음 힌트 준비중"),
            "score_detail": detail,
        })
    return out

# -----------------------------
# UI
# -----------------------------
st.title("🪪 성격 + 성(Last name) 기반 영어 이름 추천")
st.caption("성(Last name)까지 고려해서 발음 뭉침/리듬을 피하고, 더 자연스러운 조합으로 추천해줘요.")

with st.sidebar:
    st.header("설정")
    n = st.slider("추천 개수", 3, 20, 8, key="n")
    gender_label = st.selectbox("이름 성별 톤", list(GENDER_MAP.keys()), index=0, key="gender")
    prefer_short = st.toggle("짧고 부르기 쉬운 이름 선호", value=True, key="short")
    prefer_unique = st.toggle("유니크한 이름 선호", value=False, key="unique")

    st.divider()
    st.subheader("성(Last name) 옵션")
    lastname_input = st.text_input("Last name(영문)", placeholder="예: Kim, Park, Lee", key="lastname")
    avoid_collision = st.toggle("자음 충돌(끝소리-첫소리 뭉침) 피하기", value=True, key="avoid")
    strict_filter = st.toggle("충돌 강한 후보는 제외(엄격)", value=False, key="strict")

    st.divider()
    show_pron = st.toggle("발음 힌트 표시", value=True, key="show_pron")
    show_tag = st.toggle("분위기 태그 표시", value=True, key="show_tag")
    show_score = st.toggle("점수 상세(디버그) 표시", value=False, key="show_score")

st.subheader("1) 성격/분위기 입력")
text = st.text_area(
    "예: 차분하고 지적인데 따뜻한 느낌 / 밝고 사교적인 느낌 / 세련되고 모던한 느낌",
    height=80,
    key="personality_text",
)

st.subheader("2) 스타일 직접 선택(선택)")
style = st.multiselect(
    "원하는 분위기 태그를 직접 고를 수도 있어요.",
    options=ALL_TAGS,
    default=[],
    key="style",
)

auto_tags = extract_tags(text)
merged_tags = style if style else auto_tags

st.write("인식된 분위기 태그:", merged_tags if merged_tags else "없음(전체에서 추천)")

lastname_norm = normalize_name(lastname_input)
if lastname_input and not lastname_norm:
    st.warning("Last name은 영문자만 인식해요. (예: Kim, Park, Lee)")

st.markdown("---")

if st.button("이름 추천 받기", type="primary"):
    gender_key = GENDER_MAP[gender_label]

    results = recommend(
        tags=merged_tags,
        gender_key=gender_key,
        n=n,
        prefer_short=prefer_short,
        prefer_unique=prefer_unique,
        lastname=lastname_input,
        avoid_collision=avoid_collision,
        strict_filter=strict_filter,
    )

    st.subheader("추천 결과")
    if not results:
        st.error("조건이 너무 엄격해서 후보가 없어요. ‘엄격’ 옵션을 끄거나 추천 개수를 줄여봐요.")
    else:
        for i, r in enumerate(results, start=1):
            st.markdown(f"### {i}. {r['name']}" + (f"  _(Last name: {lastname_input})_" if lastname_input else ""))

            lines = [f"- 이유: {r['why']}"]
            if show_tag:
                lines.append(f"- 태그: {r['tag']}")
            if show_pron:
                lines.append(f"- 발음: {r['pron']}")

            # 성과의 조합 코멘트
            if lastname_input:
                ln_last = last_letter(lastname_input)
                fn_first = first_letter(r["name"])
                lines.append(f"- 조합 힌트: 성 끝({ln_last or '—'}) + 이름 첫({fn_first or '—'})")

            st.markdown("\n".join(lines))

            if show_score:
                st.code(r["score_detail"], language="python")

    st.markdown("---")
    st.subheader("조합 튜닝 팁")
    st.markdown(
        "- 성이 **자음으로 끝나는 경우(Kim, Park 등)**, 이름이 **모음으로 시작(A- / E- / O-)**하면 발음이 부드러운 편이에요.\n"
        "- 성이 **모음으로 끝나는 경우(예: ‘Lee’는 발음상 ‘이’로 끝)**, 이름이 **자음으로 시작**하면 또렷하게 들려요.\n"
        "- ‘엄격’ 옵션은 **발음이 뭉치는 조합을 강하게 배제**하니 후보가 줄 수 있어요."
    )
else:
    st.info("성격/분위기와 Last name을 입력하고 ‘이름 추천 받기’를 눌러봐요.")
