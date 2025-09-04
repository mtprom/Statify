# Spotify Data Explorer 🎵

An interactive Streamlit web app for analyzing your Spotify listening history from data exports.

## Features

- **File Upload**: Upload your Spotify data export ZIP file
- **Interactive Dashboard**: Explore your listening patterns with charts and metrics
- **Key Metrics**: Total listening time, top artists/tracks, and more
- **Visualizations**: Bar charts, time-series, and pie charts using Plotly
- **Date Filtering**: Analyze specific time periods
- **Detailed Tables**: Drill down into your listening data

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the app:
```bash
streamlit run streamlit_app.py
```

3. Upload your Spotify data export ZIP file and explore your listening history!

## Getting Your Spotify Data

1. Go to [Spotify Privacy Settings](https://www.spotify.com/account/privacy/)
2. Request your "Extended streaming history" 
3. Wait for the email with your data (can take up to 30 days)
4. Download the ZIP file and upload it to this app

## What You'll See

- **Top 10 Artists & Tracks** with listening hours
- **Monthly listening trends** over time
- **Platform usage** breakdown
- **Skip rate analysis** and listening patterns
- **Date range filtering** for focused analysis
- **Detailed data tables** for deeper exploration