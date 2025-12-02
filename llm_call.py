from pydantic import BaseModel, TypeAdapter
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


def call_llm(type, team_info_list):
    """
    Arge:
        - type = "gemini" || "gpt"
    """
    with open("prompt/explain.txt", "r", encoding="utf-8") as f:
        prompt = f.read()

    if type == "gemini":
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        response = client.models.generate_content(
            model="gemini-3-pro-preview",
            contents=f"{prompt} {team_info_list}",
            config={
                "response_mime_type": "application/json",
                "response_json_schema": TeamList.model_json_schema(),
            },
        )

        response = TeamList.model_validate_json(response.text)
        print(response)
        client.close()
        return response["teams"]

    elif type == "gpt":
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
