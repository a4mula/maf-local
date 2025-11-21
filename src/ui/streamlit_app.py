import streamlit as st
import psutil
import os
import asyncio
import httpx
import uuid
from datetime import datetime

# Page Config
st.set_page_config(
    page_title="Hierarchical MAF Studio",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar: Hardware Probe ---
st.sidebar.title("Hardware Probe 🖥️")

def get_system_specs():
    mem = psutil.virtual_memory()
    total_gb = round(mem.total / (1024**3), 1)
    available_gb = round(mem.available / (1024**3), 1)
    cpu_count = psutil.cpu_count(logical=False)
    
    return total_gb, available_gb, cpu_count

total_ram, avail_ram, cores = get_system_specs()

st.sidebar.metric("Total RAM", f"{total_ram} GB")
st.sidebar.metric("Available RAM", f"{avail_ram} GB")
st.sidebar.metric("Physical Cores", f"{cores}")

if total_ram < 8:
    st.sidebar.error("⚠️ Insufficient RAM (< 8GB)")
elif total_ram < 16:
    st.sidebar.warning("⚠️ Low RAM (< 16GB). Performance may be limited.")
else:
    st.sidebar.success("✅ Hardware Sufficient")

# --- Sidebar: Configuration ---
st.sidebar.title("Configuration ⚙️")
api_key = st.sidebar.text_input("OpenAI API Key (Optional)", type="password")
if api_key:
    os.environ["OPENAI_API_KEY"] = api_key
    st.sidebar.success("Key set!")

# --- Main Interface ---
st.title("Hierarchical MAF Studio 🤖")

# Tabs for different views
tab1, tab2 = st.tabs(["💬 Chat Interface", "📊 Live Agent Graph"])

with tab1:
    st.markdown("### Liaison Agent Interface")

    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add initial greeting
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "Hello! I am the Liaison Agent. I can help you plan projects, create workflows, or answer questions. How can I assist you today?"
        })

    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input
    if prompt := st.chat_input("Type your message..."):
        # 1. Display User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Send to Agent (Mocked for UI demo, real implementation connects to Agent API)
        # In a real deployment, this would hit a FastAPI endpoint exposed by the agent service
        # For now, we'll simulate the response or try to import if running locally
        
        with st.chat_message("assistant"):
            with st.spinner("Liaison is thinking..."):
                # Call the agent API
                try:
                    response = httpx.post(
                        "http://agent:8002/chat",
                        json={"message": prompt},
                        timeout=120.0  # Increased timeout for LLM processing
                    )
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        response_text = response_data.get("response", "No response from agent")
                    else:
                        response_text = f"⚠️ Agent API error: {response.status_code}"
                        
                except httpx.RequestError as e:
                    response_text = f"⚠️ Connection error: Could not reach agent service. {str(e)}"
                except Exception as e:
                    response_text = f"⚠️ Unexpected error: {str(e)}"
                
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})

with tab2:
    st.markdown("### Real-time Agent Hierarchy")
    st.info("This visualization is running on a separate service (Next.js) and embedded here.")
    
    # Embed the Next.js app running on port 3001
    # Note: In a real deployment, this URL would need to be the public URL of the UI service
    # For local development, localhost:3001 works if the user's browser can reach it
    import streamlit.components.v1 as components
    components.iframe("http://localhost:3001", height=800, scrolling=True)

# --- Footer ---
st.markdown("---")
st.caption("Hierarchical Multi-Agent Framework | v2.0.0 | Status: Online")
