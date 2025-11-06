import json
import random
from typing import List, Dict, Any

class PQLTestGenerator:
    def __init__(self, api_schema: Dict[str, Any]):
        self.api_schema = api_schema
        self.api_map = {item['api_name']: item['api_fields'] for item in api_schema['items']}
    
    def get_api_fields(self, api_name: str) -> List[str]:
        """Get fields for a specific API"""
        return self.api_map.get(api_name, [])
    
    def generate_basic_select_cases(self, api_name: str) -> List[Dict]:
        """Generate basic SELECT test cases"""
        fields = self.get_api_fields(api_name)
        if not fields:
            return []
        
        test_cases = []
        
        # Case 1: Select all fields
        all_fields = ", ".join([f"[{api_name}.{field}]" for field in fields])
        test_cases.append({
            "test_case": f"Basic SELECT all fields from {api_name}",
            "request_body": {
                "pql": f"SELECT {all_fields} FROM [{api_name}]",
                "limit": "50",
                "offset": "0"
            }
        })
        
        # Case 2: Select specific fields
        sample_fields = fields[:3]  # Take first 3 fields
        selected_fields = ", ".join([f"[{api_name}.{field}]" for field in sample_fields])
        test_cases.append({
            "test_case": f"SELECT specific fields from {api_name}",
            "request_body": {
                "pql": f"SELECT {selected_fields} FROM [{api_name}]",
                "limit": "50",
                "offset": "0"
            }
        })
        
        # Case 3: SELECT DISTINCT
        distinct_field = fields[0] if fields else "practice_id"
        test_cases.append({
            "test_case": f"SELECT DISTINCT from {api_name}",
            "request_body": {
                "pql": f"SELECT DISTINCT [{api_name}.{distinct_field}],{selected_fields} FROM [{api_name}]",
                "limit": "50",
                "offset": "0"
            }
        })
        
        return test_cases
    
    def generate_aggregation_cases(self, api_name: str) -> List[Dict]:
        """Generate aggregation function test cases"""
        fields = self.get_api_fields(api_name)
        numeric_fields = [f for f in fields if any(keyword in f.lower() for keyword in ['amount', 'balance', 'number', 'total', 'estimate'])]
        
        if not numeric_fields:
            return []
        
        test_cases = []
        
        # COUNT
        test_cases.append({
            "test_case": f"COUNT aggregation for {api_name}",
            "request_body": {
                "pql": f"SELECT COUNT([{api_name}.{numeric_fields[0]}]) FROM [{api_name}]",
                "limit": "50",
                "offset": "0"
            }
        })
        
        # SUM
        test_cases.append({
            "test_case": f"SUM aggregation for {api_name}",
            "request_body": {
                "pql": f"SELECT SUM([{api_name}.{numeric_fields[0]}]) FROM [{api_name}]",
                "limit": "50",
                "offset": "0"
            }
        })
        
        # AVG
        test_cases.append({
            "test_case": f"AVG aggregation for {api_name}",
            "request_body": {
                "pql": f"SELECT AVG([{api_name}.{numeric_fields[0]}]) FROM [{api_name}]",
                "limit": "50",
                "offset": "0"
            }
        })
        
        # MIN/MAX
        test_cases.append({
            "test_case": f"MIN and MAX aggregation for {api_name}",
            "request_body": {
                "pql": f"SELECT MIN([{api_name}.{numeric_fields[0]}]), MAX([{api_name}.{numeric_fields[0]}]) FROM [{api_name}]",
                "limit": "50",
                "offset": "0"
            }
        })
        
        return test_cases
    
    def generate_where_clause_cases(self, api_name: str) -> List[Dict]:
        """Generate WHERE clause test cases"""
        fields = self.get_api_fields(api_name)
        if not fields:
            return []
        
        test_cases = []
        sample_fields = fields[:2]
        
        # Basic WHERE with numeric field
        numeric_fields = [f for f in fields if any(keyword in f.lower() for keyword in ['amount', 'id', 'number'])]
        if numeric_fields:
            test_cases.append({
                "test_case": f"WHERE clause with numeric condition for {api_name}",
                "request_body": {
                    "pql": f"SELECT [{api_name}.{sample_fields[0]}] FROM [{api_name}] WHERE [{api_name}.{numeric_fields[0]}] > 1000",
                    "limit": "50",
                    "offset": "0"
                }
            })
        
        # WHERE with IN clause
        test_cases.append({
            "test_case": f"WHERE IN clause for {api_name}",
            "request_body": {
                "pql": f"SELECT [{api_name}.{sample_fields[0]}] FROM [{api_name}] WHERE [{api_name}.{sample_fields[0]}] IN (1, 2, 3)",
                "limit": "50",
                "offset": "0"
            }
        })
        
        # WHERE with BETWEEN
        if numeric_fields:
            test_cases.append({
                "test_case": f"WHERE BETWEEN clause for {api_name}",
                "request_body": {
                    "pql": f"SELECT [{api_name}.{sample_fields[0]}] FROM [{api_name}] WHERE [{api_name}.{numeric_fields[0]}] BETWEEN 100 AND 1000",
                    "limit": "50",
                    "offset": "0"
                }
            })
        
        return test_cases
    
    def generate_like_cases(self, api_name: str) -> List[Dict]:
        """Generate LIKE operator test cases"""
        fields = self.get_api_fields(api_name)
        text_fields = [f for f in fields if any(keyword in f.lower() for keyword in ['name', 'description', 'type'])]
        
        if not text_fields:
            return []
        
        return [{
            "test_case": f"LIKE operator for {api_name}",
            "request_body": {
                "pql": f"SELECT [{api_name}.{text_fields[0]}] FROM [{api_name}] WHERE [{api_name}.{text_fields[0]}] LIKE '%est%'",
                "limit": "50",
                "offset": "0"
            }
        }]
    
    def generate_join_cases(self, api_name: str) -> List[Dict]:
        """Generate JOIN test cases with other APIs"""
        fields = self.get_api_fields(api_name)
        common_join_fields = ['practice_id', 'cust_id', 'guarantor_id']
        
        available_join_fields = [f for f in common_join_fields if f in fields]
        if not available_join_fields:
            return []
        
        join_field = available_join_fields[0]
        
        # Find other APIs that have the same join field
        other_apis = []
        for other_api, other_fields in self.api_map.items():
            if other_api != api_name and join_field in other_fields:
                other_apis.append(other_api)
        
        test_cases = []
        for other_api in other_apis[:2]:  # Limit to 2 joins to avoid too many cases
            test_cases.append({
                "test_case": f"LEFT JOIN between {api_name} and {other_api}",
                "request_body": {
                    "pql": f"SELECT [{api_name}.{fields[0]}], [{other_api}.{self.get_api_fields(other_api)[0]}] FROM [{api_name}] LEFT JOIN [{other_api}] ON [{api_name}.{join_field}] = [{other_api}.{join_field}]",
                    "limit": "50",
                    "offset": "0"
                }
            })
        
        return test_cases
    
    def generate_group_by_having_cases(self, api_name: str) -> List[Dict]:
        """Generate GROUP BY and HAVING test cases"""
        fields = self.get_api_fields(api_name)
        groupable_fields = [f for f in fields if any(keyword in f.lower() for keyword in ['type', 'id'])]
        numeric_fields = [f for f in fields if any(keyword in f.lower() for keyword in ['amount', 'total', 'estimate'])]
        
        if not groupable_fields or not numeric_fields:
            return []
        
        return [{
            "test_case": f"GROUP BY and HAVING for {api_name}",
            "request_body": {
                "pql": f"SELECT [{api_name}.{groupable_fields[0]}], SUM([{api_name}.{numeric_fields[0]}]) FROM [{api_name}] GROUP BY [{api_name}.{groupable_fields[0]}] HAVING SUM([{api_name}.{numeric_fields[0]}]) > 1000",
                "limit": "50",
                "offset": "0"
            }
        }]
    
    def generate_subquery_cases(self, api_name: str) -> List[Dict]:
        """Generate subquery test cases"""
        fields = self.get_api_fields(api_name)
        common_fields = ['practice_id', 'cust_id']
        
        available_common_fields = [f for f in common_fields if f in fields]
        if not available_common_fields:
            return []
        
        common_field = available_common_fields[0]
        
        # Find another API for subquery
        other_apis = []
        for other_api, other_fields in self.api_map.items():
            if other_api != api_name and common_field in other_fields:
                other_apis.append(other_api)
        
        if not other_apis:
            return []
        
        other_api = other_apis[0]
        
        return [{
            "test_case": f"EXISTS subquery for {api_name}",
            "request_body": {
                "pql": f"SELECT [{api_name}.{fields[0]}] FROM [{api_name}] WHERE EXISTS (SELECT 1 FROM [{other_api}] WHERE [{other_api}.{common_field}] = [{api_name}.{common_field}])",
                "limit": "50",
                "offset": "0"
            }
        }]
    
    def generate_union_cases(self, api_name: str) -> List[Dict]:
        """Generate UNION test cases"""
        fields = self.get_api_fields(api_name)
        common_fields = ['practice_id']
        
        available_common_fields = [f for f in common_fields if f in fields]
        if not available_common_fields:
            return []
        
        common_field = available_common_fields[0]
        
        # Find another API for UNION
        other_apis = []
        for other_api, other_fields in self.api_map.items():
            if other_api != api_name and common_field in other_fields:
                other_apis.append(other_api)
        
        if not other_apis:
            return []
        
        other_api = other_apis[0]
        
        return [{
            "test_case": f"UNION between {api_name} and {other_api}",
            "request_body": {
                "pql": f"SELECT [{api_name}.{common_field}] FROM [{api_name}] UNION SELECT [{other_api}.{common_field}] FROM [{other_api}]",
                "limit": "50",
                "offset": "0"
            }
        }]
    
    def generate_all_test_cases(self, api_name: str) -> List[Dict]:
        """Generate all types of test cases for a given API"""
        if api_name not in self.api_map:
            return []
        
        all_test_cases = []
        
        # Generate all types of test cases
        all_test_cases.extend(self.generate_basic_select_cases(api_name))
        all_test_cases.extend(self.generate_aggregation_cases(api_name))
        all_test_cases.extend(self.generate_where_clause_cases(api_name))
        all_test_cases.extend(self.generate_like_cases(api_name))
        all_test_cases.extend(self.generate_join_cases(api_name))
        all_test_cases.extend(self.generate_group_by_having_cases(api_name))
        all_test_cases.extend(self.generate_subquery_cases(api_name))
        all_test_cases.extend(self.generate_union_cases(api_name))
        
        return all_test_cases
    
    def print_test_cases(self, api_name: str):
        """Print all generated test cases in a formatted way"""
        test_cases = self.generate_all_test_cases(api_name)
        
        print(f"🔍 Generated {len(test_cases)} PQL Test Cases for '{api_name}' API")
        print("=" * 80)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. {test_case['test_case']}")
            print("-" * 60)
            print("Request Body:")
            print(json.dumps(test_case['request_body'], indent=2))
            print()
    
    def save_test_cases_to_file(self, api_name: str, filename: str = None):
        """Save test cases to a JSON file"""
        if not filename:
            filename = f"pql_test_cases_{api_name}.json"
        
        test_cases = self.generate_all_test_cases(api_name)
        output = {
            "api_name": api_name,
            "total_test_cases": len(test_cases),
            "test_cases": test_cases
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"✅ Test cases saved to {filename}")

# Your API Schema
API_SCHEMA = {
    "status": "Success",
    "message": "Success",
    "items": [
        {
            "api_name": "accounts",
            "api_fields": [
                "account_number",
                "account_name",
                "account_fullname",
                "description",
                "account_type",
                "balance_total",
                "practice_id"
            ]
        },
        {
            "api_name": "accounts_receivables",
            "api_fields": [
                "write_off_estimate",
                "payment_plan_amount",
                "unapplied_payments",
                "estimated_insurance_amount",
                "estimated_patient_amount",
                "guarantor_id",
                "amount_less_than_30",
                "amount_between_30_60",
                "amount_between_60_90",
                "amount_greater_than_90",
                "practice_id",
                "entry_id",
                "current_date",
                "cust_id"
            ]
        },
    ]
}

# Usage Example
def main():
    # Initialize the test generator
    generator = PQLTestGenerator(API_SCHEMA)
    
    # Generate test cases for accounts_receivables API
    api_name = "accounts_receivables"
    
    print("🚀 PQL Test Case Generator")
    print("=" * 50)
    
    # Display available APIs
    available_apis = list(generator.api_map.keys())
    print(f"Available APIs: {', '.join(available_apis)}")
    print(f"Generating test cases for: {api_name}\n")
    
    # Print all test cases
    generator.print_test_cases(api_name)
    
    # Save to file
    generator.save_test_cases_to_file(api_name)
    
    # Generate for other APIs too
    print("\n" + "="*80)
    print("Quick overview for all APIs:")
    for api in available_apis:
        test_cases = generator.generate_all_test_cases(api)
        print(f"📊 {api}: {len(test_cases)} test cases generated")

if __name__ == "__main__":
    main()