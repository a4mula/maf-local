import streamlit as st
import psutil
import os
import asyncio
import httpx
import uuid
from datetime import datetime

# Page Config
import time
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.ui.components.gpu_stats import get_system_stats

# Page Config
st.set_page_config(
    page_title="Hierarchical MAF Studio",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar: Project Explorer ---
st.sidebar.title("MAF Studio 🛠️")

# Imports
from streamlit_tree_select import tree_select

# Initialize session state
if "current_project" not in st.session_state:
    # Default project 0 (DevStudio)
    st.session_state.current_project = {"project_id": 0, "name": "DevStudio (Self)", "path": os.getcwd()}
if "current_session" not in st.session_state:
    st.session_state.current_session = None

# API Helper
def api_request(method, endpoint, json=None):
    try:
        api_url = os.getenv("AGENT_API_URL", "http://localhost:8002")
        if method == "GET":
            resp = httpx.get(f"{api_url}{endpoint}", timeout=2.0)
        else:
            resp = httpx.post(f"{api_url}{endpoint}", json=json, timeout=2.0)
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return None

# Fetch Projects
projects = api_request("GET", "/projects/") or [{"project_id": 0, "name": "DevStudio (Self)", "path": os.getcwd()}]
project_map = {p["name"]: p for p in projects}

# Project Selector with "New Project" option
project_options = list(project_map.keys()) + ["➕ New Project..."]
selected_option = st.sidebar.selectbox(
    "Project",
    options=project_options,
    index=0 if st.session_state.current_project["name"] in project_map else 0,
    label_visibility="collapsed"
)

# Handle "New Project" Selection
if selected_option == "➕ New Project...":
    with st.sidebar.form("create_project_form"):
        st.markdown("### Create Project")
        new_name = st.text_input("Name", placeholder="MyNewApp")
        if st.form_submit_button("Create"):
            if new_name:
                # Auto-generate path as SIBLING directory (Host-Native)
                # If running in /home/robb/projects/maf-local, this creates /home/robb/projects/MyNewApp
                safe_name = "".join(c for c in new_name if c.isalnum() or c in ('-', '_'))
                auto_path = os.path.abspath(os.path.join(os.getcwd(), "..", safe_name))
                
                res = api_request("POST", "/projects/", {"name": new_name, "path": auto_path})
                if res:
                    st.success(f"Created {new_name}")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Failed")
    # Form is shown, but we don't stop execution so the rest of the UI (like the graph) still renders
    # st.stop()
    # Use current project while form is open to prevent crash
    selected_project = st.session_state.current_project
else:
    # Handle Project Switch
    selected_project = project_map[selected_option]
    # Use .get() to handle potential missing keys or legacy data
    pid = selected_project.get("project_id", selected_project.get("id", 0))
    curr_pid = st.session_state.current_project.get("project_id", st.session_state.current_project.get("id", 0))
    
    if pid != curr_pid:
        st.session_state.current_project = selected_project
        st.session_state.current_session = None
        api_request("POST", "/api/context", {
            "project_id": pid,
            "project_name": selected_project["name"]
        })
        st.rerun()

# --- File Explorer (Tree View) ---
st.sidebar.markdown("### Explorer")
project_path = selected_project.get("path", "/app")

def get_file_tree(path):
    if not os.path.exists(path):
        return []
    
    tree = []
    try:
        # Only list top 2 levels to avoid performance hit
        for root, dirs, files in os.walk(path):
            # Calculate depth
            rel_path = os.path.relpath(root, path)
            if rel_path == ".":
                depth = 0
            else:
                depth = rel_path.count(os.sep) + 1
            
            if depth > 2: continue

            # Build nodes
            nodes = []
            for d in dirs:
                if d.startswith('.'): continue # Skip hidden
                nodes.append({
                    "label": d,
                    "value": os.path.join(root, d),
                    "children": [{"label": "Loading...", "value": "loading"}] # Lazy load simulation (UI only)
                })
            for f in files:
                if f.startswith('.'): continue
                nodes.append({
                    "label": f,
                    "value": os.path.join(root, f)
                })
            
            # If it's the root, return these nodes
            if depth == 0:
                return nodes
    except Exception:
        pass
    return []

# Generate Tree Data (Simplified for now - just top level)
# A real recursive builder would be better but os.walk is flat.
# Let's use a simpler approach: Just list top-level files/folders
def build_simple_tree(path):
    nodes = []
    try:
        if not os.path.exists(path): return [{"label": "Path not found", "value": "error"}]
        
        items = sorted(os.listdir(path))
        for item in items:
            if item.startswith('.'): continue
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                # Add children for 1 level deep
                children = []
                try:
                    subitems = sorted(os.listdir(full_path))
                    for sub in subitems:
                        if sub.startswith('.'): continue
                        children.append({"label": sub, "value": os.path.join(full_path, sub)})
                except: pass
                
                nodes.append({
                    "label": f"📁 {item}",
                    "value": full_path,
                    "children": children
                })
            else:
                nodes.append({
                    "label": f"📄 {item}",
                    "value": full_path
                })
    except Exception as e:
        return [{"label": f"Error: {e}", "value": "error"}]
    return nodes

tree_data = build_simple_tree(project_path)

# Render Tree
with st.sidebar.container(height=400):
    return_val = tree_select(tree_data, expand_on_click=True, checked=[])

# --- Sessions (Compact) ---
st.sidebar.markdown("---")
with st.sidebar.expander("Sessions", expanded=False):
    sessions = api_request("GET", f"/sessions/project/{selected_project['project_id']}") or []
    session_map = {s["name"]: s for s in sessions}
    
    sel_sess = st.selectbox(
        "Active Session",
        options=["(New)"] + list(session_map.keys()),
        label_visibility="collapsed"
    )
    
    if sel_sess == "(New)":
        new_sess_name = st.text_input("New Session Name")
        if st.button("Start Session"):
            if new_sess_name:
                new_sess = api_request("POST", "/sessions/", {"project_id": selected_project["project_id"], "name": new_sess_name})
                if new_sess:
                    st.session_state.current_session = new_sess
                    api_request("POST", "/api/context", {
                        "project_id": selected_project["project_id"],
                        "project_name": selected_project["name"],
                        "session_id": new_sess["session_id"],
                        "session_name": new_sess["name"]
                    })
                    st.rerun()
    else:
        # Resume logic
        sess = session_map[sel_sess]
        if st.session_state.current_session != sess:
            st.session_state.current_session = sess
            api_request("POST", "/api/context", {
                "project_id": selected_project["id"],
                "project_name": selected_project["name"],
                "session_id": sess["session_id"],
                "session_name": sess["name"]
            })
            st.rerun()

# --- Sidebar: Telemetry (Inspector) ---
st.sidebar.markdown("---")
st.sidebar.subheader("Inspector 🔍")
stats = get_system_stats()

# GPU Stats
if stats["gpus"]:
    for gpu in stats["gpus"]:
        st.sidebar.caption(f"🎮 {gpu['name']}")
        st.sidebar.progress(gpu['gpu_util_percent'] / 100, text=f"Util: {gpu['gpu_util_percent']}%")
        st.sidebar.progress(gpu['memory_percent'] / 100, text=f"VRAM: {gpu['memory_used_gb']}/{gpu['memory_total_gb']} GB")
else:
    st.sidebar.caption("💻 CPU Mode (No GPU)")

# CPU/RAM
# CPU/RAM
col1, col2 = st.sidebar.columns(2)
col1.metric("CPU", f"{stats['cpu']['percent']}%")
col2.metric("RAM", f"{stats['ram']['percent']}%")
st.sidebar.caption(f"Available: {stats['ram']['available_gb']} GB")

# --- Main Layout (Vertical Stack) ---
# Graph on top, Chat on bottom

# Agent Graph Section (16:9 aspect ratio)
st.markdown("## 🕸️ Live Agent Graph")
import streamlit.components.v1 as components
# Next.js is running on port 3002 (3000 is used by Grafana)
components.iframe("http://localhost:3002", height=410, scrolling=False)

st.markdown("---")

# Chat Console Section (16:9 aspect ratio)
st.markdown("## 💬 Console")
st.caption(f"Project: **{selected_project['name']}** | Session: **{st.session_state.current_session['name'] if st.session_state.current_session else 'None'}**")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Ready."
    })

# Chat Container with fixed height (16:9 ratio)
chat_container = st.container(height=400)

# Display Chat
with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Chat Input
if prompt := st.chat_input("Command / Message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Executing..."):
                try:
                    payload = {"message": prompt}
                    if st.session_state.current_session:
                        payload["session_id"] = str(st.session_state.current_session["session_id"])
                    
                    api_url = os.getenv("AGENT_API_URL", "http://agent:8002")
                    response = httpx.post(f"{api_url}/chat", json=payload, timeout=120.0)
                    
                    if response.status_code == 200:
                        response_text = response.json().get("response", "No response")
                    else:
                        response_text = f"Error: {response.status_code}"
                except Exception as e:
                    response_text = f"Connection Error: {e}"
                
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})

# --- Footer ---
st.markdown("---")
st.caption("Hierarchical Multi-Agent Framework | v2.0.0 | Status: Online")
