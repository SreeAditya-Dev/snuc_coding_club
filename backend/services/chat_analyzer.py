import re
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict
import numpy as np

class WhatsAppChatAnalyzer:
    
    
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.chat_dir = os.path.join(self.data_dir, 'chat')
        
        # Keywords for different types of content
        self.event_keywords = [
            'event', 'workshop', 'competition', 'hackathon', 'meeting', 'session',
            'practice', 'performance', 'show', 'concert', 'exhibition', 'contest',
            'audition', 'registration', 'register', 'participate', 'join'
        ]
        
        self.help_keywords = [
            'help', 'doubt', 'question', 'problem', 'issue', 'stuck', 'confused',
            'clarification', 'explain', 'how to', 'can someone', 'need assistance'
        ]
        
        self.collaboration_keywords = [
            'collab', 'collaboration', 'together', 'team up', 'joint', 'partner',
            'work with', 'combine', 'merge', 'cross-club', 'inter-club'
        ]
        
        self.engagement_keywords = [
            'great', 'awesome', 'excellent', 'amazing', 'love', 'like', 'thanks',
            'thank you', 'good', 'nice', 'cool', 'interested', 'excited'
        ]
        
        # Club name mapping for chat files
        self.club_mapping = {
            'SNUC Coding Club_chat.txt': {'id': 1, 'name': 'SNUC Coding Club'},
            'Potential Robotics Club_chat.txt': {'id': 2, 'name': 'Potential Robotics Club'},
            'SSN-SNUC MUN_chat.txt': {'id': 3, 'name': 'SSN-SNUC MUN'},
            'SNUC Rhythm_chat.txt': {'id': 4, 'name': 'SNUC Rhythm'},
            'Isai_chat.txt': {'id': 5, 'name': 'Isai'},
            'Montage_chat.txt': {'id': 6, 'name': 'Montage'}
        }
    
    def parse_whatsapp_message(self, line: str) -> Optional[Dict]:
        
        # Pattern for WhatsApp message format
        pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}),?\s*(\d{1,2}:\d{2}\s*(?:am|pm|AM|PM)?)\s*-\s*([^:]+):\s*(.*)'
        
        match = re.match(pattern, line.strip())
        if match:
            date_str, time_str, sender, message = match.groups()
            
            try:
                # Parse date
                if '/' in date_str:
                    parts = date_str.split('/')
                    if len(parts[2]) == 2:
                        year = 2000 + int(parts[2])
                    else:
                        year = int(parts[2])
                    
                    date = datetime(year, int(parts[1]), int(parts[0]))
                else:
                    return None
                
                return {
                    'date': date,
                    'time': time_str.strip(),
                    'sender': sender.strip(),
                    'message': message.strip()
                }
            except:
                return None
        return None
    
    def analyze_chat_file(self, file_path: str) -> Dict:

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return {}
        
        messages = []
        for line in lines:
            parsed = self.parse_whatsapp_message(line)
            if parsed:
                messages.append(parsed)
        
        if not messages:
            return {
                'total_messages': 0,
                'unique_senders': 0,
                'activity_analysis': {},
                'engagement_score': 0.0
            }
        
        # Basic statistics
        total_messages = len(messages)
        unique_senders = len(set(msg['sender'] for msg in messages))
        
        # Content analysis
        event_messages = self._count_keyword_messages(messages, self.event_keywords)
        help_messages = self._count_keyword_messages(messages, self.help_keywords)
        collab_messages = self._count_keyword_messages(messages, self.collaboration_keywords)
        engagement_messages = self._count_keyword_messages(messages, self.engagement_keywords)
        
        # Time-based analysis
        activity_by_month = self._analyze_monthly_activity(messages)
        activity_by_hour = self._analyze_hourly_activity(messages)
        
        # Sender analysis
        sender_stats = self._analyze_sender_activity(messages)
        
        # Calculate engagement score
        engagement_score = self._calculate_engagement_score(
            total_messages, unique_senders, event_messages, 
            help_messages, engagement_messages, len(lines)
        )
        
        # Response rate analysis
        response_patterns = self._analyze_response_patterns(messages)
        
        return {
            'total_messages': total_messages,
            'total_lines': len(lines),
            'unique_senders': unique_senders,
            'avg_messages_per_sender': total_messages / unique_senders if unique_senders > 0 else 0,
            'content_analysis': {
                'event_related': event_messages,
                'help_requests': help_messages,
                'collaboration': collab_messages,
                'positive_engagement': engagement_messages
            },
            'activity_analysis': {
                'monthly': activity_by_month,
                'hourly': activity_by_hour
            },
            'sender_stats': sender_stats,
            'response_patterns': response_patterns,
            'engagement_score': engagement_score,
            'date_range': {
                'start': min(msg['date'] for msg in messages).isoformat(),
                'end': max(msg['date'] for msg in messages).isoformat()
            }
        }
    
    def _count_keyword_messages(self, messages: List[Dict], keywords: List[str]) -> int:
        
        count = 0
        for msg in messages:
            message_text = msg['message'].lower()
            if any(keyword in message_text for keyword in keywords):
                count += 1
        return count
    
    def _analyze_monthly_activity(self, messages: List[Dict]) -> Dict:
        
        monthly_counts = defaultdict(int)
        for msg in messages:
            month_key = msg['date'].strftime('%Y-%m')
            monthly_counts[month_key] += 1
        
        return dict(monthly_counts)
    
    def _analyze_hourly_activity(self, messages: List[Dict]) -> Dict:
        
        hourly_counts = defaultdict(int)
        for msg in messages:
            hour = msg['date'].hour
            hourly_counts[hour] += 1
        
        return dict(hourly_counts)
    
    def _analyze_sender_activity(self, messages: List[Dict]) -> Dict:
        
        sender_counts = Counter(msg['sender'] for msg in messages)
        
        # Calculate statistics
        message_counts = list(sender_counts.values())
        
        return {
            'most_active': dict(sender_counts.most_common(5)),
            'message_distribution': {
                'avg': np.mean(message_counts) if message_counts else 0,
                'median': np.median(message_counts) if message_counts else 0,
                'std': np.std(message_counts) if message_counts else 0
            }
        }
    
    def _analyze_response_patterns(self, messages: List[Dict]) -> Dict:
        
        response_times = []
        question_messages = []
        
        for i, msg in enumerate(messages):
            if '?' in msg['message'] or any(word in msg['message'].lower() for word in ['help', 'doubt', 'how']):
                question_messages.append((i, msg))
        
        quick_responses = 0
        total_questions = len(question_messages)
        
        for q_idx, q_msg in question_messages:
            # Check for responses within next 5 messages
            for j in range(q_idx + 1, min(q_idx + 6, len(messages))):
                if messages[j]['sender'] != q_msg['sender']:
                    time_diff = messages[j]['date'] - q_msg['date']
                    if time_diff < timedelta(hours=2):
                        quick_responses += 1
                        response_times.append(time_diff.total_seconds() / 60)  # in minutes
                    break
        
        response_rate = (quick_responses / total_questions * 100) if total_questions > 0 else 0
        
        return {
            'total_questions': total_questions,
            'quick_responses': quick_responses,
            'response_rate_percentage': response_rate,
            'avg_response_time_minutes': np.mean(response_times) if response_times else 0
        }
    
    def _calculate_engagement_score(self, total_messages: int, unique_senders: int, 
                                   event_messages: int, help_messages: int, 
                                   engagement_messages: int, total_lines: int) -> float:
        
        
        # Message density score (messages per total lines)
        density_score = min((total_messages / total_lines) * 10, 3.0) if total_lines > 0 else 0
        
        # Participation score (based on unique senders)
        participation_score = min(unique_senders / 20.0, 2.0)  # Max 2 points for 20+ unique senders
        
        # Content quality score
        content_score = min((event_messages + help_messages + engagement_messages) / total_messages * 5, 3.0) if total_messages > 0 else 0
        
        # Activity volume score
        volume_score = min(total_messages / 100.0, 2.0)  # Max 2 points for 100+ messages
        
        total_score = density_score + participation_score + content_score + volume_score
        
        return min(total_score, 10.0)
    
    def analyze_all_chats(self) -> Dict:
        
        results = {}
        
        for filename, club_info in self.club_mapping.items():
            file_path = os.path.join(self.chat_dir, filename)
            
            if os.path.exists(file_path):
                print(f"Analyzing chat for {club_info['name']}...")
                analysis = self.analyze_chat_file(file_path)
                analysis['club_id'] = club_info['id']
                analysis['club_name'] = club_info['name']
                results[f"club_{club_info['id']}"] = analysis
            else:
                print(f"Chat file not found: {filename}")
        
        return results
    
    def save_analysis_results(self, results: Dict, output_file: str = 'whatsapp_analysis.json'):
        
        output_path = os.path.join(self.data_dir, output_file)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"WhatsApp analysis saved to {output_path}")
        return output_path

    def get_comparative_metrics(self, results: Dict) -> Dict:
        
        if not results:
            return {}
        
        metrics = {
            'total_messages': [],
            'unique_senders': [],
            'engagement_scores': [],
            'event_related': [],
            'response_rates': []
        }
        
        for club_data in results.values():
            if isinstance(club_data, dict) and 'total_messages' in club_data:
                metrics['total_messages'].append(club_data.get('total_messages', 0))
                metrics['unique_senders'].append(club_data.get('unique_senders', 0))
                metrics['engagement_scores'].append(club_data.get('engagement_score', 0))
                
                content_analysis = club_data.get('content_analysis', {})
                metrics['event_related'].append(content_analysis.get('event_related', 0))
                
                response_patterns = club_data.get('response_patterns', {})
                metrics['response_rates'].append(response_patterns.get('response_rate_percentage', 0))
        
        comparative = {}
        for metric, values in metrics.items():
            if values:
                comparative[metric] = {
                    'average': np.mean(values),
                    'median': np.median(values),
                    'std': np.std(values),
                    'min': min(values),
                    'max': max(values)
                }
        
        return comparative

def main():
    
    analyzer = WhatsAppChatAnalyzer()
    
    print("Starting WhatsApp Chat Analysis...")
    results = analyzer.analyze_all_chats()
    
    # Save results
    analyzer.save_analysis_results(results)
    
    # Generate comparative metrics
    comparative = analyzer.get_comparative_metrics(results)
    
    print("\n" + "="*50)
    print("WHATSAPP CHAT ANALYSIS SUMMARY")
    print("="*50)
    
    for club_key, data in results.items():
        if isinstance(data, dict) and 'club_name' in data:
            print(f"\n{data['club_name']}:")
            print(f"  Total Messages: {data.get('total_messages', 0)}")
            print(f"  Unique Senders: {data.get('unique_senders', 0)}")
            print(f"  Engagement Score: {data.get('engagement_score', 0):.2f}/10")
            
            content_analysis = data.get('content_analysis', {})
            print(f"  Event-related Messages: {content_analysis.get('event_related', 0)}")
            
            response_patterns = data.get('response_patterns', {})
            print(f"  Response Rate: {response_patterns.get('response_rate_percentage', 0):.1f}%")
    
    print(f"\nComparative Metrics:")
    print(f"  Average Messages per Club: {comparative.get('total_messages', {}).get('average', 0):.0f}")
    print(f"  Average Engagement Score: {comparative.get('engagement_scores', {}).get('average', 0):.2f}/10")
    
    return results

if __name__ == "__main__":
    main()
