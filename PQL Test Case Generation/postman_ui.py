import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
from testgeneration import PQLTestGenerator, API_SCHEMA

# Configure the page
st.set_page_config(
    page_title="API Tester - POSTMAN Style",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for POSTMAN-like styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #FF6C37;
        text-align: center;
        margin-bottom: 1rem;
    }
    .postman-orange {
        background-color: #FF6C37;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-weight: 600;
    }
    .request-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #FF6C37;
        margin-bottom: 1rem;
    }
    .response-section {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007acc;
        margin-bottom: 1rem;
    }
    .success-badge {
        background-color: #28a745;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .error-badge {
        background-color: #dc3545;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .tab-content {
        padding: 1rem 0;
    }
    .test-case-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #FF6C37;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

class PostmanAPITester:
    def __init__(self):
        self.base_url = "https://api.sikkasoft.com/v4/practice_query"
        self.default_headers = {
            "Request-Key": "fd34a6e6b28b2a272eef19682e6c428d",
            "Content-Type": "application/json"
        }
        self.default_body = {
            "pql": "SELECT [patients.patient_id] FROM [patients]",
            "limit": "50",
            "offset": "0"
        }
    
    def execute_request(self, headers, body):
        """Execute the API request"""
        try:
            start_time = datetime.now()
            response = requests.post(
                self.base_url,
                headers=headers,
                json=body,
                timeout=30
            )
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            result = {
                "success": True,
                "status_code": response.status_code,
                "response_time": response_time,
                "headers": dict(response.headers),
                "response_text": response.text
            }
            
            try:
                result["data"] = response.json()
            except json.JSONDecodeError:
                result["data"] = {"raw_response": response.text}
                
            return result
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": None,
                "response_time": 0
            }

def format_json(data):
    """Format JSON with proper indentation"""
    try:
        return json.dumps(data, indent=2)
    except:
        return str(data)

def create_test_cases_tab():
    """Create the Test Cases tab content"""
    st.markdown("### 🧪 PQL Test Case Generator")
    st.markdown("Generate comprehensive test cases for different APIs")
    
    # Initialize test generator
    test_generator = PQLTestGenerator(API_SCHEMA)
    
    # API Selection
    available_apis = list(test_generator.api_map.keys())
    selected_api = st.selectbox("Select API", available_apis, key="api_selector")
    
    if selected_api:
        # Generate test cases
        with st.spinner("Generating test cases..."):
            test_cases = test_generator.generate_all_test_cases(selected_api)
        
        # Display test cases count
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Test Cases", len(test_cases))
        with col2:
            st.metric("API Fields", len(test_generator.get_api_fields(selected_api)))
        with col3:
            st.metric("API Selected", selected_api)
        
        # Test cases display
        st.markdown("### 📋 Generated Test Cases")
        
        if test_cases:
            for i, test_case in enumerate(test_cases, 1):
                with st.expander(f"Test Case {i}: {test_case['test_case']}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown("**Request Body:**")
                        st.code(format_json(test_case['request_body']), language='json')
                    
                    with col2:
                        if st.button(f"Use This", key=f"use_{i}", use_container_width=True):
                            # Update the request body in the main tab automatically
                            st.session_state.body_input = format_json(test_case['request_body'])
                            st.success("✅ Test case loaded into Request Body!")
            
            # Download option
            test_cases_json = json.dumps({
                "api_name": selected_api,
                "total_test_cases": len(test_cases),
                "test_cases": test_cases
            }, indent=2)
            
            st.download_button(
                label="📥 Download Test Cases as JSON",
                data=test_cases_json,
                file_name=f"pql_test_cases_{selected_api}.json",
                mime="application/json",
                use_container_width=True
            )
        else:
            st.warning(f"No test cases generated for {selected_api}. Check if the API has valid fields.")

def main():
    tester = PostmanAPITester()
    
    # Initialize session state
    if 'response_history' not in st.session_state:
        st.session_state.response_history = []
    if 'current_response' not in st.session_state:
        st.session_state.current_response = None
    if 'body_input' not in st.session_state:
        st.session_state.body_input = format_json(tester.default_body)
    
    # Header
    st.markdown('<div class="main-header">🌐 API TESTER - POSTMAN STYLE</div>', unsafe_allow_html=True)
    
    # Navigation menu in sidebar
    with st.sidebar:
        st.markdown('<div class="postman-orange">NAVIGATION</div>', unsafe_allow_html=True)
        
        # Navigation options
        nav_options = {
            "📤 Request & Response": "request",
            "🧪 Test Cases": "test_cases"
        }
        
        selected_nav = st.radio(
            "Go to:",
            options=list(nav_options.keys()),
            key="navigation"
        )
    
    # Main content based on navigation selection
    if selected_nav == "📤 Request & Response":
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown('<div class="request-section">', unsafe_allow_html=True)
            st.markdown('### 📤 REQUEST')
            
            # URL Section
            st.markdown("**🌐 API Endpoint**")
            st.code(f"POST {tester.base_url}")
            
            # Headers Section
            st.markdown("**📝 Headers**")
            headers_input = st.text_area(
                "Request Headers (JSON)",
                value=format_json(tester.default_headers),
                height=150,
                key="headers_input"
            )
            
            # Body Section
            st.markdown("**📦 Request Body**")
            body_input = st.text_area(
                "Request Body (JSON)",
                value=st.session_state.body_input,
                height=200,
                key="body_input"
            )
            
            # Parse inputs
            try:
                headers = json.loads(headers_input)
            except:
                st.error("Invalid JSON in Headers")
                headers = tester.default_headers
                
            try:
                body = json.loads(body_input)
            except:
                st.error("Invalid JSON in Body")
                body = tester.default_body
            
            # Execute button
            if st.button("🚀 SEND REQUEST", use_container_width=True, type="primary"):
                with st.spinner("Sending request..."):
                    result = tester.execute_request(headers, body)
                    st.session_state.current_response = result
                    
                    # Add to history
                    history_item = {
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                        "status": result["status_code"] if result["success"] else "Error",
                        "method": "POST",
                        "url": tester.base_url,
                        "response_time": result.get("response_time", 0)
                    }
                    st.session_state.response_history.insert(0, history_item)
                    
                    # Keep only last 10 history items
                    if len(st.session_state.response_history) > 10:
                        st.session_state.response_history = st.session_state.response_history[:10]
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="response-section">', unsafe_allow_html=True)
            st.markdown('### 📥 RESPONSE')
            
            if st.session_state.current_response:
                result = st.session_state.current_response
                
                # Status and metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if result["success"]:
                        st.markdown(f'<div class="success-badge">STATUS: {result["status_code"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="error-badge">ERROR</div>', unsafe_allow_html=True)
                
                with col2:
                    st.metric("Time", f"{result.get('response_time', 0):.0f} ms")
                
                with col3:
                    if result["success"] and "data" in result:
                        if "items" in result["data"]:
                            st.metric("Items", len(result["data"]["items"]))
                        else:
                            st.metric("Items", "N/A")
                    else:
                        st.metric("Items", "N/A")
                
                # Response tabs
                tab3, tab2, tab1, tab4 = st.tabs(["Response", "Headers", "Table", "History"])
                
                with tab1:
                    if result["success"]:
                        response_data = result.get("data", {})
                        
                        # Display metrics if available
                        if isinstance(response_data, dict):
                            metric_cols = st.columns(4)
                            with metric_cols[0]:
                                if "total_count" in response_data:
                                    st.metric("Total Count", response_data["total_count"])
                            with metric_cols[1]:
                                if "execution_time" in response_data:
                                    st.metric("Exec Time", f"{response_data['execution_time']}ms")
                            with metric_cols[2]:
                                if "limit" in response_data:
                                    st.metric("Limit", response_data["limit"])
                            with metric_cols[3]:
                                if "offset" in response_data:
                                    st.metric("Offset", response_data["offset"])
                        
                        # Display data
                        if "items" in response_data and response_data["items"]:
                            st.markdown("**📊 Data Table**")
                            df = pd.DataFrame(response_data["items"])
                            st.dataframe(df, use_container_width=True)
                            
                            # Download button
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download CSV",
                                data=csv,
                                file_name="api_response.csv",
                                mime="text/csv"
                            )
                        else:
                            st.json(response_data)
                    else:
                        st.error(f"Request failed: {result.get('error', 'Unknown error')}")
                
                with tab2:
                    st.markdown("**📝 Response Headers**")
                    if result["success"] and "headers" in result:
                        headers_df = pd.DataFrame(list(result["headers"].items()), columns=["Header", "Value"])
                        st.dataframe(headers_df, use_container_width=True)
                    else:
                        st.info("No response headers available")
                
                with tab3:
                    st.markdown("**📄 Raw Response**")
                    if result["success"]:
                        st.code(format_json(result.get("data", {})), language="json")
                    else:
                        st.code(result.get("response_text", "No response"), language="text")
                
                with tab4:
                    st.markdown("**📋 Request History**")
                    if st.session_state.response_history:
                        history_df = pd.DataFrame(st.session_state.response_history)
                        st.dataframe(history_df, use_container_width=True)
                        
                        if st.button("Clear History"):
                            st.session_state.response_history = []
                            st.rerun()
                    else:
                        st.info("No request history yet")
            
            else:
                st.info("👆 Click 'SEND REQUEST' to execute the API call and see results here")
                st.markdown("""
                **Expected Response Format:**
                ```json
                {
                    "offset": "0",
                    "limit": "50", 
                    "total_count": "399",
                    "execution_time": "37",
                    "pagination": { ... },
                    "items": [ ... ]
                }
                ```
                """)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    elif selected_nav == "🧪 Test Cases":
        create_test_cases_tab()
    
    # Quick examples in sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown('<div class="postman-orange">QUICK EXAMPLES</div>', unsafe_allow_html=True)
        
        st.markdown("**🔧 Example Queries**")
        
        examples = {
            "Basic Patient Query": {
                "pql": "SELECT [patients.patient_id] FROM [patients]",
                "limit": "50",
                "offset": "0"
            },
            "All Patient Fields": {
                "pql": "SELECT * FROM [patients]",
                "limit": "25",
                "offset": "0"
            },
            "Count Patients": {
                "pql": "SELECT COUNT([patients.patient_id]) FROM [patients]",
                "limit": "10",
                "offset": "0"
            },
            "Patient with Conditions": {
                "pql": "SELECT [patients.patient_id], [patients.first_name] FROM [patients] WHERE [patients.patient_id] > 1000",
                "limit": "20",
                "offset": "0"
            }
        }
        
        for name, body in examples.items():
            if st.button(f"📋 {name}", key=f"example_{name}"):
                st.session_state.body_input = format_json(body)
                st.rerun()
        
        st.markdown("---")
        st.markdown("**📊 API Info**")
        st.markdown("""
        - **Method**: POST
        - **Base URL**: `https://api.sikkasoft.com/v4/practice_query`
        - **Auth**: Request-Key header
        - **Format**: JSON
        """)

if __name__ == "__main__":
    main()