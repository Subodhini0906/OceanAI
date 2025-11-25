"""
Streamlit UI for Autonomous QA Agent
"""
import streamlit as st
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from backend.vector_store import VectorStore
from backend.document_parser import DocumentParser
import json
import requests
from typing import List, Dict
import ollama

# Page configuration
st.set_page_config(
    page_title="Autonomous QA Agent",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = None
if 'kb_built' not in st.session_state:
    st.session_state.kb_built = False
if 'uploaded_docs' not in st.session_state:
    st.session_state.uploaded_docs = []
if 'html_content' not in st.session_state:
    st.session_state.html_content = ""
if 'test_cases' not in st.session_state:
    st.session_state.test_cases = []
if 'selected_test_case' not in st.session_state:
    st.session_state.selected_test_case = None

# Initialize vector store
if st.session_state.vector_store is None:
    st.session_state.vector_store = VectorStore()

# Title
st.title("🤖 Autonomous QA Agent")
st.markdown("**Test Case and Selenium Script Generation System**")

# Sidebar
with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Select Page",
        ["📚 Knowledge Base", "🧪 Test Cases", "💻 Script Generation"],
        index=0
    )
    
    st.divider()
    st.header("Status")
    if st.session_state.kb_built:
        st.success("✅ Knowledge Base Built")
        st.info(f"📄 Documents: {st.session_state.vector_store.get_collection_count()} chunks")
    else:
        st.warning("⚠️ Knowledge Base Not Built")

# Main content based on selected page
if page == "📚 Knowledge Base":
    st.header("Knowledge Base Ingestion")
    
    tab1, tab2 = st.tabs(["Upload Documents", "Build Knowledge Base"])
    
    with tab1:
        st.subheader("Upload Support Documents")
        st.markdown("Upload product specifications, UI/UX guides, API documentation, etc.")
        
        uploaded_files = st.file_uploader(
            "Choose files",
            type=['txt', 'md', 'json', 'pdf', 'html'],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            for uploaded_file in uploaded_files:
                if uploaded_file.name not in [doc['name'] for doc in st.session_state.uploaded_docs]:
                    # Parse file content
                    content = uploaded_file.read()
                    text_content = DocumentParser.parse_uploaded_file(content, uploaded_file.name)
                    
                    st.session_state.uploaded_docs.append({
                        'name': uploaded_file.name,
                        'content': text_content,
                        'type': uploaded_file.type
                    })
                    st.success(f"✅ Uploaded: {uploaded_file.name}")
        
        # Display uploaded documents
        if st.session_state.uploaded_docs:
            st.subheader("Uploaded Documents")
            for doc in st.session_state.uploaded_docs:
                with st.expander(f"📄 {doc['name']}"):
                    st.text_area("Content", doc['content'], height=200, key=f"doc_{doc['name']}")
        
        st.divider()
        
        st.subheader("Upload HTML File")
        html_file = st.file_uploader("Upload checkout.html", type=['html'])
        html_text = st.text_area("Or paste HTML content", height=300)
        
        if html_file:
            st.session_state.html_content = html_file.read().decode('utf-8')
            st.success("✅ HTML file uploaded")
        elif html_text:
            st.session_state.html_content = html_text
            st.success("✅ HTML content saved")
        
        if st.session_state.html_content:
            with st.expander("View HTML Content"):
                st.code(st.session_state.html_content[:1000] + "..." if len(st.session_state.html_content) > 1000 else st.session_state.html_content)
    
    with tab2:
        st.subheader("Build Knowledge Base")
        
        if not st.session_state.uploaded_docs:
            st.warning("⚠️ Please upload at least one document first")
        elif not st.session_state.html_content:
            st.warning("⚠️ Please upload HTML content first")
        else:
            if st.button("🔨 Build Knowledge Base", type="primary"):
                with st.spinner("Building knowledge base..."):
                    try:
                        # Clear existing knowledge base
                        st.session_state.vector_store.clear()
                        
                        # Add documents to vector store
                        documents_to_add = []
                        for doc in st.session_state.uploaded_docs:
                            documents_to_add.append({
                                'content': doc['content'],
                                'metadata': {
                                    'source': doc['name'],
                                    'type': doc['type'],
                                    'document_type': 'support_doc'
                                }
                            })
                        
                        # Add HTML content
                        documents_to_add.append({
                            'content': st.session_state.html_content,
                            'metadata': {
                                'source': 'checkout.html',
                                'type': 'text/html',
                                'document_type': 'html'
                            }
                        })
                        
                        # Add to vector store
                        chunk_count = st.session_state.vector_store.add_documents(documents_to_add)
                        st.session_state.kb_built = True
                        
                        st.success(f"✅ Knowledge Base Built Successfully!")
                        st.info(f"📊 Total chunks: {chunk_count}")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ Error building knowledge base: {str(e)}")
        
        if st.session_state.kb_built:
            st.success("✅ Knowledge base is ready for test case generation!")

elif page == "🧪 Test Cases":
    st.header("Test Case Generation")
    
    if not st.session_state.kb_built:
        st.warning("⚠️ Please build the knowledge base first in the 'Knowledge Base' section")
    else:
        st.subheader("Generate Test Cases")
        
        # Query input
        query = st.text_area(
            "Enter your test case query",
            placeholder="e.g., Generate all positive and negative test cases for the discount code feature.",
            height=100
        )
        
        # Example queries
        with st.expander("💡 Example Queries"):
            st.markdown("""
            - Generate all positive and negative test cases for the discount code feature
            - Create test cases for form validation (name, email, address fields)
            - Generate test cases for shipping method selection
            - Create test cases for cart functionality (add items, update quantities)
            - Generate test cases for payment processing
            """)
        
        if st.button("🚀 Generate Test Cases", type="primary"):
            if not query:
                st.error("Please enter a query")
            else:
                with st.spinner("Generating test cases using RAG pipeline..."):
                    try:
                        # Retrieve relevant context from vector store
                        relevant_docs = st.session_state.vector_store.search(query, n_results=5)
                        
                        # Build context
                        context = "\n\n".join([
                            f"Source: {doc['metadata'].get('source', 'unknown')}\n{doc['content']}"
                            for doc in relevant_docs
                        ])
                        
                        # Generate test cases using Ollama (or other LLM)
                        prompt = f"""You are a QA expert. Based on the following documentation and HTML structure, generate comprehensive test cases.

Documentation Context:
{context}

User Query: {query}

Generate test cases in the following JSON format:
{{
  "test_cases": [
    {{
      "test_id": "TC-001",
      "feature": "Feature Name",
      "test_scenario": "Description of test scenario",
      "test_type": "positive|negative",
      "steps": ["step1", "step2", "step3"],
      "expected_result": "Expected outcome",
      "grounded_in": "source_document_name"
    }}
  ]
}}

Only generate test cases based on the provided documentation. Do not hallucinate features.
"""
                        
                        # Use Ollama for generation
                        try:
                            response = ollama.chat(
                                model='llama2',  # or 'mistral', 'codellama', etc.
                                messages=[
                                    {
                                        'role': 'system',
                                        'content': 'You are a QA expert who generates test cases based strictly on provided documentation.'
                                    },
                                    {
                                        'role': 'user',
                                        'content': prompt
                                    }
                                ]
                            )
                            result = response['message']['content']
                        except Exception as e:
                            st.warning(f"Ollama not available, using fallback. Error: {e}")
                            # Fallback: simple structured output
                            result = f"""
{{
  "test_cases": [
    {{
      "test_id": "TC-001",
      "feature": "Discount Code",
      "test_scenario": "Apply valid discount code SAVE15",
      "test_type": "positive",
      "steps": [
        "Navigate to checkout page",
        "Add items to cart",
        "Enter discount code 'SAVE15'",
        "Click 'Apply Discount' button",
        "Verify 15% discount is applied"
      ],
      "expected_result": "Total price is reduced by 15%",
      "grounded_in": "product_specs.md"
    }}
  ]
}}
"""
                        
                        # Try to parse JSON from result
                        try:
                            # Extract JSON from markdown code blocks if present
                            if "```json" in result:
                                json_start = result.find("```json") + 7
                                json_end = result.find("```", json_start)
                                result = result[json_start:json_end].strip()
                            elif "```" in result:
                                json_start = result.find("```") + 3
                                json_end = result.find("```", json_start)
                                result = result[json_start:json_end].strip()
                            
                            test_cases_data = json.loads(result)
                            st.session_state.test_cases = test_cases_data.get('test_cases', [])
                            
                            st.success(f"✅ Generated {len(st.session_state.test_cases)} test cases!")
                        except json.JSONDecodeError:
                            st.warning("Could not parse JSON, displaying raw output")
                            st.code(result)
                            # Create a simple test case from the output
                            st.session_state.test_cases = [{
                                "test_id": "TC-001",
                                "feature": "Generated Test",
                                "test_scenario": query,
                                "test_type": "positive",
                                "steps": ["See generated output"],
                                "expected_result": "Test passes",
                                "grounded_in": "documentation"
                            }]
                        
                        # Display context used
                        with st.expander("📚 Context Used for Generation"):
                            for doc in relevant_docs:
                                st.markdown(f"**Source:** {doc['metadata'].get('source', 'unknown')}")
                                st.text(doc['content'][:500] + "...")
                                st.divider()
                        
                    except Exception as e:
                        st.error(f"❌ Error generating test cases: {str(e)}")
        
        # Display generated test cases
        if st.session_state.test_cases:
            st.divider()
            st.subheader("Generated Test Cases")
            
            for i, test_case in enumerate(st.session_state.test_cases):
                with st.expander(f"🧪 {test_case.get('test_id', f'TC-{i+1:03d}')}: {test_case.get('feature', 'Unknown Feature')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Test ID:** {test_case.get('test_id', 'N/A')}")
                        st.markdown(f"**Feature:** {test_case.get('feature', 'N/A')}")
                        st.markdown(f"**Type:** {test_case.get('test_type', 'N/A')}")
                    with col2:
                        st.markdown(f"**Grounded In:** {test_case.get('grounded_in', 'N/A')}")
                    
                    st.markdown(f"**Scenario:** {test_case.get('test_scenario', 'N/A')}")
                    
                    st.markdown("**Steps:**")
                    steps = test_case.get('steps', [])
                    for j, step in enumerate(steps, 1):
                        st.markdown(f"{j}. {step}")
                    
                    st.markdown(f"**Expected Result:** {test_case.get('expected_result', 'N/A')}")
                    
                    if st.button(f"Select for Script Generation", key=f"select_{i}"):
                        st.session_state.selected_test_case = test_case
                        st.success(f"✅ Selected: {test_case.get('test_id')}")

elif page == "💻 Script Generation":
    st.header("Selenium Script Generation")
    
    if not st.session_state.kb_built:
        st.warning("⚠️ Please build the knowledge base first")
    elif not st.session_state.test_cases:
        st.warning("⚠️ Please generate test cases first")
    elif not st.session_state.selected_test_case:
        st.warning("⚠️ Please select a test case from the 'Test Cases' page")
    else:
        st.subheader("Selected Test Case")
        test_case = st.session_state.selected_test_case
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Test ID:** {test_case.get('test_id')}")
            st.markdown(f"**Feature:** {test_case.get('feature')}")
        with col2:
            st.markdown(f"**Type:** {test_case.get('test_type')}")
            st.markdown(f"**Grounded In:** {test_case.get('grounded_in')}")
        
        st.markdown(f"**Scenario:** {test_case.get('test_scenario')}")
        
        if st.button("🚀 Generate Selenium Script", type="primary"):
            with st.spinner("Generating Selenium script..."):
                try:
                    # Retrieve relevant documentation
                    query = f"{test_case.get('feature')} {test_case.get('test_scenario')}"
                    relevant_docs = st.session_state.vector_store.search(query, n_results=3)
                    
                    # Build context
                    doc_context = "\n\n".join([
                        f"Source: {doc['metadata'].get('source', 'unknown')}\n{doc['content']}"
                        for doc in relevant_docs
                    ])
                    
                    # Get HTML content
                    html_snippet = st.session_state.html_content[:2000]  # Limit HTML for prompt
                    
                    # Generate Selenium script
                    prompt = f"""You are a Selenium (Python) expert. Generate a complete, runnable Selenium test script based on the following test case and HTML structure.

Test Case:
{json.dumps(test_case, indent=2)}

HTML Structure (first 2000 chars):
{html_snippet}

Documentation Context:
{doc_context}

Requirements:
1. Use appropriate Selenium selectors (IDs, names, CSS selectors, XPath) based on the actual HTML
2. Include proper waits (WebDriverWait, expected_conditions)
3. Use Page Object Model if appropriate
4. Include proper error handling
5. Make the script fully executable
6. Use clear variable names and comments
7. Import necessary Selenium modules

Generate ONLY the Python code, no explanations outside code comments.
"""
                    
                    try:
                        response = ollama.chat(
                            model='codellama',  # or 'llama2', 'mistral', etc.
                            messages=[
                                {
                                    'role': 'system',
                                    'content': 'You are a Selenium Python expert. Generate clean, executable test scripts.'
                                },
                                {
                                    'role': 'user',
                                    'content': prompt
                                }
                            ]
                        )
                        script = response['message']['content']
                    except Exception as e:
                        st.warning(f"Ollama not available, using template. Error: {e}")
                        # Fallback template
                        script = f"""from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

def test_{test_case.get('test_id', 'TC001').lower().replace('-', '_')}():
    \"\"\"
    {test_case.get('test_scenario', 'Test scenario')}
    \"\"\"
    driver = webdriver.Chrome()
    driver.get("file:///path/to/checkout.html")
    
    try:
        # Test steps
        # TODO: Implement based on test case steps
        {chr(10).join([f'        # {step}' for step in test_case.get('steps', [])])}
        
        # Verify expected result
        # Expected: {test_case.get('expected_result', 'Test passes')}
        
        print("Test passed!")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_{test_case.get('test_id', 'TC001').lower().replace('-', '_')}()
"""
                    
                    # Clean up script (remove markdown code blocks if present)
                    if "```python" in script:
                        script_start = script.find("```python") + 8
                        script_end = script.find("```", script_start)
                        script = script[script_start:script_end].strip()
                    elif "```" in script:
                        script_start = script.find("```") + 3
                        script_end = script.find("```", script_start)
                        script = script[script_start:script_end].strip()
                    
                    st.success("✅ Selenium script generated!")
                    
                    # Display script
                    st.subheader("Generated Script")
                    st.code(script, language='python')
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Script",
                        data=script,
                        file_name=f"{test_case.get('test_id', 'test')}.py",
                        mime="text/x-python"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Error generating script: {str(e)}")

# Footer
st.divider()
st.markdown("---")
st.markdown("**Autonomous QA Agent** - Test Case and Script Generation System")

