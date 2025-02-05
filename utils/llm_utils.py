import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import requests
from dotenv import load_dotenv

class OpenAIManager:
    def __init__(self):
        """Initialize OpenAI with API key from environment"""
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        os.environ["OPENAI_API_KEY"] = self.api_key

    def generate_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a response using OpenAI's API"""
        try:
            # Prepare context
            context_str = ""
            if context and isinstance(context, dict) and 'documents' in context:
                if isinstance(context['documents'], list):
                    context_str = "\n".join(context['documents'])
                else:
                    context_str = str(context['documents'])

            # Prepare the messages
            messages = [
                {
                    "role": "system",
                    "content": """You are Pavan's AI Assistant for his portfolio website. 
                    Be professional, friendly, and informative when discussing his experience,
                    skills, and projects."""
                }
            ]

            if context_str:
                messages.append({
                    "role": "system",
                    "content": f"Context: {context_str}"
                })

            messages.append({"role": "user", "content": prompt})

            # Make the API request directly
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 500
            }

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            )

            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return "I apologize, but I'm having trouble generating a response at the moment."

        except Exception as e:
            print(f"Error in generate_response: {str(e)}")
            return "I encountered an error while processing your request. Please try again."

    def format_response(self, response: str, format_type: str = "markdown") -> str:
        """Format the response for display"""
        try:
            if not response:
                return ""
                
            if format_type == "markdown":
                # Clean and format the response
                lines = response.split('\n')
                formatted_lines = []
                for line in lines:
                    # Handle lists
                    if line.strip().startswith(('- ', '* ', '1. ')):
                        formatted_lines.append('\n' + line)
                    # Handle headers
                    elif line.strip().startswith('#'):
                        formatted_lines.append('\n' + line + '\n')
                    else:
                        formatted_lines.append(line)
                return '\n'.join(formatted_lines)
            
            return response

        except Exception as e:
            print(f"Error formatting response: {str(e)}")
            return response