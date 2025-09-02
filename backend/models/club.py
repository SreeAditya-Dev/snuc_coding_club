
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class Club(BaseModel):

    id: int
    name: str
    category: str
    description: str
    social_media: Dict[str, str]
    founded_year: int
    member_count: int
    activities: List[str]
    keywords: List[str]

class Event(BaseModel):
    id: int
    club_id: int
    name: str
    type: str
    date: str
    participants: int
    duration_hours: int
    impact_score: float
    collaboration_clubs: List[int]
    description: str

class SocialMediaMetric(BaseModel):
    club_id: int
    platform: str
    followers: int
    posts_last_month: int
    engagement_rate: float
    avg_likes: int
    avg_comments: int
    story_views: int
    collaboration_posts: int

class WhatsAppActivity(BaseModel):
    club_id: int
    month: str
    total_messages: int
    active_members: int
    avg_messages_per_day: int
    event_discussions: int
    help_requests: int
    collaboration_messages: int
    engagement_score: float

class VotingData(BaseModel):
    voter_id: str
    department: str
    year: int
    votes: Dict[str, int]
    timestamp: str

class ClubGroup(BaseModel):
    group_name: str
    description: str
    clubs: List[Club]
    similarity_score: float

class EvaluationMetrics(BaseModel):
    club_id: int
    social_media_score: float
    event_impact_score: float
    community_engagement_score: float
    collaboration_score: float
    voting_score: float
    overall_score: float

class ClubRanking(BaseModel):
    rank: int
    club: Club
    metrics: EvaluationMetrics
    group_name: Optional[str] = None
