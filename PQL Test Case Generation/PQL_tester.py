import streamlit as st
import requests
import json
import pandas as pd
from typing import Dict, Any, List
import time
from api_data import API_SCHEMA

# Configure the page
st.set_page_config(
    page_title="PQL Query Tester",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
    }
    .section-header {
        font-size: 1.4rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .subsection-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #4a5568;
        margin: 1rem 0 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .success-box {
        background-color: #f0fff4;
        border: 1px solid #9ae6b4;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #fed7d7;
        border: 1px solid #feb2b2;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #ebf8ff;
        border: 1px solid #90cdf4;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .request-box {
        background-color: #f7fafc;
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        margin: 0.5rem 0;
        max-height: 200px;
        overflow-y: auto;
    }
    .response-box {
        background-color: #f0fff4;
        border: 2px solid #9ae6b4;
        border-radius: 8px;
        padding: 1rem;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        margin: 0.5rem 0;
        max-height: 400px;
        overflow-y: auto;
    }
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    .tab-content {
        padding: 1rem 0;
    }
    .field-info {
        background-color: #f8fafc;
        border-left: 4px solid #667eea;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

class PQLTester:
    def __init__(self):
        self.base_url = "https://api.sikkasoft.com/v4/practice_query"
        self.headers = {
            "Request-Key": "d924e57fd5c68b4cf43033cbb0692db9",
            "Content-Type": "application/json"
        }
    
    def execute_query(self, pql_query: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
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
                "headers": dict(response.headers),
                "request_payload": payload
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "status": "failed",
                "request_payload": payload
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON response: {str(e)}",
                "status": "failed",
                "request_payload": payload
            }

def get_api_fields(api_name: str) -> List[str]:
    """Get fields for a specific API"""
    for api in API_SCHEMA['items']:
        if api['api_name'] == api_name:
            return api['api_fields']
    return []

def get_api_info(api_name: str) -> Dict[str, Any]:
    """Get complete API information"""
    for api in API_SCHEMA['items']:
        if api['api_name'] == api_name:
            return api
    return {}

def generate_api_specific_queries(api_name: str) -> List[Dict[str, Any]]:
    """Generate comprehensive test queries using specific API fields from JSON schema"""
    api_info = get_api_info(api_name)
    if not api_info:
        return []
    
    fields = api_info['api_fields']
    if not fields:
        return []
    
    test_queries = []
    
    # Display API field information
    st.session_state.current_api_fields = fields
    st.session_state.current_api_name = api_name
    
    # 1. Basic SELECT with all API-specific fields
    field_list = ", ".join([f"[{api_name}.{field}]" for field in fields])
    test_queries.append({
        "name": f"Basic SELECT - All {api_name} Fields",
        "query": f"SELECT {field_list} FROM [{api_name}]",
        "description": f"Select all {api_name} fields: {', '.join(fields)}",
        "type": "SELECT_BASIC",
        "fields_used": fields
    })
    
    # 2. SELECT with specific fields (first 3 fields)
    if len(fields) >= 3:
        selected_fields = fields[:3]
        field_list = ", ".join([f"[{api_name}.{field}]" for field in selected_fields])
        test_queries.append({
            "name": f"SELECT {api_name} Core Fields",
            "query": f"SELECT {field_list} FROM [{api_name}]",
            "description": f"Select core {api_name} fields: {', '.join(selected_fields)}",
            "type": "SELECT_SPECIFIC",
            "fields_used": selected_fields
        })
    
    # 3. EXISTS operator with practice_id or similar ID field
    id_fields = [f for f in fields if any(keyword in f.lower() for keyword in ['id', 'practice', 'patient', 'cust'])]
    if id_fields and api_name != 'appointments':
        id_field = id_fields[0]
        test_queries.append({
            "name": "EXISTS Operator",
            "query": f"SELECT [{api_name}.{id_field}] FROM [{api_name}] WHERE EXISTS (SELECT 1 FROM [appointments] WHERE [appointments.practice_id] = [{api_name}.{id_field}])",
            "description": f"Check EXISTS operator using {id_field} field",
            "type": "EXISTS",
            "fields_used": [id_field]
        })
    
    # 4. COUNT with EXISTS
    if id_fields:
        id_field = id_fields[0]
        test_queries.append({
            "name": "COUNT with EXISTS",
            "query": f"SELECT COUNT([{api_name}.{id_field}]) FROM [{api_name}] WHERE EXISTS (SELECT 1 FROM [appointments] WHERE [appointments.practice_id] = [{api_name}.{id_field}])",
            "description": f"Count records with EXISTS condition using {id_field}",
            "type": "COUNT_EXISTS",
            "fields_used": [id_field]
        })
    
    # 5. COUNT all records
    if fields:
        test_queries.append({
            "name": f"COUNT {api_name} Records",
            "query": f"SELECT COUNT([{api_name}.{fields[0]}]) FROM [{api_name}]",
            "description": f"Count total records in {api_name}",
            "type": "COUNT",
            "fields_used": [fields[0]]
        })
    
    # 6. MAX and MIN functions
    numeric_fields = [f for f in fields if any(keyword in f.lower() for keyword in ['id', 'amount', 'number', 'count', 'total', 'balance', 'quantity'])]
    if numeric_fields:
        field = numeric_fields[0]
        test_queries.append({
            "name": "MAX and MIN Functions",
            "query": f"SELECT MAX([{api_name}.{field}]), MIN([{api_name}.{field}]) FROM [{api_name}]",
            "description": f"Get maximum and minimum values of {field}",
            "type": "MAX_MIN",
            "fields_used": [field]
        })
    
    # 7. AVG function
    if numeric_fields:
        field = numeric_fields[0]
        test_queries.append({
            "name": "AVG Function",
            "query": f"SELECT AVG([{api_name}.{field}]) FROM [{api_name}]",
            "description": f"Calculate average of {field}",
            "type": "AVG",
            "fields_used": [field]
        })
    
    # 8. LIKE operator
    string_fields = [f for f in fields if any(keyword in f.lower() for keyword in ['name', 'description', 'note', 'comment', 'title', 'label'])]
    if string_fields:
        field = string_fields[0]
        test_queries.append({
            "name": "LIKE Operator",
            "query": f"SELECT [{api_name}.{field}] FROM [{api_name}] WHERE [{api_name}.{field}] LIKE '%example%'",
            "description": f"Search using LIKE operator on {field}",
            "type": "LIKE",
            "fields_used": [field]
        })
    
    # 9. IN operator
    if id_fields:
        field = id_fields[0]
        test_queries.append({
            "name": "IN Operator",
            "query": f"SELECT [{api_name}.{field}] FROM [{api_name}] WHERE [{api_name}.{field}] IN (1, 2, 3)",
            "description": f"Filter using IN operator on {field}",
            "type": "IN",
            "fields_used": [field]
        })
    
    # 10. BETWEEN operator
    if numeric_fields:
        field = numeric_fields[0]
        test_queries.append({
            "name": "BETWEEN Operator",
            "query": f"SELECT [{api_name}.{field}] FROM [{api_name}] WHERE [{api_name}.{field}] BETWEEN 1 AND 100",
            "description": f"Filter using BETWEEN operator on {field}",
            "type": "BETWEEN",
            "fields_used": [field]
        })
    
    # 11. ORDER BY
    if len(fields) >= 2:
        order_field = fields[0]
        display_fields = fields[:2]
        field_list = ", ".join([f"[{api_name}.{field}]" for field in display_fields])
        test_queries.append({
            "name": "ORDER BY",
            "query": f"SELECT {field_list} FROM [{api_name}] ORDER BY [{api_name}.{order_field}] ASC",
            "description": f"Order results by {order_field}",
            "type": "ORDER_BY",
            "fields_used": display_fields
        })
    
    # 12. DISTINCT
    if fields:
        field = fields[0]
        test_queries.append({
            "name": "DISTINCT Values",
            "query": f"SELECT DISTINCT [{api_name}.{field}] FROM [{api_name}]",
            "description": f"Get distinct values of {field}",
            "type": "DISTINCT",
            "fields_used": [field]
        })
    
    # 13. HAVING clause
    if numeric_fields and len(numeric_fields) >= 2:
        field1, field2 = numeric_fields[:2]
        test_queries.append({
            "name": "HAVING Clause",
            "query": f"SELECT SUM([{api_name}.{field1}]) FROM [{api_name}] HAVING COUNT([{api_name}.{field2}]) < 100",
            "description": f"Use HAVING clause with SUM({field1}) and COUNT({field2})",
            "type": "HAVING",
            "fields_used": [field1, field2]
        })
    
    # 14. Complex WHERE with multiple conditions
    where_fields = [f for f in fields if any(keyword in f.lower() for keyword in ['id', 'status', 'date', 'type'])]
    if len(where_fields) >= 2:
        field1, field2 = where_fields[:2]
        test_queries.append({
            "name": "Complex WHERE Conditions",
            "query": f"SELECT [{api_name}.{field1}], [{api_name}.{field2}] FROM [{api_name}] WHERE [{api_name}.{field1}] IS NOT NULL AND [{api_name}.{field2}] IS NOT NULL",
            "description": f"Multiple conditions on {field1} and {field2}",
            "type": "COMPLEX_WHERE",
            "fields_used": [field1, field2]
        })
    
    # 15. All fields selection (wildcard)
    test_queries.append({
        "name": f"All {api_name} Fields (Wildcard)",
        "query": f"SELECT * FROM [{api_name}]",
        "description": f"Select all {api_name} fields using wildcard",
        "type": "SELECT_ALL",
        "fields_used": fields
    })
    
    # 16. JOIN queries with related tables
    if any('id' in field.lower() for field in fields):
        common_fields = [f for f in fields if any(keyword in f.lower() for keyword in ['patient', 'practice', 'cust', 'provider', 'guarantor'])]
        if common_fields:
            join_field = common_fields[0]
            # Find compatible tables for JOIN
            join_tables = ['patients', 'appointments', 'claims', 'transactions', 'providers', 'guarantors']
            for join_table in join_tables:
                join_fields = get_api_fields(join_table)
                if join_fields and any(join_field.split('_')[-1] in f.lower() for f in join_fields):
                    # Find matching field in join table
                    matching_fields = [f for f in join_fields if join_field.split('_')[-1] in f.lower()]
                    if matching_fields:
                        join_match_field = matching_fields[0]
                        test_queries.append({
                            "name": f"LEFT JOIN with {join_table}",
                            "query": f"SELECT [{api_name}.{fields[0]}], [{join_table}.{join_fields[0]}] FROM [{api_name}] LEFT JOIN [{join_table}] ON [{api_name}.{join_field}] = [{join_table}.{join_match_field}]",
                            "description": f"LEFT JOIN with {join_table} using {join_field}",
                            "type": "LEFT_JOIN",
                            "fields_used": [fields[0], join_field]
                        })
                        break
    
    return test_queries

def format_request_body(payload: Dict[str, Any]) -> str:
    """Format request body with proper JSON formatting and commas"""
    formatted_json = json.dumps(payload, indent=2)
    lines = formatted_json.split('\n')
    formatted_lines = []
    
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        if (stripped_line and 
            not stripped_line.endswith('{') and 
            not stripped_line.endswith('[') and
            not stripped_line.endswith(',') and
            i < len(lines) - 1 and
            not lines[i + 1].strip().startswith('}') and
            not lines[i + 1].strip().startswith(']')):
            line = line + ','
        formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def display_request_response(result: Dict[str, Any], query_info: Dict[str, Any]):
    """Display request body and API response in a structured way"""
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Data Preview", "🔧 Request & Response", "📋 Full Response", "📈 Metrics"])
    
    with tab1:
        if result["success"] and "items" in result["data"] and result["data"]["items"]:
            df = pd.DataFrame(result["data"]["items"])
            st.dataframe(df, use_container_width=True)
            
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"{query_info['name'].replace(' ', '_').lower()}_results.csv",
                mime="text/csv"
            )
        else:
            st.info("No data to display in table format")
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="subsection-header">📤 Request Body</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="request-box">', unsafe_allow_html=True)
            
            request_body = result["request_payload"]
            formatted_request = format_request_body(request_body)
            st.code(formatted_request, language="json")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="subsection-header">🌐 API Details</div>', unsafe_allow_html=True)
            st.markdown(f"""
            - **Method**: POST
            - **Endpoint**: `https://api.sikkasoft.com/v4/practice_query`
            - **Content-Type**: application/json
            - **Request-Key**: `d924e57fd5c68b4cf43033cbb0692db9`
            """)
        
        with col2:
            st.markdown('<div class="subsection-header">📥 API Response</div>', unsafe_allow_html=True)
            if result["success"]:
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.success(f"✅ Success (Status: {result.get('status_code', 'N/A')})")
                
                response_data = result["data"]
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Records", response_data.get("total_count", "N/A"))
                with col2:
                    st.metric("Execution Time", f"{response_data.get('execution_time', 'N/A')}ms")
                with col3:
                    st.metric("Items Returned", len(response_data.get("items", [])))
                
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="error-box">', unsafe_allow_html=True)
                st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
                st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        if result["success"]:
            st.markdown('<div class="subsection-header">📄 Complete Response JSON</div>', unsafe_allow_html=True)
            st.markdown('<div class="response-box">', unsafe_allow_html=True)
            st.json(result["data"])
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("No response data available due to error")
    
    with tab4:
        if result["success"]:
            response_data = result["data"]
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("HTTP Status", result.get("status_code", "N/A"))
            with col2:
                st.metric("Total Count", response_data.get("total_count", "N/A"))
            with col3:
                st.metric("Execution Time", f"{response_data.get('execution_time', 'N/A')}ms")
            with col4:
                st.metric("Items in Response", len(response_data.get("items", [])))
            
            st.markdown("---")
            st.markdown('<div class="subsection-header">📋 Response Structure</div>', unsafe_allow_html=True)
            
            if "items" in response_data and response_data["items"]:
                first_item = response_data["items"][0]
                st.write("**First Item Fields:**")
                fields = list(first_item.keys())
                cols = st.columns(3)
                for i, field in enumerate(fields):
                    cols[i % 3].code(field)
            
            if "pagination" in response_data:
                st.markdown("---")
                st.markdown('<div class="subsection-header">🔗 Pagination</div>', unsafe_allow_html=True)
                pagination = response_data["pagination"]
                for key, value in pagination.items():
                    st.write(f"**{key.replace('_', ' ').title()}:** `{value}`")

def show_query_execution_modal(query_info: Dict[str, Any], tester: PQLTester, query_limit: int):
    """Show modal for editing request body before execution"""
    
    # Initialize session state for request editing
    if f"request_body_{query_info['name']}" not in st.session_state:
        st.session_state[f"request_body_{query_info['name']}"] = {
            "pql": query_info["query"],
            "limit": query_limit,
            "offset": 0
        }
    
    request_body = st.session_state[f"request_body_{query_info['name']}"]
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-header">⚡ Execute: {query_info["name"]}</div>', unsafe_allow_html=True)
    
    # Show fields used in this query
    if "fields_used" in query_info:
        st.markdown('<div class="field-info">', unsafe_allow_html=True)
        st.markdown(f"**Fields used in this query:** `{', '.join(query_info['fields_used'])}`")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display the original query
    st.markdown("**PQL Query:**")
    st.code(query_info["query"], language="sql")
    
    st.markdown("**Description:**")
    st.write(query_info["description"])
    
    # Editable request parameters
    st.markdown("---")
    st.markdown('<div class="subsection-header">🔧 Request Configuration</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        updated_pql = st.text_area(
            "PQL Query",
            value=request_body["pql"],
            height=100,
            help="Modify the PQL query if needed"
        )
    
    with col2:
        updated_limit = st.number_input(
            "Limit",
            min_value=1,
            max_value=1000,
            value=request_body["limit"],
            help="Number of records to return"
        )
        
        updated_offset = st.number_input(
            "Offset",
            min_value=0,
            value=request_body["offset"],
            help="Number of records to skip"
        )
    
    # Update request body
    updated_request_body = {
        "pql": updated_pql,
        "limit": updated_limit,
        "offset": updated_offset
    }
    
    st.session_state[f"request_body_{query_info['name']}"] = updated_request_body
    
    # Execute button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Execute Query", use_container_width=True, type="primary"):
            with st.spinner("Executing query..."):
                result = tester.execute_query(
                    updated_request_body["pql"], 
                    updated_request_body["limit"], 
                    updated_request_body["offset"]
                )
                st.session_state[f"result_{query_info['name']}"] = result
                st.session_state[f"current_query_info"] = query_info
                st.session_state["show_execution_results"] = True
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    tester = PQLTester()
    
    st.markdown('<div class="main-header">🔍 PQL Query Tester</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">⚙️ Configuration</div>', unsafe_allow_html=True)
        
        available_apis = [api['api_name'] for api in API_SCHEMA['items']]
        selected_api = st.selectbox(
            "Select API",
            available_apis,
            index=0 if available_apis else None,
            help="Choose the API to generate test queries for"
        )
        
        # Show API field information
        api_info = get_api_info(selected_api)
        if api_info:
            st.markdown(f"**{selected_api} Fields:**")
            st.code(", ".join(api_info['api_fields']))
        
        query_limit = st.slider(
            "Results Limit",
            min_value=10,
            max_value=100,
            value=50,
            help="Number of records to return per query"
        )
        
        if st.button("🎯 Generate API-Specific Test Queries", use_container_width=True):
            st.session_state.test_queries = generate_api_specific_queries(selected_api)
            st.session_state.selected_api = selected_api
            # Clear previous results when generating new queries
            if "show_execution_results" in st.session_state:
                del st.session_state["show_execution_results"]
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if 'test_queries' in st.session_state and st.session_state.selected_api == selected_api:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f'<div class="section-header">📋 Test Queries for {selected_api}</div>', unsafe_allow_html=True)
            
            # Show API-specific information
            current_fields = st.session_state.get('current_api_fields', [])
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.info(f"🎯 **{selected_api} API Specific Queries** - Using fields: {', '.join(current_fields)}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            query_types = {}
            for query in st.session_state.test_queries:
                query_type = query['type']
                if query_type not in query_types:
                    query_types[query_type] = []
                query_types[query_type].append(query)
            
            for query_type, queries in query_types.items():
                with st.expander(f"{query_type.replace('_', ' ').title()} ({len(queries)} queries)"):
                    for i, query_info in enumerate(queries):
                        st.write(f"**{query_info['name']}**")
                        st.write(f"*{query_info['description']}*")
                        
                        # Show fields used in this specific query
                        if "fields_used" in query_info:
                            st.markdown(f"<div class='field-info'>Fields: `{', '.join(query_info['fields_used'])}`</div>", 
                                      unsafe_allow_html=True)
                        
                        st.code(query_info['query'], language="sql")
                        
                        if st.button(f"🚀 Execute", key=f"exec_{query_type}_{i}", use_container_width=True):
                            st.session_state[f"current_query_{query_type}_{i}"] = query_info
                            st.session_state["current_query_key"] = f"{query_type}_{i}"
                            st.session_state["show_execution_modal"] = f"{query_type}_{i}"
                            st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">📊 Query Results</div>', unsafe_allow_html=True)
        
        # Show execution modal if a query is selected
        if "show_execution_modal" in st.session_state:
            current_key = st.session_state["show_execution_modal"]
            query_info = st.session_state.get(f"current_query_{current_key}")
            
            if query_info:
                show_query_execution_modal(query_info, tester, query_limit)
        
        # Show execution results
        if "show_execution_results" in st.session_state and st.session_state.show_execution_results:
            query_info = st.session_state.get("current_query_info")
            result = st.session_state.get(f"result_{query_info['name']}")
            
            if query_info and result:
                st.markdown(f"### {query_info['name']}")
                st.markdown(f"**Query Type:** `{query_info['type']}`")
                st.markdown(f"**Description:** {query_info['description']}")
                
                # Show fields used
                if "fields_used" in query_info:
                    st.markdown(f"**Fields Used:** `{', '.join(query_info['fields_used'])}`")
                
                st.markdown("**PQL Query:**")
                st.code(query_info['query'], language="sql")
                
                display_request_response(result, query_info)
                
                # Button to go back to query list
                if st.button("← Back to Query List", use_container_width=True):
                    st.session_state["show_execution_results"] = False
                    if "show_execution_modal" in st.session_state:
                        del st.session_state["show_execution_modal"]
                    st.rerun()
        
        elif 'test_queries' in st.session_state:
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.info("👆 Select a query and configure the request body to execute it")
            st.markdown("""
            **New Features:**
            - ✅ **API Field Visibility**: See exactly which fields are used in each query
            - ✅ **Request Body Editing**: Modify PQL, limit, and offset before execution
            - ✅ **Real-time Configuration**: Customize your API calls
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.info("👈 Select an API and generate test queries to see results here")
            st.markdown("""
            **API-Specific PQL Testing:**
            - ✅ Uses actual API field names from JSON schema
            - ✅ Dynamic field detection for any API
            - ✅ Comprehensive PQL functionality testing
            - ✅ Real-world query scenarios using specific fields
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #718096; font-size: 0.9rem;'>"
        "PQL Query Tester • Built with Streamlit • Sikkasoft API v4"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()