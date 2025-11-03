import json
import random
from typing import List, Dict, Any

class PQLTestGenerator:
    def __init__(self, api_data: Dict[str, Any]):
        self.api_data = api_data
        self.test_cases = []
        self.test_counter = 1
        
    def generate_test_cases(self, api_names: List[str] = None) -> List[Dict[str, Any]]:
        """Generate PQL test cases for specified APIs or all APIs"""
        if api_names is None:
            # Generate for all APIs
            api_names = [api['api_name'] for api in self.api_data['items']]
        
        for api_name in api_names:
            api_info = self.get_api_info(api_name)
            if api_info:
                print(f"\n🔧 Generating test cases for API: {api_name}")
                print(f"📊 Available fields: {len(api_info['api_fields'])} fields")
                self.generate_api_test_cases(api_info)
        
        return self.test_cases
    
    def get_api_info(self, api_name: str) -> Dict[str, Any]:
        """Get API information by name"""
        for api in self.api_data['items']:
            if api['api_name'] == api_name:
                return api
        return None
    
    def get_available_apis(self) -> List[str]:
        """Get list of all available API names"""
        return [api['api_name'] for api in self.api_data['items']]
    
    def generate_api_test_cases(self, api_info: Dict[str, Any]):
        """Generate test cases for a specific API"""
        api_name = api_info['api_name']
        fields = api_info['api_fields']
        
        print(f"   📝 Generating {10} different test cases...")
        
        # Test Case 1: Basic SELECT query
        self.generate_basic_select_test(api_name, fields)
        
        # Test Case 2: SELECT with WHERE clause
        self.generate_where_clause_test(api_name, fields)
        
        # Test Case 3: Aggregate functions
        self.generate_aggregate_test(api_name, fields)
        
        # Test Case 4: LIKE operator
        self.generate_like_test(api_name, fields)
        
        # Test Case 5: IN operator
        self.generate_in_test(api_name, fields)
        
        # Test Case 6: BETWEEN operator
        self.generate_between_test(api_name, fields)
        
        # Test Case 7: ORDER BY
        self.generate_order_by_test(api_name, fields)
        
        # Test Case 8: DISTINCT
        self.generate_distinct_test(api_name, fields)
        
        # Test Case 9: All fields selection
        self.generate_all_fields_test(api_name, fields)
        
        # Test Case 10: Complex WHERE with multiple conditions
        self.generate_complex_where_test(api_name, fields)
    
    def generate_basic_select_test(self, api_name: str, fields: List[str]):
        """Generate basic SELECT query test case"""
        if len(fields) >= 3:
            selected_fields = random.sample(fields, min(3, len(fields)))
            field_list = ", ".join([f"[{api_name}.{field}]" for field in selected_fields])
            
            test_case = {
                "Test Case ID": f"TC_{api_name.upper()}_{self.test_counter:03d}",
                "Test Description": f"Check basic SELECT query for {api_name} API",
                "Request Body": {
                    "pql": f"SELECT {field_list} FROM [{api_name}]",
                    "limit": "50",
                    "offset": "0"
                },
                "Expected Results": f"Should return {len(selected_fields)} selected fields from {api_name}",
                "Fields Used": selected_fields
            }
            self.test_cases.append(test_case)
            self.test_counter += 1
    
    def generate_where_clause_test(self, api_name: str, fields: List[str]):
        """Generate WHERE clause test case"""
        # Find suitable fields for WHERE clause
        where_fields = self._find_where_fields(fields)
        
        if where_fields:
            field = random.choice(where_fields)
            field_type = self._get_field_type(field)
            
            if field_type == "string":
                condition = f"[{api_name}.{field}] = 'example_value'"
            elif field_type == "numeric":
                condition = f"[{api_name}.{field}] > 0"
            elif field_type == "date":
                condition = f"[{api_name}.{field}] > '2024-01-01'"
            elif field_type == "status":
                condition = f"[{api_name}.{field}] = 'Active'"
            else:
                condition = f"[{api_name}.{field}] IS NOT NULL"
            
            test_case = {
                "Test Case ID": f"TC_{api_name.upper()}_{self.test_counter:03d}",
                "Test Description": f"Check WHERE clause with condition for {api_name} API",
                "Request Body": {
                    "pql": f"SELECT [{api_name}.{field}] FROM [{api_name}] WHERE {condition}",
                    "limit": "50",
                    "offset": "0"
                },
                "Expected Results": f"Should return records where {field} meets the condition",
                "Fields Used": [field]
            }
            self.test_cases.append(test_case)
            self.test_counter += 1
    
    def generate_aggregate_test(self, api_name: str, fields: List[str]):
        """Generate aggregate function test case"""
        numeric_fields = [f for f in fields if self._is_numeric_field(f)]
        
        if numeric_fields:
            field = random.choice(numeric_fields)
            aggregate_functions = ["COUNT", "SUM", "AVG", "MAX", "MIN"]
            
            for agg_func in random.sample(aggregate_functions, min(2, len(aggregate_functions))):
                test_case = {
                    "Test Case ID": f"TC_{api_name.upper()}_{self.test_counter:03d}",
                    "Test Description": f"Check {agg_func} aggregate function for {api_name} API",
                    "Request Body": {
                        "pql": f"SELECT {agg_func}([{api_name}.{field}]) FROM [{api_name}]",
                        "limit": "50",
                        "offset": "0"
                    },
                    "Expected Results": f"Should return {agg_func} of {field}",
                    "Fields Used": [field]
                }
                self.test_cases.append(test_case)
                self.test_counter += 1
    
    def generate_like_test(self, api_name: str, fields: List[str]):
        """Generate LIKE operator test case"""
        string_fields = [f for f in fields if self._is_string_field(f)]
        
        if string_fields:
            field = random.choice(string_fields)
            test_case = {
                "Test Case ID": f"TC_{api_name.upper()}_{self.test_counter:03d}",
                "Test Description": f"Check LIKE operator for {api_name} API",
                "Request Body": {
                    "pql": f"SELECT [{api_name}.{field}] FROM [{api_name}] WHERE [{api_name}.{field}] LIKE '%example%'",
                    "limit": "50",
                    "offset": "0"
                },
                "Expected Results": f"Should return records where {field} contains 'example'",
                "Fields Used": [field]
            }
            self.test_cases.append(test_case)
            self.test_counter += 1
    
    def generate_in_test(self, api_name: str, fields: List[str]):
        """Generate IN operator test case"""
        where_fields = self._find_where_fields(fields)
        
        if where_fields:
            field = random.choice(where_fields)
            field_type = self._get_field_type(field)
            
            if field_type == "string":
                values = "'value1', 'value2', 'value3'"
            elif field_type == "numeric":
                values = "1, 2, 3"
            elif field_type == "status":
                values = "'Active', 'Inactive', 'Pending'"
            else:
                values = "1, 2, 3"
            
            test_case = {
                "Test Case ID": f"TC_{api_name.upper()}_{self.test_counter:03d}",
                "Test Description": f"Check IN operator for {api_name} API",
                "Request Body": {
                    "pql": f"SELECT [{api_name}.{field}] FROM [{api_name}] WHERE [{api_name}.{field}] IN ({values})",
                    "limit": "50",
                    "offset": "0"
                },
                "Expected Results": f"Should return records where {field} is in specified values",
                "Fields Used": [field]
            }
            self.test_cases.append(test_case)
            self.test_counter += 1
    
    def generate_between_test(self, api_name: str, fields: List[str]):
        """Generate BETWEEN operator test case"""
        numeric_fields = [f for f in fields if self._is_numeric_field(f)]
        date_fields = [f for f in fields if self._is_date_field(f)]
        
        if numeric_fields:
            field = random.choice(numeric_fields)
            test_case = {
                "Test Case ID": f"TC_{api_name.upper()}_{self.test_counter:03d}",
                "Test Description": f"Check BETWEEN operator for numeric field in {api_name} API",
                "Request Body": {
                    "pql": f"SELECT [{api_name}.{field}] FROM [{api_name}] WHERE [{api_name}.{field}] BETWEEN 100 AND 1000",
                    "limit": "50",
                    "offset": "0"
                },
                "Expected Results": f"Should return records where {field} is between 100 and 1000",
                "Fields Used": [field]
            }
            self.test_cases.append(test_case)
            self.test_counter += 1
        
        if date_fields:
            field = random.choice(date_fields)
            test_case = {
                "Test Case ID": f"TC_{api_name.upper()}_{self.test_counter:03d}",
                "Test Description": f"Check BETWEEN operator for date field in {api_name} API",
                "Request Body": {
                    "pql": f"SELECT [{api_name}.{field}] FROM [{api_name}] WHERE [{api_name}.{field}] BETWEEN '2024-01-01' AND '2024-12-31'",
                    "limit": "50",
                    "offset": "0"
                },
                "Expected Results": f"Should return records where {field} is in 2024",
                "Fields Used": [field]
            }
            self.test_cases.append(test_case)
            self.test_counter += 1
    
    def generate_order_by_test(self, api_name: str, fields: List[str]):
        """Generate ORDER BY test case"""
        if len(fields) >= 2:
            order_field = random.choice(fields)
            test_case = {
                "Test Case ID": f"TC_{api_name.upper()}_{self.test_counter:03d}",
                "Test Description": f"Check ORDER BY for {api_name} API",
                "Request Body": {
                    "pql": f"SELECT [{api_name}.{fields[0]}], [{api_name}.{fields[1]}] FROM [{api_name}] ORDER BY [{api_name}.{order_field}] ASC",
                    "limit": "50",
                    "offset": "0"
                },
                "Expected Results": f"Should return records ordered by {order_field} in ascending order",
                "Fields Used": [fields[0], fields[1], order_field]
            }
            self.test_cases.append(test_case)
            self.test_counter += 1
    
    def generate_distinct_test(self, api_name: str, fields: List[str]):
        """Generate DISTINCT test case"""
        if fields:
            field = random.choice(fields)
            test_case = {
                "Test Case ID": f"TC_{api_name.upper()}_{self.test_counter:03d}",
                "Test Description": f"Check DISTINCT for {api_name} API",
                "Request Body": {
                    "pql": f"SELECT DISTINCT [{api_name}.{field}] FROM [{api_name}]",
                    "limit": "50",
                    "offset": "0"
                },
                "Expected Results": f"Should return unique values of {field}",
                "Fields Used": [field]
            }
            self.test_cases.append(test_case)
            self.test_counter += 1
    
    def generate_all_fields_test(self, api_name: str, fields: List[str]):
        """Generate test case for selecting all fields"""
        test_case = {
            "Test Case ID": f"TC_{api_name.upper()}_{self.test_counter:03d}",
            "Test Description": f"Check all fields can be selected from {api_name}",
            "Request Body": {
                "pql": f"SELECT * FROM [{api_name}]",
                "limit": "10",
                "offset": "0"
            },
            "Expected Results": f"Should return all {len(fields)} fields from {api_name} table",
            "Fields Used": "ALL_FIELDS"
        }
        self.test_cases.append(test_case)
        self.test_counter += 1
    
    def generate_complex_where_test(self, api_name: str, fields: List[str]):
        """Generate complex WHERE condition test case"""
        where_fields = self._find_where_fields(fields)
        
        if len(where_fields) >= 2:
            field1, field2 = random.sample(where_fields, 2)
            field1_type = self._get_field_type(field1)
            field2_type = self._get_field_type(field2)
            
            condition1 = self._generate_condition(api_name, field1, field1_type)
            condition2 = self._generate_condition(api_name, field2, field2_type)
            
            test_case = {
                "Test Case ID": f"TC_{api_name.upper()}_{self.test_counter:03d}",
                "Test Description": f"Check complex WHERE conditions for {api_name} API",
                "Request Body": {
                    "pql": f"SELECT [{api_name}.{field1}], [{api_name}.{field2}] FROM [{api_name}] WHERE {condition1} AND {condition2}",
                    "limit": "50",
                    "offset": "0"
                },
                "Expected Results": f"Should return records meeting both conditions on {field1} and {field2}",
                "Fields Used": [field1, field2]
            }
            self.test_cases.append(test_case)
            self.test_counter += 1
    
    def _find_where_fields(self, fields: List[str]) -> List[str]:
        """Find suitable fields for WHERE clauses"""
        suitable_fields = []
        for field in fields:
            field_lower = field.lower()
            if any(keyword in field_lower for keyword in ['id', 'status', 'type', 'date', 'amount', 'number', 'code']):
                suitable_fields.append(field)
        return suitable_fields if suitable_fields else fields[:3]
    
    def _get_field_type(self, field: str) -> str:
        """Determine field type based on field name"""
        field_lower = field.lower()
        
        if any(keyword in field_lower for keyword in ['date', 'time']):
            return "date"
        elif any(keyword in field_lower for keyword in ['amount', 'number', 'count', 'quantity', 'total', 'balance']):
            return "numeric"
        elif any(keyword in field_lower for keyword in ['status', 'type']):
            return "status"
        elif any(keyword in field_lower for keyword in ['name', 'description', 'note', 'comment']):
            return "string"
        else:
            return "generic"
    
    def _is_numeric_field(self, field: str) -> bool:
        return self._get_field_type(field) == "numeric"
    
    def _is_string_field(self, field: str) -> bool:
        return self._get_field_type(field) in ["string", "status"]
    
    def _is_date_field(self, field: str) -> bool:
        return self._get_field_type(field) == "date"
    
    def _generate_condition(self, api_name: str, field: str, field_type: str) -> str:
        """Generate appropriate condition based on field type"""
        if field_type == "string":
            return f"[{api_name}.{field}] IS NOT NULL"
        elif field_type == "numeric":
            return f"[{api_name}.{field}] > 0"
        elif field_type == "date":
            return f"[{api_name}.{field}] > '2024-01-01'"
        elif field_type == "status":
            return f"[{api_name}.{field}] = 'Active'"
        else:
            return f"[{api_name}.{field}] IS NOT NULL"
    
    def save_test_cases(self, filename: str):
        """Save test cases to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.test_cases, f, indent=2)
    
    def print_test_cases(self):
        """Print test cases in a readable format"""
        print(f"\n{'='*80}")
        print(f"🎯 GENERATED TEST CASES SUMMARY")
        print(f"{'='*80}")
        
        for test_case in self.test_cases:
            print(f"\n📋 Test Case ID: {test_case['Test Case ID']}")
            print(f"📖 Description: {test_case['Test Description']}")
            print(f"🔍 Fields Used: {test_case.get('Fields Used', 'N/A')}")
            print(f"🔧 PQL Query: {test_case['Request Body']['pql']}")
            print(f"✅ Expected: {test_case['Expected Results']}")
            print(f"{'-'*80}")

def get_user_input(available_apis: List[str]):
    """Get API name from user input"""
    print(f"\n{'='*80}")
    print(f"🚀 PQL TEST CASE GENERATOR")
    print(f"{'='*80}")
    print(f"📋 Available APIs: {len(available_apis)} APIs found")
    
    # Show first 10 APIs as examples
    print(f"📝 Sample APIs: {', '.join(available_apis[:10])}")
    if len(available_apis) > 10:
        print(f"   ... and {len(available_apis) - 10} more")
    
    while True:
        api_name = input("\n🎯 Enter API Name (or 'list' to see all APIs, 'quit' to exit): ").strip()
        
        if api_name.lower() == 'quit':
            return None
        elif api_name.lower() == 'list':
            print(f"\n📋 ALL AVAILABLE APIS ({len(available_apis)}):")
            for i, api in enumerate(available_apis, 1):
                print(f"   {i:2d}. {api}")
            continue
        elif api_name in available_apis:
            return api_name
        else:
            print(f"❌ API '{api_name}' not found. Please try again.")
            print(f"💡 Tip: Use 'list' to see all available APIs")

def main():
    # Your provided JSON data - replace this with your actual API_SCHEMA import
    try:
        from api_data import API_SCHEMA
        api_data = API_SCHEMA
    except ImportError:
        print("❌ Error: Could not import API_SCHEMA from api_data.py")
        print("💡 Please make sure api_data.py exists with your API schema")
        return
    
    # Initialize generator
    generator = PQLTestGenerator(api_data)
    available_apis = generator.get_available_apis()
    
    if not available_apis:
        print("❌ No APIs found in the schema. Please check your API data.")
        return
    
    print(f"✅ Loaded {len(available_apis)} APIs from schema")
    
    while True:
        # Get user input
        api_name = get_user_input(available_apis)
        
        if api_name is None:
            print("👋 Exiting PQL Test Generator. Goodbye!")
            break
        
        # Generate test cases for the selected API
        print(f"\n🎯 Generating test cases for: {api_name}")
        
        # Reset test cases and counter for new generation
        generator.test_cases = []
        generator.test_counter = 1
        
        test_cases = generator.generate_test_cases([api_name])
        
        # Print the generated test cases
        generator.print_test_cases()
        
        # Save to file
        filename = f"pql_test_cases_{api_name}.json"
        generator.save_test_cases(filename)
        
        print(f"\n💾 Test cases saved to: {filename}")
        print(f"📊 Total test cases generated: {len(test_cases)}")
        
        # Ask if user wants to generate for another API
        continue_gen = input("\n🔄 Generate test cases for another API? (y/n): ").strip().lower()
        if continue_gen not in ['y', 'yes']:
            print("👋 Exiting PQL Test Generator. Goodbye!")
            break

if __name__ == "__main__":
    main()