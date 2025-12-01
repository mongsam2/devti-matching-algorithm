"""
TODO:
    - 팀별로 카테고리 데이터에서 가장 일치도가 높은 것을 바탕으로 설명
    - 다른 팀에 비해 우리팀의 성격 유형이 어떤지를 설명 (다른팀 보다 외향적이에요! 활기차게 팀플해봐요) 어떻게 팀플을 해나가면 좋을지는 LLM에게 맏기기
"""


def create_explain(team_list):
    """
    input:
        - team_list = [
            [
                {member1},
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
    return:
        - team_info = [
            {
                "team_vibe": ("professional", 0.8),
                "active_hours": ("day", 0.5),
                "meeting_preference': ("online": 0.6),
                "ei": 0.5,
                "sn": 0.7,
                "tf": 0.9,
                "jp": 0.4,
                "poppy_list": ["리트리버", "시바견", "불독", "말티즈"]
            },
            {team},
            ...
        ]
    """
