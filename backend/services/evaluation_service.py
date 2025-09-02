import json
import os
from typing import List, Dict, Optional
import numpy as np

from models.club import Club, ClubRanking, EvaluationMetrics, Event, SocialMediaMetric, WhatsAppActivity
from services.club_service import ClubService
from services.grouping_service import ClubGroupingService

class ClubEvaluationService:

    
    def __init__(self):
        self.club_service = ClubService()
        self.grouping_service = ClubGroupingService()
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        
        # Load all data
        self.events = self._load_events()
        self.social_media_metrics = self._load_social_media_metrics()
        self.whatsapp_activity = self._load_whatsapp_activity()
        self.voting_data = self._load_voting_data()
        
        # Evaluation weights for different metrics
        self.weights = {
            "social_media": 0.2,
            "event_impact": 0.3,
            "community_engagement": 0.25,
            "collaboration": 0.15,
            "voting": 0.1
        }
    
    def _load_events(self) -> List[Event]:

        try:
            events_file = os.path.join(self.data_dir, 'events.json')
            with open(events_file, 'r', encoding='utf-8') as f:
                events_data = json.load(f)
            
            events = []
            for event_data in events_data['events']:
                event = Event(**event_data)
                events.append(event)
            
            return events
        except Exception as e:
            print(f"Error loading events: {e}")
            return []
    
    def _load_social_media_metrics(self) -> List[SocialMediaMetric]:
 
        try:
            sm_file = os.path.join(self.data_dir, 'social_media_metrics.json')
            with open(sm_file, 'r', encoding='utf-8') as f:
                sm_data = json.load(f)
            
            metrics = []
            for metric_data in sm_data['social_media_metrics']:
                metric = SocialMediaMetric(**metric_data)
                metrics.append(metric)
            
            return metrics
        except Exception as e:
            print(f"Error loading social media metrics: {e}")
            return []
    
    def _load_whatsapp_activity(self) -> List[WhatsAppActivity]:

        try:
            wa_file = os.path.join(self.data_dir, 'whatsapp_activity.json')
            with open(wa_file, 'r', encoding='utf-8') as f:
                wa_data = json.load(f)
            
            activities = []
            for activity_data in wa_data['whatsapp_activity']:
                activity = WhatsAppActivity(**activity_data)
                activities.append(activity)
            
            return activities
        except Exception as e:
            print(f"Error loading WhatsApp activity: {e}")
            return []
    
    def _load_voting_data(self) -> Dict:

        try:
            voting_file = os.path.join(self.data_dir, 'voting_data.json')
            with open(voting_file, 'r', encoding='utf-8') as f:
                voting_data = json.load(f)
            
            return voting_data
        except Exception as e:
            print(f"Error loading voting data: {e}")
            return {}
    
    def calculate_club_metrics(self, club_id: int) -> EvaluationMetrics:

        
        # Calculate individual metric scores
        social_media_score = self._calculate_social_media_score(club_id)
        event_impact_score = self._calculate_event_impact_score(club_id)
        community_engagement_score = self._calculate_community_engagement_score(club_id)
        collaboration_score = self._calculate_collaboration_score(club_id)
        voting_score = self._calculate_voting_score(club_id)
        
        # Calculate weighted overall score
        overall_score = (
            social_media_score * self.weights["social_media"] +
            event_impact_score * self.weights["event_impact"] +
            community_engagement_score * self.weights["community_engagement"] +
            collaboration_score * self.weights["collaboration"] +
            voting_score * self.weights["voting"]
        )
        
        return EvaluationMetrics(
            club_id=club_id,
            social_media_score=social_media_score,
            event_impact_score=event_impact_score,
            community_engagement_score=community_engagement_score,
            collaboration_score=collaboration_score,
            voting_score=voting_score,
            overall_score=overall_score
        )
    
    def _calculate_social_media_score(self, club_id: int) -> float:
        club_metrics = [m for m in self.social_media_metrics if m.club_id == club_id]
        
        if not club_metrics:
            return 0.0
        
        total_score = 0.0
        for metric in club_metrics:
            # Normalize metrics to 0-10 scale
            engagement_score = min(metric.engagement_rate, 10.0)
            activity_score = min(metric.posts_last_month / 5.0, 10.0)  # 5 posts per month = score of 10
            collaboration_score = min(metric.collaboration_posts * 2.0, 10.0)  # 5 collab posts = score of 10
            
            platform_score = (engagement_score + activity_score + collaboration_score) / 3.0
            total_score += platform_score
        
        return min(total_score / len(club_metrics), 10.0)
    
    def _calculate_event_impact_score(self, club_id: int) -> float:
        club_events = [e for e in self.events if e.club_id == club_id]
        
        if not club_events:
            return 0.0
        
        total_score = 0.0
        for event in club_events:
            # Factor in multiple aspects of event impact
            impact_score = event.impact_score  # Already on 0-10 scale
            participation_score = min(event.participants / 50.0, 10.0)  # 50 participants = score of 10
            duration_score = min(event.duration_hours / 8.0, 10.0)  # 8 hours = score of 10
            
            event_score = (impact_score * 0.5 + participation_score * 0.3 + duration_score * 0.2)
            total_score += event_score
        
        return min(total_score / len(club_events), 10.0)
    
    def _calculate_community_engagement_score(self, club_id: int) -> float:
        club_activities = [w for w in self.whatsapp_activity if w.club_id == club_id]
        
        if not club_activities:
            return 0.0
        
        total_score = 0.0
        for activity in club_activities:
            # Use the pre-calculated engagement score from WhatsApp analysis
            total_score += activity.engagement_score
        
        return min(total_score / len(club_activities), 10.0)
    
    def _calculate_collaboration_score(self, club_id: int) -> float:
        # Count collaborative events
        collaborative_events = [e for e in self.events if e.club_id == club_id and e.collaboration_clubs]
        
        # Count collaborative social media posts
        collaborative_posts = sum(
            m.collaboration_posts for m in self.social_media_metrics if m.club_id == club_id
        )
        
        # Count collaborative WhatsApp messages
        collaborative_messages = sum(
            w.collaboration_messages for w in self.whatsapp_activity if w.club_id == club_id
        )
        
        # Calculate score based on collaboration frequency
        event_score = min(len(collaborative_events) * 2.0, 10.0)  # 5 collab events = score of 10
        posts_score = min(collaborative_posts * 1.0, 10.0)  # 10 collab posts = score of 10
        messages_score = min(collaborative_messages / 5.0, 10.0)  # 50 collab messages = score of 10
        
        return (event_score + posts_score + messages_score) / 3.0
    
    def _calculate_voting_score(self, club_id: int) -> float:
        if not self.voting_data or 'vote_summary' not in self.voting_data:
            return 5.0  # Default neutral score
        
        vote_summary = self.voting_data['vote_summary']
        categories = vote_summary.get('categories', {})
        total_votes = vote_summary.get('total_votes', 1)
        
        total_score = 0.0
        category_count = 0
        
        for category, votes in categories.items():
            club_votes = votes.get(str(club_id), 0)
            # Normalize to 0-10 scale based on vote percentage
            category_score = (club_votes / total_votes) * 100.0  # Percentage
            category_score = min(category_score * 2.0, 10.0)  # Scale to 0-10
            
            total_score += category_score
            category_count += 1
        
        return total_score / category_count if category_count > 0 else 5.0
    
    def get_overall_rankings(self) -> List[ClubRanking]:

        clubs = self.club_service.get_all_clubs()
        rankings = []
        
        for club in clubs:
            metrics = self.calculate_club_metrics(club.id)
            ranking = ClubRanking(
                rank=0,  # Will be set after sorting
                club=club,
                metrics=metrics
            )
            rankings.append(ranking)
        
        # Sort by overall score (descending)
        rankings.sort(key=lambda x: x.metrics.overall_score, reverse=True)
        
        # Set ranks
        for i, ranking in enumerate(rankings):
            ranking.rank = i + 1
        
        return rankings
    
    def get_group_rankings(self, group_name: str) -> List[ClubRanking]:

        group = self.grouping_service.get_group_by_name(group_name)
        if not group:
            return []
        
        rankings = []
        for club in group.clubs:
            metrics = self.calculate_club_metrics(club.id)
            ranking = ClubRanking(
                rank=0,  # Will be set after sorting
                club=club,
                metrics=metrics,
                group_name=group_name
            )
            rankings.append(ranking)
        
        # Sort by overall score (descending)
        rankings.sort(key=lambda x: x.metrics.overall_score, reverse=True)
        
        # Set ranks
        for i, ranking in enumerate(rankings):
            ranking.rank = i + 1
        
        return rankings
    
    def get_social_media_analytics(self, club_id: int) -> Dict:
       
        club_metrics = [m for m in self.social_media_metrics if m.club_id == club_id]
        
        analytics = {
            "total_followers": sum(m.followers for m in club_metrics),
            "total_posts": sum(m.posts_last_month for m in club_metrics),
            "avg_engagement_rate": np.mean([m.engagement_rate for m in club_metrics]) if club_metrics else 0,
            "platforms": {}
        }
        
        for metric in club_metrics:
            analytics["platforms"][metric.platform] = {
                "followers": metric.followers,
                "posts_last_month": metric.posts_last_month,
                "engagement_rate": metric.engagement_rate,
                "avg_likes": metric.avg_likes,
                "avg_comments": metric.avg_comments,
                "collaboration_posts": metric.collaboration_posts
            }
        
        return analytics
    
    def get_event_analytics(self, club_id: int) -> Dict:

        club_events = [e for e in self.events if e.club_id == club_id]
        
        if not club_events:
            return {"total_events": 0}
        
        return {
            "total_events": len(club_events),
            "total_participants": sum(e.participants for e in club_events),
            "avg_impact_score": np.mean([e.impact_score for e in club_events]),
            "collaborative_events": len([e for e in club_events if e.collaboration_clubs]),
            "event_types": {
                event_type: len([e for e in club_events if e.type == event_type])
                for event_type in set(e.type for e in club_events)
            },
            "recent_events": sorted(club_events, key=lambda x: x.date, reverse=True)[:5]
        }
    
    def get_whatsapp_analytics(self, club_id: int) -> Dict:

        club_activities = [w for w in self.whatsapp_activity if w.club_id == club_id]
        
        if not club_activities:
            return {"total_months": 0}
        
        return {
            "total_months": len(club_activities),
            "avg_messages_per_month": np.mean([w.total_messages for w in club_activities]),
            "avg_active_members": np.mean([w.active_members for w in club_activities]),
            "avg_engagement_score": np.mean([w.engagement_score for w in club_activities]),
            "total_event_discussions": sum(w.event_discussions for w in club_activities),
            "total_help_requests": sum(w.help_requests for w in club_activities),
            "monthly_data": club_activities
        }
    
    def get_voting_summary(self) -> Dict:

        return self.voting_data.get('vote_summary', {})
    
    def get_total_events_count(self) -> int:
 
        return len(self.events)
    
    def get_total_votes_count(self) -> int:

        return self.voting_data.get('vote_summary', {}).get('total_votes', 0)
    
    def get_most_active_club(self) -> Dict:
        
        rankings = self.get_overall_rankings()
        if rankings:
            top_club = rankings[0]
            return {
                "club": top_club.club,
                "overall_score": top_club.metrics.overall_score
            }
        return {}
    
    def get_recent_events(self) -> List[Event]:

        # Sort events by date and return the 5 most recent
        sorted_events = sorted(self.events, key=lambda x: x.date, reverse=True)
        return sorted_events[:5]
