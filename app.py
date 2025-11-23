import os
import requests
import openai
import streamlit as st
import json
import pandas as pd
import base64
import re
from datetime import datetime

# Correct import statements - FIXED THE TYPOS
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("Plotly not available. Charts will be disabled.")

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# --------------------------
# BASIC CONFIG
# --------------------------
st.set_page_config(
    page_title="Multi-User Company Research Assistant", 
    page_icon="👥",
    layout="wide"
)

st.title("👥 Advanced Company Research Assistant")
st.write("💬 **Multi-persona analytics with visual insights and data-driven recommendations**")

# --------------------------
# API KEYS
# --------------------------
api_key = st.secrets.get("OPENAI_API_KEY", "")

if not api_key:
    st.warning(
        "No API key found. Please add your OpenRouter API key to secrets.toml"
    )
else:
    openai.api_key = api_key
    openai.api_base = "https://openrouter.ai/api/v1"

# --------------------------
# USER PERSONAS CONFIGURATION
# --------------------------
USER_PERSONAS = {
    "sales_executive": {
        "name": "Sales Executive",
        "description": "Focuses on revenue opportunities and sales strategies",
        "priorities": ["revenue growth", "client acquisition", "sales metrics"],
        "icon": "💰"
    },
    "market_researcher": {
        "name": "Market Researcher", 
        "description": "Focuses on market trends and competitive analysis",
        "priorities": ["market share", "industry trends", "competitive landscape"],
        "icon": "📊"
    },
    "financial_analyst": {
        "name": "Financial Analyst",
        "description": "Focuses on financial metrics and ROI analysis", 
        "priorities": ["financial performance", "ROI analysis", "risk assessment"],
        "icon": "💹"
    },
    "strategic_planner": {
        "name": "Strategic Planner",
        "description": "Focuses on long-term strategy and growth opportunities",
        "priorities": ["strategic initiatives", "growth opportunities", "market positioning"],
        "icon": "🛣️"
    },
    "product_manager": {
        "name": "Product Manager",
        "description": "Focuses on product opportunities and feature analysis",
        "priorities": ["product-market fit", "feature analysis", "customer needs"],
        "icon": "🎯"
    }
}

# --------------------------
# SESSION STATE
# --------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 **Welcome!** I'm your multi-persona Company Research Assistant. Select your role from the sidebar to get started with customized insights!"}
    ]

if "current_persona" not in st.session_state:
    st.session_state.current_persona = "sales_executive"

if "research_data" not in st.session_state:
    st.session_state.research_data = {}

# --------------------------
# VISUALIZATION FUNCTIONS
# --------------------------
def create_persona_chart(persona_key):
    """Create persona-specific visualizations"""
    if not PLOTLY_AVAILABLE:
        return None
        
    try:
        if persona_key == "sales_executive":
            fig = go.Figure(go.Funnel(
                y = ['Leads', 'MQLs', 'SQLs', 'Opportunities', 'Closed Won'],
                x = [1000, 800, 400, 200, 80],
                textinfo = "value+percent initial",
                marker = {"color": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]}
            ))
            fig.update_layout(
                title = "💰 Sales Funnel Performance",
                height = 400
            )
            
        elif persona_key == "market_researcher":
            categories = ['Market Share', 'Growth Rate', 'Customer Sat', 'Brand Awareness']
            values = [25, 18, 82, 65]
            
            fig = go.Figure(data=go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                fillcolor = 'rgba(31, 119, 180, 0.5)',
                line = dict(color = 'rgb(31, 119, 180)')
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100])
                ),
                title = "📊 Market Position Analysis",
                height = 400
            )
            
        elif persona_key == "financial_analyst":
            years = ['2022', '2023', '2024', '2025']
            revenue = [500, 650, 820, 1050]
            profit = [75, 110, 160, 220]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Revenue ($M)', x=years, y=revenue, marker_color='#2ca02c'))
            fig.add_trace(go.Bar(name='Profit ($M)', x=years, y=profit, marker_color='#1f77b4'))
            fig.update_layout(
                title = "💹 Financial Performance",
                barmode = 'group',
                height = 400
            )
            
        elif persona_key == "strategic_planner":
            phases = ['Foundation', 'Growth', 'Expansion', 'Leadership']
            resources = [1, 2, 2, 1]
            
            fig = go.Figure(go.Waterfall(
                name = "Strategic Roadmap",
                orientation = "v",
                measure = ["relative", "relative", "relative", "total"],
                x = phases,
                y = resources,
                connector = {"line": {"color": "rgb(63, 63, 63)"}},
            ))
            fig.update_layout(
                title = "🛣️ Strategic Implementation Timeline",
                height = 400
            )
            
        else:  # product_manager
            features = ['Feature A', 'Feature B', 'Feature C', 'Feature D']
            impact = [85, 70, 60, 45]
            effort = [30, 50, 70, 40]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=effort, 
                y=impact, 
                text=features, 
                mode='markers+text',
                marker=dict(
                    size=20,
                    color=impact,
                    colorscale='Viridis',
                    showscale=True
                )
            ))
            fig.update_layout(
                title = "🎯 Feature Impact vs Effort Analysis",
                xaxis_title = "Implementation Effort",
                yaxis_title = "Business Impact",
                height = 400
            )
            
        return fig
        
    except Exception as e:
        st.error(f"Chart error: {str(e)}")
        return None

# --------------------------
# DATA FUNCTIONS
# --------------------------
def create_persona_data(persona_key):
    """Create persona-specific data tables"""
    if persona_key == "sales_executive":
        data = {
            'Metric': ['Pipeline Value', 'Conversion Rate', 'Avg Deal Size', 'Sales Cycle'],
            'Value': ['$2.5M', '22%', '$125K', '67 days'],
            'Target': ['$3.0M', '25%', '$140K', '60 days']
        }
    elif persona_key == "market_researcher":
        data = {
            'Metric': ['Market Size', 'Growth Rate', 'Market Share', 'Competitors'],
            'Value': ['$15B', '18%', '12%', '8 major'],
            'Trend': ['Growing', 'Accelerating', 'Increasing', 'Consolidating']
        }
    elif persona_key == "financial_analyst":
        data = {
            'Metric': ['Revenue', 'Profit Margin', 'ROI', 'Valuation'],
            'Value': ['$850M', '18.5%', '22%', '$4.2B'],
            'YoY Growth': ['+24%', '+2.1%', '+3.5%', '+28%']
        }
    elif persona_key == "strategic_planner":
        data = {
            'Initiative': ['Market Expansion', 'Product Innovation', 'Digital Transformation'],
            'Timeline': ['6-12 months', '12-18 months', '18-24 months'],
            'Investment': ['$5M', '$8M', '$12M'],
            'ROI Potential': ['35%', '42%', '28%']
        }
    else:  # product_manager
        data = {
            'Feature': ['AI Integration', 'Mobile App', 'API Access', 'Analytics'],
            'User Impact': ['High', 'Medium', 'Low', 'High'],
            'Development Effort': ['High', 'Medium', 'Low', 'Medium'],
            'Priority': ['P0', 'P1', 'P2', 'P0']
        }
    
    return pd.DataFrame(data)

# --------------------------
# AI RESPONSE FUNCTION
# --------------------------
def generate_ai_response(user_input, persona_key):
    """Generate AI response based on persona"""
    persona = USER_PERSONAS[persona_key]
    
    prompts = {
        "sales_executive": "You are a sales executive. Focus on revenue opportunities, sales metrics, pipeline value, conversion rates, and actionable sales strategies. Provide specific numbers and revenue projections.",
        "market_researcher": "You are a market researcher. Focus on market size, growth rates, competitive analysis, consumer trends, and market share data. Provide comprehensive market intelligence.",
        "financial_analyst": "You are a financial analyst. Focus on financial metrics, ROI calculations, risk assessment, valuation, and investment recommendations. Provide precise financial numbers.",
        "strategic_planner": "You are a strategic planner. Focus on long-term strategy, growth opportunities, strategic initiatives, and implementation roadmaps. Provide forward-looking insights.",
        "product_manager": "You are a product manager. Focus on product opportunities, feature analysis, user needs, and product roadmap. Provide user-centric recommendations."
    }
    
    system_prompt = f"{prompts[persona_key]}\n\nAlways provide specific numbers, metrics, and data-driven insights. Use the persona's focus areas: {', '.join(persona['priorities'])}"
    
    try:
        if api_key:
            response = openai.ChatCompletion.create(
                model="mistralai/mixtral-8x7b-instruct",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            return response.choices[0].message.content
        else:
            # Fallback response if no API key
            return f"**{persona['name']} Analysis:** As a {persona['name'].lower()}, I would analyze this focusing on {persona['priorities'][0]}. Based on typical industry data:\n\n- **Key Metric:** 15-25% growth potential\n- **Opportunity Size:** $2-5M addressable market\n- **Implementation Timeline:** 6-12 months\n- **Success Probability:** 70-80%\n\n*Note: Add your OpenRouter API key to secrets.toml for AI-powered analysis*"
            
    except Exception as e:
        return f"**Analysis:** I encountered an error processing your request. Error: {str(e)}"

# --------------------------
# SIDEBAR - PERSONA SELECTION
# --------------------------
st.sidebar.header("👥 Select Your Role")

# Persona selection with icons
selected_persona = st.sidebar.radio(
    "Choose your persona:",
    options=list(USER_PERSONAS.keys()),
    format_func=lambda x: f"{USER_PERSONAS[x]['icon']} {USER_PERSONAS[x]['name']}",
    key="persona_selector"
)

# Update current persona
if selected_persona != st.session_state.current_persona:
    st.session_state.current_persona = selected_persona
    st.session_state.messages.append({
        "role": "assistant", 
        "content": f"🔄 **Switched to {USER_PERSONAS[selected_persona]['icon']} {USER_PERSONAS[selected_persona]['name']} Mode**\n\n*{USER_PERSONAS[selected_persona]['description']}*\n\n**Focus areas:** {', '.join(USER_PERSONAS[selected_persona]['priorities'])}"
    })

# Current persona info
current_persona = USER_PERSONAS[st.session_state.current_persona]
st.sidebar.success(f"**Active Role:** {current_persona['icon']} {current_persona['name']}")

# --------------------------
# MAIN CHAT INTERFACE
# --------------------------
st.header(f"{current_persona['icon']} {current_persona['name']} Conversation")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Display data visualization
st.subheader("📈 Persona-Specific Analytics")

col1, col2 = st.columns([2, 1])

with col1:
    # Show chart if available
    if PLOTLY_AVAILABLE:
        chart = create_persona_chart(st.session_state.current_persona)
        if chart:
            st.plotly_chart(chart, use_container_width=True)
    else:
        st.info("📊 *Install plotly for interactive charts: `pip install plotly`*")

with col2:
    # Show data table
    data_df = create_persona_data(st.session_state.current_persona)
    st.dataframe(data_df, use_container_width=True, height=300)

# --------------------------
# CHAT INPUT
# --------------------------
user_input = st.chat_input(f"Ask as {current_persona['name']}...")

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Generate and display response
    with st.chat_message("assistant"):
        with st.spinner(f"🔍 {current_persona['icon']} Analyzing..."):
            response = generate_ai_response(user_input, st.session_state.current_persona)
            st.markdown(response)
            
            # Add visualization for relevant responses
            if any(keyword in user_input.lower() for keyword in ['analyze', 'research', 'data', 'metrics']):
                if PLOTLY_AVAILABLE:
                    chart = create_persona_chart(st.session_state.current_persona)
                    if chart:
                        st.plotly_chart(chart, use_container_width=True)
                
                # Show additional data
                data_df = create_persona_data(st.session_state.current_persona)
                st.dataframe(data_df, use_container_width=True)
    
    # Add assistant message to history
    st.session_state.messages.append({"role": "assistant", "content": response})

# --------------------------
# INSTALLATION HELP
# --------------------------
with st.sidebar.expander("🔧 Installation Help"):
    st.write("""
    **If you see import errors, run in terminal:**
    ```bash
    pip install plotly matplotlib pandas streamlit openai requests
    ```
    
    **For Windows permissions issues:**
    ```bash
    pip install --user plotly matplotlib pandas streamlit openai requests
    ```
    """)

# --------------------------
# FOOTER
# --------------------------
st.markdown("---")
st.markdown(
    f"💡 **{current_persona['icon']} {current_persona['name']} Tip**: Focus on **{current_persona['priorities'][0]}** "
    f"and **{current_persona['priorities'][1]}** for maximum impact!"
)