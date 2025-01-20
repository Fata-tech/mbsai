import streamlit as st
import openai
import yfinance as yf
import pandas as pd

class MiningBusinessAnalyst:
    def __init__(self, api_key):
        openai.api_key = api_key
        
    def analyze_query(self, query, context=""):
        try:
            system_prompt = f"""You are an expert mining business analyst specializing in:
            - Market analysis
            - Strategy development
            - Investment recommendations
            - Operational optimization
            - Risk assessment
            
            Current context: {context}
            
            Provide detailed, actionable insights."""
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

    def get_market_data(self, symbol):
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            return {
                'price': info.get('currentPrice', 'N/A'),
                'volume': info.get('volume', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'pe_ratio': info.get('forwardPE', 'N/A'),
                'dividend_yield': info.get('dividendYield', 'N/A'),
                '52w_high': info.get('fiftyTwoWeekHigh', 'N/A'),
                '52w_low': info.get('fiftyTwoWeekLow', 'N/A')
            }
        except Exception as e:
            return {'error': str(e)}

def main():
    st.set_page_config(
        page_title="Mining Business & Strategy AI Agent",
        page_icon="⛏️",
        layout="wide"
    )
    
    st.title("Mining Business & Strategy AI Agent ⛏️")
    
    # Sidebar
    with st.sidebar:
        api_key = st.text_input("OpenAI API Key", type="password")
        st.divider()
        st.markdown("""
        ### Features
        - Market Analysis
        - Strategy Development
        - Investment Analysis
        - Risk Assessment
        - Competitor Analysis
        """)
    
    if not api_key:
        st.warning("Please enter your OpenAI API key to continue.")
        return
    
    # Initialize analyst
    analyst = MiningBusinessAnalyst(api_key)
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["Business Analysis", "Market Data", "Custom Query"])
    
    # Business Analysis Tab
    with tab1:
        st.header("Business Analysis")
        analysis_type = st.selectbox(
            "Select Analysis Type",
            [
                "Market Research",
                "Investment Strategy",
                "Operational Analysis",
                "Risk Assessment",
                "Competitor Analysis"
            ]
        )
        
        # Additional inputs based on analysis type
        if analysis_type == "Market Research":
            commodity = st.selectbox(
                "Select Commodity",
                ["Gold", "Silver", "Copper", "Iron Ore", "Lithium", "Coal", "Nickel"]
            )
            query = f"Provide a comprehensive market analysis for {commodity} mining industry, including current trends, prices, demand-supply dynamics, and future outlook."
        
        elif analysis_type == "Investment Strategy":
            region = st.selectbox(
                "Select Region",
                ["North America", "South America", "Australia", "Africa", "Asia"]
            )
            query = f"Develop an investment strategy for mining operations in {region}, including key opportunities, risks, and recommendations."
        
        elif analysis_type == "Operational Analysis":
            operation_type = st.selectbox(
                "Operation Type",
                ["Open Pit", "Underground", "Surface Mining", "In-Situ Recovery"]
            )
            query = f"Analyze operational considerations, best practices, and optimization strategies for {operation_type} mining operations."
        
        elif analysis_type == "Risk Assessment":
            risk_focus = st.multiselect(
                "Risk Areas",
                ["Environmental", "Regulatory", "Market", "Operational", "Political"],
                ["Environmental", "Market"]
            )
            query = f"Provide a detailed risk assessment for mining operations focusing on {', '.join(risk_focus)} risks."
        
        else:  # Competitor Analysis
            company = st.text_input("Company Name", "BHP")
            query = f"Analyze the competitive position, strengths, weaknesses, and strategy of {company} in the mining industry."
        
        if st.button("Generate Analysis"):
            with st.spinner("Analyzing..."):
                analysis = analyst.analyze_query(query)
                st.markdown(analysis)
    
    # Market Data Tab
    with tab2:
        st.header("Market Data Analysis")
        symbol = st.text_input("Enter Mining Company Stock Symbol", "BHP")
        
        if symbol:
            with st.spinner("Fetching market data..."):
                data = analyst.get_market_data(symbol)
                
                if 'error' in data:
                    st.error(data['error'])
                else:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Current Price", f"${data['price']}")
                        st.metric("Volume", f"{data['volume']:,}")
                    
                    with col2:
                        st.metric("Market Cap", f"${data['market_cap']:,}")
                        st.metric("P/E Ratio", data['pe_ratio'])
                    
                    with col3:
                        st.metric("52 Week High", f"${data['52w_high']}")
                        st.metric("52 Week Low", f"${data['52w_low']}")
                    
                    with col4:
                        st.metric("Dividend Yield", 
                                f"{data['dividend_yield']}%" if data['dividend_yield'] != 'N/A' else 'N/A')
    
    # Custom Query Tab
    with tab3:
        st.header("Custom Analysis")
        query = st.text_area(
            "Enter your mining industry analysis query",
            height=100,
            placeholder="E.g., Analyze the impact of green energy transition on copper mining demand..."
        )
        
        if st.button("Generate Custom Analysis"):
            with st.spinner("Analyzing..."):
                analysis = analyst.analyze_query(query)
                st.markdown(analysis)

if __name__ == "__main__":
    main()
