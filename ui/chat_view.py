import os
import time
import requests
import logfire
import streamlit as st

AI_AVATAR = "🤖"
USER_AVATAR = "👤"

def render_chat_view():
    st.title("🤖 Enterprise Agentic Assistant")
    st.caption("Ask technical questions about Kubernetes, architectures, or internal systems.")
    
    # Render existing conversation
    for message in st.session_state.messages:
        avatar = AI_AVATAR if message["role"] == "assistant" else USER_AVATAR
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # Handle new input
    if prompt := st.chat_input("Ask about your system architecture or documentation..."):
        with logfire.span("💬 User Chat Interaction", user_query=prompt, session_id=st.session_state.session_id):
            
            # Append & display user prompt
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar=USER_AVATAR):
                st.markdown(prompt)

            # Generate response
            with st.chat_message("assistant", avatar=AI_AVATAR):
                with st.status("🔍 Agent is thinking...", expanded=True) as status:
                    try:
                        with logfire.span("📡 Calling RAG Backend"):
                            base_url = os.getenv("BACKEND_URL", "http://localhost:8000")
                            response = requests.post(
                                f"{base_url}/query",
                                json={"q": prompt, "thread_id": st.session_state.session_id},
                                timeout=60
                            )
                            response.raise_for_status()
                            data = response.json()
                        
                        # Display Agent Reasoning Steps
                        steps = data.get("thought_process", [])
                        if steps:
                            st.markdown("**🧠 Reasoning Trace:**")
                            for step in steps:
                                st.markdown(f"- `⚙️` *{step}*")
                        
                        status.update(label="✅ Answer Synthesized", state="complete", expanded=False)
                        
                        # Display Retrieved Sources cleanly
                        sources = data.get("sources", [])
                        if sources:
                            with st.expander(f"📄 Retrieved Context ({len(sources)} sources used)"):
                                for i, source in enumerate(sources):
                                    preview = source[:80].replace("\n", " ") + "..."
                                    with st.expander(f"Source [{i+1}]: {preview}"):
                                        st.code(source, language="markdown")
                                        
                    except Exception as e:
                        logfire.error(f"❌ UI-Backend Connection Failed: {e}")
                        status.update(label="❌ Connection Failed", state="error")
                        st.error(f"Backend Offline or Error: `{e}`")
                        st.stop()

                # Stream final answer
                answer_placeholder = st.empty()
                full_answer = data.get("answer", "No response generated.")
                
                curr_text = ""
                for char in full_answer:
                    curr_text += char
                    answer_placeholder.markdown(curr_text + "▌")
                    time.sleep(0.003)
                
                answer_placeholder.markdown(full_answer)
                st.session_state.messages.append({"role": "assistant", "content": full_answer})
                logfire.info("✅ Chat cycle completed successfully.")
