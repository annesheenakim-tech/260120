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
