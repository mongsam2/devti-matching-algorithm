"""
team_info = [
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

CATEGORY_DATA = {
    # element: [name1, name2]
    "team_vibe": ["learning", "professional"],
    "active_hours": ["day", "night"],
    "meeting_preference": ["online", "offline"],
}


def get_category_score(team_info: list[list[dict]]):
    category_weight = _category_weight(team_info)
    all_team_similarity = []

    for team in team_info:
        # 한 팀의 카테고리 유사도 딕셔너리
        team_similarity = _team_similarity(team)
        all_team_similarity.append(team_similarity)

    team_scores = []
    for team_similarity in all_team_similarity:
        team_score = 0
        for element, [name, rate] in team_similarity:
            team_score += rate * category_weight[element][name]
        team_scores.append(team_score / len(team_similarity))

    return sum(team_scores) / len(team_scores)


def _team_similarity(member_list: list[dict]) -> dict[list]:
    """
    한 팀의 카테고리 데이터 유사도를 반환 [highest_name, rate]
    """
    team_size = len(member_list)
    team_category_count = {}  # 카테고리 개수를 저장할 딕셔너리
    for names in CATEGORY_DATA.values():
        for name in names:
            team_category_count[name] = 0

    for member in member_list:  # team category info에 값을 채움
        for element in CATEGORY_DATA:
            team_category_count[member[element]] += 1

    # category 항목별 가장 빈도수가 높은 값과, 그 비율을 저장
    result = {}
    for element in CATEGORY_DATA:
        result[element] = []
        highest_name, highest_count = "", 0

        for name in CATEGORY_DATA[element]:
            if team_category_count[name] > highest_count:
                highest_name = name
                highest_count = team_category_count[name]

        result[element] = [highest_name, highest_count / team_size]
    return result


def _category_weight(team_info: list[list[dict]]):
    """
    카테고리 데이터의 가중치 정보를 담은 딕셔너리를 반환
    {
        element: {
            name1: 0.82, name2: 0.18
        }
    }
    """
    category_count = {}  # 카테고리 통계
    for element in CATEGORY_DATA:
        count = [0 for _ in range(len(CATEGORY_DATA[element]))]
        mapping = {name: i for i, name in enumerate(CATEGORY_DATA[element])}
        for member_list in team_info:
            for member in member_list:
                count[mapping[member[element]]] += 1

    output = {}
    for element in CATEGORY_DATA:
        total = sum(category_count[element])
        output[element] = {
            name: 1 - (category_count[i] / total)
            for i, name in enumerate(CATEGORY_DATA[element])
        }
    return output
