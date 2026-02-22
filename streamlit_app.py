import streamlit as st
import pandas as pd
from recommender import recommend, df
import plotly.graph_objects as go
import plotly.express as px
from collections import Counter

st.set_page_config(
    page_title="E-commerce Recommendation System",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
        .main {
            padding: 2rem;
        }
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 10px;
            color: white;
            text-align: center;
        }
        .recommendation-card {
            background: #f8f9fa;
            padding: 1.2rem;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            margin: 0.5rem 0;
        }
        .header-title {
            color: #667eea;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .subheader {
            color: #666;
            font-size: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/shopping-cart.png", width=80)
    st.title("🛍️ Recommendation Engine")
    st.divider()
    
    page = st.radio(
        "Navigate",
        ["Home", "Make Recommendation", "Customer Analytics", "System Stats"]
    )

# Home Page
if page == "Home":
    st.markdown('<div class="header-title">E-commerce Recommendation System</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader">Powered by Hybrid Collaborative Filtering</div>', unsafe_allow_html=True)
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Customers", len(df["Customer ID"].unique()), delta="Active")
    
    with col2:
        st.metric("Total Records", len(df), delta="In Database")
    
    with col3:
        st.metric("Categories", len(set([cat for cats in df["Purchase History"].apply(
            lambda x: [item.get("Product Category") or item.get("Category") for item in x if isinstance(x, list)] or []
        ).values for cat in cats])), delta="Available")
    
    st.divider()
    
    st.subheader("✨ How It Works")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**Step 1: Analyze**\nFind customer's favorite product category")
    
    with col2:
        st.info("**Step 2: Match**\nIdentify similar customers in that category")
    
    with col3:
        st.info("**Step 3: Recommend**\nSuggest top-rated customers with high ratings")
    
    st.divider()
    
    st.subheader("📌 Features")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        - 🎯 Personalized Recommendations
        - 📊 Real-time Analytics
        - 🔍 Advanced Search
        - 💾 MongoDB Integration
        """)
    
    with col2:
        st.markdown("""
        - ⚡ Fast Processing
        - 🛡️ Error Handling
        - 📈 Performance Metrics
        - 🌐 Scalable Architecture
        """)

# Make Recommendation Page
elif page == "Make Recommendation":
    st.markdown('<div class="header-title">Get Personalized Recommendations</div>', unsafe_allow_html=True)
    st.divider()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        customer_id = st.number_input(
            "Enter Customer ID",
            min_value=1001,
            max_value=1050,
            value=1001,
            step=1,
            help="Select a customer ID between 1001-1050"
        )
    
    with col2:
        search_button = st.button("🔍 Get Recommendations", use_container_width=True)
    
    if search_button or customer_id:
        with st.spinner("🔄 Fetching recommendations..."):
            result = recommend(customer_id)
        
        if "error" in result:
            st.error(f"❌ {result['error']}")
        elif "message" in result and "No purchase history" in result["message"]:
            st.warning(f"⚠️ {result['message']}")
        else:
            # Display customer info
            customer_data = df[df["Customer ID"] == customer_id]
            
            if not customer_data.empty:
                col1, col2, col3, col4 = st.columns(4)
                
                cust = customer_data.iloc[0]
                with col1:
                    st.metric("Customer ID", customer_id)
                with col2:
                    st.metric("Age", int(cust.get("Age", 0)))
                with col3:
                    st.metric("Annual Income", f"${int(cust.get('Annual Income', 0)):,}")
                with col4:
                    st.metric("Location", cust.get("Location", "N/A"))
            
            st.divider()
            
            # Display favorite category
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("🎯 Favorite Category")
                st.info(f"**{result['Favorite Category']}**")
            
            with col2:
                st.subheader("⭐ Recommendations")
            
            st.divider()
            
            # Display recommendations
            recommendations = result.get("Top Recommendations", [])
            
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    col1, col2, col3 = st.columns([1, 2, 2])
                    
                    with col1:
                        st.metric(f"#{i}", f"ID {rec['Customer ID']}")
                    
                    with col2:
                        rating_stars = "⭐" * int(rec["Rating"]) if rec["Rating"] else "N/A"
                        st.markdown(f"**Rating:** {rating_stars} ({rec['Rating']}/5.0)")
                    
                    with col3:
                        income = rec.get("Income", 0)
                        st.markdown(f"**Annual Income:** ${income:,}")
                    
                    st.markdown("---")
            else:
                st.info("No recommendations available for this customer in their favorite category.")

# Customer Analytics Page
elif page == "Customer Analytics":
    st.markdown('<div class="header-title">Customer Analytics & Insights</div>', unsafe_allow_html=True)
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Category distribution
        all_categories = []
        for hist in df["Purchase History"]:
            if isinstance(hist, list):
                for item in hist:
                    cat = item.get("Product Category") or item.get("Category")
                    if cat:
                        all_categories.append(cat)
        
        category_counts = Counter(all_categories)
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(category_counts.keys()),
                y=list(category_counts.values()),
                marker=dict(color=['#667eea', '#764ba2', '#f093fb', '#4facfe'])
            )
        ])
        fig.update_layout(
            title="Purchase Distribution by Category",
            xaxis_title="Category",
            yaxis_title="Count",
            height=400,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Age distribution
        fig = go.Figure(data=[
            go.Histogram(
                x=df["Age"].dropna(),
                nbinsx=15,
                marker=dict(color='#667eea')
            )
        ])
        fig.update_layout(
            title="Age Distribution of Customers",
            xaxis_title="Age",
            yaxis_title="Count",
            height=400,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Income distribution
        fig = go.Figure(data=[
            go.Box(
                y=df["Annual Income"].dropna(),
                marker=dict(color='#764ba2'),
                boxmean='sd'
            )
        ])
        fig.update_layout(
            title="Annual Income Distribution",
            yaxis_title="Income ($)",
            height=400,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Time on site
        fig = go.Figure(data=[
            go.Scatter(
                y=df["Time on Site"].dropna(),
                mode='markers',
                marker=dict(
                    size=df["Annual Income"].dropna() / 10000,
                    color=df["Time on Site"].dropna(),
                    colorscale='Viridis',
                    showscale=True
                ),
                text=df["Customer ID"],
                hovertemplate="<b>Customer %{text}</b><br>Time: %{y:.2f}h"
            )
        ])
        fig.update_layout(
            title="Time on Site vs Customer ID",
            yaxis_title="Time (hours)",
            height=400,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

# System Stats Page
elif page == "System Stats":
    st.markdown('<div class="header-title">System Statistics & Performance</div>', unsafe_allow_html=True)
    st.divider()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Customers", len(df["Customer ID"].unique()), delta="+50 active")
    
    with col2:
        st.metric("Avg Age", f"{df['Age'].mean():.1f}", delta="+2.3 yrs")
    
    with col3:
        st.metric("Avg Income", f"${df['Annual Income'].mean():,.0f}", delta="+$5K")
    
    with col4:
        st.metric("Avg Time", f"{df['Time on Site'].mean():.1f}h", delta="+1.2h")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Data Quality")
        quality_metrics = {
            "Complete Records": f"{(df.notna().sum().sum() / (len(df) * len(df.columns)) * 100):.1f}%",
            "Customers": f"{len(df['Customer ID'].unique())}",
            "Total Entries": f"{len(df)}",
            "Features": f"{len(df.columns)}"
        }
        
        for metric, value in quality_metrics.items():
            st.write(f"**{metric}:** {value}")
    
    with col2:
        st.subheader("🎯 Recommendation Coverage")
        
        successful_recs = 0
        total_customers = len(df["Customer ID"].unique())
        
        for cid in df["Customer ID"].unique()[:10]:  # Sample 10
            result = recommend(cid)
            if "error" not in result and "message" not in result:
                successful_recs += 1
        
        coverage = (successful_recs / 10) * 100
        
        fig = go.Figure(data=[
            go.Indicator(
                mode="gauge+number+delta",
                value=coverage,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Success Rate"},
                gauge=dict(
                    axis=dict(range=[0, 100]),
                    bar=dict(color="#667eea"),
                    steps=[
                        {'range': [0, 50], 'color': "#f0f0f0"},
                        {'range': [50, 100], 'color': "#e8f5e9"}
                    ]
                )
            )
        ])
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    st.subheader("📊 Sample Data")
    st.dataframe(df[["Customer ID", "Age", "Gender", "Location", "Annual Income", "Time on Site"]].head(10))

# Footer
st.divider()
st.markdown("""
---
<div style='text-align: center; color: #999; font-size: 0.85rem;'>
    <p>🛍️ E-commerce Recommendation System | Powered by Streamlit & MongoDB</p>
    <p>Built with ❤️ for personalized shopping experiences</p>
</div>
""", unsafe_allow_html=True)
