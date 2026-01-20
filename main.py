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
        "neutral": ["River", "Indigo", "Phoeni]()
