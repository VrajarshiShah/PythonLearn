import streamlit as st
import requests
import json
import pandas as pd

# Configure the page
st.set_page_config(
    page_title="Simple API Tester",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Simple API Tester")

class SimpleAPITester:
    def __init__(self):
        self.base_url = "https://api.sikkasoft.com/v4/practice_query"
        self.headers = {
            "Request-Key": "d924e57fd5c68b4cf43033cbb0692db9",
            "Content-Type": "application/json"
        }
    
    def execute_query(self, pql_query: str, limit: int = 50, offset: int = 0):
        """Execute a PQL query and return the response"""
        payload = {
            "pql": pql_query,
            "limit": limit,
            "offset": offset
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return {
                "success": True,
                "data": response.json(),
                "status_code": response.status_code,
                "headers": dict(response.headers)
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }

def main():
    tester = SimpleAPITester()
    
    # Input section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        pql_query = st.text_area(
            "PQL Query",
            value="SELECT [patients.patient_id] FROM [patients]",
            height=100
        )
    
    with col2:
        limit = st.number_input("Limit", min_value=1, max_value=1000, value=50)
        offset = st.number_input("Offset", min_value=0, value=0)
    
    # Execute button
    if st.button("🚀 Execute Query", type="primary", use_container_width=True):
        with st.spinner("Executing query..."):
            result = tester.execute_query(pql_query, limit, offset)
            
            # Display results in tabs
            tab1, tab2, tab3 = st.tabs(["📊 Response", "🔧 Request Details", "📋 Raw Response"])
            
            with tab1:
                if result["success"]:
                    st.success(f"✅ Request Successful (Status: {result['status_code']})")
                    
                    response_data = result["data"]
                    
                    # Display metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Records", response_data.get("total_count", "N/A"))
                    with col2:
                        st.metric("Items Returned", len(response_data.get("items", [])))
                    with col3:
                        st.metric("Execution Time", f"{response_data.get('execution_time', 'N/A')}ms")
                    
                    # Display data table
                    if "items" in response_data and response_data["items"]:
                        df = pd.DataFrame(response_data["items"])
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("No data items in response")
                        
                else:
                    st.error(f"❌ Request Failed: {result.get('error', 'Unknown error')}")
                    if result.get('status_code'):
                        st.write(f"Status Code: {result['status_code']}")
            
            with tab2:
                st.subheader("🌐 URL")
                st.code(tester.base_url)
                
                st.subheader("📝 Headers")
                headers_df = pd.DataFrame(list(tester.headers.items()), columns=["Header", "Value"])
                st.dataframe(headers_df, hide_index=True, use_container_width=True)
                
                st.subheader("📦 Request Body")
                request_body = {
                    "pql": pql_query,
                    "limit": limit,
                    "offset": offset
                }
                st.json(request_body)
            
            with tab3:
                if result["success"]:
                    st.subheader("📄 Full Response JSON")
                    st.json(result["data"])
                else:
                    st.error("No response data available due to error")

if __name__ == "__main__":
    main()