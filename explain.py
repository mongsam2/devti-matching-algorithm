"""
TODO:
    - 팀별로 카테고리 데이터에서 가장 일치도가 높은 것을 바탕으로 설명
    - 다른 팀에 비해 우리팀의 성격 유형이 어떤지를 설명 (다른팀 보다 외향적이에요! 활기차게 팀플해봐요) 어떻게 팀플을 해나가면 좋을지는 LLM에게 맏기기
"""

from parameter import CATEGORY
from category import _get_team_category_rate


def create_explain(team_list):
    """
    input:
        - team_list = [
            [
                {
                    "id": 1,
                    "part": "",
                    "team_vibe": "learning",
                    "active_hours": "day",
                    "meeting_preference": "offline",
                    "ei": 0.65,
                    "sn": 0.73,
                    "tf": 0.42,
                    "jp": 0.58,
                    "devti": "골든 리트리버"
                },
                {member2},
                ...
            ],
            [],
            [],
            ...
        ]
    """


def _get_team_info(team_list):
    """
    팀 매칭 결과에 대한 설명글을 작성하기 위해 LLM에 전달할 팀별 통계 데이터를 반환

    input:
        - team_list = [
            [
                {
                    "id": 1,
                    "part": "",
                    "team_vibe": "learning",
                    "active_hours": "day",
                    "meeting_preference": "offline",
                    "ei": 0.65,
                    "sn": 0.73,
                    "tf": 0.42,
                    "jp": 0.58,
                    "devti": "골든 리트리버"
                },
                {member2},
                ...
            ],
            [],
            [],
            ...
        ]

    return:
        - team_info_list = [
            {
                "team_vibe": ("professional", 0.8),
                "active_hours": ("day", 0.5),
                "meeting_preference": ("online": 0.6),
                "ei": 0.5,
                "sn": 0.7,
                "tf": 0.9,
                "jp": 0.4,
                "poppy_list": ["골든 리트리버", "시바견", "불독", "말티즈"]
            },
            {team},
            ...
        ]
    """
    team_info_list = []
    for team in team_list:
        team_info = {}

        # 팀별 가장 높은 카테고리 데이터와 비율
        team_category_rate = _get_team_category_rate(team)
        for key, rate_dict in team_category_rate:
            max_value, rate = max(rate_dict.items(), key=lambda x: x[1])
            team_info[key] = (max_value, rate)

        # 팀별 mbti 통계
        ei_mean = sum([member["ei"] for member in team]) / len(team)
        sn_mean = sum([member["sn"] for member in team]) / len(team)
        tf_mean = sum([member["tf"] for member in team]) / len(team)
        jp_mean = sum([member["jp"] for member in team]) / len(team)
        team_info["ei"] = ei_mean
        team_info["sn"] = sn_mean
        team_info["tf"] = tf_mean
        team_info["jp"] = jp_mean

        # 팀에 있는 강아지 목록 추가
        team_info["poppy_list"] = [member["devti"] for member in team]

        team_info_list.append(team_info)

    return team_info_list
