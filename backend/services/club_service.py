
import json
import os
from typing import List, Optional
from models.club import Club

class ClubService:
    """Service class for managing club operations"""
    
    def __init__(self):
        """Initialize the club service and load data"""
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.clubs = self._load_clubs()
    
    def _load_clubs(self) -> List[Club]:
        """Load clubs from JSON data file"""
        try:
            clubs_file = os.path.join(self.data_dir, 'clubs.json')
            with open(clubs_file, 'r', encoding='utf-8') as f:
                clubs_data = json.load(f)
            
            clubs = []
            for club_data in clubs_data['clubs']:
                club = Club(**club_data)
                clubs.append(club)
            
            return clubs
        except Exception as e:
            print(f"Error loading clubs: {e}")
            return []
    
    def get_all_clubs(self) -> List[Club]:
        """Get all clubs"""
        return self.clubs
    
    def get_club_by_id(self, club_id: int) -> Optional[Club]:
        """Get a specific club by ID"""
        for club in self.clubs:
            if club.id == club_id:
                return club
        return None
    
    def get_clubs_by_category(self, category: str) -> List[Club]:
        """Get clubs filtered by category"""
        return [club for club in self.clubs if club.category == category]
    
    def get_clubs_by_activity(self, activity: str) -> List[Club]:
        """Get clubs that have a specific activity"""
        return [club for club in self.clubs if activity in club.activities]
    
    def search_clubs_by_keyword(self, keyword: str) -> List[Club]:
        """Search clubs by keyword in name, description, or keywords"""
        keyword_lower = keyword.lower()
        matching_clubs = []
        
        for club in self.clubs:
            # Check name
            if keyword_lower in club.name.lower():
                matching_clubs.append(club)
                continue
            
            # Check description
            if keyword_lower in club.description.lower():
                matching_clubs.append(club)
                continue
            
            # Check keywords
            if any(keyword_lower in kw.lower() for kw in club.keywords):
                matching_clubs.append(club)
                continue
        
        return matching_clubs
    
    def get_club_statistics(self) -> dict:
        """Get basic statistics about clubs"""
        if not self.clubs:
            return {}
        
        categories = {}
        total_members = 0
        oldest_year = float('inf')
        newest_year = 0
        
        for club in self.clubs:
            # Count by category
            if club.category in categories:
                categories[club.category] += 1
            else:
                categories[club.category] = 1
            
            # Sum members
            total_members += club.member_count
            
            # Track founding years
            if club.founded_year < oldest_year:
                oldest_year = club.founded_year
            if club.founded_year > newest_year:
                newest_year = club.founded_year
        
        return {
            "total_clubs": len(self.clubs),
            "categories": categories,
            "total_members": total_members,
            "avg_members_per_club": total_members / len(self.clubs),
            "oldest_club_year": oldest_year,
            "newest_club_year": newest_year
        }
