from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
import json
import os
from datetime import datetime

from models.club import Club, ClubGroup, ClubRanking
from services.club_service import ClubService
from services.grouping_service import ClubGroupingService
from services.evaluation_service import ClubEvaluationService

# Initialize FastAPI app
app = FastAPI(
    title="Club Award System",
    description="API for evaluating and ranking college clubs",
)

# Initialize services
club_service = ClubService()
grouping_service = ClubGroupingService()
evaluation_service = ClubEvaluationService()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Club Award System API is running!"}

@app.get("/clubs", response_model=List[Club])
async def get_all_clubs():
    """Get all clubs with their basic information"""
    try:
        clubs = club_service.get_all_clubs()
        return clubs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching clubs: {str(e)}")

@app.get("/clubs/{club_id}", response_model=Club)
async def get_club_by_id(club_id: int):
    """Get detailed information about a specific club"""
    try:
        club = club_service.get_club_by_id(club_id)
        if not club:
            raise HTTPException(status_code=404, detail="Club not found")
        return club
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching club: {str(e)}")

@app.get("/groups", response_model=List[ClubGroup])
async def get_club_groups():
    """Get clubs grouped by their activities and purpose"""
    try:
        groups = grouping_service.group_clubs()
        return groups
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error grouping clubs: {str(e)}")

@app.get("/rankings/overall", response_model=List[ClubRanking])
async def get_overall_rankings():
    """Get overall club rankings based on evaluation metrics"""
    try:
        rankings = evaluation_service.get_overall_rankings()
        return rankings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating rankings: {str(e)}")

@app.get("/rankings/group/{group_name}", response_model=List[ClubRanking])
async def get_group_rankings(group_name: str):
    """Get rankings within a specific group"""
    try:
        rankings = evaluation_service.get_group_rankings(group_name)
        return rankings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating group rankings: {str(e)}")

@app.get("/analytics/social-media/{club_id}")
async def get_social_media_analytics(club_id: int):
    """Get social media analytics for a specific club"""
    try:
        analytics = evaluation_service.get_social_media_analytics(club_id)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching social media analytics: {str(e)}")

@app.get("/analytics/events/{club_id}")
async def get_event_analytics(club_id: int):
    """Get event analytics for a specific club"""
    try:
        analytics = evaluation_service.get_event_analytics(club_id)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching event analytics: {str(e)}")

@app.get("/analytics/whatsapp/{club_id}")
async def get_whatsapp_analytics(club_id: int):
    """Get WhatsApp group activity analytics for a specific club"""
    try:
        analytics = evaluation_service.get_whatsapp_analytics(club_id)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching WhatsApp analytics: {str(e)}")

@app.get("/voting/summary")
async def get_voting_summary():
    """Get voting results summary"""
    try:
        summary = evaluation_service.get_voting_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching voting summary: {str(e)}")

@app.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get comprehensive statistics for the dashboard"""
    try:
        stats = {
            "total_clubs": len(club_service.get_all_clubs()),
            "total_groups": len(grouping_service.group_clubs()),
            "total_events": evaluation_service.get_total_events_count(),
            "total_votes": evaluation_service.get_total_votes_count(),
            "most_active_club": evaluation_service.get_most_active_club(),
            "recent_events": evaluation_service.get_recent_events()
        }
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard stats: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
