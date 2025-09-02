import json
import os
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from models.club import Club, ClubGroup
from services.club_service import ClubService

class ClubGroupingService:
    """Service for grouping clubs based on similarity"""
    
    def __init__(self):
        self.club_service = ClubService()
        self.clubs = self.club_service.get_all_clubs()
        
        # Define predefined group mappings for better categorization
        self.group_definitions = {
            "Technical & Innovation": {
                "keywords": ["coding", "programming", "technology", "software", "robotics", "automation", "electronics", "IoT"],
                "categories": ["technical"],
                "description": "Clubs focused on technology, programming, and technical innovation"
            },
            "Performing Arts": {
                "keywords": ["dance", "music", "performance", "singing", "instruments", "choreography"],
                "categories": ["performing_arts"],
                "description": "Clubs dedicated to music, dance, and live performances"
            },
            "Creative & Visual Arts": {
                "keywords": ["photography", "videography", "visual", "creativity", "editing", "storytelling"],
                "categories": ["creative_arts"],
                "description": "Clubs focused on visual arts, photography, and creative expression"
            },
            "Leadership & Communication": {
                "keywords": ["debate", "public speaking", "leadership", "diplomacy", "communication"],
                "categories": ["debate_discussion"],
                "description": "Clubs emphasizing leadership, debate, and communication skills"
            }
        }
    
    def group_clubs(self) -> List[ClubGroup]:
        """Group clubs based on their activities and characteristics"""
        if not self.clubs:
            return []
        
        # Method 1: Use predefined categories and keywords
        predefined_groups = self._create_predefined_groups()
        
        # Method 2: Use machine learning clustering for additional insights
        ml_groups = self._create_ml_groups()
        
        # Combine both methods, prioritizing predefined groups
        final_groups = predefined_groups
        
        # Add any ungrouped clubs to a miscellaneous group
        grouped_club_ids = set()
        for group in final_groups:
            for club in group.clubs:
                grouped_club_ids.add(club.id)
        
        ungrouped_clubs = [club for club in self.clubs if club.id not in grouped_club_ids]
        if ungrouped_clubs:
            misc_group = ClubGroup(
                group_name="Miscellaneous",
                description="Clubs with unique characteristics that don't fit other categories",
                clubs=ungrouped_clubs,
                similarity_score=0.5
            )
            final_groups.append(misc_group)
        
        return final_groups
    
    def _create_predefined_groups(self) -> List[ClubGroup]:
        """Create groups based on predefined categories and keywords"""
        groups = []
        
        for group_name, group_def in self.group_definitions.items():
            group_clubs = []
            
            for club in self.clubs:
                # Check if club matches by category
                if club.category in group_def["categories"]:
                    group_clubs.append(club)
                    continue
                
                # Check if club matches by keywords
                club_keywords_lower = [kw.lower() for kw in club.keywords]
                club_activities_lower = [act.lower() for act in club.activities]
                
                keyword_match = any(
                    any(group_kw.lower() in club_kw for club_kw in club_keywords_lower)
                    for group_kw in group_def["keywords"]
                )
                
                activity_match = any(
                    any(group_kw.lower() in activity for activity in club_activities_lower)
                    for group_kw in group_def["keywords"]
                )
                
                if keyword_match or activity_match:
                    group_clubs.append(club)
            
            if group_clubs:
                # Calculate similarity score based on keyword overlap
                similarity_score = self._calculate_group_similarity(group_clubs, group_def["keywords"])
                
                group = ClubGroup(
                    group_name=group_name,
                    description=group_def["description"],
                    clubs=group_clubs,
                    similarity_score=similarity_score
                )
                groups.append(group)
        
        return groups
    
    def _create_ml_groups(self) -> List[ClubGroup]:
        """Create groups using machine learning clustering"""
        if len(self.clubs) < 2:
            return []
        
        try:
            # Prepare text data for clustering
            club_texts = []
            for club in self.clubs:
                # Combine all textual features
                text = f"{club.description} {' '.join(club.keywords)} {' '.join(club.activities)}"
                club_texts.append(text)
            
            # Create TF-IDF vectors
            vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(club_texts)
            
            # Perform clustering
            n_clusters = min(3, len(self.clubs))  # Reasonable number of clusters
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(tfidf_matrix)
            
            # Create groups from clusters
            clusters = {}
            for i, label in enumerate(cluster_labels):
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(self.clubs[i])
            
            groups = []
            for cluster_id, cluster_clubs in clusters.items():
                if len(cluster_clubs) > 1:  # Only create groups with multiple clubs
                    # Calculate similarity score
                    similarity_score = self._calculate_cluster_similarity(cluster_clubs, tfidf_matrix, cluster_labels, cluster_id)
                    
                    group = ClubGroup(
                        group_name=f"ML Cluster {cluster_id + 1}",
                        description=f"Automatically grouped clubs with similar characteristics",
                        clubs=cluster_clubs,
                        similarity_score=similarity_score
                    )
                    groups.append(group)
            
            return groups
        
        except Exception as e:
            print(f"Error in ML grouping: {e}")
            return []
    
    def _calculate_group_similarity(self, clubs: List[Club], group_keywords: List[str]) -> float:
        """Calculate similarity score for a predefined group"""
        if not clubs:
            return 0.0
        
        total_score = 0.0
        for club in clubs:
            club_keywords_lower = [kw.lower() for kw in club.keywords]
            club_activities_lower = [act.lower() for act in club.activities]
            
            # Count keyword matches
            keyword_matches = sum(
                1 for group_kw in group_keywords
                if any(group_kw.lower() in club_kw for club_kw in club_keywords_lower) or
                   any(group_kw.lower() in activity for activity in club_activities_lower)
            )
            
            # Calculate score as percentage of matching keywords
            score = keyword_matches / len(group_keywords) if group_keywords else 0
            total_score += score
        
        return min(total_score / len(clubs), 1.0)  # Normalize to 0-1 range
    
    def _calculate_cluster_similarity(self, clubs: List[Club], tfidf_matrix, cluster_labels, cluster_id) -> float:
        """Calculate similarity score for an ML-generated cluster"""
        try:
            # Get indices of clubs in this cluster
            cluster_indices = [i for i, label in enumerate(cluster_labels) if label == cluster_id]
            
            if len(cluster_indices) < 2:
                return 0.5
            
            # Calculate average pairwise similarity within cluster
            similarities = []
            for i in range(len(cluster_indices)):
                for j in range(i + 1, len(cluster_indices)):
                    sim = cosine_similarity(
                        tfidf_matrix[cluster_indices[i]], 
                        tfidf_matrix[cluster_indices[j]]
                    )[0][0]
                    similarities.append(sim)
            
            return np.mean(similarities) if similarities else 0.5
        
        except Exception as e:
            print(f"Error calculating cluster similarity: {e}")
            return 0.5
    
    def get_group_by_name(self, group_name: str) -> ClubGroup:
        """Get a specific group by name"""
        groups = self.group_clubs()
        for group in groups:
            if group.group_name == group_name:
                return group
        return None
    
    def get_similar_clubs(self, club_id: int, threshold: float = 0.3) -> List[Club]:
        """Find clubs similar to a given club"""
        target_club = self.club_service.get_club_by_id(club_id)
        if not target_club:
            return []
        
        similar_clubs = []
        
        for club in self.clubs:
            if club.id == club_id:
                continue
            
            # Calculate similarity based on keywords and activities
            similarity = self._calculate_club_similarity(target_club, club)
            if similarity >= threshold:
                similar_clubs.append(club)
        
        return similar_clubs
    
    def _calculate_club_similarity(self, club1: Club, club2: Club) -> float:
        """Calculate similarity between two clubs"""
        # Compare keywords
        keywords1 = set(kw.lower() for kw in club1.keywords)
        keywords2 = set(kw.lower() for kw in club2.keywords)
        keyword_similarity = len(keywords1.intersection(keywords2)) / len(keywords1.union(keywords2)) if keywords1.union(keywords2) else 0
        
        # Compare activities
        activities1 = set(act.lower() for act in club1.activities)
        activities2 = set(act.lower() for act in club2.activities)
        activity_similarity = len(activities1.intersection(activities2)) / len(activities1.union(activities2)) if activities1.union(activities2) else 0
        
        # Compare categories
        category_similarity = 1.0 if club1.category == club2.category else 0.0
        
        # Weighted average
        return (keyword_similarity * 0.4 + activity_similarity * 0.4 + category_similarity * 0.2)
