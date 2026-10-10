from pydantic import BaseModel
from typing import List, Optional


class FlashcardItem(BaseModel):
    question: str
    answer: str


class TopicItem(BaseModel):
    title: str
    definition: str


class TopicsResponse(BaseModel):
    topics: List[TopicItem]


class ExamRequest(BaseModel):
    marks_1: int = 2
    marks_2: int = 5
    marks_5: int = 3
    marks_10: int = 0


class SummaryResponse(BaseModel):
    summary: str


class StudyResponse(BaseModel):
    study_notes: str


class MindMapResponse(BaseModel):
    mind_map: str


class ExamResponse(BaseModel):
    exam_paper: str
