from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
from io import BytesIO
import base64
import google.generativeai as genai

# load_dotenv()  
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
load_dotenv()


def get_gemini_response(image,input,prompt):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "max_output_tokens": 8192,
    }
    model = GenerativeModel(
        'gemini-1.5-pro',
        system_instruction=["""Your task is to generate P&ID's symbols count for the user provided images"""]
    )
    image_part = Part.from_data(
    mime_type="image/png",
    data=base64.b64decode(image_base64))

    if input != "":
        response = model.generate_content([image_part,input,prompt], generation_config=generation_config,stream=True)
    else:
        response = model.generate_content(image_part, generation_config=generation_config,stream=True)
    result = ""
    for responses in response:
        result+=responses.text
    return result

# Function to handle processing the user input
def process_input(image, user_input, prompt):
    """Process the user input and get a response from the model."""
    try:
        response = get_gemini_response(image, user_input, prompt)
        return response
    except Exception as e:
        st.error(f"Error processing the input: {str(e)}")
        return None

# Function to display the chat history in the Streamlit app
def display_chat_history(chat_history):
    """Display chat history."""
    st.subheader(":blue[Result:]")
    for message in chat_history:
        role = message["role"]
        content = message["content"]
        if role == "user":
            with st.chat_message("user"):
                st.markdown(f"**You:** {content}")
        elif role == "assistant":
            with st.chat_message("assistant"):
                st.markdown(f"**Assistant:** {content}")


prompt="""You are an AI assistant specialized in understanding and analyzing Piping and Instrumentation Diagrams (P&IDs). Your goal is to assist users in exploring and querying the diagram details interactively. You can provide information on material flows, symbol meanings, connections, and directions, as well as respond to specific queries about the diagram.
          
        User can ask questions such as:

        'Explain the material flow throughout the entire diagram.'
        'Describe the direction of arrows between nitrogen and hot water storage.'
        'Give me the count and display of the P&ID symbols and numbers.'
        'Explain each P&ID symbol in detail.'
        Your responses should be clear, concise, and accurate, pulling information from the diagram context. If symbols, flows, or connections are mentioned, provide detailed explanations of their roles and relationships within the diagram. Also, ensure you maintain a structured approach when walking the user through complex queries."""


# Sample questions
sample_questions = """
1. Give me the count and display of the P&ID symbols and numbers
2. Describe the direction of arrows between nitrogen and hot water storage
3. Can you Provide details of each P&ID symbol?
4. Explain the material flow throughout the entire diagram
"""

# Main application logic
def main():
# Sidebar configuration
    st.subheader("Intelligent :green[P&ID] Analyzer: :blue[AI-Driven] Interactive Exploration of Piping and Instrumentation Diagrams", divider="rainbow")
    st.sidebar.header("P&ID Image", divider="green")

    # Upload image functionality
    uploaded_file = st.sidebar.file_uploader("**Choose an image**", type=["jpg", "jpeg", "png"])

    st.sidebar.text_area("**Sample Questions**", sample_questions, height=200)

    image = None
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
        except Exception as e:
            st.error(f"Error loading the image: {str(e)}")

    # Initialize chat history if not already present
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Input box for user prompt
    user_input = st.chat_input("Enter your prompt")
    

    # Handle user input
    if user_input:
        if not uploaded_file:
            
            st.error("Please upload an image before entering the prompt.")
        else:
            # Add the user's question to chat history and display it immediately
            
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            display_chat_history(st.session_state.chat_history)

            # Show a spinner while processing the input
            with st.spinner("Processing..."):
                # Get response from the model
                response = process_input(image, user_input, prompt)
                if response:
                    # Add the model's response to the chat history
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    st.rerun()
                

    # # Always display the chat history after any updates
    if st.session_state.chat_history:
        display_chat_history(st.session_state.chat_history)



if __name__ == "__main__":
    main()