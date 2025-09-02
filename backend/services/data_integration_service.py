import json
import os
from typing import List, Dict, Optional
from datetime import datetime
import numpy as np

class DataIntegrationService:
    """
    Service to integrate real scraped data (WhatsApp analysis, social media data)
    and transform it into a format that the evaluation service can use.
    """
    
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.scrapper_dir = os.path.join(os.path.dirname(__file__), '..', 'Scrapper')
    
    def get_social_media_metrics(self) -> List[Dict]:
        """
        Extract social media metrics from the scraped social media data
        """
        try:
            social_media_file = os.path.join(self.scrapper_dir, 'social_media_data.json')
            with open(social_media_file, 'r', encoding='utf-8') as f:
                social_data = json.load(f)
            
            metrics = []
            
            for club_key, club_data in social_data.items():
                club_id = club_data['club_id']
                social_media = club_data.get('social_media', {})
                
                # Process Instagram data
                if 'instagram' in social_media:
                    instagram_data = social_media['instagram']
                    
                    # Convert followers string to integer (remove commas)
                    followers_str = instagram_data.get('followers', '0')
                    followers = int(followers_str.replace(',', '').replace('.', ''))
                    
                    # Estimate engagement metrics based on followers
                    # These are estimates since we don't have exact metrics from scraping
                    estimated_posts = max(5, followers // 100)  # Estimate posts based on followers
                    estimated_engagement_rate = min(8.0, max(2.0, followers / 500))  # Rough estimate
                    estimated_likes = max(10, followers // 10)
                    estimated_comments = max(2, followers // 50)
                    
                    metrics.append({
                        "club_id": club_id,
                        "platform": "instagram",
                        "followers": followers,
                        "posts_last_month": estimated_posts,
                        "engagement_rate": estimated_engagement_rate,
                        "avg_likes": estimated_likes,
                        "avg_comments": estimated_comments,
                        "story_views": int(followers * 0.7),  # Estimate 70% of followers see stories
                        "collaboration_posts": np.random.randint(0, 4)  # Random estimate
                    })
                
                # Process LinkedIn data
                if 'linkedin' in social_media:
                    linkedin_data = social_media['linkedin']
                    
                    # Convert followers string to integer
                    followers_str = linkedin_data.get('followers', '0')
                    followers = int(followers_str.replace(',', '').replace('.', ''))
                    
                    # LinkedIn typically has lower engagement
                    estimated_posts = max(2, followers // 50)
                    estimated_engagement_rate = min(5.0, max(1.0, followers / 100))
                    estimated_likes = max(5, followers // 20)
                    estimated_comments = max(1, followers // 100)
                    
                    metrics.append({
                        "club_id": club_id,
                        "platform": "linkedin",
                        "followers": followers,
                        "posts_last_month": estimated_posts,
                        "engagement_rate": estimated_engagement_rate,
                        "avg_likes": estimated_likes,
                        "avg_comments": estimated_comments,
                        "story_views": 0,  # LinkedIn doesn't have story views
                        "collaboration_posts": np.random.randint(0, 2)  # Random estimate
                    })
            
            return metrics
            
        except Exception as e:
            print(f"Error processing social media data: {e}")
            return []
    
    def get_whatsapp_activity_metrics(self) -> List[Dict]:
        """
        Extract WhatsApp activity metrics from the analyzed chat data
        """
        try:
            whatsapp_file = os.path.join(self.data_dir, 'whatsapp_analysis.json')
            with open(whatsapp_file, 'r', encoding='utf-8') as f:
                whatsapp_data = json.load(f)
            
            activities = []
            
            for club_key, club_data in whatsapp_data.items():
                if isinstance(club_data, dict) and 'club_id' in club_data:
                    club_id = club_data['club_id']
                    
                    # Extract monthly activity data
                    monthly_activity = club_data.get('activity_analysis', {}).get('monthly', {})
                    
                    if monthly_activity:
                        # Process each month
                        for month, message_count in monthly_activity.items():
                            # Calculate estimated active members based on unique senders
                            unique_senders = club_data.get('unique_senders', 0)
                            estimated_active_members = min(unique_senders, max(5, message_count // 10))
                            
                            # Calculate daily average
                            days_in_month = 30  # Simplified
                            avg_messages_per_day = message_count // days_in_month if days_in_month > 0 else 0
                            
                            # Extract content analysis
                            content_analysis = club_data.get('content_analysis', {})
                            
                            activities.append({
                                "club_id": club_id,
                                "month": month,
                                "total_messages": message_count,
                                "active_members": estimated_active_members,
                                "avg_messages_per_day": avg_messages_per_day,
                                "event_discussions": content_analysis.get('event_related', 0),
                                "help_requests": content_analysis.get('help_requests', 0),
                                "collaboration_messages": content_analysis.get('collaboration', 0),
                                "engagement_score": club_data.get('engagement_score', 0)
                            })
                    else:
                        # If no monthly data, create a single entry with overall data
                        total_messages = club_data.get('total_messages', 0)
                        unique_senders = club_data.get('unique_senders', 0)
                        content_analysis = club_data.get('content_analysis', {})
                        
                        activities.append({
                            "club_id": club_id,
                            "month": "2024-overall",
                            "total_messages": total_messages,
                            "active_members": unique_senders,
                            "avg_messages_per_day": total_messages // 365 if total_messages > 0 else 0,
                            "event_discussions": content_analysis.get('event_related', 0),
                            "help_requests": content_analysis.get('help_requests', 0),
                            "collaboration_messages": content_analysis.get('collaboration', 0),
                            "engagement_score": club_data.get('engagement_score', 0)
                        })
            
            return activities
            
        except Exception as e:
            print(f"Error processing WhatsApp data: {e}")
            return []
    
    def generate_social_media_metrics_file(self):
        """
        Generate social_media_metrics.json file from real scraped data
        """
        metrics = self.get_social_media_metrics()
        
        output_data = {
            "social_media_metrics": metrics
        }
        
        output_file = os.path.join(self.data_dir, 'social_media_metrics.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"Generated social media metrics file: {output_file}")
        return output_file
    
    def generate_whatsapp_activity_file(self):
        """
        Generate whatsapp_activity.json file from real analyzed data
        """
        activities = self.get_whatsapp_activity_metrics()
        
        output_data = {
            "whatsapp_activity": activities
        }
        
        output_file = os.path.join(self.data_dir, 'whatsapp_activity.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"Generated WhatsApp activity file: {output_file}")
        return output_file
    
    def update_clubs_data_with_real_metrics(self):
        """
        Update clubs.json with real social media data
        """
        try:
            # Load current clubs data
            clubs_file = os.path.join(self.data_dir, 'clubs.json')
            with open(clubs_file, 'r', encoding='utf-8') as f:
                clubs_data = json.load(f)
            
            # Load social media data
            social_media_file = os.path.join(self.scrapper_dir, 'social_media_data.json')
            with open(social_media_file, 'r', encoding='utf-8') as f:
                social_data = json.load(f)
            
            # Update clubs with real member counts from scraped data
            for club in clubs_data['clubs']:
                club_id = club['id']
                
                # Find corresponding social media data
                for club_key, club_data in social_data.items():
                    if club_data['club_id'] == club_id:
                        social_media = club_data.get('social_media', {})
                        
                        # Update member count based on social media followers
                        total_followers = 0
                        if 'instagram' in social_media:
                            followers_str = social_media['instagram'].get('followers', '0')
                            instagram_followers = int(followers_str.replace(',', '').replace('.', ''))
                            total_followers += instagram_followers
                        
                        if 'linkedin' in social_media:
                            followers_str = social_media['linkedin'].get('followers', '0')
                            linkedin_followers = int(followers_str.replace(',', '').replace('.', ''))
                            total_followers += linkedin_followers
                        
                        # Estimate actual member count (assuming not all members follow on social media)
                        estimated_members = max(club.get('member_count', 50), int(total_followers * 1.2))
                        club['member_count'] = estimated_members
                        break
            
            # Save updated clubs data
            with open(clubs_file, 'w', encoding='utf-8') as f:
                json.dump(clubs_data, f, indent=2, ensure_ascii=False)
            
            print(f"Updated clubs data with real metrics: {clubs_file}")
            return clubs_file
            
        except Exception as e:
            print(f"Error updating clubs data: {e}")
            return None
    
    def integrate_all_data(self):
        """
        Integrate all real scraped data and generate necessary files
        """
        print("Starting data integration...")
        
        # Generate social media metrics from scraped data
        social_media_file = self.generate_social_media_metrics_file()
        
        # Generate WhatsApp activity from analyzed chat data
        whatsapp_file = self.generate_whatsapp_activity_file()
        
        # Update clubs data with real metrics
        clubs_file = self.update_clubs_data_with_real_metrics()
        
        print("Data integration completed!")
        
        return {
            "social_media_metrics": social_media_file,
            "whatsapp_activity": whatsapp_file,
            "clubs_data": clubs_file
        }

def main():
    """
    Main function to run data integration
    """
    service = DataIntegrationService()
    results = service.integrate_all_data()
    
    print("\nIntegrated data files:")
    for file_type, file_path in results.items():
        print(f"  {file_type}: {file_path}")

if __name__ == "__main__":
    main()
