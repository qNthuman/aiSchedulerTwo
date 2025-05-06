# planner/ai_planner.py

import openai
from dotenv import load_dotenv
import os

# Load environment variables (OpenAI API key)
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_plan_with_ai(subject, topics):
    """
    Generate a detailed study plan using LangChain and OpenAI's GPT model.
    The model will break down topics and estimate hours for each.

    Parameters:
        subject (str): Subject the user is studying (e.g., Physics, Chemistry).
        topics (list): List of topics to be studied, given by the user.

    Returns:
        dict: Breakdown of topics and their estimated hours.
    """

    # Construct the prompt for OpenAI GPT
    prompt = f"""
    I am studying {subject}. Below are the topics I need to cover:

    {', '.join(topics)}

    Break down each topic into smaller subtopics (if applicable) and estimate the number of hours needed to study each subtopic.
    Ensure the breakdown is manageable and efficient for a student with {len(topics)} total topics to study in a limited time frame.
    Provide the breakdown as a dictionary where the key is the topic/subtopic and the value is the estimated hours to study.
    """

    # Send the request to the OpenAI API
    response = openai.Completion.create(
        engine="text-davinci-003",  # You can use different engines, e.g., "gpt-4" if available
        prompt=prompt,
        max_tokens=150,
        temperature=0.7,
    )

    # Get the generated text from the response
    plan_text = response.choices[0].text.strip()

    # Convert the output text into a dictionary (assuming the model provides it in the correct format)
    # For simplicity, you might need to parse or clean up the response if it's not well-formed JSON
    try:
        ai_plan = eval(plan_text)  # Evaluating as Python dictionary (ensure response is safe)
    except Exception as e:
        return {"error": f"Failed to parse AI plan: {str(e)}"}

    return ai_plan
