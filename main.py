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


@st.cache_data
def load_devti_data():
    with open("sample_data/devti_list.json", "r", encoding="utf-8") as f:
        devti_list = json.load(f)
    return devti_list


participants, waggings = load_data()
devti_list = load_devti_data()

st.title("🎯 팀 매칭 알고리즘 데모")
st.markdown("---")

# 탭 생성
tab1, tab2 = st.tabs(["👥 팀 매칭", "📝 DEVTI 검사"])

with tab1:
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
                            "카테고리": [
                                "Team Vibe",
                                "Active Hours",
                                "Meeting Preference",
                            ],
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
                    team_start_idx = sum(
                        len(optimized_teams[i]) for i in range(team_idx)
                    )
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

with tab2:
    st.header("📝 DEVTI 검사 테스트")

    # 질문 데이터 정의
    questions = [
        {
            "dimension": "IE",
            "direction": "E",
            "text": "프로젝트 초기에 서먹한 분위기를 깨기 위해 먼저 말을 걸고 단톡방에서 대화를 주도하는 편이다.",
        },
        {
            "dimension": "NS",
            "direction": "S",
            "text": "프로젝트의 배경이나 의도를 직접 이해하면서 따라가는 것보다, 내가 처리해야 할 구체적인 작업 목록(To-Do)과 마감기한만 정해주고 일을 시킬 때 더 편안함을 느낀다.",
        },
        {
            "dimension": "FT",
            "direction": "T",
            "text": "팀원이 만든 산출물(기획안, 디자인, 코드 등)에 미묘한 문제가 있을 때, 감정을 고려해 표현을 둥글게 하기보다 구체적인 문제를 빠르게 지적하는 것이 더 효율적이라고 생각한다.",
        },
        {
            "dimension": "PJ",
            "direction": "J",
            "text": "프로젝트 시작 전, 주차별 개발 일정과 역할 분담이 문서(Notion, Excel 등)에 완벽하게 정리되어 있어야 마음이 편하다.",
        },
        {
            "dimension": "IE",
            "direction": "I",
            "text": "회의가 끝나고 다 같이 밥을 먹거나 뒤풀이를 가기보다는, 빨리 집으로 가서 혼자 재충전하는 시간을 갖고 싶다.",
        },
        {
            "dimension": "NS",
            "direction": "N",
            "text": "기획 단계에서 당장 구현 가능한 기능 위주로 논의하기보다, 나중에 추가될지 모를 미래의 확장성까지 상상하며 이야기하는 것을 좋아한다.",
        },
        {
            "dimension": "FT",
            "direction": "F",
            "text": "팀 분위기가 조금 어수선하더라도, 결과물의 퀄리티가 좋고 기술적으로 완벽하다면 프로젝트는 성공적이라고 생각한다.",
        },
        {
            "dimension": "PJ",
            "direction": "P",
            "text": "일단 개발하면서 수정하자는 방식이 설계에 시간을 많이 쓰는 것보다 효율적이라고 느낀다.",
        },
        {
            "dimension": "IE",
            "direction": "E",
            "text": "혼자 조용히 코딩하거나 디자인 작업에 몰두할 때보다, 팀원들과 모여 짝(Pair) 프로그래밍이나 아이디에이션을 할 때 에너지가 솟는다.",
        },
        {
            "dimension": "NS",
            "direction": "S",
            "text": "검증되지 않은 최신 트렌드 기술(Hip한 기술)을 도입하는 것보다, 레퍼런스가 많고 안정적인 기존 기술 스택을 사용하는 것을 선호한다.",
        },
        {
            "dimension": "FT",
            "direction": "T",
            "text": "팀 내 갈등 상황에서 누가 얼마나 마음이 상했는지(감정)보다, 누구의 말이 논리적으로 맞는지(팩트)를 따지는 것이 중요하다.",
        },
        {
            "dimension": "PJ",
            "direction": "J",
            "text": "개발이나 디자인을 할 때 폴더 구조(Directory Structure)나 네이밍 컨벤션을 미리 엄격하게 정해두고 칼같이 지키는 편이다.",
        },
        {
            "dimension": "IE",
            "direction": "I",
            "text": "모르는 기술적 문제가 발생했을 때, 바로 옆 사람에게 물어보기보다는 혼자 구글링으로 해결책을 찾을 때까지 파고드는 편이다.",
        },
        {
            "dimension": "NS",
            "direction": "N",
            "text": "디자인이나 코드를 짤 때, 기존의 관습이나 템플릿을 따르기보다 완전히 새롭고 독창적인 구조를 시도해보고 싶다.",
        },
        {
            "dimension": "FT",
            "direction": "T",
            "text": "QA 담당자가 내 기분을 먼저 생각하기 보단 사실 기반으로 재현 절차를 포함해 피드백 해줬으면 좋겠다.",
        },
        {
            "dimension": "PJ",
            "direction": "P",
            "text": "마감 기한이 임박해서 몰아치며 작업할 때 의외로 집중력이 폭발하고 좋은 결과물이 나온다.",
        },
        {
            "dimension": "IE",
            "direction": "E",
            "text": "내가 작업한 결과물을 팀 전체에게 발표하고 피드백 받는 자리가 긴장되기보단 즐겁고 기다려진다.",
        },
        {
            "dimension": "NS",
            "direction": "S",
            "text": "숲(전체적인 서비스 아키텍처나 사용자 흐름)을 보는 것보다 나무(지금 당장 작성 중인 함수의 로직, 픽셀 단위 디테일)에 집중하는 편이다.",
        },
        {
            "dimension": "FT",
            "direction": "T",
            "text": "사용자의 감성을 자극하는 스토리텔링보다는, 데이터 처리 속도가 빠르고 오류가 없는 기능적 완벽함이 더 우선이다.",
        },
        {
            "dimension": "PJ",
            "direction": "J",
            "text": "회의 안건(Agenda) 없이 모여서 의식의 흐 flow대로 진행되는 자유로운 토론 시간은 비효율적이라고 느낀다.",
        },
        {
            "dimension": "IE",
            "direction": "I",
            "text": "해커톤이나 연합 행사처럼 모르는 사람들이 많은 시끌벅적한 네트워킹 자리는 기가 빨려서 피하고 싶다.",
        },
        {
            "dimension": "NS",
            "direction": "N",
            "text": "개발 문서를 볼 때 예제 코드부터 복사해서 돌려보는 것보다, 원리나 개념(Concept)부터 이해해야 직성이 풀린다.",
        },
        {
            "dimension": "FT",
            "direction": "F",
            "text": "팀원이 개인적인 사정으로 맡은 일을 못 했을 때, 대책을 세우기(해결) 전에 먼저 사정을 들어주고 공감(위로)해주는 편이다.",
        },
        {
            "dimension": "PJ",
            "direction": "P",
            "text": "예상치 못한 버그나 기획 변경으로 일정이 틀어졌을 때, 스트레스를 받기보다 유연하게 대처하며 상황을 즐기는 편이다.",
        },
        {
            "dimension": "IE",
            "direction": "E",
            "text": "급한 이슈가 생겼을 때 텍스트(슬랙, 카톡)로 설명하기보다 바로 보이스톡을 걸거나 만나서 말하는 것이 편하다.",
        },
        {
            "dimension": "NS",
            "direction": "S",
            "text": "회의 중 아이디어를 낼 때 현실적인 제약 사항(시간, 비용)을 먼저 고려하여 실현 가능한 범위 내에서 제안한다.",
        },
        {
            "dimension": "FT",
            "direction": "T",
            "text": "칭찬을 들을 때 정말 고생 많으셨어요(노력 인정)보다 코드가 정말 깔끔하네요, 디자인이 정말 깔끔하네요 라는 능력을 인정해주는 말이 더 기분 좋다.",
        },
        {
            "dimension": "PJ",
            "direction": "J",
            "text": "할 일 목록(To-Do List)을 작성하고 하나씩 체크해서 지워나가는 과정에서 큰 희열을 느낀다.",
        },
    ]

    # 세션 상태 초기화
    if "devti_current_question" not in st.session_state:
        st.session_state.devti_current_question = 0
    if "devti_answers" not in st.session_state:
        st.session_state.devti_answers = [None] * len(questions)

    # 결과 계산 함수
    def calculate_devti_result(answers, questions):
        scores = {"IE": 0, "NS": 0, "FT": 0, "PJ": 0}
        counts = {"IE": 0, "NS": 0, "FT": 0, "PJ": 0}

        for i, answer in enumerate(answers):
            question = questions[i]
            dimension = question["dimension"]
            direction = question["direction"]

            # direction이 뒤쪽 글자(E, S, T, J)면 그대로, 앞쪽이면 반전
            if direction in ["E", "S", "T", "J"]:
                scores[dimension] += answer
            else:
                scores[dimension] += 4 - answer
            counts[dimension] += 1

        # 정규화 (0~1 범위)
        max_score_per_dimension = 4 * 7  # 각 차원당 7개 질문, 최대 4점
        normalized = {
            "ei": scores["IE"] / max_score_per_dimension,
            "sn": scores["NS"] / max_score_per_dimension,
            "tf": scores["FT"] / max_score_per_dimension,
            "jp": scores["PJ"] / max_score_per_dimension,
        }

        # MBTI 타입 결정
        mbti = ""
        mbti += "E" if normalized["ei"] >= 0.5 else "I"
        mbti += "N" if normalized["sn"] < 0.5 else "S"
        mbti += "F" if normalized["tf"] < 0.5 else "T"
        mbti += "P" if normalized["jp"] < 0.5 else "J"

        return normalized, mbti

    # 결과 화면이 아닐 때만 질문 표시
    if not st.session_state.get("devti_test_completed", False):
        current_q = st.session_state.devti_current_question
        total_q = len(questions)

        # 진행률 표시
        progress = (current_q) / total_q
        st.progress(progress, text=f"진행률: {current_q}/{total_q}")

        st.markdown("---")

        # 현재 질문 표시
        question = questions[current_q]

        st.subheader(f"질문 {current_q + 1}/{total_q}")

        # 질문 차원 표시
        dimension_labels = {
            "IE": "외향(E) ↔ 내향(I)",
            "NS": "직관(N) ↔ 감각(S)",
            "FT": "감정(F) ↔ 사고(T)",
            "PJ": "인식(P) ↔ 판단(J)",
        }
        st.caption(f"📊 측정 차원: {dimension_labels[question['dimension']]}")

        st.markdown(f"### {question['text']}")

        st.markdown("---")

        # 답변 선택 (오지선다)
        answer_labels = [
            "전혀 아니다 (0)",
            "아니다 (1)",
            "보통이다 (2)",
            "그렇다 (3)",
            "매우 그렇다 (4)",
        ]

        # 현재 답변 가져오기
        current_answer = st.session_state.devti_answers[current_q]
        default_index = current_answer if current_answer is not None else 2

        answer = st.radio(
            "답변을 선택하세요:",
            options=[0, 1, 2, 3, 4],
            format_func=lambda x: answer_labels[x],
            index=default_index,
            key=f"question_{current_q}",
            horizontal=True,
        )

        # 답변 저장
        st.session_state.devti_answers[current_q] = answer

        st.markdown("---")

        # 네비게이션 버튼
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if current_q > 0:
                if st.button("⬅️ 이전", use_container_width=True):
                    st.session_state.devti_current_question -= 1
                    st.rerun()

        with col2:
            answered_count = sum(
                1 for a in st.session_state.devti_answers if a is not None
            )
            st.metric("답변 완료", f"{answered_count}/{total_q}")

        with col3:
            if current_q < total_q - 1:
                if st.button("다음 ➡️", use_container_width=True):
                    st.session_state.devti_current_question += 1
                    st.rerun()
            else:
                # 마지막 질문에서는 결과 보기 버튼
                all_answered = all(
                    a is not None for a in st.session_state.devti_answers
                )
                if st.button(
                    "📊 결과 보기",
                    type="primary",
                    use_container_width=True,
                    disabled=not all_answered,
                ):
                    st.session_state.devti_test_completed = True
                    st.rerun()

        # 답변 현황 표시
        st.markdown("---")
        st.caption("💡 답변 현황:")
        answer_status = []
        for i, ans in enumerate(st.session_state.devti_answers):
            if ans is not None:
                answer_status.append("✅")
            elif i == current_q:
                answer_status.append("📍")
            else:
                answer_status.append("⭕")

        # 7개씩 묶어서 표시
        for i in range(0, len(answer_status), 7):
            st.text(" ".join(answer_status[i : i + 7]))

    else:
        # 결과 화면
        st.subheader("🎉 DEVTI 검사 결과")

        # 결과 계산
        normalized_scores, mbti_type = calculate_devti_result(
            st.session_state.devti_answers, questions
        )

        # 해당하는 강아지 정보 찾기
        dog_info = next((dog for dog in devti_list if dog["mbti"] == mbti_type), None)

        if dog_info:
            # 결과 표시
            st.markdown("---")
            col1, col2 = st.columns([1, 2])

            with col1:
                st.markdown(f"## 🐕 {dog_info['breed']}")
                st.markdown(f"### {mbti_type}")
                st.markdown(f"*{dog_info['introduce']}*")
                st.markdown(f"**{dog_info['keyword']}**")

            with col2:
                # MBTI 점수 시각화
                st.subheader("📊 당신의 DEVTI 점수")

                score_df = pd.DataFrame(
                    {
                        "차원": ["E ↔ I", "S ↔ N", "T ↔ F", "J ↔ P"],
                        "점수": [
                            normalized_scores["ei"],
                            normalized_scores["sn"],
                            normalized_scores["tf"],
                            normalized_scores["jp"],
                        ],
                    }
                )

                fig = px.bar(
                    score_df,
                    x="차원",
                    y="점수",
                    title="DEVTI 차원별 점수",
                    range_y=[0, 1],
                )
                fig.add_hline(
                    y=0.5, line_dash="dash", line_color="red", annotation_text="중립"
                )
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            # 상세 정보
            col3, col4 = st.columns(2)

            with col3:
                st.subheader("💪 잘하는 것")
                st.write(dog_info["good_at"])

                st.subheader("🎯 최적 포지션")
                st.write(dog_info["best_position"])

            with col4:
                st.subheader("✨ 특징")
                st.write(dog_info["habit"])

                st.subheader("⚠️ 주의할 점")
                st.write(dog_info["risk"])

            st.markdown("---")

            # 베스트 파트너
            st.subheader("🤝 베스트 파트너")
            for bestie in dog_info["bestie"]:
                with st.expander(f"{bestie['mbti']} - {bestie['breed']}"):
                    st.write(f"**시너지:** {bestie['synergy']}")

            st.markdown("---")

            # 다시 하기 버튼
            col_reset1, col_reset2, col_reset3 = st.columns([1, 1, 1])
            with col_reset2:
                if st.button("🔄 다시 검사하기", use_container_width=True):
                    st.session_state.devti_current_question = 0
                    st.session_state.devti_answers = [None] * len(questions)
                    st.session_state.devti_test_completed = False
                    st.rerun()

        else:
            st.error("결과를 찾을 수 없습니다. 다시 시도해주세요.")
