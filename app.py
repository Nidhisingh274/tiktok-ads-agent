import streamlit as st
import time
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from typing import Optional, Literal

st.set_page_config(page_title="TikTok Ads AI Agent", layout="centered")

with st.sidebar:
    st.header("⚙️ Configuration")
    groq_key = st.text_input("Groq API Key", type="password")
    use_mock = st.checkbox("Use Mock TikTok API?", value=True)

    if not groq_key:
        st.warning("⚠️ Please enter a Groq API Key to proceed.")
        st.markdown("[Get a Free Key Here](https://console.groq.com/keys)")
        st.stop()

llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=groq_key, temperature=0)

class TikTokAdConfig(BaseModel):
    campaign_name: str = Field(..., min_length=3, description="Name of the campaign")
    objective: Literal['Traffic', 'Conversions'] = Field(..., description="Campaign objective")
    ad_text: str = Field(..., max_length=100, description="Ad caption text")
    cta: str = Field(..., description="Call to Action button text")
    music_id: Optional[str] = Field(None, description="The ID of the music track")

def mock_tiktok_oauth():
    time.sleep(1.0)
    return {"status": "success", "token": "mock_access_token_12345"}

def validate_music_id(music_id: str):
    if "invalid" in music_id.lower():
        return False, "Music ID not found in library (404)."
    if "banned" in music_id.lower():
        return False, "Track is geo-restricted in this region (403)."
    return True, "Valid"

def submit_ad(payload: dict):
    time.sleep(1.5)
    if "restricted" in payload.get('ad_text', '').lower():
        return {"error": "Geo-restriction (403): Content not allowed in this region."}
    return {"status": "success", "ad_id": "987654321"}

def get_ai_response(user_input, current_data):
    system_prompt = f"""
    You are an expert TikTok Ad Creation Assistant.
    
    CURRENT AD STATE: {current_data}

    YOUR GOAL:
    Guide the user to complete the ad configuration. 
    Maintain a professional yet helpful tone.

    STRICT BUSINESS RULES:
    1. Campaign Name must be > 3 characters.
    2. Ad Text must be < 100 characters.
    3. MUSIC LOGIC: 
       - If Objective is 'Conversions', Music is MANDATORY.
       - If Objective is 'Traffic', Music is OPTIONAL.
       - If the user explicitly declines music for a 'Conversions' ad, you MUST reject the request and explain the rule.

    INSTRUCTIONS:
    - If data is missing, ask for it one field at a time.
    - If the user provides input, assume it is for the current missing field and validate it.
    - Once all fields are valid, present a summary and ask for confirmation to 'Submit'.
    """
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_input)]
    response = llm.invoke(messages)
    return response.content

st.title("🎵 TikTok Ads Agent")
st.caption("AI Agent with OAuth Simulation & Guardrails")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm your TikTok Ads Assistant. Let's set up a new campaign. What should we name it?"}]
if "ad_data" not in st.session_state:
    st.session_state.ad_data = {}
if "token" not in st.session_state:
    st.session_state.token = None

if not st.session_state.token:
    st.info("🔒 Authentication Required")
    if st.button("Connect TikTok Account"):
        with st.spinner("Redirecting to TikTok OAuth..."):
            res = mock_tiktok_oauth()
            st.session_state.token = res['token']
            st.success("Successfully Authenticated!")
            time.sleep(1)
            st.rerun()
else:
    st.success(f"✅ Authenticated (Token: {st.session_state.token[:8]}...)")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Type your response..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Agent is thinking..."):
                
                if "submit" in prompt.lower():
                    res = submit_ad(st.session_state.ad_data)
                    if "error" in res:
                        reply = f"❌ **Submission Failed**\n\n**API Error:** `{res['error']}`\n\n**Reasoning:** The API rejected the content due to restriction policies. Please modify the ad text."
                    else:
                        reply = f"🚀 **Success!** Ad Campaign created successfully.\n\n**Campaign ID:** `{res['ad_id']}`"
                
                elif "music id" in prompt.lower():
                    words = prompt.split()
                    music_id = words[-1] 
                    is_valid, reason = validate_music_id(music_id)
                    
                    if is_valid:
                        st.session_state.ad_data['music_id'] = music_id
                        reply = f"✅ Music ID `{music_id}` validated successfully. What is the Ad Text?"
                    else:
                        reply = f"⚠️ **Validation Error:** TikTok API rejected Music ID `{music_id}`.\n\n**Reason:** {reason}\n\nPlease provide a valid ID."
                
                else:
                    if "traffic" in prompt.lower(): st.session_state.ad_data['objective'] = "Traffic"
                    if "conversions" in prompt.lower(): st.session_state.ad_data['objective'] = "Conversions"
                    
                    reply = get_ai_response(prompt, str(st.session_state.ad_data))
                
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

    with st.expander("🔍 View Internal Agent State (JSON)"):
        st.json(st.session_state.ad_data)