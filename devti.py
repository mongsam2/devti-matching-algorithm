import streamlit as st
import pandas as pd
import json
import random

from utils import get_team_size, random_team_assignment

st.title("DevTI 팀 매팅 알고리즘 테스트")


def load_sample_data(file_name):
    with open(file_name, encoding="utf-8") as f:
        data = json.load(f)
    return data


participant_data = load_sample_data("participant_sample.json")
wagging_data = load_sample_data("wagging_sample.json")

st.subheader("테스트 데이터 원본")
st.write(pd.DataFrame(participant_data).set_index("id"))
st.write(pd.DataFrame(wagging_data).set_index("id"))

st.subheader("적절한 팀원 수 추출")

teams_info = []
if st.button("팀 생성"):
    teams_info = get_team_size(participant_list=participant_data)
    cols = st.columns(len(teams_info))
    for i, team_info in enumerate(teams_info):
        cols[i].badge

        for part, count in team_info.items():
            cols[i].badge(f"{part}: {count}")

    team_result = random_team_assignment(participant_data, teams_info)
    st.write(team_result)
