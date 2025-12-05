from pydantic import BaseModel
from google import genai
from openai import OpenAI
import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

class TeamVibe(BaseModel):
    vibe: str
    score: float


class ActiveHours(BaseModel):
    hours: str
    score: float


class MeetingPreference(BaseModel):
    preference: str
    score: float


class Team(BaseModel):
    team_vibe: TeamVibe
    active_hours: ActiveHours
    meeting_preference: MeetingPreference
    ei: float
    sn: float
    tf: float
    jp: float
    poppy_list: List[str]
    reason: str


class TeamList(BaseModel):
    teams: List[Team]


def call_llm(team_info_list):
    """
    Arge:
        - type = "gemini" || "gpt"
    """
    with open("prompt/explain.txt", "r", encoding="utf-8") as f:
        prompt = f.read()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.beta.chat.completions.parse(
        model="gpt-5.1",
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
            {"role": "user", "content": f"{team_info_list}"},
        ],
        response_format=TeamList,
    )
    return response.choices[0].message.parsed.teams
