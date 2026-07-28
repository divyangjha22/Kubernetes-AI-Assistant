import os
import base64
from pathlib import Path
import streamlit as st

def get_files_in_dir(doc_path: str):
    """Scan directory recursively for .md and .pdf files."""
    md_files = []
    pdf_files = []
    
    if not os.path.exists(doc_path):
        return md_files, pdf_files

    for root, _, files in os.walk(doc_path):
        for file in sorted(files):
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, doc_path)
            if file.endswith(".md"):
                md_files.append((rel_path, full_path))
            elif file.endswith(".pdf"):
                pdf_files.append((rel_path, full_path))
                
    return md_files, pdf_files

def render_pdf_viewer(file_path: str):
    """Embed PDF directly inside Streamlit using an iframe and provide a download fallback."""
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    
    # Download Button
    file_name = os.path.basename(file_path)
    st.download_button(
        label="⬇️ Download PDF Document",
        data=open(file_path, "rb"),
        file_name=file_name,
        mime="application/pdf",
        use_container_width=True
    )
    
    # Embedded HTML Iframe
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="850px" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def render_docs_view(docs_dir: str):
    st.title("📚 Documentation & Architecture Guides")
    st.caption("Browse system overviews, ingestion mechanics, LLM gateways, and guardrail evaluations.")
    st.divider()

    md_files, pdf_files = get_files_in_dir(docs_dir)

    if not md_files and not pdf_files:
        st.warning(f"No `.md` or `.pdf` files found in `{docs_dir}`. Check your directory structure.")
        return

    # Two-column layout: Navigation selector on the left, Content on the right
    col_nav, col_content = st.columns([1, 3])

    with col_nav:
        st.subheader("📁 Files")
        doc_type = st.radio("Document Type", ["📖 Markdown Guides", "📑 PDF Reports"], label_visibility="collapsed")
        st.markdown("---")
        
        selected_file_path = None
        
        if doc_type == "📖 Markdown Guides":
            if md_files:
                selected_rel, selected_file_path = st.radio(
                    "Select Guide:",
                    options=md_files,
                    format_func=lambda x: x[0].replace("_", " ").replace(".md", ""),
                )
            else:
                st.info("No Markdown files found.")
                
        elif doc_type == "📑 PDF Reports":
            if pdf_files:
                selected_rel, selected_file_path = st.radio(
                    "Select Report:",
                    options=pdf_files,
                    format_func=lambda x: os.path.basename(x[0]),
                )
            else:
                st.info("No PDF files found.")

    with col_content:
        if selected_file_path and os.path.exists(selected_file_path):
            file_name = os.path.basename(selected_file_path)
            st.subheader(f"📄 {file_name}")
            st.markdown("---")
            
            if selected_file_path.endswith(".md"):
                with open(selected_file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                # Render clean markdown
                st.markdown(content, unsafe_allow_html=True)
            elif selected_file_path.endswith(".pdf"):
                render_pdf_viewer(selected_file_path)
        else:
            st.info("👈 Please select a document from the left panel to begin reading.")
