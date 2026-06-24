import streamlit as st
import PyPDF2
import anthropic

st.set_page_config(page_title="Annual Report Analyzer", layout="wide")
st.title("📊 Annual Report Qualitative Analyzer")
st.markdown("Upload a PDF annual report and get qualitative analysis across 27 key points in 2-3 minutes.")

st.markdown("---")

# Sidebar for API key
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter Anthropic API Key", type="password", help="Get one at console.anthropic.com")

if not api_key:
    st.warning("⚠️ Please enter your Anthropic API key in the sidebar to proceed.")
    st.info("Get a free key at https://console.anthropic.com")
    st.stop()

# File upload
uploaded_file = st.file_uploader("Upload Annual Report (PDF)", type="pdf")

if uploaded_file:
    st.info(f"📄 Loaded: {uploaded_file.name}")
    
    if st.button("🔍 Analyze Report", use_container_width=True):
        with st.spinner("Reading PDF... this may take a moment"):
            # Extract text from PDF
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            pdf_text = ""
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    pdf_text += text
            
            if not pdf_text:
                st.error("Could not extract text from PDF. Make sure it's not scanned/image-only.")
                st.stop()
            
            # Limit text to first 100k chars to stay within token limits
            pdf_text = pdf_text[:100000]
        
        with st.spinner("Analyzing with Claude... this takes 1-2 minutes"):
            try:
                client = anthropic.Anthropic(api_key=api_key)
                
                prompt = """Analyze this annual report across these 27 qualitative points.

For EACH point, provide exactly:
- Assessment: [Strong|Moderate|Weak|Missing]
- Evidence: [1-2 key facts/quotes from report]
- Page: [page number if available]

Be concise. Analyst needs to scan quickly.

STRATEGIC & OPERATIONAL:
1. Management Philosophy & Capital Discipline
2. Business Model & Competitive Positioning
3. Organizational Capability Building
4. Scale & Operational Efficiency Focus

RISK MANAGEMENT:
5. Enterprise Risk Management Framework
6. Risk Mitigations (commodity prices, geopolitical, forex, supply chain)
7. Supply Chain Resilience & Diversification
8. Technology & Innovation Risk

GOVERNANCE:
9. Related Party Transaction Disclosures
10. Board Composition & Independence
11. Internal Control System Adequacy
12. Governance Philosophy

CAPITAL ALLOCATION:
13. Dividend Policy Rationale
14. Capex Philosophy & ROCE Focus
15. Cash Position & Liquidity

MARKET POSITIONING:
16. Customer Concentration & Dependency
17. Market Share & Competitive Dynamics
18. Product Differentiation

MACRO TAILWINDS:
19. Industry Tailwinds & Structural Trends
20. Government Policy & Regulatory Support
21. Export/Geographic Diversification

SUSTAINABILITY:
22. Energy & Environmental Investments
23. Labor Practices & Employee Well-being
24. Community Investment

FINANCIAL HEALTH:
25. Balance Sheet Strength & Debt Philosophy
26. Working Capital Management
27. Accounting Quality & Transparency

RED FLAGS TO REPORT:
- Missing risk disclosures
- Vague mitigation strategies
- Excessive related-party transactions
- Capital allocation concerns
- Concentration risks
- Governance weaknesses

Format clearly. Use bullet points. Keep each assessment to 2-3 lines max."""

                message = client.messages.create(
                    model="claude-opus-4-6",
                    max_tokens=4000,
                    messages=[
                        {
                            "role": "user",
                            "content": f"{prompt}\n\n---ANNUAL REPORT TEXT---\n{pdf_text}"
                        }
                    ]
                )
                
                results = message.content[0].text
                
                st.success("✅ Analysis Complete!")
                st.markdown("---")
                
                # Display results
                st.markdown(results)
                
                # Copy box
                st.markdown("---")
                st.markdown("**Copy results below:**")
                st.text_area("", value=results, height=300, disabled=True)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Make sure your API key is valid. Get one at https://console.anthropic.com")
