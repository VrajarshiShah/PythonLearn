import pyodbc
import json

# Database config
server = 'ip-172-30-0-236.ec2.internal'
database = 'mssql-0.sikka.cloud'
username = 'Sa'
password = 'your_password'
driver = '{ODBC Driver 17 for SQL Server}'

# Connect and query
conn_str = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"

# Load test data from JSON file
with open('test_data.json', 'r') as file:
    test_data = json.load(file)

user_data = test_data["user_data"]
username_to_search = user_data["first_name"]

try:
    with pyodbc.connect(conn_str) as conn:
        cursor = conn.cursor()
        
        # Step 1: Get devID from userMaster
        cursor.execute("SELECT devID FROM userMaster WHERE username = ?", (username_to_search,))
        user_result = cursor.fetchone()
        
        if not user_result:
            print(" User not found in userMaster table")
            exit()
            
        dev_id = user_result[0]
        print(f"✅ User found - devID: {dev_id}")
        
        # Step 2: Check credit_card_details
        cc_query = """
        SELECT customer_profile_id, customer_payment_id, masked_card_number 
        FROM credit_card_details 
        WHERE devID = ?
        AND customer_profile_id IS NOT NULL AND customer_profile_id != ''
        AND customer_payment_id IS NOT NULL AND customer_payment_id != ''
        AND masked_card_number IS NOT NULL AND masked_card_number != ''
        """
        cursor.execute(cc_query, (dev_id,))
        cc_result = cursor.fetchone()
        
        if not cc_result:
            print("❌ Credit card details incomplete or missing")
            exit()
            
        print("✅ Credit card details validated")
        
        # Step 3: Check appmaster matches
        am_query = """
        SELECT customer_profile_id, customer_payment_id 
        FROM appmaster 
        WHERE devID = ?
        AND customer_profile_id = ?
        AND customer_payment_id = ?
        """
        cursor.execute(am_query, (dev_id, cc_result.customer_profile_id, cc_result.customer_payment_id))
        am_result = cursor.fetchone()
        
        if not am_result:
            print("❌ Profile/Payment IDs don't match between credit_card_details and appmaster")
            exit()
            
        print("✅ Profile/Payment IDs match between tables")
        
        # Step 4: Check publisAppMaster status
        pam_query = "SELECT status FROM publisAppMaster WHERE devID = ? AND status = 'Public'"
        cursor.execute(pam_query, (dev_id,))
        pam_result = cursor.fetchone()
        
        if not pam_result:
            print("❌ App status is not 'Public' in publisAppMaster")
            exit()
            
        print("✅ App status is 'Public'")
        
        # Final success message
        print("\n🎉 ALL VALIDATIONS PASSED SUCCESSFULLY!")
        print(f"devID: {dev_id}")
        print(f"Customer Profile ID: {cc_result.customer_profile_id}")
        print(f"Customer Payment ID: {cc_result.customer_payment_id}")
        print(f"Masked Card: {cc_result.masked_card_number}")
        print(f"Status: {pam_result.status}")
                
except Exception as e:
    print(f"Error: {e}")