import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import zipfile
import io
from datetime import datetime
from collections import Counter

st.set_page_config(
    page_title="Spotify Data Explorer",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

def process_spotify_zip(uploaded_file):
    """Process uploaded Spotify ZIP file and return DataFrame"""
    records = []
    
    with zipfile.ZipFile(uploaded_file, 'r') as zip_file:
        # Find all Streaming_History_Audio_*.json files
        streaming_files = [f for f in zip_file.namelist() if 'Streaming_History_Audio_' in f and f.endswith('.json')]
        
        if not streaming_files:
            st.error("No Streaming_History_Audio_*.json files found in the ZIP file.")
            return None
        
        for file_name in streaming_files:
            with zip_file.open(file_name) as json_file:
                data = json.load(json_file)
                for entry in data:
                    timestamp = entry.get('ts')
                    if not timestamp:
                        continue  # sskips if there is no timestamp (error on a few lines)
                    ms_played = entry.get('ms_played')
                    
                    # Filter out tracks longer than 1 hour (3,600,000 ms)
                    if ms_played and ms_played > 3600000:
                        continue
                    
                    record = {
                        'timestamp': timestamp,
                        'platform': entry.get('platform'),
                        'ms_played': ms_played,
                        'track_name': entry.get('master_metadata_track_name'),
                        'artist': entry.get('master_metadata_album_artist_name'),
                        'album': entry.get('master_metadata_album_album_name'),
                        'spotify_uri': entry.get('spotify_track_uri'),
                        'skipped': entry.get('skipped'),
                        'shuffle': entry.get('shuffle'),
                        'offline': entry.get('offline'),
                        'incognito_mode': entry.get('incognito_mode'),
                        'source_file': file_name
                    }
                    records.append(record)
    
    if not records:
        st.error("No valid streaming records found in the files.")
        return None
    
    df = pd.DataFrame(records)
    df['timestamp'] = pd.to_datetime(df['timestamp'].str.replace('Z', '+00:00'))
    df['hours_played'] = df['ms_played'] / (1000 * 60 * 60)
    df['date'] = df['timestamp'].dt.date
    df['month'] = df['timestamp'].dt.to_period('M')
    
    return df

def calculate_metrics(df):
    """Calculate key metrics from the DataFrame"""
    total_hours = df['hours_played'].sum()
    total_tracks = len(df)
    unique_artists = df['artist'].nunique()
    unique_tracks = df['track_name'].nunique()
    
    top_artists = df.groupby('artist')['hours_played'].sum().nlargest(10)
    top_tracks = df.groupby(['track_name', 'artist'])['hours_played'].sum().nlargest(10)
    monthly_listening = df.groupby('month')['hours_played'].sum()
    
    return {
        'total_hours': total_hours,
        'total_tracks': total_tracks,
        'unique_artists': unique_artists,
        'unique_tracks': unique_tracks,
        'top_artists': top_artists,
        'top_tracks': top_tracks,
        'monthly_listening': monthly_listening
    }

def main():
    st.title("Spotify Data Explorer")
    st.markdown("Upload your Spotify data export ZIP file to explore your listening history!")
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Upload Data")
        uploaded_file = st.file_uploader(
            "Choose your Spotify data ZIP file",
            type=['zip'],
            help="Download your data from Spotify's privacy settings"
        )
        
        if uploaded_file is not None:
            with st.spinner("Processing your Spotify data..."):
                df = process_spotify_zip(uploaded_file)
            
            if df is not None:
                metrics = calculate_metrics(df)
                
                st.success(f"✅ Processed {len(df):,} streams!")
                
                st.header("📊 Quick Stats")
                st.metric("Total Listening Time", f"{metrics['total_hours']:.1f} hours")
                st.metric("Total Streams", f"{metrics['total_tracks']:,}")
                st.metric("Unique Artists", f"{metrics['unique_artists']:,}")
                st.metric("Unique Tracks", f"{metrics['unique_tracks']:,}")
                
                # Date range
                date_range = st.date_input(
                    "Filter by date range",
                    value=(df['date'].min(), df['date'].max()),
                    min_value=df['date'].min(),
                    max_value=df['date'].max()
                )
                
                # Filter dataframe by date range
                if len(date_range) == 2:
                    mask = (df['date'] >= date_range[0]) & (df['date'] <= date_range[1])
                    df_filtered = df[mask]
                    metrics_filtered = calculate_metrics(df_filtered)
                else:
                    df_filtered = df
                    metrics_filtered = metrics
                
                # Main dashboard
                if not df_filtered.empty:
                    show_dashboard(df_filtered, metrics_filtered)
                else:
                    st.warning("No data in selected date range.")

def show_dashboard(df, metrics):
    """Display the main dashboard with charts and tables"""
    
    # Top Artists Chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎤 Top 10 Artists")
        fig_artists = px.bar(
            x=metrics['top_artists'].values,
            y=metrics['top_artists'].index,
            orientation='h',
            labels={'x': 'Hours Listened', 'y': 'Artist'},
            color=metrics['top_artists'].values,
            color_continuous_scale='viridis'
        )
        fig_artists.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_artists, use_container_width=True)
    
    with col2:
        st.subheader("🎵 Top 10 Tracks")
        top_tracks_formatted = [f"{track} - {artist}" for (track, artist), _ in metrics['top_tracks'].items()]
        fig_tracks = px.bar(
            x=metrics['top_tracks'].values,
            y=top_tracks_formatted,
            orientation='h',
            labels={'x': 'Hours Listened', 'y': 'Track'},
            color=metrics['top_tracks'].values,
            color_continuous_scale='plasma'
        )
        fig_tracks.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_tracks, use_container_width=True)
    
    # Listening Activity Over Time
    st.subheader("📈 Listening Activity Over Time")
    monthly_data = metrics['monthly_listening'].reset_index()
    monthly_data['month_str'] = monthly_data['month'].astype(str)
    
    fig_timeline = px.line(
        monthly_data,
        x='month_str',
        y='hours_played',
        title='Monthly Listening Hours',
        labels={'month_str': 'Month', 'hours_played': 'Hours Listened'}
    )
    fig_timeline.update_layout(height=400)
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Additional insights
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("📱 Platform Usage")
        platform_data = df.groupby('platform')['hours_played'].sum().sort_values(ascending=False)
        if len(platform_data) > 1:
            fig_platform = px.pie(
                values=platform_data.values,
                names=platform_data.index,
                title="Listening by Platform"
            )
            st.plotly_chart(fig_platform, use_container_width=True)
        else:
            st.info(f"All listening on: {platform_data.index[0]}")
    
    with col4:
        st.subheader("⏭️ Skip Rate Analysis")
        # Consider tracks with less than 30 seconds as skipped
        df['likely_skipped'] = df['ms_played'] < 30000
        skip_rate = (df['likely_skipped'].sum() / len(df)) * 100
        
        st.metric("Estimated Skip Rate", f"{skip_rate:.1f}%")
        
        # Average listening time
        avg_listen_time = df['ms_played'].mean() / 1000
        st.metric("Average Listen Time", f"{avg_listen_time:.0f} seconds")
    
    # Detailed Tables
    with st.expander("📋 Detailed Data Tables"):
        tab1, tab2, tab3 = st.tabs(["Top Artists", "Top Tracks", "Recent Activity"])
        
        with tab1:
            artists_df = metrics['top_artists'].reset_index()
            artists_df.columns = ['Artist', 'Hours Listened']
            artists_df['Hours Listened'] = artists_df['Hours Listened'].round(2)
            st.dataframe(artists_df, use_container_width=True)
        
        with tab2:
            tracks_df = pd.DataFrame([
                {'Track': track, 'Artist': artist, 'Hours Listened': round(hours, 2)}
                for (track, artist), hours in metrics['top_tracks'].items()
            ])
            st.dataframe(tracks_df, use_container_width=True)
        
        with tab3:
            recent_df = df.nlargest(100, 'timestamp')[['timestamp', 'track_name', 'artist', 'ms_played']].copy()
            recent_df['minutes_played'] = (recent_df['ms_played'] / (1000 * 60)).round(2)
            recent_df = recent_df.drop('ms_played', axis=1)
            st.dataframe(recent_df, use_container_width=True)

if __name__ == "__main__":
    main()