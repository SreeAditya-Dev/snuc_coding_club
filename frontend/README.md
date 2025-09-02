# SNUCC Club Award System - Frontend

A simple Streamlit frontend for the SNUCC Club Award System API.

## Features

- **Dashboard**: Overview of key statistics and metrics
- **Club Rankings**: View overall rankings and group-specific rankings
- **Club Groups**: Browse clubs organized by categories
- **Club Details**: Detailed information about individual clubs
- **Analytics**: Social media, events, and WhatsApp analytics for clubs
- **Voting Results**: Summary of voting data

## Setup and Installation

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Make sure the backend API is running**
   - The backend should be running on `http://localhost:8000`
   - Start the backend by running `uvicorn main:app --reload` in the backend directory

3. **Run the Streamlit app**
   ```bash
   streamlit run app.py
   ```

4. **Access the application**
   - Open your browser and go to `http://localhost:8501`

## Usage

- Use the sidebar navigation to switch between different pages
- The dashboard provides a quick overview of all club statistics
- Rankings page shows both overall and group-specific club rankings
- Club Details page allows you to view comprehensive information about any club
- Analytics page provides detailed metrics for individual clubs

## API Endpoints Used

- `/dashboard/stats` - Dashboard statistics
- `/clubs` - All clubs data
- `/clubs/{club_id}` - Individual club details
- `/groups` - Club groups
- `/rankings/overall` - Overall rankings
- `/rankings/group/{group_name}` - Group-specific rankings
- `/analytics/social-media/{club_id}` - Social media analytics
- `/analytics/events/{club_id}` - Event analytics
- `/analytics/whatsapp/{club_id}` - WhatsApp analytics
- `/voting/summary` - Voting results

## Requirements

- Python 3.7+
- Backend API running on localhost:8000
- Internet connection for Plotly charts
