import streamlit as st
from langchain_community.document_loaders import WebBaseLoader

from chain import Chain
from portfolio import Portfolio
from utils import clean_text

# Define a function to generate the email
def generate_email(llm, portfolio, url, tone):
    """Handles the email generation process and returns the email content."""
    try:
        # Show a spinner while the process is running
        with st.spinner("🚀 Generating your email... This might take a moment."):
            loader = WebBaseLoader([url])
            data = clean_text(loader.load().pop().page_content)
            portfolio.load_portfolio()
            jobs = llm.extract_jobs(data)

            if not jobs:
                st.warning("No relevant job details could be extracted from the URL. Please try a different link.")
                return None
            
            # Assuming the prompt can handle tone
            job = jobs[0]
            skills = job.get('skills', [])
            links = portfolio.query_links(skills)
            
            # Pass the selected tone to the write_mail function
            email = llm.write_mail(job, links, tone=tone)
            st.success("🎉 Email generated successfully!")
            return email

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        st.info("Please ensure the URL is correct and the page contains a valid job description.")
        return None

# The main app function
def main():
    # Set the page configuration at the very top
    st.set_page_config(layout="wide", page_title="Fictgenics Cold Email Generator", page_icon="📧")

    # Sidebar for controls and branding
    with st.sidebar:
        st.header("Settings")
        st.markdown("**Adjust the tone of your cold email.**")
        tone = st.radio(
            "Select Email Tone:",
            options=["Professional", "Enthusiastic", "Friendly", "Concise"]
        )
        st.markdown("---")
        st.info("""
        **About This App:**
        This tool, powered by **Fictgenics**, scrapes a job description from a URL and automatically generates a personalized cold email, matching your skills and portfolio links to the job's requirements.
        """)

    # Main content area with a cleaner layout
    st.title("📧 Fictgenics Cold Email Generator")
    st.markdown("### Your secret weapon for outreach. Just paste, generate, and land the gig.")
    
    # Use a container for the input section
    input_container = st.container()
    with input_container:
        url_input = st.text_input(
            "Enter a job posting URL:",
            placeholder="e.g., https://careers.google.com/...",
            key="url_input"
        )
        col1, col2 = st.columns([1, 6])
        with col1:
            submit_button = st.button("Generate Email", type="primary")

    # Use a container for the output, which will be populated only after generation
    output_container = st.container()
    if submit_button and url_input:
        with output_container:
            chain = Chain()
            portfolio = Portfolio()
            email_content = generate_email(chain, portfolio, url_input, tone)
            
            if email_content:
                st.markdown("### Your Personalized Email")
                # Use an expander to keep the UI clean
                with st.expander("Click to view and copy your email", expanded=True):
                    st.code(email_content, language='markdown')
                
                # Add a button to copy to clipboard for a seamless UX
                st.button("Copy to Clipboard", help="Click to copy the email to your clipboard.", on_click=lambda: st.write(f'<script>navigator.clipboard.writeText(`{email_content}`)</script>', unsafe_allow_html=True))
    
if __name__ == "__main__":
    main()