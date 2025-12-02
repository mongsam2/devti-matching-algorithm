import streamlit as st
import json
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from matching import random_team_assignment, simulated_annealing, evaluate_solution
from category import get_category_score
from wagging import get_wagging_score
from explain import get_matching_explanations

# 페이지 설정
st.set_page_config(page_title="팀 매칭 알고리즘 데모", layout="wide")


# 데이터 로드
@st.cache_data
def load_data():
    with open("sample_data/participant.json", "r", encoding="utf-8") as f:
        participants = json.load(f)
    with open("sample_data/wagging.json", "r", encoding="utf-8") as f:
        waggings = json.load(f)
    return participants, waggings


participants, waggings = load_data()

st.title("🎯 팀 매칭 알고리즘 데모")
st.markdown("---")

# 사전 통계 섹션
st.header("📊 매칭 전 참가자 통계")

col1, col2 = st.columns(2)

with col1:
    st.subheader("파트별 분포")
    part_counts = {}
    for p in participants:
        part = p["part"]
        part_counts[part] = part_counts.get(part, 0) + 1

    fig_part = px.pie(
        values=list(part_counts.values()),
        names=list(part_counts.keys()),
        title="참가자 파트 분포",
    )
    st.plotly_chart(fig_part, use_container_width=True)

with col2:
    st.subheader("팀 분위기 선호도")
    vibe_counts = {}
    for p in participants:
        vibe = p["team_vibe"]
        vibe_counts[vibe] = vibe_counts.get(vibe, 0) + 1

    fig_vibe = px.pie(
        values=list(vibe_counts.values()),
        names=list(vibe_counts.keys()),
        title="팀 분위기 선호도 분포",
    )
    st.plotly_chart(fig_vibe, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.subheader("활동 시간대 선호도")
    hours_counts = {}
    for p in participants:
        hours = p["active_hours"]
        hours_counts[hours] = hours_counts.get(hours, 0) + 1

    fig_hours = px.pie(
        values=list(hours_counts.values()),
        names=list(hours_counts.keys()),
        title="활동 시간대 분포",
    )
    st.plotly_chart(fig_hours, use_container_width=True)

with col4:
    st.subheader("회의 방식 선호도")
    meeting_counts = {}
    for p in participants:
        meeting = p["meeting_preference"]
        meeting_counts[meeting] = meeting_counts.get(meeting, 0) + 1

    fig_meeting = px.pie(
        values=list(meeting_counts.values()),
        names=list(meeting_counts.keys()),
        title="회의 방식 선호도 분포",
    )
    st.plotly_chart(fig_meeting, use_container_width=True)

st.markdown("---")

# 매칭 실행 버튼
st.header("🚀 팀 매칭 실행")

if st.button("매칭 시작", type="primary", use_container_width=True):
    with st.spinner("매칭 알고리즘 실행 중..."):
        # 초기 랜덤 매칭
        initial_teams = random_team_assignment(participants)
        initial_score = evaluate_solution(initial_teams, waggings)

        # 최적화된 매칭
        optimized_teams, optimized_score = simulated_annealing(
            initial_teams,
            waggings=waggings,
            initial_temp=1.0,
            min_temp=0.001,
            cooling_rate=0.995,
            max_iterations=10000,
        )

        # 매칭 이유 생성
        matching_reasons = get_matching_explanations(optimized_teams)

        # 세션 상태에 저장
        st.session_state["initial_teams"] = initial_teams
        st.session_state["initial_score"] = initial_score
        st.session_state["optimized_teams"] = optimized_teams
        st.session_state["optimized_score"] = optimized_score
        st.session_state["matching_reasons"] = matching_reasons
        st.session_state["matching_done"] = True

    st.success("매칭 완료!")
    st.rerun()

# 매칭 결과 표시
if st.session_state.get("matching_done", False):
    st.markdown("---")
    st.header("📈 매칭 결과 분석")

    initial_teams = st.session_state["initial_teams"]
    initial_score = st.session_state["initial_score"]
    optimized_teams = st.session_state["optimized_teams"]
    optimized_score = st.session_state["optimized_score"]

    # 팀별 점수 비교
    st.subheader("팀별 점수 상세 비교")

    initial_category_scores = get_category_score(initial_teams)
    optimized_category_scores = get_category_score(optimized_teams)

    initial_wagging_scores, initial_team_wagging = get_wagging_score(
        initial_teams, waggings
    )
    optimized_wagging_scores, optimized_team_wagging = get_wagging_score(
        optimized_teams, waggings
    )

    score_df = pd.DataFrame(
        {
            "팀": [f"Team {i+1}" for i in range(len(initial_teams))],
            "초기 카테고리 점수(100)": initial_category_scores,
            "최적화 카테고리 점수(100)": optimized_category_scores,
            "초기 꼬리흔들기 매칭 일치도(%)": initial_team_wagging,
            "최적화 꼬리흔들기 매칭 일치도(%)": optimized_team_wagging,
        }
    )

    st.dataframe(score_df, use_container_width=True)

    # 각 팀별 상세 정보
    st.markdown("---")
    st.header("👥 팀별 상세 정보")

    matching_reasons = st.session_state.get("matching_reasons", [])

    for team_idx, team in enumerate(optimized_teams):
        with st.expander(f"Team {team_idx + 1} 상세 정보"):
            # 매칭 이유 섹션 추가
            st.subheader("💡 매칭 이유")
            if team_idx < len(matching_reasons):
                st.write(matching_reasons[team_idx].reason)
            else:
                st.write("매칭 이유를 생성할 수 없습니다.")

            st.markdown("---")

            col1, col2 = st.columns(2)

            with col1:
                # 파트 분포
                st.subheader("파트 분포")
                team_parts = {}
                for member in team:
                    part = member["part"]
                    team_parts[part] = team_parts.get(part, 0) + 1

                fig_team_part = px.bar(
                    x=list(team_parts.keys()),
                    y=list(team_parts.values()),
                    labels={"x": "파트", "y": "인원 수"},
                    title=f"Team {team_idx + 1} 파트 구성",
                )
                st.plotly_chart(fig_team_part, use_container_width=True)

                # 선호도 일치율
                st.subheader("선호도 일치율")
                vibe_match = {}
                hours_match = {}
                meeting_match = {}

                for member in team:
                    vibe = member["team_vibe"]
                    hours = member["active_hours"]
                    meeting = member["meeting_preference"]

                    vibe_match[vibe] = vibe_match.get(vibe, 0) + 1
                    hours_match[hours] = hours_match.get(hours, 0) + 1
                    meeting_match[meeting] = meeting_match.get(meeting, 0) + 1

                match_df = pd.DataFrame(
                    {
                        "카테고리": ["Team Vibe", "Active Hours", "Meeting Preference"],
                        "최다 선호": [
                            max(vibe_match, key=vibe_match.get),
                            max(hours_match, key=hours_match.get),
                            max(meeting_match, key=meeting_match.get),
                        ],
                        "일치 인원": [
                            max(vibe_match.values()),
                            max(hours_match.values()),
                            max(meeting_match.values()),
                        ],
                        "일치율 (%)": [
                            f"{max(vibe_match.values()) / len(team) * 100:.1f}",
                            f"{max(hours_match.values()) / len(team) * 100:.1f}",
                            f"{max(meeting_match.values()) / len(team) * 100:.1f}",
                        ],
                    }
                )
                st.dataframe(match_df, use_container_width=True)

            with col2:
                # 성격 유형 분포
                st.subheader("평균 MBTI 특성")
                mbti_traits = {
                    "ei": [],
                    "sn": [],
                    "tf": [],
                    "jp": [],
                }

                for member in team:
                    for trait in mbti_traits.keys():
                        mbti_traits[trait].append(member[trait])

                avg_traits = {
                    trait: sum(values) / len(values)
                    for trait, values in mbti_traits.items()
                }

                fig_personality = go.Figure(
                    data=go.Scatterpolar(
                        r=list(avg_traits.values()),
                        theta=[
                            "외향성(E)-내향성(I)",
                            "직관(N)-감각(S)",
                            "감정(F)-사고(T)",
                            "인식(P)-판단(J)",
                        ],
                        fill="toself",
                    )
                )
                fig_personality.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                    title=f"Team {team_idx + 1} 평균 MBTI 특성",
                )
                st.plotly_chart(fig_personality, use_container_width=True)

                # 팀원 목록
                st.subheader("팀원 목록")
                member_list = []
                for member in team:
                    member_list.append(
                        {
                            "ID": member["id"],
                            "파트": member["part"],
                            "DEVTI": member["devti"],
                            "팀 분위기": member["team_vibe"],
                            "활동 시간": member["active_hours"],
                            "회의 방식": member["meeting_preference"],
                        }
                    )
                st.dataframe(pd.DataFrame(member_list), use_container_width=True)

                # 팀원별 꼬리흔들기 정보 추가
                st.subheader("팀원별 꼬리흔들기 현황")
                team_ids = [m["id"] for m in team]
                wagging_info = []

                # 현재 팀의 개별 wagging 점수 가져오기
                team_start_idx = sum(len(optimized_teams[i]) for i in range(team_idx))
                individual_wagging_scores = optimized_wagging_scores[
                    team_start_idx : team_start_idx + len(team)
                ]

                for idx, member in enumerate(team):
                    my_id = member["id"]
                    my_waggees = [
                        w["waggee"]
                        for w in waggings
                        if w["wagger"] == my_id and w["waggee"] in team_ids
                    ]
                    wagging_info.append(
                        {
                            "ID": my_id,
                            "내가 꼬리 흔든 팀원": (
                                ", ".join(str(wid) for wid in my_waggees)
                                if my_waggees
                                else "-"
                            ),
                            "팀원 중 적중수": individual_wagging_scores[idx],
                        }
                    )
                st.dataframe(pd.DataFrame(wagging_info), use_container_width=True)
