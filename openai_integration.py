import openai
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env
openai.api_key = os.getenv("OPENAI_API_KEY")

class OpenAIIntegration:
    def analyze_sentiment(self, text):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI trained to analyze sentiment from text. Your task is to read the following piece of text and determine if the overall sentiment is positive, negative, or neutral."},
                    {"role": "user", "content": text},
                    {"role": "system", "content": "Please provide your analysis on the sentiment of the above text."}
                ]
            )
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message['content'].strip()
            else:
                return "Failed to analyze sentiment; no response."
        except Exception as e:
            print(f"Error in analyzing sentiment: {str(e)}")
            return None

