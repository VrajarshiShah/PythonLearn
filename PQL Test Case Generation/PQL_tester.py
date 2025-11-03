import streamlit as st
import requests
import json
import pandas as pd
from typing import Dict, Any, List
import time
import random
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
    .fields-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 0.5rem;
        margin: 1rem 0;
    }
    .field-item {
        background-color: #edf2f7;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-family: 'Courier New', monospace;
    }
    .new-field-highlight {
        background-color: #e6fffa !important;
        border: 2px solid #38b2ac !important;
        font-weight: 600;
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

def display_api_fields_grid(fields: List[str], title: str = "Available Fields", highlight_fields: List[str] = None):
    """Display API fields in a nice grid layout with highlighting for new fields"""
    st.write(f"**{title}:**")
    
    if highlight_fields is None:
        highlight_fields = []
    
    # Create a grid of fields
    cols = st.columns(4)
    col_index = 0
    
    for i, field in enumerate(fields):
        with cols[col_index]:
            if field in highlight_fields:
                st.markdown(f'<div class="field-item new-field-highlight">✨ {field}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="field-item">{field}</div>', unsafe_allow_html=True)
        col_index = (col_index + 1) % 4

def generate_api_specific_queries(api_name: str, new_fields: List[str] = None) -> List[Dict[str, Any]]:
    """Generate comprehensive test queries using specific API fields from JSON schema"""
    api_info = get_api_info(api_name)
    if not api_info:
        return []
    
    fields = api_info['api_fields']
    if not fields:
        return []
    
    # Combine original fields with newly added fields
    all_fields = fields.copy()
    if new_fields:
        # Add new fields that don't already exist
        for field in new_fields:
            if field.strip() and field not in all_fields:
                all_fields.append(field.strip())
    
    test_queries = []
    
    # Store API fields in session state for display
    st.session_state.current_api_fields = all_fields
    st.session_state.current_api_name = api_name
    st.session_state.new_fields = new_fields or []
    
    # Display all available fields for this API
    with st.expander(f"📋 All Available {api_name} Fields ({len(all_fields)} fields)", expanded=False):
        display_api_fields_grid(all_fields, highlight_fields=new_fields or [])
        if new_fields:
            st.info(f"✨ **{len(new_fields)} newly added field(s) highlighted**")
    
    # 1. Basic SELECT with all API-specific fields (including new ones)
    field_list = ", ".join([f"[{api_name}.{field}]" for field in all_fields])
    test_queries.append({
        "name": f"Basic SELECT - All {api_name} Fields",
        "query": f"SELECT {field_list} FROM [{api_name}]",
        "description": f"Select all {api_name} fields including newly added ones",
        "type": "SELECT_BASIC",
        "fields_used": all_fields,
        "all_fields": True,
        "api_fields": all_fields,
        "new_fields": new_fields or []
    })
    
    # 2. SELECT with specific fields (include new fields + first few original fields)
    display_fields = []
    if new_fields:
        display_fields.extend(new_fields[:2])  # Include up to 2 new fields
    # Add original fields to make total 8-10 fields
    remaining_slots = max(6, 10 - len(display_fields))
    display_fields.extend(fields[:remaining_slots])
    
    field_list = ", ".join([f"[{api_name}.{field}]" for field in display_fields])
    test_queries.append({
        "name": f"SELECT {api_name} Core Fields",
        "query": f"SELECT {field_list} FROM [{api_name}]",
        "description": f"Select core {api_name} fields including newly added ones",
        "type": "SELECT_SPECIFIC",
        "fields_used": display_fields,
        "api_fields": all_fields,
        "new_fields": new_fields or []
    })
    
    # 3. COUNT all records using ID field (prefer new ID fields if available)
    id_fields = [f for f in all_fields if "id" in f.lower()]
    if new_fields:
        # Prefer new ID fields
        new_id_fields = [f for f in new_fields if "id" in f.lower()]
        if new_id_fields:
            count_field = random.choice(new_id_fields)
        else:
            count_field = random.choice(id_fields) if id_fields else all_fields[0]
    else:
        count_field = random.choice(id_fields) if id_fields else all_fields[0]
    
    test_queries.append({
        "name": f"COUNT {api_name} Records",
        "query": f"SELECT COUNT([{api_name}.{count_field}]) FROM [{api_name}]",
        "description": f"Count total records in {api_name} using {count_field}",
        "type": "COUNT",
        "fields_used": [count_field],
        "api_fields": all_fields,
        "new_fields": new_fields or []
    })
    
    # 4. EXISTS operator with ID fields (prefer new ID fields)
    id_fields = [f for f in all_fields if any(keyword in f.lower() for keyword in ['id', 'practice', 'patient', 'cust'])]
    if id_fields:
        # Prefer new ID fields
        if new_fields:
            new_id_fields = [f for f in new_fields if any(keyword in f.lower() for keyword in ['id', 'practice', 'patient', 'cust'])]
            id_field = new_id_fields[0] if new_id_fields else id_fields[0]
        else:
            id_field = id_fields[0]
        
        # Find a compatible table for EXISTS
        compatible_tables = ['patients', 'appointments', 'claims', 'transactions', 'providers']
        for table in compatible_tables:
            if table != api_name and get_api_fields(table):
                test_queries.append({
                    "name": "EXISTS Operator",
                    "query": f"SELECT [{api_name}.{id_field}] FROM [{api_name}] WHERE EXISTS (SELECT 1 FROM [{table}] WHERE [{table}.practice_id] = [{api_name}.{id_field}])",
                    "description": f"Check EXISTS operator using {id_field} field with {table} table",
                    "type": "EXISTS",
                    "fields_used": [id_field],
                    "api_fields": all_fields,
                    "new_fields": new_fields or []
                })
                break
    
    # 5. MAX and MIN functions with numeric fields (prefer new numeric fields)
    numeric_fields = [f for f in all_fields if any(keyword in f.lower() for keyword in ['id', 'amount', 'number', 'count', 'total', 'balance', 'quantity', 'time', 'length'])]
    if numeric_fields:
        # Prefer new numeric fields
        if new_fields:
            new_numeric_fields = [f for f in new_fields if any(keyword in f.lower() for keyword in ['id', 'amount', 'number', 'count', 'total', 'balance', 'quantity', 'time', 'length'])]
            field = new_numeric_fields[0] if new_numeric_fields else numeric_fields[0]
        else:
            field = numeric_fields[0]
        
        test_queries.append({
            "name": "MAX and MIN Functions",
            "query": f"SELECT MAX([{api_name}.{field}]), MIN([{api_name}.{field}]) FROM [{api_name}]",
            "description": f"Get maximum and minimum values of {field}",
            "type": "MAX_MIN",
            "fields_used": [field],
            "api_fields": all_fields,
            "new_fields": new_fields or []
        })
    
    # 6. AVG function with numeric fields (prefer new numeric fields)
    if numeric_fields:
        if new_fields:
            new_numeric_fields = [f for f in new_fields if any(keyword in f.lower() for keyword in ['id', 'amount', 'number', 'count', 'total', 'balance', 'quantity', 'time', 'length'])]
            field = new_numeric_fields[0] if new_numeric_fields else numeric_fields[0]
        else:
            field = numeric_fields[0]
        
        test_queries.append({
            "name": "AVG Function",
            "query": f"SELECT AVG([{api_name}.{field}]) FROM [{api_name}]",
            "description": f"Calculate average of {field}",
            "type": "AVG",
            "fields_used": [field],
            "api_fields": all_fields,
            "new_fields": new_fields or []
        })
    
    # 7. LIKE operator with string fields (prefer new string fields)
    string_fields = [f for f in all_fields if any(keyword in f.lower() for keyword in ['name', 'description', 'note', 'comment', 'title', 'label', 'status', 'type'])]
    if string_fields:
        if new_fields:
            new_string_fields = [f for f in new_fields if any(keyword in f.lower() for keyword in ['name', 'description', 'note', 'comment', 'title', 'label', 'status', 'type'])]
            field = new_string_fields[0] if new_string_fields else string_fields[0]
        else:
            field = string_fields[0]
        
        test_queries.append({
            "name": "LIKE Operator",
            "query": f"SELECT [{api_name}.{field}] FROM [{api_name}] WHERE [{api_name}.{field}] LIKE '%example%'",
            "description": f"Search using LIKE operator on {field}",
            "type": "LIKE",
            "fields_used": [field],
            "api_fields": all_fields,
            "new_fields": new_fields or []
        })
    
    # 8. IN operator with ID fields (prefer new ID fields)
    if id_fields:
        if new_fields:
            new_id_fields = [f for f in new_fields if any(keyword in f.lower() for keyword in ['id', 'practice', 'patient', 'cust'])]
            field = new_id_fields[0] if new_id_fields else id_fields[0]
        else:
            field = id_fields[0]
        
        test_queries.append({
            "name": "IN Operator",
            "query": f"SELECT [{api_name}.{field}] FROM [{api_name}] WHERE [{api_name}.{field}] IN (1, 2, 3)",
            "description": f"Filter using IN operator on {field}",
            "type": "IN",
            "fields_used": [field],
            "api_fields": all_fields,
            "new_fields": new_fields or []
        })
    
    # 9. BETWEEN operator with numeric/date fields (prefer new fields)
    if numeric_fields:
        if new_fields:
            new_numeric_fields = [f for f in new_fields if any(keyword in f.lower() for keyword in ['id', 'amount', 'number', 'count', 'total', 'balance', 'quantity', 'time', 'length'])]
            field = new_numeric_fields[0] if new_numeric_fields else numeric_fields[0]
        else:
            field = numeric_fields[0]
        
        test_queries.append({
            "name": "BETWEEN Operator",
            "query": f"SELECT [{api_name}.{field}] FROM [{api_name}] WHERE [{api_name}.{field}] BETWEEN 1 AND 100",
            "description": f"Filter using BETWEEN operator on {field}",
            "type": "BETWEEN",
            "fields_used": [field],
            "api_fields": all_fields,
            "new_fields": new_fields or []
        })
    
    # 10. ORDER BY with fields (include new fields)
    if len(all_fields) >= 2:
        # Use a new field for ordering if available, otherwise first field
        order_field = new_fields[0] if new_fields else all_fields[0]
        display_fields = [order_field, all_fields[1] if len(all_fields) > 1 else all_fields[0]]
        field_list = ", ".join([f"[{api_name}.{field}]" for field in display_fields])
        test_queries.append({
            "name": "ORDER BY",
            "query": f"SELECT {field_list} FROM [{api_name}] ORDER BY [{api_name}.{order_field}] ASC",
            "description": f"Order results by {order_field}",
            "type": "ORDER_BY",
            "fields_used": display_fields,
            "api_fields": all_fields,
            "new_fields": new_fields or []
        })
    
    # 11. DISTINCT with fields (prefer new fields)
    if all_fields:
        field = new_fields[0] if new_fields else all_fields[0]
        test_queries.append({
            "name": "DISTINCT Values",
            "query": f"SELECT DISTINCT [{api_name}.{field}] FROM [{api_name}]",
            "description": f"Get distinct values of {field}",
            "type": "DISTINCT",
            "fields_used": [field],
            "api_fields": all_fields,
            "new_fields": new_fields or []
        })
    
    # 12. WHERE with multiple conditions (include new fields)
    where_fields = [f for f in all_fields if any(keyword in f.lower() for keyword in ['id', 'status', 'date', 'type', 'name'])]
    if len(where_fields) >= 2:
        # Include new fields in WHERE conditions
        field1 = where_fields[0]
        field2 = where_fields[1] if len(where_fields) > 1 else where_fields[0]
        test_queries.append({
            "name": "Complex WHERE Conditions",
            "query": f"SELECT [{api_name}.{field1}], [{api_name}.{field2}] FROM [{api_name}] WHERE [{api_name}.{field1}] IS NOT NULL AND [{api_name}.{field2}] IS NOT NULL",
            "description": f"Multiple conditions on {field1} and {field2}",
            "type": "COMPLEX_WHERE",
            "fields_used": [field1, field2],
            "api_fields": all_fields,
            "new_fields": new_fields or []
        })
    
    # 13. All fields selection (wildcard) - includes new fields automatically
    test_queries.append({
        "name": f"All {api_name} Fields (Wildcard)",
        "query": f"SELECT * FROM [{api_name}]",
        "description": f"Select all {api_name} fields using wildcard (includes new fields)",
        "type": "SELECT_ALL",
        "fields_used": all_fields,
        "all_fields": True,
        "api_fields": all_fields,
        "new_fields": new_fields or []
    })
    
    # 14. JOIN queries with related tables (use new ID fields if available)
    if id_fields:
        join_field = new_fields[0] if new_fields and any('id' in f.lower() for f in new_fields) else id_fields[0]
        # Find compatible tables for JOIN
        join_tables = ['patients', 'appointments', 'claims', 'transactions', 'providers', 'guarantors']
        for join_table in join_tables:
            if join_table != api_name:
                join_fields = get_api_fields(join_table)
                if join_fields:
                    # Use first field from join table for display
                    join_display_field = join_fields[0]
                    test_queries.append({
                        "name": f"LEFT JOIN with {join_table}",
                        "query": f"SELECT [{api_name}.{all_fields[0]}], [{join_table}.{join_display_field}] FROM [{api_name}] LEFT JOIN [{join_table}] ON [{api_name}.{join_field}] = [{join_table}.practice_id]",
                        "description": f"LEFT JOIN with {join_table} using {join_field}",
                        "type": "LEFT_JOIN",
                        "fields_used": [all_fields[0], join_field],
                        "api_fields": all_fields,
                        "new_fields": new_fields or []
                    })
                    break
    
    # 15. Date range queries (if date fields exist, prefer new date fields)
    date_fields = [f for f in all_fields if 'date' in f.lower()]
    if date_fields:
        if new_fields:
            new_date_fields = [f for f in new_fields if 'date' in f.lower()]
            date_field = new_date_fields[0] if new_date_fields else date_fields[0]
        else:
            date_field = date_fields[0]
        
        test_queries.append({
            "name": "Date Range Query",
            "query": f"SELECT [{api_name}.{date_field}] FROM [{api_name}] WHERE [{api_name}.{date_field}] >= '2023-01-01'",
            "description": f"Filter by date range using {date_field}",
            "type": "DATE_RANGE",
            "fields_used": [date_field],
            "api_fields": all_fields,
            "new_fields": new_fields or []
        })
    
    # 16. GROUP BY with aggregate functions (include new fields)
    if len(all_fields) >= 2:
        group_field = new_fields[0] if new_fields else all_fields[0]
        agg_field = all_fields[1] if len(all_fields) > 1 else all_fields[0]
        test_queries.append({
            "name": "GROUP BY with COUNT",
            "query": f"SELECT [{api_name}.{group_field}], COUNT([{api_name}.{agg_field}]) FROM [{api_name}] GROUP BY [{api_name}.{group_field}]",
            "description": f"Group by {group_field} with count of {agg_field}",
            "type": "GROUP_BY",
            "fields_used": [group_field, agg_field],
            "api_fields": all_fields,
            "new_fields": new_fields or []
        })
    
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
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Data Preview", "🔧 Request & Response", "📋 Full Response", "📈 Metrics", "🔍 API Fields"])
    
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
    
    with tab5:
        # Show API fields information
        if "api_fields" in query_info:
            st.markdown('<div class="subsection-header">🔍 API Fields Information</div>', unsafe_allow_html=True)
            
            st.write(f"**All Available {st.session_state.current_api_name} Fields ({len(query_info['api_fields'])} fields):**")
            display_api_fields_grid(query_info["api_fields"], highlight_fields=query_info.get("new_fields", []))
            
            if query_info.get("new_fields"):
                st.info(f"✨ **{len(query_info['new_fields'])} newly added field(s) highlighted in green**")
            
            st.markdown("---")
            
            # Show fields used in this specific query
            if "fields_used" in query_info:
                if query_info.get("all_fields", False):
                    st.write(f"**This query uses all {len(query_info['fields_used'])} available fields**")
                    if query_info.get("new_fields"):
                        st.write(f"**Including {len(query_info['new_fields'])} newly added fields:** `{', '.join(query_info['new_fields'])}`")
                else:
                    st.write(f"**Fields used in this query ({len(query_info['fields_used'])} fields):**")
                    display_api_fields_grid(query_info["fields_used"], highlight_fields=query_info.get("new_fields", []))

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
    
    # Show API fields information
    if "api_fields" in query_info:
        with st.expander(f"📋 View All {len(query_info['api_fields'])} API Fields", expanded=False):
            display_api_fields_grid(query_info["api_fields"], f"All {st.session_state.current_api_name} Fields", 
                                  highlight_fields=query_info.get("new_fields", []))
            if query_info.get("new_fields"):
                st.info(f"✨ **{len(query_info['new_fields'])} newly added field(s) highlighted**")
    
    # Show fields used in this query
    if "fields_used" in query_info:
        st.markdown('<div class="field-info">', unsafe_allow_html=True)
        if query_info.get("all_fields", False):
            st.markdown(f"**All {len(query_info['fields_used'])} fields from {st.session_state.current_api_name} are used in this query**")
            if query_info.get("new_fields"):
                st.markdown(f"**Including {len(query_info['new_fields'])} newly added fields:** `{', '.join(query_info['new_fields'])}`")
        else:
            used_fields = query_info['fields_used']
            new_used_fields = [f for f in used_fields if f in query_info.get("new_fields", [])]
            if new_used_fields:
                st.markdown(f"**Fields used in this query:** `{', '.join(used_fields)}`")
                st.markdown(f"**✨ Newly added fields in this query:** `{', '.join(new_used_fields)}`")
            else:
                st.markdown(f"**Fields used in this query:** `{', '.join(used_fields)}`")
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
            st.markdown(f"**{selected_api} API Fields Preview:**")
            fields_preview = api_info['api_fields'][:8]  # Show first 8 fields
            for field in fields_preview:
                st.code(field, language=None)
            if len(api_info['api_fields']) > 8:
                st.info(f"... and {len(api_info['api_fields']) - 8} more fields")
        
        # User input for newly added fields
        st.markdown("---")
        st.markdown('<div class="subsection-header">✨ Add New Fields</div>', unsafe_allow_html=True)
        
        new_fields_input = st.text_area(
            "Newly Added Fields",
            placeholder="Enter field names separated by commas\ne.g., new_field1, new_field2, custom_field",
            help="Add field names that are not in the original API schema but should be included in test queries"
        )
        
        # Parse new fields
        new_fields = []
        if new_fields_input:
            new_fields = [field.strip() for field in new_fields_input.split(',') if field.strip()]
            if new_fields:
                st.success(f"✅ Added {len(new_fields)} new field(s): {', '.join(new_fields)}")
        
        query_limit = st.slider(
            "Results Limit",
            min_value=10,
            max_value=100,
            value=50,
            help="Number of records to return per query"
        )
        
        if st.button("🎯 Generate API-Specific Test Queries", use_container_width=True):
            st.session_state.test_queries = generate_api_specific_queries(selected_api, new_fields)
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
            new_fields_count = len(st.session_state.get('new_fields', []))
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            if new_fields_count > 0:
                st.info(f"🎯 **{selected_api} API Specific Queries** - Total {len(current_fields)} fields available ({new_fields_count} newly added)")
            else:
                st.info(f"🎯 **{selected_api} API Specific Queries** - Total {len(current_fields)} fields available")
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
                            if query_info.get("all_fields", False):
                                new_count = len(query_info.get("new_fields", []))
                                if new_count > 0:
                                    st.markdown(f"<div class='field-info'>Uses all {len(query_info['fields_used'])} {selected_api} fields (including {new_count} newly added)</div>", 
                                              unsafe_allow_html=True)
                                else:
                                    st.markdown(f"<div class='field-info'>Uses all {len(query_info['fields_used'])} {selected_api} fields</div>", 
                                              unsafe_allow_html=True)
                            else:
                                used_fields = query_info['fields_used']
                                new_used = [f for f in used_fields if f in query_info.get("new_fields", [])]
                                if new_used:
                                    st.markdown(f"<div class='field-info'>Fields: `{', '.join(used_fields)}`<br>✨ New: `{', '.join(new_used)}`</div>", 
                                              unsafe_allow_html=True)
                                else:
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
                    if query_info.get("all_fields", False):
                        new_count = len(query_info.get("new_fields", []))
                        if new_count > 0:
                            st.markdown(f"**Fields Used:** All {len(query_info['fields_used'])} {st.session_state.current_api_name} fields (including {new_count} newly added)")
                            st.markdown(f"**✨ New Fields:** `{', '.join(query_info.get('new_fields', []))}`")
                        else:
                            st.markdown(f"**Fields Used:** All {len(query_info['fields_used'])} {st.session_state.current_api_name} fields")
                    else:
                        used_fields = query_info['fields_used']
                        new_used = [f for f in used_fields if f in query_info.get("new_fields", [])]
                        if new_used:
                            st.markdown(f"**Fields Used:** `{', '.join(used_fields)}`")
                            st.markdown(f"**✨ New Fields in Query:** `{', '.join(new_used)}`")
                        else:
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
            **Features:**
            - ✅ **API Field Visibility**: See exactly which fields are used in each query
            - ✅ **Request Body Editing**: Modify PQL, limit, and offset before execution
            - ✅ **Real-time Configuration**: Customize your API calls
            - ✅ **Complete Field Coverage**: All test queries use actual API fields
            - ✅ **API Fields Tab**: New tab showing all available API fields for reference
            - ✅ **✨ New Fields Support**: Add custom fields to include in all test queries
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
            - ✅ ✨ **New**: Add custom fields to test queries
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