import streamlit as st
import os
import openai
from datetime import datetime, timedelta
from typing import Dict, Any
import requests

class PortfolioAssistant:
    def __init__(self):
        """Initialize Portfolio Assistant"""
        # Set OpenAI API key from Streamlit secrets
        openai.api_key = st.secrets["OPENAI_API_KEY"]
        
        # Load personal information
        self.personal_info = self._load_personal_info()
        
        # Initialize session state for chat
        if 'messages' not in st.session_state:
            st.session_state.messages = []

    def _load_personal_info(self) -> Dict[str, Any]:
        """Load personal information"""
        return {
            "name": "Pavan Tejavath",
            "title": "Full Stack Developer & ML Engineer",
            "bio": """Full Stack Developer and Machine Learning enthusiast with a passion for building interactive web applications. 
            Originally from Hyderabad, India, and currently pursuing a Master's in Computer Science in the United States.""",
            "skills": {
                "Programming": ["Python", "JavaScript", "Java"],
                "Web Development": ["React", "Node.js", "Django"],
                "ML/AI": ["TensorFlow", "PyTorch", "NLP"]
            }
        }

    def initialize_streamlit(self):
        """Initialize Streamlit configuration"""
        st.set_page_config(
            page_title="Chat with Pavan's AI Assistant",
            page_icon="🤖",
            layout="wide"
        )
        
        # Dark theme CSS
        st.markdown("""
            <style>
            .stApp {
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
            .stMarkdown {
                color: #FFFFFF;
            }
            h1, h2, h3 {
                color: #FFFFFF !important;
            }
            .stButton > button {
                background-color: #2E2E2E;
                color: #FFFFFF;
            }
            .stTextInput > div > div > input {
                background-color: #2E2E2E;
                color: #FFFFFF;
            }
            .stChatMessage {
                background-color: #2E2E2E !important;
            }
            </style>
            """, unsafe_allow_html=True)

    def generate_response(self, prompt: str) -> str:
        """Generate AI response"""
        try:
            messages = [
                {"role": "system", "content": """You are Pavan's AI assistant. Help users learn about his experience, schedule meetings, and answer questions about his skills and projects.
                When users want to schedule a meeting, guide them to send an email to tejavathpavan2000@gmail.com with their preferred time slots."""}
            ]

            # Add chat history
            for message in st.session_state.messages:
                messages.append({"role": message["role"], "content": message["content"]})

            # Add current prompt
            messages.append({"role": "user", "content": prompt})

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message["content"]
        except Exception as e:
            print(f"Error: {e}")
            return "I apologize, but I'm having trouble generating a response. Please try again."

    def show_chat_interface(self):
        """Display the chat interface"""
        st.title("Chat with Pavan's AI Assistant")
        st.write("Ask me anything about Pavan's experience, skills, or schedule a meeting!")

        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Type your message here..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate and display response
            with st.chat_message("assistant"):
                response = self.generate_response(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

    def run(self):
        """Main application entry point"""
        self.initialize_streamlit()
        self.show_chat_interface()

if __name__ == "__main__":
    assistant = PortfolioAssistant()
    assistant.run()