import json
import os
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

@dataclass
class ClubEvaluationResult:

    club_id: int
    club_name: str
    overall_score: float
    social_media_score: float
    chat_engagement_score: float
    combined_reach_score: float
    community_activity_score: float
    content_quality_score: float
    rank: int = 0
    
    def to_dict(self):
        return {
            'club_id': self.club_id,
            'club_name': self.club_name,
            'overall_score': round(self.overall_score, 2),
            'social_media_score': round(self.social_media_score, 2),
            'chat_engagement_score': round(self.chat_engagement_score, 2),
            'combined_reach_score': round(self.combined_reach_score, 2),
            'community_activity_score': round(self.community_activity_score, 2),
            'content_quality_score': round(self.content_quality_score, 2),
            'rank': self.rank
        }

class ComprehensiveClubEvaluator:
    
    
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.scrapper_dir = os.path.join(os.path.dirname(__file__), '..', 'Scrapper')
        
        # Load data sources
        self.social_media_data = self._load_social_media_data()
        self.whatsapp_data = self._load_whatsapp_data()
        self.clubs_data = self._load_clubs_data()
        
        # Evaluation weights
        self.weights = {
            'social_media': 0.35,      # Instagram + LinkedIn metrics
            'chat_engagement': 0.25,    # WhatsApp engagement quality
            'reach': 0.20,             # Combined follower reach
            'community_activity': 0.15, # Chat activity volume
            'content_quality': 0.05    # Content relevance and quality
        }
    
    def _load_social_media_data(self) -> Dict:

        try:
            sm_file = os.path.join(self.scrapper_dir, 'social_media_data.json')
            with open(sm_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading social media data: {e}")
            return {}
    
    def _load_whatsapp_data(self) -> Dict:
        """Load WhatsApp analysis data"""
        try:
            wa_file = os.path.join(self.data_dir, 'whatsapp_analysis.json')
            with open(wa_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading WhatsApp data: {e}")
            return {}
    
    def _load_clubs_data(self) -> Dict:
       
        try:
            clubs_file = os.path.join(self.data_dir, 'clubs.json')
            with open(clubs_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {club['id']: club for club in data['clubs']}     
        except Exception as e:
            print(f"Error loading clubs data: {e}")
            return {}
    
    def calculate_social_media_score(self, club_id: int) -> float:
        
        club_key = f"club_{club_id}"
        if club_key not in self.social_media_data:
            return 0.0
        
        club_sm = self.social_media_data[club_key].get('social_media', {})
        
        total_score = 0.0
        platform_count = 0
        
        # Instagram metrics
        if 'instagram' in club_sm:
            ig = club_sm['instagram']
            followers = self._parse_number(ig.get('followers', '0'))
            
            # Instagram scoring
            follower_score = min(followers / 100, 5.0)  # Max 5 points for 1000+ followers
            bio_quality = 3.0 if len(ig.get('bio', '')) > 50 else 1.0
            
            ig_score = follower_score + bio_quality
            total_score += min(ig_score, 8.0)
            platform_count += 1
        
        # LinkedIn metrics
        if 'linkedin' in club_sm:
            li = club_sm['linkedin']
            followers = self._parse_number(li.get('followers', '0'))
            about = li.get('about', '')
            
            # LinkedIn scoring
            follower_score = min(followers / 50, 4.0)  # Max 4 points for 200+ followers
            about_quality = 4.0 if len(about) > 100 and 'N/A' not in about else 1.0
            
            li_score = follower_score + about_quality
            total_score += min(li_score, 8.0)
            platform_count += 1
        
        return min(total_score / platform_count, 10.0) if platform_count > 0 else 0.0
    
    def calculate_chat_engagement_score(self, club_id: int) -> float:
        club_key = f"club_{club_id}"
        if club_key not in self.whatsapp_data:
            return 0.0
        
        chat_data = self.whatsapp_data[club_key]
        
        # Use the pre-calculated engagement score from chat analyzer
        base_score = chat_data.get('engagement_score', 0.0)
        
        # Additional factors
        response_rate = chat_data.get('response_patterns', {}).get('response_rate_percentage', 0)
        content_analysis = chat_data.get('content_analysis', {})
        
        # Bonus for good response rate
        response_bonus = min(response_rate / 100 * 2, 2.0)  # Max 2 points for 100% response rate
        
        # Bonus for content quality
        event_ratio = content_analysis.get('event_related', 0) / max(chat_data.get('total_messages', 1), 1)
        content_bonus = min(event_ratio * 10, 1.0)  # Max 1 point for high event content
        
        total_score = base_score + response_bonus + content_bonus
        return min(total_score, 10.0)
    
    def calculate_combined_reach_score(self, club_id: int) -> float:
        club_key = f"club_{club_id}"
        
        total_followers = 0
        
        # Social media followers
        if club_key in self.social_media_data:
            club_sm = self.social_media_data[club_key].get('social_media', {})
            
            if 'instagram' in club_sm:
                total_followers += self._parse_number(club_sm['instagram'].get('followers', '0'))
            
            if 'linkedin' in club_sm:
                total_followers += self._parse_number(club_sm['linkedin'].get('followers', '0'))
        
        # WhatsApp group members
        if club_key in self.whatsapp_data:
            total_followers += self.whatsapp_data[club_key].get('unique_senders', 0) * 2  # Estimate total members
        
        # Score based on total reach
        reach_score = min(total_followers / 200, 10.0)  # Max 10 points for 2000+ total reach
        
        return reach_score
    
    def calculate_community_activity_score(self, club_id: int) -> float:
        club_key = f"club_{club_id}"
        
        if club_key not in self.whatsapp_data:
            return 0.0
        
        chat_data = self.whatsapp_data[club_key]
        
        # Message volume score
        total_messages = chat_data.get('total_messages', 0)
        message_score = min(total_messages / 200, 5.0)  # Max 5 points for 1000+ messages
        
        # Participation score
        unique_senders = chat_data.get('unique_senders', 0)
        participation_score = min(unique_senders / 20, 3.0)  # Max 3 points for 60+ unique senders
        
        # Consistency score (monthly activity)
        monthly_activity = chat_data.get('activity_analysis', {}).get('monthly', {})
        active_months = len([count for count in monthly_activity.values() if count > 0])
        consistency_score = min(active_months / 6, 2.0)  # Max 2 points for 12+ active months
        
        total_score = message_score + participation_score + consistency_score
        return min(total_score, 10.0)
    
    def calculate_content_quality_score(self, club_id: int) -> float:
        """Calculate content quality and relevance score (0-10)"""
        club_key = f"club_{club_id}"
        
        score = 0.0
        
        # Social media content quality
        if club_key in self.social_media_data:
            club_sm = self.social_media_data[club_key].get('social_media', {})
            
            # Instagram bio quality
            if 'instagram' in club_sm:
                bio = club_sm['instagram'].get('bio', '')
                if len(bio) > 50 and any(word in bio.lower() for word in ['official', 'club', 'community']):
                    score += 2.0
            
            # LinkedIn about quality
            if 'linkedin' in club_sm:
                about = club_sm['linkedin'].get('about', '')
                if len(about) > 100 and 'N/A' not in about:
                    score += 3.0
        
        # WhatsApp content quality
        if club_key in self.whatsapp_data:
            chat_data = self.whatsapp_data[club_key]
            content_analysis = chat_data.get('content_analysis', {})
            total_messages = max(chat_data.get('total_messages', 1), 1)
            
            # Event-related content
            event_ratio = content_analysis.get('event_related', 0) / total_messages
            score += min(event_ratio * 30, 3.0)  # Max 3 points for high event content ratio
            
            # Help and collaboration
            help_ratio = content_analysis.get('help_requests', 0) / total_messages
            collab_ratio = content_analysis.get('collaboration', 0) / total_messages
            score += min((help_ratio + collab_ratio) * 20, 2.0)  # Max 2 points for helpful content
        
        return min(score, 10.0)
    
    def evaluate_club(self, club_id: int) -> ClubEvaluationResult:
        club_info = self.clubs_data.get(club_id, {})
        club_name = club_info.get('name', f'Club {club_id}')
        
        # Calculate individual scores
        social_media_score = self.calculate_social_media_score(club_id)
        chat_engagement_score = self.calculate_chat_engagement_score(club_id)
        combined_reach_score = self.calculate_combined_reach_score(club_id)
        community_activity_score = self.calculate_community_activity_score(club_id)
        content_quality_score = self.calculate_content_quality_score(club_id)
        
        # Calculate weighted overall score
        overall_score = (
            social_media_score * self.weights['social_media'] +
            chat_engagement_score * self.weights['chat_engagement'] +
            combined_reach_score * self.weights['reach'] +
            community_activity_score * self.weights['community_activity'] +
            content_quality_score * self.weights['content_quality']
        )
        
        return ClubEvaluationResult(
            club_id=club_id,
            club_name=club_name,
            overall_score=overall_score,
            social_media_score=social_media_score,
            chat_engagement_score=chat_engagement_score,
            combined_reach_score=combined_reach_score,
            community_activity_score=community_activity_score,
            content_quality_score=content_quality_score
        )
    
    def evaluate_all_clubs(self) -> List[ClubEvaluationResult]:
        results = []
        
        # Get all club IDs from available data
        club_ids = set()
        
        if self.social_media_data:
            club_ids.update([int(key.split('_')[1]) for key in self.social_media_data.keys() if key.startswith('club_')])
        
        if self.whatsapp_data:
            club_ids.update([int(key.split('_')[1]) for key in self.whatsapp_data.keys() if key.startswith('club_')])
        
        club_ids.update(self.clubs_data.keys())
        
        # Evaluate each club
        for club_id in club_ids:
            result = self.evaluate_club(club_id)
            results.append(result)
        
        # Sort by overall score (descending)
        results.sort(key=lambda x: x.overall_score, reverse=True)
        
        # Assign ranks
        for i, result in enumerate(results):
            result.rank = i + 1
        
        return results
    
    def get_detailed_analysis(self, club_id: int) -> Dict:
        result = self.evaluate_club(club_id)
        
        club_key = f"club_{club_id}"
        
        # Social media details
        sm_details = {}
        if club_key in self.social_media_data:
            sm_details = self.social_media_data[club_key].get('social_media', {})
        
        # WhatsApp details
        wa_details = {}
        if club_key in self.whatsapp_data:
            wa_details = self.whatsapp_data[club_key]
        
        return {
            'evaluation': result.to_dict(),
            'social_media_details': sm_details,
            'whatsapp_details': wa_details,
            'recommendations': self._generate_recommendations(result, sm_details, wa_details)
        }
    
    def _generate_recommendations(self, result: ClubEvaluationResult, sm_details: Dict, wa_details: Dict) -> List[str]:
        recommendations = []
        
        if result.social_media_score < 5.0:
            recommendations.append("Improve social media presence by posting more regularly and engaging with followers")
        
        if result.chat_engagement_score < 5.0:
            recommendations.append("Increase WhatsApp group engagement by organizing more discussions and responding to members")
        
        if result.combined_reach_score < 5.0:
            recommendations.append("Focus on growing follower base across all platforms")
        
        if result.community_activity_score < 5.0:
            recommendations.append("Encourage more community participation and regular communication")
        
        if result.content_quality_score < 5.0:
            recommendations.append("Improve content quality by sharing more event-related and educational content")
        
        # Specific recommendations based on data
        if sm_details:
            instagram = sm_details.get('instagram', {})
            if instagram and self._parse_number(instagram.get('followers', '0')) < 500:
                recommendations.append("Focus on Instagram growth through consistent posting and community engagement")
        
        return recommendations
    
    def _parse_number(self, value: str) -> int:
        if isinstance(value, (int, float)):
            return int(value)
        
        if isinstance(value, str):
            # Remove commas and convert to int
            cleaned = value.replace(',', '').replace('N/A', '0')
            try:
                return int(float(cleaned))
            except ValueError:
                return 0
        
        return 0
    
    def save_evaluation_results(self, results: List[ClubEvaluationResult], filename: str = 'comprehensive_evaluation.json'):
        output_data = {
            'evaluation_date': datetime.now().isoformat(),
            'methodology': {
                'weights': self.weights,
                'description': 'Comprehensive club evaluation using social media data and WhatsApp chat analysis'
            },
            'rankings': [result.to_dict() for result in results]
        }
        
        output_path = os.path.join(self.data_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"Evaluation results saved to {output_path}")
        return output_path

def main():
    evaluator = ComprehensiveClubEvaluator()
    
    print("Starting Comprehensive Club Evaluation...")
    print("Using Social Media Data + WhatsApp Chat Analysis")
    print("="*60)
    
    # Evaluate all clubs
    results = evaluator.evaluate_all_clubs()
    
    # Display results
    print(f"\n{'Rank':<4} {'Club Name':<25} {'Overall':<8} {'Social':<7} {'Chat':<6} {'Reach':<6} {'Activity':<8} {'Content':<8}")
    print("-" * 80)
    
    for result in results:
        print(f"{result.rank:<4} {result.club_name:<25} {result.overall_score:<8.2f} {result.social_media_score:<7.2f} {result.chat_engagement_score:<6.2f} {result.combined_reach_score:<6.2f} {result.community_activity_score:<8.2f} {result.content_quality_score:<8.2f}")
    
    # Save results
    evaluator.save_evaluation_results(results)
    
    # Show detailed analysis for top 3 clubs
    print(f"\n{'='*60}")
    print("DETAILED ANALYSIS - TOP 3 CLUBS")
    print("="*60)
    
    for i, result in enumerate(results[:3]):
        print(f"\n{i+1}. {result.club_name} (Score: {result.overall_score:.2f})")
        analysis = evaluator.get_detailed_analysis(result.club_id)
        
        print(f"   Strengths:")
        if result.social_media_score >= 7:
            print(f"   • Strong social media presence ({result.social_media_score:.1f}/10)")
        if result.chat_engagement_score >= 7:
            print(f"   • High community engagement ({result.chat_engagement_score:.1f}/10)")
        if result.combined_reach_score >= 7:
            print(f"   • Excellent reach across platforms ({result.combined_reach_score:.1f}/10)")
        
        recommendations = analysis['recommendations']
        if recommendations:
            print(f"   Recommendations:")
            for rec in recommendations[:2]:  # Show top 2 recommendations
                print(f"   • {rec}")
    
    return results

if __name__ == "__main__":
    main()
