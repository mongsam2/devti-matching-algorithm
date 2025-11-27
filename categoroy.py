"""
team_list = [
    [
        {
            "id" 1,
            "team_vibe": "빡세게",
            "active_hours": "밤",
            "meeting_preference": "온라인",
            "waggee_list": [1, 3, 4, 5, 6, 9],
            "openness": 0.84,
            "conscientiousness": 0.34,
            "extraversion": 0.56,
            "agreeableness": 0.34,
            "neuroticism': 0.99,
        },
        {},
        {},
        ...
    ],
    [],
    []
]
"""

CATEGORY = {
    # element: [name1, name2]
    "team_vibe": ["learning", "professional"],
    "active_hours": ["day", "night"],
    "meeting_preference": ["online", "offline"],
}


def get_category_score(team_list: list[list[dict]]) -> list[dict]:
    """
    모든 팀의 카테고리 데이터 점수를 반환

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

    return:
        - category_score = [0.45, 0.88]
    """
    category_weight = _get_category_weight(team_list)
    category_score = []

    for team in team_list:
        team_similarity = _get_team_similarity(team)
        team_score = 0  # 한 팀의 카테고리 점수

        for key, values in team_similarity.items():
            most_frequent_value, rate = [
                (value, team_similarity[key][value]) for value in values
            ].sorted(key=lambda x: -x[1])[0]
            weight = category_weight[key][most_frequent_value]
            score = rate * weight
            team_score += score
        team_score = round(team_score / len(team_similarity), 2)
        category_score.append(team_score)

    return category_score


def _get_team_similarity(member_list: list[dict]) -> dict[dict]:
    """
    한 팀의 카테고리 데이터 유사도를 반환

    input:
        - member_list = [
                {member1},
                {member2},
                ...
            ]

    return:
        - similarity = {
                "team_vibe": {"learning": 0.65, "professional": 0.35},
                "active_hours": {},
                "meeting_preference: {}
            }
    """
    team_size = len(member_list)

    # 카테고리 개수를 저장할 딕셔너리
    team_category_count = {
        key: {value: 0 for value in values} for key, values in CATEGORY.items()
    }

    # team _category_count 업데이트
    for member in member_list:
        for category_key in CATEGORY:
            team_category_count[category_key][member[category_key]] += 1

    # 각 카테고리의 유사도를 저장 (카테고리가 일치하는 사람의 비율)
    similarity = {}
    for key, values in team_category_count.items():
        similarity[key] = {}  # 추가 필요
        value_total = sum(team_category_count[key][value] for value in values)

        for value in values:
            similarity[key][value] = round(
                team_category_count[key][value] / value_total, 2
            )

    return similarity


def _get_category_weight(team_list: list[list[dict]]) -> dict[dict]:
    """
    카테고리 데이터의 가중치 정보를 담은 딕셔너리를 반환

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

    return:
        - category_weight = {
            team_vibe: {learning: 0.82, professional: 0.18},
            active_hours: {},
        }
    """
    # 카테고리 통계
    category_count = {
        key: {value: 0 for value in values} for key, values in CATEGORY.items()
    }
    for team in team_list:
        for member in team:
            for key in CATEGORY:
                category_count[key][member[key]] += 1

    category_weight = {}
    for key, values in category_count.items():
        value_total = sum(category_count[key][value] for value in values)

        for value in values:
            category_weight[key][value] = 1 - round(
                category_count[key][value] / value_total, 2
            )

    return category_weight
