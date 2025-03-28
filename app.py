import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
from PIL import Image
import requests
from textblob import TextBlob
import warnings
import io
import base64
from datetime import datetime, timedelta
import random
import time

warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(
    page_title="UnicornVision - Investment Analytics Platform",
    page_icon="🦄",
    layout="wide"
)

# Custom CSS for enhanced visuals
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(45deg, #FF4B4B, #4B4BFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .sub-header {
        font-size: 1.5rem;
        color: #4B4BFF;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .highlight {
        background-color: #F0F2F6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #FF4B4B;
    }
    
    .feature-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 10px;
    }
    
    .feature-title {
        font-weight: bold;
        margin-bottom: 10px;
        color: #4B4BFF;
    }
    
    .metric-container {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 20px;
        text-align: center;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF4B4B;
    }
    
    .metric-label {
        font-size: 1rem;
        color: #4B4BFF;
    }
    
    .footer {
        text-align: center;
        margin-top: 50px;
        padding: 20px;
        background-color: #F0F2F6;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Load data files locally
@st.cache_data
def load_data():
    # Load with proper column mapping
    main_data = pd.read_csv("main_data.csv", encoding='utf-8')
    market_data = pd.read_csv("market_main.csv", encoding='utf-8')
    
    # For main_data, create mappings based on actual columns
    main_data = main_data.rename(columns={
        "normalized_name": "Startup_Name",
        "category_code": "Industry_Vertical",
        "country_code": "City_Location",
        "relationships": "Investors_Name",
        "funding_rounds": "Investment_Type",
        "funding_total_usd": "Amount_in_USD"
    })
    
    # Clean market_data 
    if "Total Funding Amount Currency (in USD)" in market_data.columns:
        market_data["Total Funding Amount USD"] = pd.to_numeric(
            market_data["Total Funding Amount Currency (in USD)"].astype(str).str.replace("[$,]", "", regex=True),
            errors="coerce"
        )
        market_data["Last Funding Amount USD"] = pd.to_numeric(
            market_data["Last Funding Amount Currency (in USD)"].astype(str).str.replace("[$,]", "", regex=True),
            errors="coerce"
        )
    
    return main_data, market_data

# Load AI model (simulated since we don't have access to Mistral model locally)
def simulate_ai_response(prompt, name, perspective):
    """Simulate AI response since we don't have the Mistral model locally"""
    responses = {
        "Visionary": {
            "insight": "This startup shows strong potential for disruption in its sector with innovative technology.",
            "score": np.random.randint(70, 95)
        },
        "Skeptic": {
            "insight": "The market is saturated and competition is fierce. Cautious approach recommended.",
            "score": np.random.randint(30, 70)
        },
        "Analyst": {
            "insight": "Historical funding patterns suggest moderate growth potential with careful cash management.",
            "score": np.random.randint(50, 85)
        },
        "Scout": {
            "insight": "Compared to similar startups, this one has unique technology but faces scaling challenges.",
            "score": np.random.randint(60, 90)
        },
        "Oracle": {
            "insight": "Overall investment verdict is cautiously optimistic with close monitoring advised.",
            "score": np.random.randint(65, 85)
        }
    }
    
    return f"Insight: {responses[name]['insight']}\nConfidence Score: {responses[name]['score']}"

# Generate a simple logo for local use
def generate_logo():
    # Create a blank image with a gradient background
    img = Image.new('RGB', (600, 400), color=(255, 255, 255))
    pixels = img.load()
    
    # Create a gradient background
    for i in range(img.width):
        for j in range(img.height):
            r = int(255 - i * 0.4)
            g = int(100 + j * 0.3)
            b = int(200 + i * 0.2)
            pixels[i, j] = (r, g, b)
    
    # Save to buffer
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

# Create hero image
def generate_hero_image():
    # Create a more complex image for the hero section
    img = Image.new('RGB', (800, 400), color=(240, 240, 255))
    pixels = img.load()
    
    # Create a pattern
    for i in range(img.width):
        for j in range(img.height):
            if (i + j) % 20 < 10:
                r = int(75 + i * 0.2)
                g = int(100 + j * 0.15)
                b = int(200 - i * 0.1)
                pixels[i, j] = (r, g, b)
    
    # Save to buffer
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

# Initialize session state for portfolio
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = []
    
# Initialize session state for challenges in AI Investment Council
if 'active_challenge' not in st.session_state:
    st.session_state.active_challenge = {
        "agent": None,
        "challenge_text": None,
        "is_submitted": False
    }
    
# Initialize session state for page navigation
if 'page' not in st.session_state:
    st.session_state.page = "Home"
    
# Sidebar navigation
st.sidebar.title("🦄 UnicornVision")

# Use local logo instead of external URL
logo_data = generate_logo()
st.sidebar.image(logo_data, use_container_width=True)

# Navigation
page = st.sidebar.radio(
    "Navigation",
    ["Home", "Market Analysis", "Competitor Analysis", "Sentiment Analysis", 
     "Portfolio Management", "Investment Council"],
    key="navigation",
    index=["Home", "Market Analysis", "Competitor Analysis", "Sentiment Analysis", 
           "Portfolio Management", "Investment Council"].index(st.session_state.page)
)

# Update session state when sidebar navigation changes
st.session_state.page = page

# Load data
main_data, market_data = load_data()

# Home Page
if page == "Home":
    # Modern web-like landing page
    # Remove the old title and replace with a more appealing hero section
    st.markdown(
        """
        <div style="padding: 2rem 0; text-align: center; background: linear-gradient(120deg, #6e48aa, #9d50bb, #6e48aa); border-radius: 15px; margin-bottom: 2rem;">
            <h1 style="font-size: 3.5rem; font-weight: 800; color: white; margin-bottom: 1rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);">UnicornVision</h1>
            <h2 style="font-size: 1.8rem; color: white; font-weight: 300; opacity: 0.9; margin-bottom: 2rem;">AI-Powered Investment Analytics Platform</h2>
            <div style="background: rgba(255,255,255,0.15); width: 80%; margin: 0 auto; height: 5px; border-radius: 10px;"></div>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Interactive value proposition and CTA
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 3rem; padding: 1rem; background: linear-gradient(to right, #f8f9fa, #ffffff, #f8f9fa); border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
            <h2 style="color: #333; margin-bottom: 1.5rem; font-weight: 600;">Discover Your Next Unicorn Investment</h2>
            <p style="font-size: 1.25rem; color: #555; max-width: 800px; margin: 0 auto;">
                UnicornVision combines <span style="color: #6e48aa; font-weight: 600;">AI intelligence</span> with <span style="color: #6e48aa; font-weight: 600;">market data</span> to help you make smarter investment decisions.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Dashboard metrics with modern style
    st.markdown("<h3 style='text-align: center; color: #333; margin-bottom: 2rem;'>Dashboard Insights</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            f"""
            <div style="background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); padding: 1.5rem; text-align: center; height: 200px; display: flex; flex-direction: column; justify-content: center; transition: transform 0.3s;">
                <div style="font-size: 3rem; font-weight: 800; background: linear-gradient(45deg, #6e48aa, #9d50bb); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">{len(main_data.Startup_Name.unique()):,}</div>
                <div style="font-size: 1rem; color: #666; font-weight: 500;">Startups in Database</div>
                <div style="width: 60%; height: 4px; background: linear-gradient(90deg, #6e48aa, #9d50bb); margin: 1rem auto 0;"></div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div style="background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); padding: 1.5rem; text-align: center; height: 200px; display: flex; flex-direction: column; justify-content: center; transition: transform 0.3s;">
                <div style="font-size: 3rem; font-weight: 800; background: linear-gradient(45deg, #6e48aa, #9d50bb); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">${main_data.Amount_in_USD.sum()/1e6:.1f}M</div>
                <div style="font-size: 1rem; color: #666; font-weight: 500;">Total Investments Tracked</div>
                <div style="width: 60%; height: 4px; background: linear-gradient(90deg, #6e48aa, #9d50bb); margin: 1rem auto 0;"></div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"""
            <div style="background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); padding: 1.5rem; text-align: center; height: 200px; display: flex; flex-direction: column; justify-content: center; transition: transform 0.3s;">
                <div style="font-size: 2.5rem; font-weight: 800; background: linear-gradient(45deg, #6e48aa, #9d50bb); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem; overflow: hidden; text-overflow: ellipsis;">{main_data.Industry_Vertical.value_counts().index[0]}</div>
                <div style="font-size: 1rem; color: #666; font-weight: 500;">Top Industry</div>
                <div style="width: 60%; height: 4px; background: linear-gradient(90deg, #6e48aa, #9d50bb); margin: 1rem auto 0;"></div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # Features section with interactive cards
    st.markdown("<h3 style='text-align: center; color: #333; margin: 3rem 0 2rem;'>What We Offer</h3>", unsafe_allow_html=True)
    
    # Create feature cards with click handlers
    features = [
        {
            "icon": "📊", 
            "title": "Market Analysis",
            "description": "Analyze global investment trends, industry verticals, and funding patterns to identify emerging opportunities.",
            "page": "Market Analysis",
            "color": "#6e48aa"
        },
        {
            "icon": "🔍", 
            "title": "Competitor Analysis",
            "description": "Compare startups head-to-head to understand competitive positioning and market potential.",
            "page": "Competitor Analysis",
            "color": "#9d50bb"
        },
        {
            "icon": "💰", 
            "title": "Portfolio Management",
            "description": "Build and track your investment portfolio with ROI projections and performance tracking.",
            "page": "Portfolio Management",
            "color": "#6e48aa"
        },
        {
            "icon": "💬", 
            "title": "Sentiment Analysis",
            "description": "Analyze news sentiment and market perception to understand media coverage impact.",
            "page": "Sentiment Analysis",
            "color": "#9d50bb"
        },
        {
            "icon": "🧠", 
            "title": "AI Investment Council",
            "description": "Get AI-powered investment recommendations from multiple expert perspectives.",
            "page": "Investment Council",
            "color": "#6e48aa"
        }
    ]
    
    # Create a clickable card for each feature
    for i in range(0, len(features), 2):
        col1, col2 = st.columns(2)
        
        # First card in row
        with col1:
            if i < len(features):
                feature = features[i]
                if st.button(f"{feature['icon']} {feature['title']}", key=f"feature_{i}", use_container_width=True):
                    # This will navigate to the page when clicked
                    st.session_state.page_navigation = feature['page']
                    
                st.markdown(
                    f"""
                    <div style="background: white; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); padding: 1.5rem; margin-bottom: 1.5rem; border-left: 5px solid {feature['color']}; height: 170px;">
                        <div style="font-size: 1.4rem; font-weight: 600; color: {feature['color']}; margin-bottom: 0.7rem; display: flex; align-items: center;">
                            <span style="font-size: 2rem; margin-right: 10px;">{feature['icon']}</span> {feature['title']}
                        </div>
                        <p style="color: #666; font-size: 1rem;">{feature['description']}</p>
                        <div style="margin-top: 1rem; text-align: right;">
                            <span style="color: {feature['color']}; font-weight: 500; cursor: pointer;">Explore →</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        # Second card in row
        with col2:
            if i+1 < len(features):
                feature = features[i+1]
                if st.button(f"{feature['icon']} {feature['title']}", key=f"feature_{i+1}", use_container_width=True):
                    # This will navigate to the page when clicked
                    st.session_state.page_navigation = feature['page']
                    
                st.markdown(
                    f"""
                    <div style="background: white; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); padding: 1.5rem; margin-bottom: 1.5rem; border-left: 5px solid {feature['color']}; height: 170px;">
                        <div style="font-size: 1.4rem; font-weight: 600; color: {feature['color']}; margin-bottom: 0.7rem; display: flex; align-items: center;">
                            <span style="font-size: 2rem; margin-right: 10px;">{feature['icon']}</span> {feature['title']}
                        </div>
                        <p style="color: #666; font-size: 1rem;">{feature['description']}</p>
                        <div style="margin-top: 1rem; text-align: right;">
                            <span style="color: {feature['color']}; font-weight: 500; cursor: pointer;">Explore →</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    
    # Add navigation from button clicks
    if 'page_navigation' in st.session_state:
        # Set the sidebar radio to the selected page
        page = st.session_state.page_navigation
        # Clear the state to prevent infinite loop
        del st.session_state.page_navigation
        st.rerun()
    
    # Testimonials section
    st.markdown("<h3 style='text-align: center; color: #333; margin: 3rem 0 2rem;'>What Our Users Say</h3>", unsafe_allow_html=True)
    
    testimonials = [
        {"name": "Michael J.", "position": "Angel Investor", "text": "UnicornVision helped me identify promising startups before they became mainstream. The AI recommendations are spot on!", "rating": 5},
        {"name": "Sarah L.", "position": "VC Analyst", "text": "The competitive analysis features save me hours of research. I can't imagine going back to manual methods.", "rating": 5},
        {"name": "David K.", "position": "Portfolio Manager", "text": "The sentiment analysis gives me insights that numbers alone can't provide. It's like having an extra team member.", "rating": 4},
    ]
    
    cols = st.columns(3)
    for i, testimonial in enumerate(testimonials):
        with cols[i]:
            stars = "⭐" * testimonial["rating"]
            st.markdown(
                f"""
                <div style='background: white; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); padding: 1.5rem; height: 250px; display: flex; flex-direction: column; justify-content: space-between;'>
                    <div>
                        <div style='font-size: 1rem; color: #888; margin-bottom: 1rem;'>{stars}</div>
                        <p style='color: #555; font-style: italic; font-size: 1rem;'>"{testimonial['text']}"</p>
                    </div>
                    <div>
                        <div style='font-weight: 600; color: #333;'>{testimonial['name']}</div>
                        <div style='font-size: 0.9rem; color: #888;'>{testimonial['position']}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    # Modern footer
    st.markdown(
        """
        <footer style="margin-top: 5rem; padding: 2rem; background: #f8f9fa; border-radius: 10px; text-align: center;">
            <div style="margin-bottom: 1rem;">
                <span style="font-size: 1.6rem; font-weight: 600; background: linear-gradient(45deg, #6e48aa, #9d50bb); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">UnicornVision</span>
            </div>
            <p style="color: #666; margin-bottom: 1.5rem; font-size: 0.9rem;">© 2025 UnicornVision - Empowering investors with AI-driven analytics</p>
            <div style="color: #888; font-size: 0.8rem;">
                <span style="margin: 0 10px; cursor: pointer;">Privacy Policy</span> • 
                <span style="margin: 0 10px; cursor: pointer;">Terms of Service</span> • 
                <span style="margin: 0 10px; cursor: pointer;">Contact Us</span>
            </div>
        </footer>
        """,
        unsafe_allow_html=True
    )

# Market Analysis Page
elif page == "Market Analysis":
    st.markdown("<h1 class='main-header'>Market Analysis</h1>", unsafe_allow_html=True)
    
    # Modern dashboard introduction with key metrics
    st.markdown(
        """
        <div style="background: linear-gradient(to right, #f8f9fa, #ffffff); padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem; border-left: 5px solid #4B4BFF;">
            <h3 style="color: #333; margin-bottom: 1rem;">Global Startup Investment Analytics</h3>
            <p style="color: #555;">Explore real-time investment trends, funding patterns, and market opportunities across industries and regions.</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Dashboard filters
    st.markdown("### 🔍 Filter Your Analysis")
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        # Filter by funding type
        funding_types = ["All Types"] + sorted(market_data["Last Funding Type"].dropna().unique().tolist())
        selected_funding_type = st.selectbox("Funding Type", funding_types)
        
    with filter_col2:
        # Filter by year range
        market_data["Founded Date"] = pd.to_datetime(market_data["Founded Date"], errors="coerce")
        market_data["Founded Year"] = market_data["Founded Date"].dt.year
        years = market_data["Founded Year"].dropna().astype(int).unique()
        min_year, max_year = int(min(years)), int(max(years))
        year_range = st.slider("Founded Year Range", min_year, max_year, (min_year, max_year))
        
    with filter_col3:
        # Filter by operating status
        statuses = ["All Statuses"] + sorted(market_data["Operating Status"].dropna().unique().tolist())
        selected_status = st.selectbox("Operating Status", statuses)
    
    # Apply filters to the data
    filtered_data = market_data.copy()
    
    if selected_funding_type != "All Types":
        filtered_data = filtered_data[filtered_data["Last Funding Type"] == selected_funding_type]
        
    filtered_data = filtered_data[
        (filtered_data["Founded Year"] >= year_range[0]) & 
        (filtered_data["Founded Year"] <= year_range[1])
    ]
    
    if selected_status != "All Statuses":
        filtered_data = filtered_data[filtered_data["Operating Status"] == selected_status]
    
    # Generate dynamic analytics data
    category_funding = (
        filtered_data.groupby("Categories")["Total Funding Amount USD"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    region_funding = (
        filtered_data.groupby("Headquarters Regions")["Total Funding Amount USD"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    top_funded = filtered_data[["Organization Name", "Total Funding Amount USD"]].dropna()
    top_funded = top_funded.sort_values(by="Total Funding Amount USD", ascending=False).head(10)

    status_counts = filtered_data["Operating Status"].value_counts()
    type_funding = filtered_data["Last Funding Type"].value_counts().head(10)
    
    # Key metrics in cards
    st.markdown("### 📊 Key Market Insights")
    
    # Create dynamic summary cards
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        total_funding = filtered_data["Total Funding Amount USD"].sum()
        avg_funding = filtered_data["Total Funding Amount USD"].mean()
        
        st.markdown(
            f"""
            <div style="background: white; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); padding: 1.5rem; text-align: center; height: 150px;">
                <div style="font-size: 2.5rem; font-weight: 800; background: linear-gradient(45deg, #4B4BFF, #6E6EFF); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">${total_funding/1e9:.1f}B</div>
                <div style="font-size: 1rem; color: #666; font-weight: 500;">Total Funding</div>
                <div style="width: 60%; height: 4px; background: linear-gradient(90deg, #4B4BFF, #6E6EFF); margin: 1rem auto 0;"></div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with metric_col2:
        total_startups = len(filtered_data["Organization Name"].unique())
        
        st.markdown(
            f"""
            <div style="background: white; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); padding: 1.5rem; text-align: center; height: 150px;">
                <div style="font-size: 2.5rem; font-weight: 800; background: linear-gradient(45deg, #FF4B4B, #FF6E6E); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{total_startups:,}</div>
                <div style="font-size: 1rem; color: #666; font-weight: 500;">Active Startups</div>
                <div style="width: 60%; height: 4px; background: linear-gradient(90deg, #FF4B4B, #FF6E6E); margin: 1rem auto 0;"></div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with metric_col3:
        # Top category by funding
        top_category = category_funding.idxmax() if not category_funding.empty else "N/A"
        top_category_val = category_funding.max() if not category_funding.empty else 0
        
        st.markdown(
            f"""
            <div style="background: white; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); padding: 1.5rem; text-align: center; height: 150px;">
                <div style="font-size: 1.5rem; font-weight: 800; background: linear-gradient(45deg, #4CAF50, #8BC34A); -webkit-background-clip: text; -webkit-text-fill-color: transparent; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{top_category}</div>
                <div style="font-size: 1rem; color: #666; font-weight: 500;">Top Category</div>
                <div style="font-size: 0.9rem; color: #888;">${top_category_val/1e9:.1f}B funding</div>
                <div style="width: 60%; height: 4px; background: linear-gradient(90deg, #4CAF50, #8BC34A); margin: 0.5rem auto 0;"></div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with metric_col4:
        # Top region by funding
        top_region = region_funding.idxmax() if not region_funding.empty else "N/A"
        top_region_val = region_funding.max() if not region_funding.empty else 0
        
        st.markdown(
            f"""
            <div style="background: white; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); padding: 1.5rem; text-align: center; height: 150px;">
                <div style="font-size: 1.5rem; font-weight: 800; background: linear-gradient(45deg, #9C27B0, #673AB7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{top_region}</div>
                <div style="font-size: 1rem; color: #666; font-weight: 500;">Leading Region</div>
                <div style="font-size: 0.9rem; color: #888;">${top_region_val/1e9:.1f}B funding</div>
                <div style="width: 60%; height: 4px; background: linear-gradient(90deg, #9C27B0, #673AB7); margin: 0.5rem auto 0;"></div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # Organized visualizations with tabs
    st.markdown("<h3 style='margin-top: 2rem;'>🔍 Detailed Analytics</h3>", unsafe_allow_html=True)
    
    tabs = st.tabs(["Funding by Category", "Regional Analysis", "Top Startups", "Time Trends", "Funding Types"])
    
    with tabs[0]:
        st.markdown("#### Top 10 Categories by Total Funding")
        if not category_funding.empty:
            fig1, ax1 = plt.subplots(figsize=(10, 6))
            bars = ax1.bar(
                category_funding.index, 
                category_funding.values / 1e9,  # Convert to billions
                color=sns.color_palette("Blues_r", len(category_funding))
            )
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax1.text(
                    bar.get_x() + bar.get_width()/2.,
                    height + 0.1,
                    f'${height:.1f}B',
                    ha='center', va='bottom',
                    fontsize=9, fontweight='bold'
                )
                
            ax1.set_title("Top 10 Categories by Total Funding (Billions USD)", fontsize=14, pad=20)
            ax1.set_ylabel("Total Funding (Billions USD)", fontsize=12)
            ax1.set_xlabel("Category", fontsize=12)
            plt.xticks(rotation=45, ha="right", fontsize=10)
            ax1.grid(axis='y', alpha=0.3)
            ax1.spines['top'].set_visible(False)
            ax1.spines['right'].set_visible(False)
            plt.tight_layout()
            st.pyplot(fig1)
            
            # Show data table below chart
            st.markdown("##### Funding Details by Category")
            category_funding_df = pd.DataFrame({
                'Category': category_funding.index,
                'Total Funding (USD)': category_funding.values,
                'Funding (Billions)': category_funding.values / 1e9
            })
            st.dataframe(category_funding_df.set_index('Category'), use_container_width=True)
        else:
            st.info("No category data available with the current filters.")
    
    with tabs[1]:
        st.markdown("#### Regional Funding Distribution")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if not region_funding.empty:
                # Create the map visualization
                st.markdown("##### Global Funding Heatmap")
                # For now, we'll use a bar chart as a placeholder since we can't create a real map
                fig3, ax3 = plt.subplots(figsize=(10, 6))
                bars = ax3.bar(
                    region_funding.index, 
                    region_funding.values / 1e9,
                    color=sns.color_palette("YlOrRd", len(region_funding))
                )
                
                # Add value labels
                for bar in bars:
                    height = bar.get_height()
                    ax3.text(
                        bar.get_x() + bar.get_width()/2.,
                        height + 0.1,
                        f'${height:.1f}B',
                        ha='center', va='bottom',
                        fontsize=9, fontweight='bold'
                    )
                
                ax3.set_title("Top 10 Regions by Total Funding (Billions USD)", fontsize=14, pad=20)
                ax3.set_ylabel("Total Funding (Billions USD)", fontsize=12)
                ax3.set_xlabel("Region", fontsize=12)
                plt.xticks(rotation=45, ha="right", fontsize=10)
                ax3.grid(axis='y', alpha=0.3)
                ax3.spines['top'].set_visible(False)
                ax3.spines['right'].set_visible(False)
                plt.tight_layout()
                st.pyplot(fig3)
            else:
                st.info("No regional data available with the current filters.")
        
        with col2:
            if not region_funding.empty:
                # Create a pie chart for visual comparison
                st.markdown("##### Percentage Distribution")
                fig3b, ax3b = plt.subplots(figsize=(8, 8))
                ax3b.pie(
                    region_funding.values,
                    labels=region_funding.index,
                    autopct='%1.1f%%',
                    startangle=90,
                    shadow=False,
                    wedgeprops={'edgecolor': 'white', 'linewidth': 1},
                    textprops={'fontsize': 9},
                    colors=sns.color_palette("YlOrRd", len(region_funding))
                )
                ax3b.axis('equal')
                plt.tight_layout()
                st.pyplot(fig3b)
            else:
                st.info("No regional data available with the current filters.")
            
    with tabs[2]:
        st.markdown("#### Top Funded Startups")
        if not top_funded.empty:
            # Sort by funding amount to show largest first
            top_funded_sorted = top_funded.sort_values("Total Funding Amount USD", ascending=True)
            
            fig4, ax4 = plt.subplots(figsize=(10, 6))
            bars = ax4.barh(
                top_funded_sorted["Organization Name"], 
                top_funded_sorted["Total Funding Amount USD"] / 1e9,
                color=sns.color_palette("viridis", len(top_funded_sorted))
            )
            
            # Add value labels
            for bar in bars:
                width = bar.get_width()
                ax4.text(
                    width + 0.1,
                    bar.get_y() + bar.get_height()/2,
                    f'${width:.1f}B',
                    va='center', fontsize=9, fontweight='bold'
                )
                
            ax4.set_title("Top 10 Funded Startups (Billions USD)", fontsize=14, pad=20)
            ax4.set_xlabel("Total Funding (Billions USD)", fontsize=12)
            ax4.grid(axis='x', alpha=0.3)
            ax4.spines['top'].set_visible(False)
            ax4.spines['right'].set_visible(False)
            plt.tight_layout()
            st.pyplot(fig4)
            
            # Show the top funded startups in a table
            st.markdown("##### Details of Top Funded Startups")
            top_funded_display = top_funded.sort_values("Total Funding Amount USD", ascending=False).copy()
            top_funded_display["Funding (Billions)"] = top_funded_display["Total Funding Amount USD"] / 1e9
            top_funded_display = top_funded_display[["Organization Name", "Funding (Billions)"]]
            st.dataframe(top_funded_display.set_index("Organization Name"), use_container_width=True)
        else:
            st.info("No startup funding data available with the current filters.")
    
    with tabs[3]:
        st.markdown("#### Startup Creation & Funding Trends Over Time")
        
        # Get yearly funding trends
        yearly_data = filtered_data.copy()
        yearly_data["Founded Year"] = pd.to_datetime(yearly_data["Founded Date"], errors="coerce").dt.year
        
        # Startups founded per year
        startup_years = yearly_data["Founded Year"].value_counts().sort_index().dropna()
        
        if not startup_years.empty:
            # Convert index to int to ensure proper sorting
            startup_years.index = startup_years.index.astype(int)
            startup_years = startup_years.sort_index()
            
            fig5, ax5 = plt.subplots(figsize=(12, 6))
            
            # Line for number of startups
            line = ax5.plot(
                startup_years.index, 
                startup_years.values,
                marker='o',
                markersize=8,
                linewidth=3,
                color='#4B4BFF',
                label='Startups Founded'
            )
            
            # Add light area under the line
            ax5.fill_between(
                startup_years.index,
                startup_years.values,
                alpha=0.2,
                color='#4B4BFF'
            )
            
            # Add value labels on key points
            for i, (year, count) in enumerate(zip(startup_years.index, startup_years.values)):
                if i % max(1, len(startup_years) // 5) == 0:  # Label every 5th point approximately
                    ax5.annotate(
                        f'{count}',
                        (year, count),
                        textcoords="offset points",
                        xytext=(0, 10),
                        ha='center',
                        fontweight='bold'
                    )
            
            ax5.set_title("Startups Founded Per Year", fontsize=14, pad=20)
            ax5.set_xlabel("Year", fontsize=12)
            ax5.set_ylabel("Number of Startups", fontsize=12)
            ax5.grid(True, alpha=0.3)
            ax5.spines['top'].set_visible(False)
            ax5.spines['right'].set_visible(False)
            
            # Improve x-axis ticks
            years_range = range(min(startup_years.index), max(startup_years.index) + 1, max(1, len(startup_years) // 10))
            plt.xticks(years_range, fontsize=10)
            
            plt.tight_layout()
            st.pyplot(fig5)
            
            # Show the data in a table format
            st.markdown("##### Annual Startup Formation")
            startup_years_df = pd.DataFrame({
                'Year': startup_years.index,
                'Number of Startups': startup_years.values
            })
            st.dataframe(startup_years_df.set_index('Year'), use_container_width=True)
        else:
            st.info("No time trend data available with the current filters.")
        
    with tabs[4]:
        st.markdown("#### Funding Types Distribution")
        
        if not type_funding.empty:
            fig6, (ax6a, ax6b) = plt.subplots(1, 2, figsize=(14, 7))
            
            # Bar chart
            bars = ax6a.bar(
                type_funding.index, 
                type_funding.values,
                color=sns.color_palette("magma", len(type_funding))
            )
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax6a.text(
                    bar.get_x() + bar.get_width()/2.,
                    height + 0.1,
                    f'{height:,.0f}',
                    ha='center', va='bottom',
                    fontsize=9, fontweight='bold'
                )
            
            ax6a.set_title("Number of Startups by Funding Type", fontsize=14, pad=20)
            ax6a.set_ylabel("Number of Startups", fontsize=12)
            plt.setp(ax6a.get_xticklabels(), rotation=45, ha="right", fontsize=10)
            ax6a.grid(axis='y', alpha=0.3)
            ax6a.spines['top'].set_visible(False)
            ax6a.spines['right'].set_visible(False)
            
            # Pie chart
            ax6b.pie(
                type_funding.values,
                labels=type_funding.index,
                autopct='%1.1f%%',
                startangle=90,
                shadow=False,
                wedgeprops={'edgecolor': 'white', 'linewidth': 1},
                textprops={'fontsize': 9},
                colors=sns.color_palette("magma", len(type_funding))
            )
            ax6b.axis('equal')
            ax6b.set_title("Percentage Distribution of Funding Types", fontsize=14, pad=20)
            
            plt.tight_layout()
            st.pyplot(fig6)
            
            # Display the data table
            st.markdown("##### Funding Type Distribution Details")
            type_funding_df = pd.DataFrame({
                'Funding Type': type_funding.index,
                'Count': type_funding.values,
                'Percentage': (type_funding.values / type_funding.values.sum() * 100).round(1)
            })
            st.dataframe(type_funding_df.set_index('Funding Type'), use_container_width=True)
        else:
            st.info("No funding type data available with the current filters.")
    
    # Display dynamic insights generated from data
    st.markdown("<h3 style='margin-top: 2rem;'>💡 Market Insights</h3>", unsafe_allow_html=True)
    
    # Create real-time insights based on the filtered data
    insights = []
    
    # Add dynamic insights based on the data
    if not category_funding.empty:
        top_category = category_funding.idxmax()
        category_percentage = (category_funding.max() / category_funding.sum() * 100).round(1)
        insights.append(f"The {top_category} sector dominates with {category_percentage}% of all funding among top categories.")
    
    if not region_funding.empty:
        top_region = region_funding.idxmax()
        second_region = region_funding.iloc[1:2].idxmax() if len(region_funding) > 1 else None
        
        # Fix the region ratio calculation to handle integer properly
        if len(region_funding) > 1:
            region_ratio = round(float(region_funding.max()) / float(region_funding.iloc[1]), 1)
        else:
            region_ratio = 0
        
        if second_region:
            insights.append(f"{top_region} leads the funding race, with {region_ratio}x more investment than the second-placed {second_region}.")
    
    if 'Last Funding Amount USD' in filtered_data.columns:
        avg_funding = filtered_data['Last Funding Amount USD'].mean()
        insights.append(f"The average last funding round is ${avg_funding/1e6:.1f}M across all startups in the selected filters.")
    
    # Operating status insights
    if not status_counts.empty:
        top_status = status_counts.idxmax()
        status_percentage = (status_counts.max() / status_counts.sum() * 100).round(1)
        insights.append(f"{status_percentage}% of startups are currently in {top_status} status.")
    
    # Time trend insights
    if not startup_years.empty and len(startup_years) > 1:
        latest_year = startup_years.index.max()
        previous_year = latest_year - 1
        
        if latest_year in startup_years.index and previous_year in startup_years.index:
            growth_rate = ((startup_years[latest_year] / startup_years[previous_year]) - 1) * 100
            trend_text = "increased" if growth_rate > 0 else "decreased"
            insights.append(f"Startup formation {trend_text} by {abs(growth_rate):.1f}% in {latest_year} compared to {previous_year}.")
    
    if len(insights) > 0:
        # Display insights in an attractive format
        insight_cols = st.columns(min(len(insights), 2))
        
        for i, insight in enumerate(insights):
            with insight_cols[i % 2]:
                st.markdown(
                    f"""
                    <div style="background: white; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
                          margin-bottom: 1rem; padding: 1.2rem; border-left: 4px solid #4B4BFF;">
                        <p style="color: #555; font-size: 1rem; margin: 0;">💡 {insight}</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
    else:
        st.info("Adjust filters to generate market insights.")

# Competitor Analysis Page
elif page == "Competitor Analysis":
    st.markdown("<h1 class='main-header'>Competitor Analysis</h1>", unsafe_allow_html=True)
    st.write("Compare startups head-to-head to understand competitive positioning")
    
    # Get list of startups - handle possible column name variations
    try:
        # Detect the startup name column
        startup_name_col = None
        possible_columns = ["Startup_Name", "Organization Name", "Company", "Startup", "Name"]
        for col in possible_columns:
            if col in main_data.columns:
                startup_name_col = col
                break
        
        if startup_name_col:
            startup_list = main_data[startup_name_col].unique()
            
            col1, col2 = st.columns(2)
            
            with col1:
                startup_1 = st.selectbox("Select First Startup", startup_list)
            
            with col2:
                # Filter out the first selection
                remaining_startups = [s for s in startup_list if s != startup_1]
                startup_2 = st.selectbox("Select Second Startup", remaining_startups)
            
            if st.button("Compare Startups"):
                # Fetch their rows
                startup_df_1 = main_data[main_data[startup_name_col] == startup_1]
                startup_df_2 = main_data[main_data[startup_name_col] == startup_2]
                
                # Convert to pandas for easier display
                pdf1 = startup_df_1
                pdf2 = startup_df_2
                
                # Show comparison
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"### {startup_1}")
                    st.dataframe(pdf1.iloc[0:1].T)
                
                with col2:
                    st.markdown(f"### {startup_2}")
                    st.dataframe(pdf2.iloc[0:1].T)
                
                # Comparison summary
                st.markdown("### Comparison Summary")
                
                # Try to detect key comparison columns
                industry_col = next((col for col in ["Industry_Vertical", "Industry", "Sector"] if col in pdf1.columns), None)
                location_col = next((col for col in ["City_Location", "Location", "Headquarters"] if col in pdf1.columns), None)
                investment_col = next((col for col in ["Investment_Type", "Funding Type", "Round"] if col in pdf1.columns), None)
                investors_col = next((col for col in ["Investors_Name", "Investors", "Backers"] if col in pdf1.columns), None)
                amount_col = next((col for col in ["Amount_in_USD", "Funding Amount", "Raised"] if col in pdf1.columns), None)
                
                s1 = pdf1.iloc[0]
                s2 = pdf2.iloc[0]
                
                # Build comparison data with available columns
                comparison_data = []
                
                if industry_col:
                    comparison_data.append({"Metric": "Industry", "Startup 1": s1[industry_col], "Startup 2": s2[industry_col]})
                
                if location_col:
                    comparison_data.append({"Metric": "City", "Startup 1": s1[location_col], "Startup 2": s2[location_col]})
                
                if investment_col:
                    comparison_data.append({"Metric": "Investment Type", "Startup 1": s1[investment_col], "Startup 2": s2[investment_col]})
                
                if investors_col:
                    comparison_data.append({"Metric": "Investors", "Startup 1": s1[investors_col], "Startup 2": s2[investors_col]})
                
                # Try to parse funding amounts
                if amount_col:
                    try:
                        amt1 = float(str(s1[amount_col]).replace(',', ''))
                        amt2 = float(str(s2[amount_col]).replace(',', ''))
                        comparison_data.append({"Metric": "Funding", "Startup 1": f"${amt1:,.0f}", "Startup 2": f"${amt2:,.0f}"})
                    except:
                        comparison_data.append({"Metric": "Funding", "Startup 1": "N/A", "Startup 2": "N/A"})
                
                st.table(pd.DataFrame(comparison_data))
        else:
            st.error("Could not find startup name column in the dataset. Please check data format.")
    except Exception as e:
        st.error(f"An error occurred while processing startup data: {e}")
        st.info("This may be due to missing or incorrectly formatted data. Please check the dataset structure.")

# Sentiment Analysis Page
elif page == "Sentiment Analysis":
    st.markdown("<h1 class='main-header'>Sentiment Analysis</h1>", unsafe_allow_html=True)
    
    # Modern dashboard introduction
    st.markdown(
        """
        <div style="background: linear-gradient(to right, #f8f9fa, #ffffff); padding: 1.5rem; border-radius: 10px; 
                  margin-bottom: 2rem; border-left: 5px solid #4B4BFF;">
            <h3 style="color: #333; margin-bottom: 1rem;">Market Perception Analytics</h3>
            <p style="color: #555;">Analyze news sentiment and market perception for startups to make data-driven investment decisions.</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Create tabs for the two analysis types
    analysis_tabs = st.tabs(["Live News Analysis", "Dataset Startups Analysis"])
    
    with analysis_tabs[0]:
        st.markdown("### 🔍 Live News Sentiment Analysis")
        st.markdown(
            """
            <p style="color: #555; margin-bottom: 1.5rem;">
            Get real-time sentiment analysis from latest news articles about any startup.
            </p>
            """, 
            unsafe_allow_html=True
        )
        
        # Input methods
        input_method = st.radio(
            "Choose how to input startup information:",
            ["Select from database", "Enter manually"],
            horizontal=True
        )
        
        if input_method == "Select from database":
            # Get startup names from database
            if "Organization Name" in market_data.columns:
                startup_names = market_data["Organization Name"].dropna().unique()
                startup_name = st.selectbox("Select a startup from our database:", startup_names, key="live_news_startup_select")
            else:
                st.warning("Database not properly loaded. Try entering a startup name manually.")
                startup_name = st.text_input("Enter startup name:", placeholder="e.g., Stripe, Coinbase, Robinhood")
        else:
            # Manual input
            startup_name = st.text_input("Enter startup name:", placeholder="e.g., Stripe, Coinbase, Robinhood")
        
        # NewsAPI integration (mock for now, can be replaced with actual API)
        def fetch_live_news_articles(startup_name, max_articles=10):
            # This would be replaced with actual NewsAPI call
            # Using more realistic mock data with proper links
            current_date = datetime.now().strftime("%Y-%m-%d")
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            
            mock_articles = [
                {
                    "title": f"{startup_name} Announces New AI-Powered Platform",
                    "description": f"{startup_name} today unveiled its latest artificial intelligence platform aimed at revolutionizing customer analytics and engagement.",
                    "url": "https://techcrunch.com/startups/news",
                    "source": "TechCrunch",
                    "published_at": current_date
                },
                {
                    "title": f"Investors Rally Behind {startup_name}'s Latest Funding Round",
                    "description": f"The startup has successfully raised $50M in Series B funding led by prominent venture capital firms, valuing the company at over $500M.",
                    "url": "https://www.forbes.com/startups",
                    "source": "Forbes",
                    "published_at": current_date
                },
                {
                    "title": f"Market Analysts Question {startup_name}'s Business Model Sustainability",
                    "description": f"Despite recent growth, questions remain about the long-term viability of {startup_name}'s approach to monetization and customer acquisition costs.",
                    "url": "https://www.wsj.com/markets/startups",
                    "source": "Wall Street Journal",
                    "published_at": yesterday
                },
                {
                    "title": f"{startup_name} Reports Strong Quarterly Growth Exceeding Projections",
                    "description": f"The company announced a 45% year-over-year revenue increase, beating analyst expectations and strengthening its market position.",
                    "url": "https://www.cnbc.com/earnings",
                    "source": "CNBC",
                    "published_at": yesterday
                },
                {
                    "title": f"Technical Issues Plague {startup_name}'s Platform, Users Report Frustration",
                    "description": f"Multiple outages and performance problems have affected {startup_name}'s service in recent weeks, raising concerns about its technical infrastructure.",
                    "url": "https://www.theverge.com/tech",
                    "source": "The Verge",
                    "published_at": yesterday
                }
            ]
            return mock_articles
        
        # Improved sentiment analysis function with confidence scores
        def analyze_sentiment_with_confidence(text):
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # Range: -1 to 1
            subjectivity = blob.sentiment.subjectivity  # Range: 0 to 1
            
            # Calculate confidence based on polarity and subjectivity
            if abs(polarity) < 0.2:
                confidence = 30 + abs(polarity) * 100  # Lower confidence for neutral
            else:
                confidence = 50 + abs(polarity) * 100  # Higher confidence for stronger sentiment
                
            # Adjust confidence based on subjectivity (more subjective = less confident)
            confidence = min(100, max(1, confidence * (1 - subjectivity * 0.5)))
            
            # Determine sentiment category and recommendation
            if polarity > 0.1:
                sentiment = "Positive"
                recommendation = "Invest"
                color = "#4CAF50"  # Green
            elif polarity < -0.1:
                sentiment = "Negative"
                recommendation = "Avoid"
                color = "#F44336"  # Red
            else:
                sentiment = "Neutral"
                recommendation = "Wait"
                color = "#FFC107"  # Yellow
                
            return {
                "sentiment": sentiment,
                "polarity": polarity,
                "confidence": confidence,
                "recommendation": recommendation,
                "color": color
            }
        
        # Live news analysis button
        if st.button("Fetch Latest News"):
            if startup_name:
                with st.spinner(f"Fetching and analyzing latest news about {startup_name}..."):
                    # Simulate loading delay
                    time.sleep(2)
                    
                    # Fetch news articles
                    articles = fetch_live_news_articles(startup_name)
                    
                    if articles:
                        # Analyze sentiment for each article
                        sentiment_distribution = {"Positive": 0, "Neutral": 0, "Negative": 0}
                        sentiment_insights = []
                        
                        for article in articles:
                            title = article["title"]
                            description = article.get("description", "")
                            full_text = f"{title}. {description}"
                            
                            # Get sentiment analysis
                            sentiment_data = analyze_sentiment_with_confidence(full_text)
                            sentiment_distribution[sentiment_data["sentiment"]] += 1
                            
                            # Add to insights
                            sentiment_insights.append({
                                "title": title,
                                "description": description,
                                "source": article["source"],
                                "published_at": article["published_at"],
                                "url": article["url"],
                                "sentiment": sentiment_data["sentiment"],
                                "polarity": sentiment_data["polarity"],
                                "confidence": sentiment_data["confidence"],
                                "recommendation": sentiment_data["recommendation"],
                                "color": sentiment_data["color"]
                            })
                        
                        # Display overall sentiment distribution
                        st.markdown("#### 📊 Overall Sentiment Distribution")
                        
                        # Calculate the dominant sentiment
                        max_sentiment = max(sentiment_distribution.items(), key=lambda x: x[1])[0]
                        overall_recommendation = "Invest" if max_sentiment == "Positive" else "Avoid" if max_sentiment == "Negative" else "Wait"
                        recommendation_color = {"Invest": "#4CAF50", "Wait": "#FFC107", "Avoid": "#F44336"}[overall_recommendation]
                        
                        # Display recommendation prominently
                        st.markdown(
                            f"""
                            <div style="background: white; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); padding: 1.5rem; margin-bottom: 2rem; text-align: center;">
                                <h2 style="margin-bottom: 0.5rem; color: {recommendation_color}; font-weight: 700;">{overall_recommendation}</h2>
                                <p style="color: #555; font-size: 1.1rem;">Based on current news sentiment</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        # Display sentiment distribution chart
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            # Create sentiment distribution chart
                            sentiment_df = pd.DataFrame({
                                'Sentiment': list(sentiment_distribution.keys()),
                                'Count': list(sentiment_distribution.values())
                            })
                            
                            fig, ax = plt.subplots(figsize=(10, 6))
                            bars = ax.bar(
                                sentiment_df['Sentiment'],
                                sentiment_df['Count'],
                                color=['#4CAF50', '#FFC107', '#F44336']
                            )
                            
                            # Add count labels on bars
                            for bar in bars:
                                height = bar.get_height()
                                ax.text(
                                    bar.get_x() + bar.get_width()/2.,
                                    height + 0.1,
                                    f'{int(height)}',
                                    ha='center', fontweight='bold'
                                )
                            
                            ax.set_title(f"News Sentiment Analysis for {startup_name}", fontsize=14, pad=20)
                            ax.set_ylabel("Number of Articles", fontsize=12)
                            ax.grid(axis='y', alpha=0.3)
                            ax.spines['top'].set_visible(False)
                            ax.spines['right'].set_visible(False)
                            plt.tight_layout()
                            st.pyplot(fig)
                        
                        with col2:
                            # Display sentiment percentages
                            total_articles = sum(sentiment_distribution.values())
                            
                            for sentiment, count in sentiment_distribution.items():
                                if total_articles > 0:
                                    percentage = (count / total_articles) * 100
                                else:
                                    percentage = 0
                                    
                                sentiment_color = "#4CAF50" if sentiment == "Positive" else "#F44336" if sentiment == "Negative" else "#FFC107"
                                
                                st.markdown(
                                    f"""
                                    <div style="background: white; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
                                          padding: 1.2rem; margin-bottom: 1rem; text-align: center;">
                                        <div style="font-size: 2rem; font-weight: 700; color: {sentiment_color};">{percentage:.1f}%</div>
                                        <div style="color: #555;">{sentiment}</div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                        
                        # Display article cards with detailed sentiment analysis
                        st.markdown("#### 📰 News Articles with Sentiment Analysis")
                        
                        for i, article in enumerate(sentiment_insights):
                            # Format confidence as a percentage
                            confidence_pct = f"{article['confidence']:.1f}%"
                            
                            # Create a card for each article
                            st.markdown(
                                f"""
                                <div style="background: white; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
                                      margin: 0 0 1.5rem 0; overflow: hidden;">
                                    <div style="padding: 1.5rem; border-bottom: 1px solid #f0f0f0;">
                                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                            <span style="font-size: 0.9rem; color: #777;">
                                                {article["source"]} • {article["published_at"]}
                                            </span>
                                            <span style="font-weight: 600; color: {article["color"]}; 
                                                  background: {article["color"]}20; padding: 0.3rem 0.8rem; 
                                                  border-radius: 50px; font-size: 0.9rem;">
                                                {article["sentiment"]}
                                            </span>
                                        </div>
                                        <h3 style="margin: 0.5rem 0; font-size: 1.2rem;">
                                            <a href="{article["url"]}" target="_blank" style="color: #333; text-decoration: none; 
                                               hover: text-decoration: underline;">
                                                {article["title"]}
                                            </a>
                                        </h3>
                                        <p style="color: #555; margin-bottom: 1rem; font-size: 0.95rem;">
                                            {article["description"]}
                                        </p>
                                    </div>
                                    <div style="background: #f9f9f9; padding: 1rem 1.5rem; display: flex; justify-content: space-between;">
                                        <div>
                                            <span style="font-weight: 600; color: #555; font-size: 0.9rem;">Recommendation:</span>
                                            <span style="font-weight: 700; color: {article["color"]}; margin-left: 0.5rem;">
                                                {article["recommendation"]}
                                            </span>
                                        </div>
                                        <div style="display: flex; align-items: center;">
                                            <span style="font-size: 0.9rem; color: #777; margin-right: 0.5rem;">Confidence:</span>
                                            <div style="width: 100px; background: #e0e0e0; height: 8px; border-radius: 4px; overflow: hidden;">
                                                <div style="width: {article["confidence"]}%; background: {article["color"]}; height: 100%;"></div>
                                            </div>
                                            <span style="font-size: 0.9rem; color: #555; margin-left: 0.5rem; font-weight: 600;">
                                                {confidence_pct}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                    else:
                        st.error("No news articles found. Try a different startup name.")
            else:
                st.warning("Please enter a startup name.")
    
    with analysis_tabs[1]:
        st.markdown("### 🔍 Dataset-Based Sentiment Analysis")
        st.markdown(
            """
            <p style="color: #555; margin-bottom: 1.5rem;">
            Select a startup from our database to analyze stored sentiment information and get investment recommendations.
            </p>
            """, 
            unsafe_allow_html=True
        )
        
        # Create a dataset of startup organizations
        if "Organization Name" in market_data.columns:
            startup_names = market_data["Organization Name"].dropna().unique()
            selected_startup = st.selectbox("Select a startup from our database:", startup_names, key="database_sentiment_startup_select")
            
            # Generate preset sentiment data for selected startup
            def generate_startup_sentiment_data(startup_name):
                # Generate a deterministic but seemingly random sentiment based on the name
                seed = sum(ord(c) for c in startup_name)
                random.seed(seed)
                
                # Generate number of articles with positive, neutral, and negative sentiment
                total_articles = random.randint(5, 15)
                
                # Generate the sentiment distribution
                positive = random.randint(1, total_articles)
                remaining = total_articles - positive
                negative = random.randint(0, remaining)
                neutral = remaining - negative
                
                sentiment_distribution = {
                    "Positive": positive,
                    "Neutral": neutral,
                    "Negative": negative
                }
                
                # Generate article data
                articles = []
                for i in range(total_articles):
                    if i < positive:
                        sentiment = "Positive"
                        polarity = random.uniform(0.2, 0.9)
                        confidence = random.uniform(60, 95)
                        recommendation = "Invest"
                        color = "#4CAF50"
                    elif i < positive + neutral:
                        sentiment = "Neutral"
                        polarity = random.uniform(-0.1, 0.1)
                        confidence = random.uniform(40, 70)
                        recommendation = "Wait"
                        color = "#FFC107"
                    else:
                        sentiment = "Negative"
                        polarity = random.uniform(-0.9, -0.2)
                        confidence = random.uniform(60, 90)
                        recommendation = "Avoid"
                        color = "#F44336"
                    
                    # Create article
                    article_type = ["Funding", "Product Launch", "Earnings", "Partnership", "Market Analysis"]
                    article_title = f"{startup_name} {random.choice(article_type)} News"
                    
                    if sentiment == "Positive":
                        description = f"Positive developments for {startup_name} as they announce new successes."
                    elif sentiment == "Neutral":
                        description = f"Mixed results for {startup_name} as the market evaluates recent developments."
                    else:
                        description = f"Challenges ahead for {startup_name} as they navigate recent setbacks."
                    
                    articles.append({
                        "title": article_title,
                        "description": description,
                        "sentiment": sentiment,
                        "polarity": polarity,
                        "confidence": confidence,
                        "recommendation": recommendation,
                        "color": color
                    })
                
                return sentiment_distribution, articles
            
            if st.button("Analyze Startup Sentiment"):
                with st.spinner(f"Analyzing sentiment data for {selected_startup}..."):
                    # Get sentiment data from our dataset
                    sentiment_distribution, sentiment_articles = generate_startup_sentiment_data(selected_startup)
                    
                    # Calculate the dominant sentiment
                    max_sentiment = max(sentiment_distribution.items(), key=lambda x: x[1])[0]
                    overall_recommendation = "Invest" if max_sentiment == "Positive" else "Avoid" if max_sentiment == "Negative" else "Wait"
                    recommendation_color = {"Invest": "#4CAF50", "Wait": "#FFC107", "Avoid": "#F44336"}[overall_recommendation]
                    
                    # Display the recommendation prominently
                    st.markdown(
                        f"""
                        <div style="background: white; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); padding: 1.5rem; 
                              margin-bottom: 2rem; text-align: center; border: 2px solid {recommendation_color};">
                            <h2 style="margin-bottom: 0.5rem; color: {recommendation_color}; font-weight: 700; font-size: 2rem;">{overall_recommendation}</h2>
                            <p style="color: #555; font-size: 1.1rem;">Investment recommendation based on sentiment analysis</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # Display sentiment distribution
                    st.markdown("#### 📊 Sentiment Analysis Results")
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        # Create sentiment distribution chart
                        sentiment_df = pd.DataFrame({
                            'Sentiment': list(sentiment_distribution.keys()),
                            'Count': list(sentiment_distribution.values())
                        })
                        
                        # Create a horizontal bar chart with nice colors
                        fig, ax = plt.subplots(figsize=(10, 6))
                        colors = {'Positive': '#4CAF50', 'Neutral': '#FFC107', 'Negative': '#F44336'}
                        
                        # Sort by sentiment to ensure consistent ordering
                        sentiment_df = sentiment_df.sort_values('Sentiment', key=lambda x: pd.Categorical(x, categories=['Positive', 'Neutral', 'Negative']))
                        
                        bars = ax.barh(
                            sentiment_df['Sentiment'],
                            sentiment_df['Count'],
                            color=[colors[s] for s in sentiment_df['Sentiment']]
                        )
                        
                        # Add count labels inside bars
                        for bar in bars:
                            width = bar.get_width()
                            ax.text(
                                width - 0.5,
                                bar.get_y() + bar.get_height()/2,
                                f'{int(width)}',
                                ha='right', va='center', 
                                color='white', fontweight='bold'
                            )
                        
                        ax.set_title(f"Sentiment Analysis for {selected_startup}", fontsize=14, pad=20)
                        ax.set_xlabel("Number of Data Points", fontsize=12)
                        ax.grid(axis='x', alpha=0.3)
                        ax.spines['top'].set_visible(False)
                        ax.spines['right'].set_visible(False)
                        plt.tight_layout()
                        st.pyplot(fig)
                    
                    with col2:
                        # Calculate total and percentages
                        total = sum(sentiment_distribution.values())
                        for sentiment, count in sentiment_distribution.items():
                            if total > 0:
                                percentage = (count / total) * 100
                            else:
                                percentage = 0
                                
                            sentiment_color = colors[sentiment]
                            
                            st.markdown(
                                f"""
                                <div style="background: white; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
                                      padding: 1.2rem; margin-bottom: 1rem; text-align: center;">
                                    <div style="font-size: 2rem; font-weight: 700; color: {sentiment_color};">{percentage:.1f}%</div>
                                    <div style="color: #555;">{sentiment}</div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                    
                    # Display key sentiment indicators
                    st.markdown("#### 🔍 Sentiment Indicators")
                    
                    # Create three columns for key metrics
                    indicator_cols = st.columns(3)
                    
                    with indicator_cols[0]:
                        # Positive sentiment ratio
                        positive_ratio = sentiment_distribution["Positive"] / total if total > 0 else 0
                        positive_score = int(positive_ratio * 100)
                        
                        st.markdown(
                            f"""
                            <div style="background: white; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); padding: 1.5rem; text-align: center; height: 150px;">
                                <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">Positive Sentiment</div>
                                <div style="font-size: 2.5rem; font-weight: 800; color: #4CAF50;">{positive_score}%</div>
                                <div style="width: 70%; height: 8px; background: #e0e0e0; border-radius: 4px; margin: 1rem auto 0;">
                                    <div style="width: {positive_score}%; background: #4CAF50; height: 100%; border-radius: 4px;"></div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    
                    with indicator_cols[1]:
                        # Mixed signals indicator
                        if abs(sentiment_distribution["Positive"] - sentiment_distribution["Negative"]) < 2:
                            mixed_signals = "High"
                            mixed_score = 75
                            mixed_color = "#FFC107"
                        elif abs(sentiment_distribution["Positive"] - sentiment_distribution["Negative"]) < 4:
                            mixed_signals = "Medium"
                            mixed_score = 50
                            mixed_color = "#FF9800"
                        else:
                            mixed_signals = "Low"
                            mixed_score = 25
                            mixed_color = "#4CAF50"
                        
                        st.markdown(
                            f"""
                            <div style="background: white; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); padding: 1.5rem; text-align: center; height: 150px;">
                                <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">Mixed Signals</div>
                                <div style="font-size: 2.5rem; font-weight: 800; color: {mixed_color};">{mixed_signals}</div>
                                <div style="width: 70%; height: 8px; background: #e0e0e0; border-radius: 4px; margin: 1rem auto 0;">
                                    <div style="width: {mixed_score}%; background: {mixed_color}; height: 100%; border-radius: 4px;"></div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    
                    with indicator_cols[2]:
                        # Risk assessment
                        negative_ratio = sentiment_distribution["Negative"] / total if total > 0 else 0
                        risk_score = int(negative_ratio * 100)
                        
                        if risk_score < 20:
                            risk_level = "Low"
                            risk_color = "#4CAF50"
                        elif risk_score < 40:
                            risk_level = "Medium"
                            risk_color = "#FFC107"
                        else:
                            risk_level = "High"
                            risk_color = "#F44336"
                        
                        st.markdown(
                            f"""
                            <div style="background: white; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); padding: 1.5rem; text-align: center; height: 150px;">
                                <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">Risk Assessment</div>
                                <div style="font-size: 2.5rem; font-weight: 800; color: {risk_color};">{risk_level}</div>
                                <div style="width: 70%; height: 8px; background: #e0e0e0; border-radius: 4px; margin: 1rem auto 0;">
                                    <div style="width: {risk_score}%; background: {risk_color}; height: 100%; border-radius: 4px;"></div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    
                    # Display detailed sentiment cards
                    st.markdown("#### 📰 Detailed Sentiment Analysis")
                    
                    for article in sentiment_articles:
                        # Format confidence as a percentage
                        confidence_pct = f"{article['confidence']:.1f}%"
                        
                        # Create a card for each article
                        st.markdown(
                            f"""
                            <div style="background: white; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
                                  margin: 0 0 1.5rem 0; overflow: hidden;">
                                <div style="padding: 1.5rem; border-bottom: 1px solid #f0f0f0;">
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                        <span style="font-weight: 600; color: {article["color"]}; 
                                              background: {article["color"]}20; padding: 0.3rem 0.8rem; 
                                              border-radius: 50px; font-size: 0.9rem;">
                                            {article["sentiment"]}
                                        </span>
                                    </div>
                                    <h3 style="margin: 0.5rem 0; font-size: 1.2rem; color: #333;">
                                        {article["title"]}
                                    </h3>
                                    <p style="color: #555; margin-bottom: 1rem; font-size: 0.95rem;">
                                        {article["description"]}
                                    </p>
                                </div>
                                <div style="background: #f9f9f9; padding: 1rem 1.5rem; display: flex; justify-content: space-between;">
                                    <div>
                                        <span style="font-weight: 600; color: #555; font-size: 0.9rem;">Recommendation:</span>
                                        <span style="font-weight: 700; color: {article["color"]}; margin-left: 0.5rem;">
                                            {article["recommendation"]}
                                        </span>
                                    </div>
                                    <div style="display: flex; align-items: center;">
                                        <span style="font-size: 0.9rem; color: #777; margin-right: 0.5rem;">Confidence:</span>
                                        <div style="width: 100px; background: #e0e0e0; height: 8px; border-radius: 4px; overflow: hidden;">
                                            <div style="width: {article["confidence"]}%; background: {article["color"]}; height: 100%;"></div>
                                        </div>
                                        <span style="font-size: 0.9rem; color: #555; margin-left: 0.5rem; font-weight: 600;">
                                            {confidence_pct}
                                        </span>
                                    </div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
        else:
            st.warning("No startup data available in the dataset. Please check your data loading process.")

# Portfolio Management Page
elif page == "Portfolio Management":
    st.markdown("<h1 class='main-header'>Portfolio Management</h1>", unsafe_allow_html=True)
    
    # Modern introduction
    st.markdown(
        """
        <div style="background: linear-gradient(to right, #f8f9fa, #ffffff); padding: 1.5rem; border-radius: 10px; 
                  margin-bottom: 2rem; border-left: 5px solid #4B4BFF;">
            <h3 style="color: #333; margin-bottom: 1rem;">Investment Portfolio Dashboard</h3>
            <p style="color: #555;">Build and track your investment portfolio with ROI projections and performance tracking.</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Check if we've just added a startup from Investment Council
    if 'newly_added_startup' in st.session_state:
        startup = st.session_state.newly_added_startup
        st.success(f"✅ Successfully added {startup} to your portfolio from Investment Council!")
        # Clear the newly added status
        del st.session_state.newly_added_startup
    
    # Add a new investment
    st.markdown("### Add New Investment")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        startup_names = main_data["Startup_Name"].unique()
        selected_startup = st.selectbox("Select a startup", startup_names, key="portfolio_startup_select")
    
    with col2:
        amount_invested = st.number_input("Enter amount invested (USD)", min_value=1000, step=1000)
    
    with col3:
        confidence_score = st.slider("Confidence score (0-100)", 0, 100, 50)
        sentiment_label = st.selectbox("Sentiment", ["Positive", "Neutral", "Negative"])
    
    if st.button("Add to Portfolio"):
        # Calculate expected ROI
        roi_base = {"Positive": 0.3, "Neutral": 0.15, "Negative": 0.05}
        expected_roi_pct = roi_base.get(sentiment_label, 0.1) + (confidence_score / 1000)
        expected_return = round(amount_invested * expected_roi_pct, 2)
        projected_value = round(amount_invested + expected_return, 2)
        
        # Get startup row
        startup_row = main_data[main_data["Startup_Name"] == selected_startup].iloc[0]
        industry = startup_row["Industry_Vertical"]
        
        # Create portfolio entry
        portfolio_entry = {
            "Startup": selected_startup,
            "Industry": industry,
            "Amount Invested": amount_invested,
            "Confidence Score": confidence_score,
            "Sentiment": sentiment_label,
            "Expected ROI (%)": round(expected_roi_pct * 100, 2),
            "Expected Return": expected_return,
            "Projected Value": projected_value,
            "Date Added": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Add to portfolio
        st.session_state.portfolio.append(portfolio_entry)
        st.success(f"Added {selected_startup} to your portfolio!")
    
    # Show portfolio
    if st.session_state.portfolio:
        st.markdown("### Your Investment Portfolio")
        
        portfolio_df = pd.DataFrame(st.session_state.portfolio)
        st.dataframe(portfolio_df)
        
        # Portfolio summary
        total_invested = portfolio_df['Amount Invested'].sum()
        total_projected = portfolio_df['Projected Value'].sum()
        total_return = portfolio_df['Expected Return'].sum()
        avg_roi = (total_return / total_invested) * 100
        
        st.markdown("### Portfolio Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Invested", f"${total_invested:,.2f}")
        
        with col2:
            st.metric("Expected Return", f"${total_return:,.2f}")
        
        with col3:
            st.metric("Projected Value", f"${total_projected:,.2f}")
        
        with col4:
            st.metric("Average ROI", f"{avg_roi:.2f}%")
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Investment by Industry")
            industry_investment = portfolio_df.groupby("Industry")["Amount Invested"].sum()
            
            fig1, ax1 = plt.subplots(figsize=(10, 6))
            plt.pie(
                industry_investment, 
                labels=industry_investment.index, 
                autopct='%1.1f%%', 
                startangle=90,
                colors=sns.color_palette("pastel", len(industry_investment))
            )
            plt.axis('equal')
            plt.title("Investment Distribution by Industry")
            st.pyplot(fig1)
        
        with col2:
            st.markdown("### Expected Returns by Startup")
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            plt.bar(
                portfolio_df["Startup"], 
                portfolio_df["Expected Return"],
                color=sns.color_palette("viridis", len(portfolio_df))
            )
            plt.xticks(rotation=45, ha="right")
            plt.title("Expected Returns by Startup")
            plt.ylabel("Expected Return (USD)")
            plt.tight_layout()
            st.pyplot(fig2)
    else:
        st.info("Your portfolio is empty. Add investments to see them here.")

# Investment Council Page
elif page == "Investment Council":
    st.markdown("<h1 class='main-header'>AI Investment Council</h1>", unsafe_allow_html=True)
    
    # Modern dashboard introduction
    st.markdown(
        """
        <div style="background: linear-gradient(to right, #f8f9fa, #ffffff); padding: 1.5rem; border-radius: 10px; 
                  margin-bottom: 2rem; border-left: 5px solid #4B4BFF;">
            <h3 style="color: #333; margin-bottom: 1rem;">AI-Powered Investment Analysis</h3>
            <p style="color: #555;">Get comprehensive investment recommendations from multiple AI expert perspectives with detailed insights and rationale.</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Define the investment agents and their roles
    agents = {
        "Visionary": "Optimistic about the startup's future and long-term growth.",
        "Skeptic": "Identifies risks, weaknesses, and potential failures.",
        "Analyst": "Provides data-driven insights based on past performance and market trends.",
        "Scout": "Compares the startup with competitors in the industry.",
        "Oracle": "Gives a final investment verdict after analyzing all factors."
    }
    
    # Show agent descriptions
    st.markdown("### 🧠 Your Investment Council")
    
    # Display agents in a more visual way
    agent_cols = st.columns(5)
    agent_colors = {
        "Visionary": "#4CAF50",
        "Skeptic": "#F44336",
        "Analyst": "#2196F3",
        "Scout": "#FF9800",
        "Oracle": "#9C27B0"
    }
    
    for i, (agent, role) in enumerate(agents.items()):
        with agent_cols[i]:
            st.markdown(
                f"""
                <div style="background: white; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
                      padding: 1.2rem; margin-bottom: 1rem; text-align: center; min-height: 130px; 
                      border-top: 4px solid {agent_colors[agent]};">
                    <div style="font-size: 1.2rem; font-weight: 700; color: {agent_colors[agent]}; margin-bottom: 0.7rem;">{agent}</div>
                    <div style="color: #555; font-size: 0.9rem; line-height: 1.4;">{role}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    st.markdown("---")
    
    # Input methods
    input_method = st.radio(
        "Choose how to input startup information:",
        ["Select from database", "Enter manually"],
        horizontal=True
    )
    
    startup_details = ""
    
    if input_method == "Select from database":
        # Try to get startup names, handling potential errors
        try:
            # Detect the startup name column
            startup_name_col = None
            possible_columns = ["Startup_Name", "Organization Name", "Company", "Startup", "Name"]
            for col in possible_columns:
                if col in main_data.columns:
                    startup_name_col = col
                    break
            
            if startup_name_col:
                startup_names = main_data[startup_name_col].unique()
                selected_startup = st.selectbox("Select a startup", startup_names)
                
                # Only show details and set startup_details if a startup is selected
                if selected_startup and len(selected_startup.strip()) > 0:
                    # Get startup details
                    startup_row = main_data[main_data[startup_name_col] == selected_startup].iloc[0]
                    
                    # Detect key data columns
                    industry_col = next((col for col in ["Industry_Vertical", "Industry", "Sector"] if col in main_data.columns), None)
                    location_col = next((col for col in ["City_Location", "Location", "Headquarters"] if col in main_data.columns), None)
                    investors_col = next((col for col in ["Investors_Name", "Investors", "Backers"] if col in main_data.columns), None)
                    amount_col = next((col for col in ["Amount_in_USD", "Funding Amount", "Raised"] if col in main_data.columns), None)
                    
                    # Format the funding amount properly
                    if amount_col:
                        try:
                            funding_amount = float(str(startup_row[amount_col]).replace(',', ''))
                            funding_formatted = f"${funding_amount:,.0f}"
                        except:
                            funding_formatted = "Unknown"
                    else:
                        funding_formatted = "Unknown"
                    
                    # Build startup details based on available columns
                    startup_details = f"Startup Name: {selected_startup}\n"
                    
                    if industry_col:
                        startup_details += f"Industry: {startup_row[industry_col]}\n"
                    
                    if location_col:
                        startup_details += f"Location: {startup_row[location_col]}\n"
                    
                    startup_details += f"Funding: {funding_formatted}\n"
                    
                    if investors_col:
                        startup_details += f"Investors: {startup_row[investors_col]}\n"
                    
                    # Display startup details in a card with only available information
                    table_rows = ""
                    table_rows += f"""<tr>
                        <td style="padding: 0.5rem; color: #666; width: 120px;">Startup Name:</td>
                        <td style="padding: 0.5rem; font-weight: 600;">{selected_startup}</td>
                    </tr>"""
                    
                    if industry_col:
                        table_rows += f"""<tr>
                            <td style="padding: 0.5rem; color: #666;">Industry:</td>
                            <td style="padding: 0.5rem;">{startup_row[industry_col]}</td>
                        </tr>"""
                        
                    if location_col:
                        table_rows += f"""<tr>
                            <td style="padding: 0.5rem; color: #666;">Location:</td>
                            <td style="padding: 0.5rem;">{startup_row[location_col]}</td>
                        </tr>"""
                    
                    table_rows += f"""<tr>
                        <td style="padding: 0.5rem; color: #666;">Funding:</td>
                        <td style="padding: 0.5rem;">{funding_formatted}</td>
                    </tr>"""
                    
                    if investors_col:
                        table_rows += f"""<tr>
                            <td style="padding: 0.5rem; color: #666;">Investors:</td>
                            <td style="padding: 0.5rem;">{startup_row[investors_col]}</td>
                        </tr>"""
                    
                    st.markdown(
                        f"""
                        <div style="background: white; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
                              padding: 1.5rem; margin: 1.5rem 0;">
                            <h3 style="margin-bottom: 1rem; color: #333;">Selected Startup Details</h3>
                            <table style="width: 100%;">
                                {table_rows}
                            </table>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.warning("Startup data not found. Please enter startup details manually.")
        except Exception as e:
            st.warning(f"Error loading startup data: {e}. Please enter startup details manually.")
    else:
        # Manual input with better styling
        st.markdown(
            """
            <div style="margin: 1.5rem 0;">
                <h3 style="margin-bottom: 1rem; color: #333;">Enter Startup Details</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Startup Name")
            industry = st.text_input("Industry Vertical")
            location = st.text_input("Location (City)")
        
        with col2:
            funding = st.text_input("Funding Amount in USD")
            stage = st.text_input("Funding Stage (e.g. Series A)")
            investors = st.text_input("Key Investors")
        
        if name and industry:
            startup_details = f"""
            Startup Name: {name}
            Industry: {industry}
            Location: {location}
            Funding: ${funding}
            Stage: {stage}
            Investors: {investors}
            """
    
    # Initialize conversation state if not already present
    if 'council_conversation' not in st.session_state:
        st.session_state.council_conversation = []
    if 'council_analysis_done' not in st.session_state:
        st.session_state.council_analysis_done = False
    if 'agent_analyses' not in st.session_state:
        st.session_state.agent_analyses = {}
    if 'final_recommendation' not in st.session_state:
        st.session_state.final_recommendation = None
    
    # Function to get an AI agent response with advanced insights
    def get_agent_analysis(agent_name, perspective, startup_details, challenge=None):
        # Get basic analysis first
        base_result = simulate_ai_response(startup_details, agent_name, perspective)
        insight, score_line = base_result.split("\n")
        base_insight = insight.split(": ")[1]
        confidence_score = int(score_line.split(": ")[1])
        
        # Extract startup name for metadata
        startup_name = "Unnamed Startup"
        if startup_details:
            first_line = startup_details.split("\n")[0]
            if ":" in first_line:
                startup_name = first_line.split(": ")[1].strip()
        
        # Add more elaborate insights based on agent type
        agent_specific_insights = []
        
        if agent_name == "Visionary":
            agent_specific_insights = [
                "The company's technology shows potential for significant market disruption.",
                "Their leadership team has a track record of successful execution.",
                "The addressable market is growing rapidly, offering expansion opportunities."
            ]
            chart_type = "growth_projection"
            
        elif agent_name == "Skeptic":
            agent_specific_insights = [
                "Cash burn rate may be unsustainable without significant revenue growth.",
                "The competitive landscape is becoming increasingly crowded.",
                "There are regulatory challenges that could impact future operations."
            ]
            chart_type = "risk_assessment"
            
        elif agent_name == "Analyst":
            agent_specific_insights = [
                "The funding round timing aligns with market trends in this sector.",
                "Comparable startups have shown 30-40% annual growth after similar funding rounds.",
                "The unit economics appear sustainable based on available data."
            ]
            chart_type = "market_comparison"
            
        elif agent_name == "Scout":
            agent_specific_insights = [
                "The startup has unique technological advantages compared to key competitors.",
                "Their go-to-market strategy is differentiated in meaningful ways.",
                "There are gaps in their product offering compared to established players."
            ]
            chart_type = "competitive_analysis"
            
        elif agent_name == "Oracle":
            agent_specific_insights = [
                "Considering all factors, this represents a balanced risk-reward opportunity.",
                "The timing for this investment aligns with current market conditions.",
                "A staged investment approach would be advisable to mitigate potential downside."
            ]
            chart_type = "investment_recommendation"
        
        # If this is a challenge to the agent, generate a defense of their position
        if challenge:
            defense_responses = {
                "Visionary": [
                    "While risks exist, the upside potential still outweighs the downside scenarios.",
                    "Historical patterns show that early doubts about disruptive companies often prove unfounded.",
                    "The team's expertise specifically addresses the concerns you've raised."
                ],
                "Skeptic": [
                    "Optimism shouldn't overshadow the fundamental challenges in their business model.",
                    "Similar startups have faced these exact issues and struggled to overcome them.",
                    "The market conditions are more challenging than surface-level analysis suggests."
                ],
                "Analyst": [
                    "The data pattern is consistent across multiple similar cases in our database.",
                    "When controlling for market conditions, the metrics still indicate this conclusion.",
                    "Quantitative assessment shows these concerns are already priced into the valuation."
                ],
                "Scout": [
                    "Our competitive analysis includes emerging players that aren't yet widely tracked.",
                    "The differentiation factors have proven significant in analogous market segments.",
                    "The competitive landscape is shifting in ways that actually favor this company."
                ],
                "Oracle": [
                    "A balanced perspective requires acknowledging both the opportunities and challenges.",
                    "The recommendation accounts for both positive signals and concerning indicators.",
                    "Risk management suggests this approach provides optimal exposure to the opportunity."
                ]
            }
            
            # Select a random defense response
            response_to_challenge = random.choice(defense_responses[agent_name])
            
            # Adjust confidence slightly based on challenge
            confidence_adjustment = random.randint(-10, 5)
            adjusted_confidence = max(min(confidence_score + confidence_adjustment, 100), 20)
            
            return {
                "agent": agent_name,
                "base_insight": base_insight,
                "detailed_insights": agent_specific_insights,
                "challenge_response": response_to_challenge,
                "confidence": adjusted_confidence,
                "chart_type": chart_type,
                "metadata": {
                    "Startup": startup_name
                }
            }
        
        return {
            "agent": agent_name,
            "base_insight": base_insight,
            "detailed_insights": agent_specific_insights,
            "confidence": confidence_score,
            "chart_type": chart_type,
            "metadata": {
                "Startup": startup_name
            }
        }
    
    # Function to generate mock charts based on agent
    def generate_agent_chart(agent, startup_name):
        fig, ax = plt.subplots(figsize=(10, 5))
        
        if agent["chart_type"] == "growth_projection":
            # Growth projection chart
            years = np.array([2023, 2024, 2025, 2026, 2027])
            optimistic = np.array([1, 2.5, 5, 8, 12])
            realistic = np.array([1, 2, 3.5, 5, 7])
            conservative = np.array([1, 1.5, 2, 3, 4])
            
            ax.plot(years, optimistic, 'g-', linewidth=3, label='Optimistic')
            ax.plot(years, realistic, 'b--', linewidth=2, label='Realistic')
            ax.plot(years, conservative, 'r:', linewidth=2, label='Conservative')
            ax.set_title(f"Growth Projection for {startup_name}", fontsize=14)
            ax.set_xlabel("Year", fontsize=12)
            ax.set_ylabel("Projected Growth Multiple", fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend()
            
        elif agent["chart_type"] == "risk_assessment":
            # Risk assessment radar chart
            categories = ['Market', 'Competition', 'Execution', 'Financial', 'Regulatory']
            values = np.random.randint(25, 85, size=5)
            
            # Create radar chart
            angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
            values = values.tolist()
            values += values[:1]  # Close the loop
            angles += angles[:1]  # Close the loop
            categories += categories[:1]  # Close the loop
            
            ax.plot(angles, values, 'r-', linewidth=2)
            ax.fill(angles, values, 'r', alpha=0.2)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories[:-1])
            ax.set_yticks([20, 40, 60, 80, 100])
            ax.set_title(f"Risk Assessment for {startup_name}", fontsize=14)
            ax.grid(True, alpha=0.3)
            
        elif agent["chart_type"] == "market_comparison":
            # Market comparison chart
            competitors = ['Competitor A', 'Competitor B', 'Competitor C', startup_name, 'Competitor D']
            metrics = np.random.randint(30, 90, size=5)
            
            # Make the startup's bar stand out
            colors = ['#3498db', '#3498db', '#3498db', '#e74c3c', '#3498db']
            
            bars = ax.bar(competitors, metrics, color=colors)
            ax.set_title(f"Market Position Comparison", fontsize=14)
            ax.set_ylabel("Market Position Score", fontsize=12)
            ax.set_ylim(0, 100)
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                        f'{height:.0f}', ha='center', fontsize=10)
            
        elif agent["chart_type"] == "competitive_analysis":
            # Competitive analysis chart - bubble chart
            x = np.random.randint(20, 80, size=5)
            y = np.random.randint(20, 80, size=5)
            size = np.random.randint(100, 1000, size=5)
            companies = ['Competitor A', 'Competitor B', startup_name, 'Competitor C', 'Competitor D']
            colors = ['#3498db', '#3498db', '#e74c3c', '#3498db', '#3498db']
            
            scatter = ax.scatter(x, y, s=size, c=colors, alpha=0.6)
            ax.set_title(f"Competitive Positioning", fontsize=14)
            ax.set_xlabel("Market Innovation", fontsize=12)
            ax.set_ylabel("Market Share", fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.set_xlim(0, 100)
            ax.set_ylim(0, 100)
            
            # Add labels for each point
            for i, company in enumerate(companies):
                ax.annotate(company, (x[i], y[i]), xytext=(5, 5), textcoords='offset points')
            
        elif agent["chart_type"] == "investment_recommendation":
            # Investment recommendation chart
            categories = ['Return Potential', 'Risk Level', 'Market Timing', 'Team Strength', 'Innovation']
            values = np.random.randint(40, 90, size=5)
            
            # Create radar chart
            angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
            values = values.tolist()
            values += values[:1]  # Close the loop
            angles += angles[:1]  # Close the loop
            categories += categories[:1]  # Close the loop
            
            ax.plot(angles, values, 'g-', linewidth=2)
            ax.fill(angles, values, 'g', alpha=0.2)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories[:-1])
            ax.set_yticks([20, 40, 60, 80, 100])
            ax.set_title(f"Investment Factors Analysis for {startup_name}", fontsize=14)
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    # Function to calculate the overall investment recommendation
    def calculate_overall_recommendation(agent_analyses):
        # Extract the confidence scores
        total_confidence = 0
        weighted_score = 0
        
        # Assign weights to different agents
        weights = {
            "Visionary": 0.2,
            "Skeptic": 0.2,
            "Analyst": 0.25,
            "Scout": 0.15,
            "Oracle": 0.2
        }
        
        for agent_name, analysis in agent_analyses.items():
            confidence = analysis["confidence"]
            # Convert confidence to a score from 0-100, where higher is more positive
            if agent_name == "Skeptic":
                # Invert the skeptic's confidence since high confidence means more negative
                score = 100 - confidence
            else:
                score = confidence
            
            weighted_score += score * weights[agent_name]
            total_confidence += weights[agent_name]
        
        # Calculate final score
        if total_confidence > 0:
            final_score = weighted_score / total_confidence
        else:
            final_score = 50  # Neutral if no analyses
        
        # Determine recommendation
        if final_score >= 70:
            recommendation = "Invest"
            color = "#4CAF50"  # Green
        elif final_score >= 45:
            recommendation = "Wait"
            color = "#FFC107"  # Yellow
        else:
            recommendation = "Avoid"
            color = "#F44336"  # Red
        
        return {
            "score": final_score,
            "recommendation": recommendation,
            "color": color
        }
    
    # Analyze button
    if st.button("Get AI Investment Council Recommendations") and startup_details:
        # Reset previous analyses
        st.session_state.council_conversation = []
        st.session_state.agent_analyses = {}
        st.session_state.council_analysis_done = False
        st.session_state.final_recommendation = None
        
        # Extract startup name for charts
        startup_name = startup_details.split("\n")[0].split(": ")[1] if ":" in startup_details.split("\n")[0] else "Startup"
        
        # Set up the analysis area
        st.markdown("### 📝 Investment Council Analysis")
        analysis_placeholder = st.empty()
        
        # Create a placeholder for each agent
        agent_placeholders = {}
        for agent_name in agents.keys():
            agent_placeholders[agent_name] = st.empty()
        
        # Placeholder for the final recommendation
        final_recommendation_placeholder = st.empty()
        
        # Animate the analysis for each agent
        with analysis_placeholder.container():
            for agent_name, perspective in agents.items():
                color = agent_colors[agent_name]
                
                # Show loading animation
                with agent_placeholders[agent_name].container():
                    st.markdown(
                        f"""
                        <div style="margin-bottom:20px; padding:15px; border-radius:5px; border:1px solid {color};">
                            <h4 style="color:{color};">{agent_name}</h4>
                            <p>Analyzing startup data...</p>
                            <div style="display: flex; justify-content: center; margin: 20px 0;">
                                <div class="loader"></div>
                            </div>
                            <style>
                                .loader {{
                                    border: 5px solid #f3f3f3;
                                    border-top: 5px solid {color};
                                    border-radius: 50%;
                                    width: 50px;
                                    height: 50px;
                                    animation: spin 1s linear infinite;
                                }}
                                @keyframes spin {{
                                    0% {{ transform: rotate(0deg); }}
                                    100% {{ transform: rotate(360deg); }}
                                }}
                            </style>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                # Simulate analysis delay
                time.sleep(1.5)
                
                # Get agent analysis
                agent_analysis = get_agent_analysis(agent_name, perspective, startup_details)
                st.session_state.agent_analyses[agent_name] = agent_analysis
                
                # Generate chart for this agent
                fig = generate_agent_chart(agent_analysis, startup_name)
                
                # Display the analysis
                with agent_placeholders[agent_name].container():
                    col1, col2 = st.columns([3, 2])
                    
                    with col1:
                        # Create a container for the agent insights with better alignment
                        st.markdown(
                            f"""
                            <div style="margin-bottom:20px; padding:20px; border-radius:5px; border:1px solid {color}; height: 100%;">
                                <h4 style="color:{color}; margin-top: 0;">{agent_name}</h4>
                                <p style="font-weight: 600; margin-bottom: 10px;">{agent_analysis['base_insight']}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        # Use Streamlit native expander instead of JavaScript
                        with st.expander("Show Detailed Insights", expanded=False):
                            for insight in agent_analysis['detailed_insights']:
                                st.markdown(f"• {insight}")
                        
                        # Show confidence score
                        st.progress(agent_analysis['confidence']/100.0, f"Confidence: {agent_analysis['confidence']}%")
                    
                    with col2:
                        st.pyplot(fig)
                    
                    # Remove challenge section
        
        # Mark analysis as complete
        st.session_state.council_analysis_done = True
        
        # Remove challenge handling - we're simplifying the interface
        # Check if there's a challenge to process
        if st.session_state.active_challenge["is_submitted"]:
            st.session_state.active_challenge = {
                "agent": None,
                "challenge_text": None,
                "is_submitted": False
            }
        
        # Calculate final recommendation
        final_rec = calculate_overall_recommendation(st.session_state.agent_analyses)
        st.session_state.final_recommendation = final_rec
        
        # Display the final recommendation
        with final_recommendation_placeholder.container():
            st.markdown("### 🎯 Overall Investment Recommendation")
            
            # Create a recommendation card with appropriate color
            st.markdown(
                f"""
                <div style="margin: 30px 0; padding: 30px; border-radius: 10px; background-color: white; 
                      box-shadow: 0 4px 20px rgba(0,0,0,0.1); text-align: center; border: 2px solid {final_rec['color']};">
                    <h2 style="color: {final_rec['color']}; font-weight: 700; font-size: 2.5rem; margin-bottom: 10px;">
                        {final_rec['recommendation']}
                    </h2>
                    <div style="background-color: #f0f0f0; height: 15px; border-radius: 10px; margin: 20px auto; max-width: 400px;">
                        <div style="background-color: {final_rec['color']}; width: {final_rec['score']}%; height: 15px; border-radius: 10px;"></div>
                    </div>
                    <p style="color: #555; font-size: 1.2rem;">
                        Investment confidence score: {final_rec['score']:.1f}%
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Extract startup name for portfolio - use the value from the recommendation for persistence
            startup_name = ""
            # First try to get from startup_details if available
            if 'startup_details' in locals() and startup_details:
                first_line = startup_details.split("\n")[0]
                if ":" in first_line:
                    startup_name = first_line.split(": ")[1].strip()
            
            # If not found, try to extract from agent analyses
            if not startup_name:
                for k, v in st.session_state.agent_analyses.items():
                    # Try to extract from Oracle or any other agent's metadata
                    if "metadata" in v and "Startup" in v["metadata"]:
                        startup_name = v["metadata"]["Startup"]
                        break
            
            if not startup_name:
                startup_name = "Unnamed Startup"
                
            # Add portfolio action buttons based on recommendation
            st.markdown("### Update Your Portfolio")
            
            if final_rec['recommendation'] == "Invest":
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Add to Portfolio", key="invest_rec_btn", use_container_width=True):
                        # Add to portfolio with positive sentiment
                        portfolio_entry = {
                            "Startup": startup_name,
                            "Industry": "Technology",  # Default
                            "Amount Invested": 100000,
                            "Confidence Score": final_rec['score'],
                            "Sentiment": "Positive",
                            "Expected ROI (%)": 30.0,
                            "Expected Return": 30000,
                            "Projected Value": 130000,
                            "Date Added": datetime.now().strftime("%Y-%m-%d")
                        }
                        st.session_state.portfolio.append(portfolio_entry)
                        st.success(f"✅ Added {startup_name} to your portfolio with an Invest recommendation!")
                        # Set the newly added flag for Portfolio Management
                        st.session_state.newly_added_startup = startup_name
                        # Show guidance for viewing the portfolio
                        st.info("💡 Go to the Portfolio Management page to see your investments.")
                        # Add a button to view portfolio
                        if st.button("View Portfolio", key="view_portfolio_btn"):
                            # Set the page in session state to trigger navigation
                            st.session_state.page = "Portfolio Management"
                            st.rerun()
                
                with col2:
                    if st.button("Ignore Recommendation", key="ignore_invest_btn", use_container_width=True):
                        st.info("Recommendation ignored.")
            
            elif final_rec['recommendation'] == "Wait":
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Add to Watchlist", key="wait_rec_btn", use_container_width=True):
                        # Add to portfolio with neutral sentiment
                        portfolio_entry = {
                            "Startup": startup_name,
                            "Industry": "Technology",  # Default
                            "Amount Invested": 50000,
                            "Confidence Score": final_rec['score'],
                            "Sentiment": "Neutral",
                            "Expected ROI (%)": 15.0,
                            "Expected Return": 7500,
                            "Projected Value": 57500,
                            "Date Added": datetime.now().strftime("%Y-%m-%d")
                        }
                        st.session_state.portfolio.append(portfolio_entry)
                        st.info(f"⏳ Added {startup_name} to your watchlist with a Wait recommendation.")
                        # Set the newly added flag for Portfolio Management
                        st.session_state.newly_added_startup = startup_name
                        # Show guidance for viewing the portfolio
                        st.info("💡 Go to the Portfolio Management page to see your investments.")
                        # Add a button to view portfolio
                        if st.button("View Portfolio", key="view_portfolio_wait_btn"):
                            # Set the page in session state to trigger navigation
                            st.session_state.page = "Portfolio Management"
                            st.rerun()
                
                with col2:
                    if st.button("Ignore Recommendation", key="ignore_wait_btn", use_container_width=True):
                        st.info("Recommendation ignored.")
            
            else:  # Avoid
                if st.button("Mark as 'Avoid'", key="avoid_rec_btn", use_container_width=True):
                    st.warning(f"⛔ Marked {startup_name} as 'Avoid' - not added to portfolio.")
            
            # Generate summary insights from all agents
            st.markdown("### Key Insights Summary")
            
            # Extract one insight from each agent
            summary_insights = []
            for agent_name, analysis in st.session_state.agent_analyses.items():
                if analysis["detailed_insights"]:
                    # Pick the first insight
                    summary_insights.append({
                        "agent": agent_name,
                        "color": agent_colors[agent_name],
                        "insight": analysis["detailed_insights"][0]
                    })
            
            # Display the insights in two columns
            cols = st.columns(2)
            for i, insight in enumerate(summary_insights):
                with cols[i % 2]:
                    st.markdown(
                        f"""
                        <div style="margin-bottom: 15px; padding: 15px; border-radius: 5px; background-color: white; 
                              box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-left: 4px solid {insight['color']};">
                            <p style="color: {insight['color']}; font-weight: 600; margin-bottom: 5px;">
                                {insight['agent']}
                            </p>
                            <p style="color: #555;">
                                {insight['insight']}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    # Display conversation history
    elif st.session_state.council_analysis_done:
        # Show the final recommendation
        if st.session_state.final_recommendation:
            final_rec = st.session_state.final_recommendation
            
            st.markdown("### 🎯 Overall Investment Recommendation")
            
            # Create a recommendation card with appropriate color
            st.markdown(
                f"""
                <div style="margin: 30px 0; padding: 30px; border-radius: 10px; background-color: white; 
                      box-shadow: 0 4px 20px rgba(0,0,0,0.1); text-align: center; border: 2px solid {final_rec['color']};">
                    <h2 style="color: {final_rec['color']}; font-weight: 700; font-size: 2.5rem; margin-bottom: 10px;">
                        {final_rec['recommendation']}
                    </h2>
                    <div style="background-color: #f0f0f0; height: 15px; border-radius: 10px; margin: 20px auto; max-width: 400px;">
                        <div style="background-color: {final_rec['color']}; width: {final_rec['score']}%; height: 15px; border-radius: 10px;"></div>
                    </div>
                    <p style="color: #555; font-size: 1.2rem;">
                        Investment confidence score: {final_rec['score']:.1f}%
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Show conversation history
        if st.session_state.council_conversation:
            st.markdown("### Conversation History")
            
            # This section can be removed since we no longer have challenges
            st.session_state.council_conversation = []