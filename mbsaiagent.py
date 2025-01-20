import streamlit as st
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool
import pandas as pd
import yfinance as yf
from typing import Optional, Type
from pydantic import BaseModel, Field

class MiningIndustryAgent:
    def __init__(self, openai_api_key):
        self.llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.tools = self._create_tools()
        self.agent = self._create_agent()
        
    def _create_tools(self):
        """Create the agent's toolset"""
        class StockDataInput(BaseModel):
            symbol: str = Field(description="Stock symbol of the mining company")
            
        class MarketAnalysisInput(BaseModel):
            sector: str = Field(description="Mining sector to analyze")
            
        class CompetitorAnalysisInput(BaseModel):
            company: str = Field(description="Company to analyze")

        class StockDataTool(BaseTool):
            name = "stock_data"
            description = "Get financial data for mining companies"
            args_schema: Type[BaseModel] = StockDataInput
            
            def _run(self, symbol: str) -> str:
                stock = yf.Ticker(symbol)
                data = stock.info
                return f"Financial data for {symbol}: {data}"
                
            def _arun(self, symbol: str):
                raise NotImplementedError("Async not implemented")

        class MarketAnalysisTool(BaseTool):
            name = "market_analysis"
            description = "Analyze mining market trends and opportunities"
            args_schema: Type[BaseModel] = MarketAnalysisInput
            
            def _run(self, sector: str) -> str:
                # Implement market analysis logic
                return f"Market analysis for {sector} mining sector"
                
            def _arun(self, sector: str):
                raise NotImplementedError("Async not implemented")

        class CompetitorAnalysisTool(BaseTool):
            name = "competitor_analysis"
            description = "Analyze mining company competitors"
            args_schema: Type[BaseModel] = CompetitorAnalysisInput
            
            def _run(self, company: str) -> str:
                # Implement competitor analysis logic
                return f"Competitor analysis for {company}"
                
            def _arun(self, company: str):
                raise NotImplementedError("Async not implemented")

        return [
            StockDataTool(),
            MarketAnalysisTool(),
            CompetitorAnalysisTool()
        ]

    def _create_agent(self):
        """Create the LLM agent with tools"""
        prompt = PromptTemplate(
            template="""You are an AI business strategist specialized in the mining industry.
            Use the following tools to help answer questions and develop strategies:
            {tools}
            
            Previous conversation history:
            {chat_history}
            
            Human: {input}
            AI: Let me think about this step by step:""",
            input_variables=["input", "chat_history", "tools"]
        )
        
        llm_chain = LLMChain(llm=self.llm, prompt=prompt)
        
        tool_names = [tool.name for tool in self.tools]
        agent = LLMSingleActionAgent(
            llm_chain=llm_chain,
            tools=self.tools,
            allowed_tools=tool_names
        )
        
        return AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True
        )

    def process_input(self, user_input: str) -> str:
        """Process user input and return agent's response"""
        try:
            response = self.agent.run(user_input)
            return response
        except Exception as e:
            return f"Error processing request: {str(e)}"

# Streamlit interface
def main():
    st.title("Mining Industry AI Agent")
    
    # Get OpenAI API key
    openai_api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")
    
    if not openai_api_key:
        st.warning("Please enter your OpenAI API key to continue.")
        return
    
    # Initialize agent
    agent = MiningIndustryAgent(openai_api_key)
    
    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    if prompt := st.chat_input("What would you like to know about the mining industry?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate agent response
        with st.chat_message("assistant"):
            response = agent.process_input(prompt)
            st.markdown(response)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()

