import streamlit as st
import pandas as pd
import json
import random
import math

from utils import (
    get_team_size,
    random_team_assignment,
    evaluate_solution,
    neighbor_solution,
    simulated_annealing,
)

st.title("DevTI 팀 매팅 알고리즘 테스트")


def load_sample_data(file_name):
    with open(file_name, encoding="utf-8") as f:
        data = json.load(f)
    return data


def display_team_members(team, teams_info):
    """팀원의 모든 정보를 테이블 형식으로 표시"""
    team_id = team["id"]
    members_data = []
    members_list = []

    for part in teams_info[0].keys():
        for member in team.get(part, []):
            members_data.append(
                {
                    "ID": member["id"],
                    "파트": part,
                    "외향성": f"{member.get('extraversion', 0):.3f}",
                    "신경증": f"{member.get('neuroticism', 0):.3f}",
                    "성실도": f"{member.get('conscientiousness', 0):.3f}",
                    "개방성": f"{member.get('openness', 0):.3f}",
                    "친화성": f"{member.get('agreeableness', 0):.3f}",
                }
            )
            members_list.append(member)

    if members_data:
        df = pd.DataFrame(members_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # 각 팀원의 성격 설명 표시
        st.write("**성격 설명**")
        for member in members_list:
            with st.expander(f"팀원 {member['id']} - {member['part'].upper()}"):
                st.write(member.get("personality", "설명이 없습니다."))
    else:
        st.write("팀원이 없습니다.")


participant_data = load_sample_data("participant_sample.json")
wagging_data = load_sample_data("wagging_sample.json")

st.subheader("테스트 데이터 원본")
st.write(pd.DataFrame(participant_data).set_index("id"))
st.write(pd.DataFrame(wagging_data).set_index("id"))

st.subheader("적절한 팀원 수 추출")

if st.button("팀 매칭 시작"):
    # 1단계: 팀 구성 요구사항 생성
    teams_info = get_team_size(participant_list=participant_data)

    if not teams_info:
        st.error("팀을 생성할 수 없습니다.")
    else:
        st.subheader("팀 구성 요구사항")
        cols = st.columns(len(teams_info))
        for i, team_info in enumerate(teams_info):
            with cols[i]:
                st.write(f"**팀 {i+1}**")
                for part, count in team_info.items():
                    st.badge(f"{part}: {count}", color="blue")

        # 2단계: 초기 랜덤 팀 생성 및 점수 계산
        st.subheader("1️⃣ 초기 랜덤 팀 매칭 결과")
        initial_teams = random_team_assignment(participant_data, teams_info)
        initial_score = evaluate_solution(initial_teams, wagging_data)

        st.metric("초기 팀 점수", f"{initial_score:.4f}", delta="시작점")

        # 초기 팀 명단 표시
        with st.expander("초기 팀 명단 보기"):
            for i, team in enumerate(initial_teams):
                st.write(f"**팀 {team['id']}**")
                display_team_members(team, teams_info)
                st.divider()

        # 3단계: Simulated Annealing 실행 및 시각화
        st.subheader("2️⃣ Simulated Annealing 최적화 진행 중...")

        # 진행 상황 표시 공간
        progress_placeholder = st.empty()
        metrics_placeholder = st.empty()
        chart_placeholder = st.empty()

        # SA 실행 중 실시간 데이터 수집
        iteration_history = []
        score_history = []
        best_score_history = []

        current_solution = initial_teams
        current_score = initial_score
        best_solution = current_solution
        best_score = current_score

        initial_temp = 1.0
        min_temp = 0.001
        cooling_rate = 0.995
        max_iterations = 10000

        T = initial_temp
        iteration = 0

        while T > min_temp and iteration < max_iterations:
            # Neighbor 생성
            new_solution = neighbor_solution(current_solution)
            new_score = evaluate_solution(new_solution, wagging_data)

            # Score 차이
            delta = new_score - current_score

            # 더 좋으면 무조건 채택
            if delta < 0:
                accept = True
            else:
                # 더 나쁜 해는 확률적으로 채택
                p = math.exp(-delta / T) if T > 0 else 0
                accept = random.random() < p

            if accept:
                current_solution = new_solution
                current_score = new_score

            # Best 업데이트
            if current_score < best_score:
                best_solution = current_solution
                best_score = current_score

            # 데이터 수집
            iteration_history.append(iteration)
            score_history.append(current_score)
            best_score_history.append(best_score)

            # 진행 상황 표시 (매 100회 반복마다)
            if iteration % 100 == 0:
                with progress_placeholder:
                    st.progress(min(iteration / max_iterations, 1.0))

                with metrics_placeholder:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("반복 횟수", f"{iteration:,}")
                    with col2:
                        st.metric("현재 점수", f"{current_score:.4f}")
                    with col3:
                        st.metric("최고 점수", f"{best_score:.4f}")
                    with col4:
                        st.metric("온도", f"{T:.6f}")

                with chart_placeholder:
                    df = pd.DataFrame(
                        {
                            "반복": iteration_history,
                            "현재 점수": score_history,
                            "최고 점수": best_score_history,
                        }
                    )
                    st.line_chart(df.set_index("반복"))

            # 온도 감소
            T *= cooling_rate
            iteration += 1

        # 4단계: 최종 결과 표시
        st.subheader("3️⃣ 최적화 완료 ✨")

        # 성능 비교
        improvement = (
            ((initial_score - best_score) / abs(initial_score)) * 100
            if initial_score != 0
            else 0
        )

        result_col1, result_col2, result_col3 = st.columns(3)
        with result_col1:
            st.metric("초기 점수", f"{initial_score:.4f}")
        with result_col2:
            st.metric("최종 점수", f"{best_score:.4f}")
        with result_col3:
            st.metric(
                "개선도",
                f"{improvement:.2f}%",
                delta=f"{best_score - initial_score:.4f}",
            )

        # 최종 팀 명단
        st.subheader("최적화된 팀 명단")
        for i, team in enumerate(best_solution):
            st.write(f"**팀 {team['id']}**")
            display_team_members(team, teams_info)
            st.divider()

        # 최종 그래프
        st.subheader("최적화 과정")
        df_final = pd.DataFrame(
            {
                "반복": iteration_history,
                "현재 점수": score_history,
                "최고 점수": best_score_history,
            }
        )
        st.line_chart(df_final.set_index("반복"))
