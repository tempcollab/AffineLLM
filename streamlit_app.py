import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("Multiplyr LLM Playground")
st.write(
    "Chat with LLMs hosted by Multiplyr"
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = st.text_input("API Key", type="password")
if not openai_api_key:
    st.info("Please add your API key to continue. Request new API keys [here](https://x.com/AffineDeFi).", icon="🗝️")
else:

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key, base_url="http://38.99.105.121:20186/v1")

    # user message with right alignment
    st.html(
        """
    <style>
        .stChatMessage:has(.chat-user) {
            flex-direction: row-reverse;
            text-align: right;
        }
    </style>
    """
    )

    with st.sidebar:
        st.header("Model")
        model_choice = st.selectbox("Select Model", ["Meta-Llama-3.1-70B-Instruct"])
        
        st.header("Parameters")
        output_length = st.slider("Output Length", min_value=100, max_value=4096, value=512)
        temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.05)
        top_p = st.slider("Top-P", min_value=0.0, max_value=1.0, value=0.7, step=0.05)
        top_k = st.slider("Top-K", min_value=1, max_value=100, value=50, step=1)
        # frequency_penalty = st.slider("Frequency Penalty", min_value=1.0, max_value=4.0, value=1.0)

    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.html(f"<span class='chat-{message['role']}'></span>")
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    if prompt := st.chat_input("What is up?"):

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.html(f"<span class='chat-user'></span>")
            st.markdown(prompt)

        # Generate a response using the OpenAI API.
        stream = client.chat.completions.create(
            model="neuralmagic/Meta-Llama-3.1-70B-Instruct-FP8",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
            max_tokens=output_length,
            temperature=temperature,
            top_p=top_p,
            # topk=50#int(top_k),
            # frequency_penalty=frequency_penalty
        )

        # Stream the response to the chat using `st.write_stream`, then store it in 
        # session state.
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
