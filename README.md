# SNUCC Club Award System

A comprehensive system for evaluating and ranking college clubs with a FastAPI backend and Streamlit frontend.

## Project Structure

```
SNUCC_club/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main API application
│   ├── requirements.txt    # Backend dependencies
│   ├── models/             # Data models
│   ├── services/           # Business logic services
│   ├── data/               # JSON data files
│   └── Scrapper/           # Data scraping utilities
├── frontend/               # Streamlit frontend
│   ├── app.py              # Main Streamlit application
│   ├── requirements.txt    # Frontend dependencies
│   └── README.md           # Frontend documentation
├── start_app.bat           # Windows batch script to start both services
└── start_app.ps1           # PowerShell script to start both services
```

## Features

### Backend (FastAPI)
- **RESTful API** with comprehensive endpoints
- **Club Management**: CRUD operations for clubs
- **Ranking System**: Overall and group-based rankings
- **Analytics**: Social media, events, and WhatsApp analytics
- **Grouping**: Automatic club categorization
- **Voting System**: Integration with voting data
- **Data Models**: Pydantic models for type safety

### Frontend (Streamlit)
- **Dashboard**: Key metrics and statistics overview
- **Club Rankings**: Interactive rankings with visualizations
- **Club Groups**: Browse clubs by categories
- **Club Details**: Comprehensive club information
- **Analytics Dashboard**: Visual analytics for individual clubs
- **Voting Results**: Summary of voting data
- **Responsive Design**: Clean and modern UI

## Quick Start

### Option 1: Use Startup Scripts
1. **Windows Batch File**:
   ```bash
   double-click start_app.bat
   ```

2. **PowerShell Script**:
   ```powershell
   .\start_app.ps1
   ```

### Option 2: Manual Start

1. **Start Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   pip install -r requirements.txt
   streamlit run app.py
   ```

## Access URLs

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Frontend**: http://localhost:8501

## API Endpoints

### Core Endpoints
- `GET /` - Health check
- `GET /clubs` - Get all clubs
- `GET /clubs/{club_id}` - Get specific club details
- `GET /groups` - Get club groups
- `GET /rankings/overall` - Overall rankings
- `GET /rankings/group/{group_name}` - Group rankings

### Analytics Endpoints
- `GET /analytics/social-media/{club_id}` - Social media analytics
- `GET /analytics/events/{club_id}` - Event analytics
- `GET /analytics/whatsapp/{club_id}` - WhatsApp analytics
- `GET /voting/summary` - Voting results summary
- `GET /dashboard/stats` - Dashboard statistics

## Data Sources

The system processes data from multiple sources:
- **Club Information**: Basic club details and metadata
- **Social Media Metrics**: Instagram, LinkedIn engagement data
- **Event Data**: Club events and participation metrics
- **WhatsApp Analytics**: Group activity and engagement
- **Voting Data**: Student voting results
- **Scraped Data**: Additional social media insights

## Key Features

### 1. Multi-dimensional Ranking
- Social media engagement scores
- Event impact assessments
- Community engagement metrics
- Collaboration scores
- Voting results integration

### 2. Interactive Frontend
- Real-time data visualization with Plotly
- Responsive design with custom CSS
- Tabbed interface for organized content
- Error handling and user feedback

### 3. Comprehensive Analytics
- Club performance metrics
- Comparative analysis tools
- Trend visualization
- Export capabilities

### 4. Scalable Architecture
- Modular service architecture
- Pydantic data validation
- RESTful API design
- Caching for performance

## Technical Stack

### Backend
- **FastAPI**: Modern, fast web framework
- **Pydantic**: Data validation and settings management
- **Python 3.9+**: Core language
- **JSON**: Data storage format

### Frontend
- **Streamlit**: Interactive web app framework
- **Plotly**: Interactive charts and visualizations
- **Pandas**: Data manipulation and analysis
- **Requests**: HTTP client for API communication

## Development

### Adding New Features
1. **Backend**: Add new endpoints in `main.py` and services in `services/`
2. **Frontend**: Add new pages or components in `app.py`
3. **Data Models**: Update models in `models/club.py`

### Data Updates
- Update JSON files in `backend/data/` directory
- Restart backend to load new data

### Customization
- Modify CSS in `app.py` for styling changes
- Update API endpoints in frontend for new backend features
- Add new visualization types using Plotly

## Troubleshooting

### Common Issues
1. **Backend not starting**: Check if port 8000 is available
2. **Frontend connection error**: Ensure backend is running first
3. **Data not loading**: Verify JSON files in `backend/data/`
4. **Package conflicts**: Use virtual environment

### Logs and Debugging
- Backend logs: Check terminal running uvicorn
- Frontend logs: Check Streamlit terminal output
- API testing: Use http://localhost:8000/docs

## Future Enhancements

- Database integration (PostgreSQL/MongoDB)
- User authentication and authorization
- Real-time notifications
- Advanced analytics and ML predictions
- Mobile-responsive design improvements
- Export functionality for reports
- Email integration for notifications
