import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="SNUCC Club Award System",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    .club-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #e1e5e9;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
@st.cache_data(ttl=300)
def fetch_data(endpoint):
    """Fetch data from API endpoint with caching"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching data from {endpoint}: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the API. Please make sure the backend server is running on http://localhost:8000")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def display_club_card(club):
    """Display a club information card"""
    with st.container():
        st.markdown(f"""
        <div class="club-card">
            <h3>{club['name']}</h3>
            <p><strong>Category:</strong> {club['category']}</p>
            <p><strong>Founded:</strong> {club['founded_year']}</p>
            <p><strong>Members:</strong> {club['member_count']}</p>
            <p><strong>Description:</strong> {club['description']}</p>
            <p><strong>Activities:</strong> {', '.join(club['activities'])}</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🏆 SNUCC Club Award System</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["Dashboard", "Club Rankings", "Club Groups", "Club Details", "Analytics", "Voting Results"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Club Rankings":
        show_rankings()
    elif page == "Club Groups":
        show_groups()
    elif page == "Club Details":
        show_club_details()
    elif page == "Analytics":
        show_analytics()
    elif page == "Voting Results":
        show_voting_results()

def show_dashboard():
    st.header("📊 Dashboard")
    
    # Fetch dashboard stats
    stats = fetch_data("/dashboard/stats")
    
    if stats:
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Clubs", stats.get('total_clubs', 0))
        
        with col2:
            st.metric("Total Groups", stats.get('total_groups', 0))
        
        with col3:
            st.metric("Total Events", stats.get('total_events', 0))
        
        with col4:
            st.metric("Total Votes", stats.get('total_votes', 0))
        
        # Most active club
        if 'most_active_club' in stats and stats['most_active_club']:
            st.subheader("🌟 Most Active Club")
            st.success(f"**{stats['most_active_club']}**")
        
        # Recent events
        if 'recent_events' in stats and stats['recent_events']:
            st.subheader("📅 Recent Events")
            for event in stats['recent_events'][:5]:  # Show top 5
                st.write(f"• **{event.get('name', 'N/A')}** - {event.get('date', 'N/A')}")

def show_rankings():
    st.header("🏆 Club Rankings")
    
    # Toggle between overall and group rankings
    ranking_type = st.radio("Select ranking type:", ["Overall Rankings", "Group Rankings"])
    
    if ranking_type == "Overall Rankings":
        rankings = fetch_data("/rankings/overall")
        
        if rankings:
            st.subheader("Overall Club Rankings")
            
            # Create a dataframe for display
            ranking_data = []
            for ranking in rankings:
                ranking_data.append({
                    'Rank': ranking['rank'],
                    'Club Name': ranking['club']['name'],
                    'Category': ranking['club']['category'],
                    'Overall Score': round(ranking['metrics']['overall_score'], 2),
                    'Social Media Score': round(ranking['metrics']['social_media_score'], 2),
                    'Event Impact Score': round(ranking['metrics']['event_impact_score'], 2),
                    'Community Engagement': round(ranking['metrics']['community_engagement_score'], 2),
                    'Voting Score': round(ranking['metrics']['voting_score'], 2)
                })
            
            df = pd.DataFrame(ranking_data)
            
            # Display as table
            st.dataframe(df, use_container_width=True)
            
            # Create visualization
            if len(df) > 0:
                fig = px.bar(
                    df.head(10), 
                    x='Club Name', 
                    y='Overall Score',
                    title="Top 10 Clubs by Overall Score",
                    color='Overall Score',
                    color_continuous_scale='viridis'
                )
                fig.update_xaxis(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
    
    else:  # Group Rankings
        # Get available groups first
        groups = fetch_data("/groups")
        if groups:
            group_names = [group['group_name'] for group in groups]
            selected_group = st.selectbox("Select a group:", group_names)
            
            if selected_group:
                group_rankings = fetch_data(f"/rankings/group/{selected_group}")
                
                if group_rankings:
                    st.subheader(f"Rankings for {selected_group}")
                    
                    ranking_data = []
                    for ranking in group_rankings:
                        ranking_data.append({
                            'Rank': ranking['rank'],
                            'Club Name': ranking['club']['name'],
                            'Overall Score': round(ranking['metrics']['overall_score'], 2),
                            'Members': ranking['club']['member_count']
                        })
                    
                    df = pd.DataFrame(ranking_data)
                    st.dataframe(df, use_container_width=True)

def show_groups():
    st.header("👥 Club Groups")
    
    groups = fetch_data("/groups")
    
    if groups:
        for group in groups:
            with st.expander(f"{group['group_name']} ({len(group['clubs'])} clubs)"):
                st.write(f"**Description:** {group['description']}")
                st.write(f"**Similarity Score:** {group['similarity_score']:.2f}")
                
                st.subheader("Clubs in this group:")
                for club in group['clubs']:
                    display_club_card(club)

def show_club_details():
    st.header("🏢 Club Details")
    
    # Get all clubs for selection
    clubs = fetch_data("/clubs")
    
    if clubs:
        club_names = {club['name']: club['id'] for club in clubs}
        selected_club_name = st.selectbox("Select a club:", list(club_names.keys()))
        
        if selected_club_name:
            club_id = club_names[selected_club_name]
            club_details = fetch_data(f"/clubs/{club_id}")
            
            if club_details:
                # Display club information
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Basic Information")
                    st.write(f"**Name:** {club_details['name']}")
                    st.write(f"**Category:** {club_details['category']}")
                    st.write(f"**Founded:** {club_details['founded_year']}")
                    st.write(f"**Members:** {club_details['member_count']}")
                    st.write(f"**Description:** {club_details['description']}")
                
                with col2:
                    st.subheader("Activities & Keywords")
                    st.write("**Activities:**")
                    for activity in club_details['activities']:
                        st.write(f"• {activity}")
                    
                    st.write("**Keywords:**")
                    keywords_text = ", ".join(club_details['keywords'])
                    st.write(keywords_text)
                
                # Social Media Information
                if club_details['social_media']:
                    st.subheader("Social Media")
                    for platform, handle in club_details['social_media'].items():
                        st.write(f"**{platform.title()}:** {handle}")

def show_analytics():
    st.header("📈 Analytics")
    
    # Get all clubs for selection
    clubs = fetch_data("/clubs")
    
    if clubs:
        club_names = {club['name']: club['id'] for club in clubs}
        selected_club_name = st.selectbox("Select a club for analytics:", list(club_names.keys()))
        
        if selected_club_name:
            club_id = club_names[selected_club_name]
            
            # Analytics tabs
            tab1, tab2, tab3 = st.tabs(["Social Media", "Events", "WhatsApp Activity"])
            
            with tab1:
                social_analytics = fetch_data(f"/analytics/social-media/{club_id}")
                if social_analytics:
                    st.json(social_analytics)
                else:
                    st.info("No social media analytics available for this club.")
            
            with tab2:
                event_analytics = fetch_data(f"/analytics/events/{club_id}")
                if event_analytics:
                    st.json(event_analytics)
                else:
                    st.info("No event analytics available for this club.")
            
            with tab3:
                whatsapp_analytics = fetch_data(f"/analytics/whatsapp/{club_id}")
                if whatsapp_analytics:
                    st.json(whatsapp_analytics)
                else:
                    st.info("No WhatsApp analytics available for this club.")

def show_voting_results():
    st.header("🗳️ Voting Results")
    
    voting_summary = fetch_data("/voting/summary")
    
    if voting_summary:
        st.subheader("Voting Summary")
        st.json(voting_summary)
    else:
        st.info("No voting data available.")

if __name__ == "__main__":
    main()
