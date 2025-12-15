import json
import os
import uuid
from datetime import datetime, timedelta
import streamlit as st
from database import get_connection, init_database, migrate_from_json, add_missing_columns, check_database_health, migrate_created_by_field
from email_utils import email_service

# Session state management
def ensure_session_state():
    """Ensure session state is properly initialized"""
    defaults = {
        "logged_in": False,
        "username": None,
        "role": None,
        "current_page": "Dashboard",
        "show_owner_signup": False,
        "pending_transaction_data": None,
        "transaction_page": 1,
        "show_reset_confirmation": False,
        "database_initialized": False,
        "utang_pending_otp": False,
        "payment_pending_otp": False,
        "pending_transaction_id": None,
        "pending_customer": None,
        "payment_amount": None,
        "outstanding_balance": None,
        "payment_type": None,
        "payment_description": None,
        "partial_payment_confirmed": False,
        "due_date": None,
        "utang_amount": None,
        "transaction_description": None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ID and date generation
def generate_id():
    """Generate unique ID"""
    return str(uuid.uuid4())

def get_current_date():
    """Get current date in YYYY-MM-DD format"""
    return datetime.now().strftime("%Y-%m-%d")

def get_current_datetime():
    """Get current datetime"""
    return datetime.now().isoformat()

def calculate_due_date(days=30):
    """Calculate default due date (30 days from today)"""
    return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

# Account Management
def get_account(username):
    """Get account by username"""
    conn = get_connection()
    if not conn:
        return None
        
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM accounts WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        personal_info = json.loads(row[4]) if row[4] else {}
        
        return {
            "username": row[0],
            "password": row[1],
            "role": row[2],
            "debtLimit": row[3],
            "personalInfo": personal_info,
            "created_date": row[5],
            "created_by": row[6] if len(row) > 6 else "system"
        }
    except Exception as e:
        conn.close()
        return None

def create_account(username, password, role, personal_info=None, created_by=None):
    """Create new account with creator tracking"""
    if not username or not password:
        return False, "Username and password are required"
    
    if get_account(username):
        return False, "Username already exists"
    
    if role == "Customer":
        debt_limit = float(get_setting("customerCreditLimit", 10000.00))
    else:
        debt_limit = 0
    
    if personal_info is None:
        personal_info = {
            "full_name": "",
            "email": "",
            "address": ""
        }
    
    personal_info_json = json.dumps(personal_info)
    
    # Set created_by to current user if not specified
    if created_by is None:
        created_by = st.session_state.get("username", "system")
    
    conn = get_connection()
    if not conn:
        return False, "Database connection failed"
        
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO accounts (username, password, role, debt_limit, personal_info, created_date, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (username, password, role, debt_limit, personal_info_json, get_current_datetime(), created_by))
        
        conn.commit()
        conn.close()
        
        # Send welcome alert to the new account
        if role == "Customer":
            send_alert(username, f"Welcome to IUMS! Your account has been created by {created_by}.")
        
        return True, f"{role} account created successfully!"
    except Exception as e:
        conn.close()
        return False, f"Error creating account: {str(e)}"

def list_accounts(role_filter=None):
    """Get all accounts with optional role filter"""
    conn = get_connection()
    if not conn:
        return []
        
    cursor = conn.cursor()
    
    try:
        if role_filter:
            cursor.execute('SELECT * FROM accounts WHERE role = ?', (role_filter,))
        else:
            cursor.execute('SELECT * FROM accounts')
        
        rows = cursor.fetchall()
        conn.close()
        
        accounts = []
        for row in rows:
            personal_info = json.loads(row[4]) if row[4] else {}
            accounts.append({
                "username": row[0],
                "password": row[1],
                "role": row[2],
                "debtLimit": row[3],
                "personalInfo": personal_info,
                "created_date": row[5],
                "created_by": row[6] if len(row) > 6 else "system"
            })
        
        return accounts
    except Exception as e:
        conn.close()
        return []

def list_my_accounts(owner_username=None):
    """Get accounts created by a specific owner"""
    if owner_username is None:
        owner_username = st.session_state.get("username")
        if not owner_username:
            return []
    
    conn = get_connection()
    if not conn:
        return []
        
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM accounts WHERE created_by = ?', (owner_username,))
        rows = cursor.fetchall()
        conn.close()
        
        accounts = []
        for row in rows:
            personal_info = json.loads(row[4]) if row[4] else {}
            accounts.append({
                "username": row[0],
                "password": row[1],
                "role": row[2],
                "debtLimit": row[3],
                "personalInfo": personal_info,
                "created_date": row[5],
                "created_by": row[6] if len(row) > 6 else "system"
            })
        
        return accounts
    except Exception as e:
        conn.close()
        return []

def delete_account(username):
    """Delete account and related data"""
    if not get_account(username):
        return False, "Account not found"
    
    if username == st.session_state.get("username"):
        return False, "Cannot delete your own account"
    
    # Check if current user is the creator of this account
    account = get_account(username)
    current_user = st.session_state.get("username")
    
    if account.get("created_by") != current_user and current_user != username:
        return False, "You can only delete accounts you created"
    
    conn = get_connection()
    if not conn:
        return False, "Database connection failed"
        
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM accounts WHERE username = ?', (username,))
        cursor.execute('DELETE FROM alerts WHERE username = ?', (username,))
        cursor.execute('DELETE FROM transactions WHERE customer = ?', (username,))
        
        conn.commit()
        conn.close()
        return True, "Account deleted successfully"
    except Exception as e:
        conn.close()
        return False, f"Error deleting account: {str(e)}"

def update_account_password(username, new_password):
    """Update account password"""
    conn = get_connection()
    if not conn:
        return False, "Database connection failed"
        
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE accounts SET password = ? WHERE username = ?
        ''', (new_password, username))
        
        conn.commit()
        conn.close()
        
        send_alert(username, "Your account password has been updated successfully.")
        return True, "Password updated successfully"
    except Exception as e:
        conn.close()
        return False, f"Error updating password: {str(e)}"

def update_account_username(old_username, new_username):
    """Update account username"""
    if get_account(new_username):
        return False, "Username already exists"
    
    conn = get_connection()
    if not conn:
        return False, "Database connection failed"
        
    cursor = conn.cursor()
    
    try:
        cursor.execute('UPDATE accounts SET username = ? WHERE username = ?', (new_username, old_username))
        cursor.execute('UPDATE transactions SET customer = ? WHERE customer = ?', (new_username, old_username))
        cursor.execute('UPDATE alerts SET username = ? WHERE username = ?', (new_username, old_username))
        
        conn.commit()
        conn.close()
        
        send_alert(new_username, f"Your account username has been updated from '{old_username}' to '{new_username}'.")
        return True, "Username updated successfully"
    except Exception as e:
        conn.close()
        return False, f"Error updating username: {str(e)}"

# Transaction Management with Due Date Support
def create_pending_transaction_with_due_date(customer, transaction_type, description, amount, created_by=None, interest_rate=0, due_date=None):
    """Create a pending transaction with due date that waits for OTP confirmation"""
    if not get_account(customer):
        return None, "Customer account not found"
    
    # COMPREHENSIVE None handling for amount
    if amount is None:
        return None, "Amount cannot be empty"
    
    # Handle different types of None values
    if isinstance(amount, str) and amount.strip() == "":
        return None, "Amount cannot be empty"
    
    try:
        # Convert to float safely with comprehensive error handling
        amount_float = float(amount)
        if amount_float <= 0:
            return None, "Amount must be greater than 0"
    except (ValueError, TypeError) as e:
        print(f"Amount conversion error: {e}, amount value: {amount}, type: {type(amount)}")
        return None, f"Please enter a valid amount. Error: {str(e)}"
    
    transaction_id = generate_id()
    otp = str(uuid.uuid4().int)[:6]
    
    # Calculate interest if applicable
    final_amount = round(amount_float, 2)
    interest_amount = 0
    
    if transaction_type == "utang" and interest_rate > 0:
        interest_amount = round(final_amount * (interest_rate / 100), 2)
        final_amount += interest_amount
    
    # Set default due date if not provided (30 days from today)
    if not due_date:
        due_date = calculate_due_date(30)
    
    conn = get_connection()
    if not conn:
        return None, "Database connection failed"
        
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO transactions 
            (id, customer, type, description, amount, date, confirmed, otp, created_by, created_at, status, interest_rate, interest_amount, principal_amount, due_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            transaction_id, customer, transaction_type, description, final_amount,
            get_current_date(), False, otp, created_by or "system", 
            get_current_datetime(), "pending_otp", interest_rate, interest_amount, 
            round(amount_float, 2), due_date
        ))
        
        conn.commit()
        conn.close()
        
        # Get customer details for email
        customer_account = get_account(customer)
        customer_name = customer_account.get("personalInfo", {}).get("full_name", customer)
        customer_email = customer_account.get("personalInfo", {}).get("email", "")
        
        # Send OTP to customer via email AND alert
        due_date_obj = datetime.strptime(due_date, '%Y-%m-%d').date()
        today = datetime.now().date()
        days_until_due = (due_date_obj - today).days
        
        # Send email if email is provided and service is configured
        if customer_email and email_service.is_configured:
            email_sent = email_service.send_otp_email(
                recipient_email=customer_email,
                customer_name=customer_name,
                otp_code=otp,
                transaction_type=transaction_type,
                amount=final_amount,
                description=description,
                due_date=due_date if transaction_type == "utang" else None
            )
            
            if email_sent:
                email_status = " (Email sent)"
            else:
                email_status = " (Email failed)"
        else:
            email_status = " (Email not configured)"
        
        # Also send alert to customer's web account
        if transaction_type == "utang":
            if interest_rate > 0:
                alert_message = f"📝 NEW UTANG PENDING: {description}\nAmount: {format_currency(final_amount)} (Principal: {format_currency(amount_float)} + {interest_rate}% Interest: {format_currency(interest_amount)})\nDue Date: {due_date} ({days_until_due} days from today)\nOTP for confirmation: {otp}{email_status}"
            else:
                alert_message = f"📝 NEW UTANG PENDING: {description}\nAmount: {format_currency(amount_float)}\nDue Date: {due_date} ({days_until_due} days from today)\nOTP for confirmation: {otp}{email_status}"
        else:
            alert_message = f"💰 PAYMENT PENDING: {description}\nAmount: {format_currency(amount_float)}\nOTP for confirmation: {otp}{email_status}"
        
        send_alert(customer, alert_message)
        
        transaction = {
            "id": transaction_id,
            "customer": customer,
            "type": transaction_type,
            "description": description,
            "amount": final_amount,
            "date": get_current_date(),
            "confirmed": False,
            "otp": otp,
            "created_by": created_by or "system",
            "created_at": get_current_datetime(),
            "status": "pending_otp",
            "interest_rate": interest_rate,
            "interest_amount": interest_amount,
            "principal_amount": round(amount_float, 2),
            "due_date": due_date
        }
        
        print(f"✅ Transaction created with ID: {transaction_id}")
        return transaction, f"OTP sent to customer. Please ask customer for OTP to complete transaction."
    except Exception as e:
        conn.close()
        return None, f"Error creating transaction: {str(e)}"

def confirm_transaction_with_otp(transaction_id, otp):
    """Confirm a pending transaction with OTP"""
    conn = get_connection()
    if not conn:
        return False, "Database connection failed"
        
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM transactions WHERE id = ?', (transaction_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return False, "Transaction not found"
        
        if row[6]:  # confirmed field
            conn.close()
            return False, "Transaction already confirmed"
        
        if row[7] != otp:  # otp field
            conn.close()
            return False, "Invalid OTP"
        
        cursor.execute('''
            UPDATE transactions 
            SET confirmed = 1, confirmed_at = ?, status = 'confirmed'
            WHERE id = ?
        ''', (get_current_datetime(), transaction_id))
        
        conn.commit()
        
        customer = row[1]
        transaction_type = row[2]
        description = row[3]
        amount = row[4]
        due_date = row[15] if len(row) > 15 else None
        interest_rate = row[12] if len(row) > 12 else 0
        interest_amount = row[13] if len(row) > 13 else 0
        principal_amount = row[14] if len(row) > 14 else amount
        
        # Update due date status when payment is confirmed
        if transaction_type == "payment":
            update_due_date_status(customer)
        
        # Send confirmation alert
        if transaction_type == "utang":
            if interest_rate > 0:
                alert_message = f"✅ UTANG CONFIRMED: {description}\nTotal: {format_currency(amount)} (Principal: {format_currency(principal_amount)} + Interest: {format_currency(interest_amount)})"
            else:
                alert_message = f"✅ UTANG CONFIRMED: {description}\nAmount: {format_currency(amount)}"
            
            if due_date:
                due_date_obj = datetime.strptime(due_date, '%Y-%m-%d').date()
                today = datetime.now().date()
                days_until_due = (due_date_obj - today).days
                alert_message += f"\n📅 Due Date: {due_date} ({days_until_due} days from today)"
        else:
            alert_message = f"✅ PAYMENT CONFIRMED: {description}\nAmount: {format_currency(amount)}"
        
        send_alert(customer, alert_message)
        conn.close()
        return True, "Transaction confirmed successfully"
    except Exception as e:
        conn.close()
        return False, f"Error confirming transaction: {str(e)}"

def get_customer_transactions(username):
    """Get all transactions for a customer with safe column access"""
    conn = get_connection()
    if not conn:
        return []
        
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM transactions WHERE customer = ? ORDER BY date DESC', (username,))
        rows = cursor.fetchall()
        conn.close()
        
        transactions = []
        for row in rows:
            try:
                transaction = {
                    "id": row[0] if row[0] is not None else "",
                    "customer": row[1] if row[1] is not None else "",
                    "type": row[2] if row[2] is not None else "utang",
                    "description": row[3] if row[3] is not None else "",
                    "amount": float(row[4]) if row[4] is not None else 0.0,
                    "date": row[5] if row[5] is not None else get_current_date(),
                    "confirmed": bool(row[6]) if row[6] is not None else False,
                    "otp": row[7] if row[7] is not None else "",
                    "created_by": row[8] if row[8] is not None else "system",
                    "created_at": row[9] if row[9] is not None else get_current_datetime(),
                    "confirmed_at": row[10] if row[10] is not None else "",
                    "status": row[11] if row[11] is not None else "pending",
                    "interest_rate": float(row[12]) if len(row) > 12 and row[12] is not None else 0.0,
                    "interest_amount": float(row[13]) if len(row) > 13 and row[13] is not None else 0.0,
                    "principal_amount": float(row[14]) if len(row) > 14 and row[14] is not None else float(row[4]) if row[4] is not None else 0.0,
                    "due_date": row[15] if len(row) > 15 and row[15] is not None else None
                }
                transactions.append(transaction)
            except Exception as e:
                print(f"Error processing transaction row: {e}")
                continue
        
        return transactions
    except Exception as e:
        conn.close()
        print(f"Error getting customer transactions: {e}")
        return []

def get_pending_transactions(customer_username=None):
    """Get pending transactions (unconfirmed)"""
    conn = get_connection()
    if not conn:
        return []
        
    cursor = conn.cursor()
    
    try:
        if customer_username:
            cursor.execute('SELECT * FROM transactions WHERE confirmed = 0 AND customer = ?', (customer_username,))
        else:
            cursor.execute('SELECT * FROM transactions WHERE confirmed = 0')
        
        rows = cursor.fetchall()
        conn.close()
        
        pending = []
        for row in rows:
            transaction = {
                "id": row[0],
                "customer": row[1],
                "type": row[2],
                "description": row[3],
                "amount": row[4],
                "date": row[5],
                "confirmed": bool(row[6]),
                "otp": row[7],
                "created_by": row[8],
                "created_at": row[9],
                "confirmed_at": row[10],
                "status": row[11],
                "interest_rate": row[12] if len(row) > 12 else 0,
                "interest_amount": row[13] if len(row) > 13 else 0,
                "principal_amount": row[14] if len(row) > 14 else row[4],
                "due_date": row[15] if len(row) > 15 else None
            }
            pending.append(transaction)
        
        return pending
    except Exception as e:
        conn.close()
        return []

def delete_transaction(transaction_id):
    """Delete a transaction"""
    conn = get_connection()
    if not conn:
        return False
        
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        return False

def get_all_transactions():
    """Get all transactions from the database with comprehensive None handling"""
    conn = get_connection()
    if not conn:
        return []
        
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM transactions ORDER BY date DESC, created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        transactions = []
        for row in rows:
            try:
                transaction = {
                    "id": row[0] if row[0] is not None else "",
                    "customer": row[1] if row[1] is not None else "",
                    "type": row[2] if row[2] is not None else "utang",
                    "description": row[3] if row[3] is not None else "",
                    "amount": float(row[4]) if row[4] is not None else 0.0,
                    "date": row[5] if row[5] is not None else get_current_date(),
                    "confirmed": bool(row[6]) if row[6] is not None else False,
                    "otp": row[7] if row[7] is not None else "",
                    "created_by": row[8] if row[8] is not None else "system",
                    "created_at": row[9] if row[9] is not None else get_current_datetime(),
                    "confirmed_at": row[10] if row[10] is not None else "",
                    "status": row[11] if row[11] is not None else "pending",
                    "interest_rate": float(row[12]) if row[12] is not None else 0.0,
                    "interest_amount": float(row[13]) if row[13] is not None else 0.0,
                    "principal_amount": float(row[14]) if row[14] is not None else float(row[4]) if row[4] is not None else 0.0,
                    "due_date": row[15] if row[15] is not None else None
                }
                transactions.append(transaction)
            except Exception as e:
                print(f"Error processing transaction row: {e}")
                continue
        
        return transactions
    except Exception as e:
        conn.close()
        print(f"Error getting all transactions: {e}")
        return []

def get_my_transactions(owner_username):
    """Get transactions for customers created by a specific owner"""
    # First get all customers created by this owner
    my_customers = [acc["username"] for acc in list_my_accounts(owner_username) if acc["role"] == "Customer"]
    
    if not my_customers:
        return []
    
    conn = get_connection()
    if not conn:
        return []
        
    cursor = conn.cursor()
    
    try:
        # Create placeholders for SQL query
        placeholders = ','.join(['?' for _ in my_customers])
        query = f'SELECT * FROM transactions WHERE customer IN ({placeholders}) ORDER BY date DESC, created_at DESC'
        
        cursor.execute(query, my_customers)
        rows = cursor.fetchall()
        conn.close()
        
        transactions = []
        for row in rows:
            try:
                transaction = {
                    "id": row[0] if row[0] is not None else "",
                    "customer": row[1] if row[1] is not None else "",
                    "type": row[2] if row[2] is not None else "utang",
                    "description": row[3] if row[3] is not None else "",
                    "amount": float(row[4]) if row[4] is not None else 0.0,
                    "date": row[5] if row[5] is not None else get_current_date(),
                    "confirmed": bool(row[6]) if row[6] is not None else False,
                    "otp": row[7] if row[7] is not None else "",
                    "created_by": row[8] if row[8] is not None else "system",
                    "created_at": row[9] if row[9] is not None else get_current_datetime(),
                    "confirmed_at": row[10] if row[10] is not None else "",
                    "status": row[11] if row[11] is not None else "pending",
                    "interest_rate": float(row[12]) if row[12] is not None else 0.0,
                    "interest_amount": float(row[13]) if row[13] is not None else 0.0,
                    "principal_amount": float(row[14]) if row[14] is not None else float(row[4]) if row[4] is not None else 0.0,
                    "due_date": row[15] if row[15] is not None else None
                }
                transactions.append(transaction)
            except Exception as e:
                print(f"Error processing transaction row: {e}")
                continue
        
        return transactions
    except Exception as e:
        conn.close()
        print(f"Error getting my transactions: {e}")
        return []

# Due Date Management System
def check_due_dates():
    """Check all due dates and send reminders for APPROACHING deadlines - ONLY FOR UNPAID UTANG"""
    conn = get_connection()
    if not conn:
        return False, "Database connection failed"
        
    cursor = conn.cursor()
    
    try:
        # Get all confirmed utang transactions with due dates that are STILL UNPAID
        cursor.execute('''
            SELECT t.id, t.customer, t.description, t.amount, t.due_date 
            FROM transactions t
            WHERE t.type = 'utang' 
            AND t.confirmed = 1 
            AND t.due_date IS NOT NULL
            AND t.due_date != ''
            AND EXISTS (
                SELECT 1 FROM accounts a 
                WHERE a.username = t.customer 
                AND (
                    SELECT COALESCE(SUM(
                        CASE WHEN t2.type = 'utang' THEN t2.amount ELSE -t2.amount END
                    ), 0)
                    FROM transactions t2 
                    WHERE t2.customer = t.customer AND t2.confirmed = 1
                ) > 0  -- Only include if customer has ACTUAL outstanding balance
            )
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        reminders_sent = 0
        email_reminders_sent = 0
        today = datetime.now().date()
        total_checked = 0
        
        for row in rows:
            transaction_id, customer, description, amount, due_date = row
            total_checked += 1
            
            if not due_date:
                continue
                
            try:
                due_date_obj = datetime.strptime(due_date, '%Y-%m-%d').date()
                days_until_due = (due_date_obj - today).days
                
                # Send reminders for due dates within 7 days or overdue
                if days_until_due <= 7:
                    # Double-check if this specific utang is still unpaid
                    customer_balance = calculate_balance(customer)
                    if customer_balance["outstanding"] > 0:
                        
                        if days_until_due == 0:
                            reminder_message = f"🚨 DUE TODAY: Your utang '{description}' for {format_currency(amount)} is DUE TODAY! Please make payment immediately."
                        elif days_until_due < 0:
                            reminder_message = f"🚨 OVERDUE: Your utang '{description}' for {format_currency(amount)} was due {abs(days_until_due)} days ago! Please pay immediately."
                        elif days_until_due <= 3:
                            reminder_message = f"⏰ URGENT: Your utang '{description}' for {format_currency(amount)} is due in {days_until_due} days ({due_date}). Please prepare payment."
                        else:
                            reminder_message = f"📅 REMINDER: Your utang '{description}' for {format_currency(amount)} is due in {days_until_due} days ({due_date})."
                        
                        # Send web alert
                        if send_alert(customer, reminder_message):
                            reminders_sent += 1
                        
                        # Send email reminder if configured
                        customer_account = get_account(customer)
                        customer_name = customer_account.get("personalInfo", {}).get("full_name", customer)
                        customer_email = customer_account.get("personalInfo", {}).get("email", "")
                        
                        if customer_email and email_service.is_configured:
                            if email_service.send_due_date_reminder(
                                customer_email, customer_name, description, amount, due_date, days_until_due
                            ):
                                email_reminders_sent += 1
                                
            except Exception as e:
                print(f"Error processing due date for {customer}: {e}")
                continue
        
        email_status = f" + {email_reminders_sent} email reminders" if email_reminders_sent > 0 else ""
        return True, f"✅ Checked {total_checked} utang with due dates. Sent {reminders_sent} web alerts{email_status} for ACTIVE utang."
    except Exception as e:
        if conn:
            conn.close()
        return False, f"Error checking due dates: {str(e)}"

def get_upcoming_due_dates(days_threshold=7):
    """Get all utang with due dates approaching within the specified days - ONLY FOR UNPAID UTANG"""
    conn = get_connection()
    if not conn:
        return []
        
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT t.customer, t.description, t.amount, t.due_date 
            FROM transactions t
            WHERE t.type = 'utang' 
            AND t.confirmed = 1 
            AND t.due_date IS NOT NULL
            AND EXISTS (
                SELECT 1 FROM accounts a 
                WHERE a.username = t.customer 
                AND (
                    SELECT COALESCE(SUM(
                        CASE WHEN t2.type = 'utang' THEN t2.amount ELSE -t2.amount END
                    ), 0)
                    FROM transactions t2 
                    WHERE t2.customer = t.customer AND t2.confirmed = 1
                ) > 0  -- Only include if customer has outstanding balance
            )
            ORDER BY t.due_date ASC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        upcoming_due_dates = []
        today = datetime.now().date()
        
        for row in rows:
            customer, description, amount, due_date = row
            
            if not due_date:
                continue
                
            due_date_obj = datetime.strptime(due_date, '%Y-%m-%d').date()
            days_until_due = (due_date_obj - today).days
            
            # Include overdue and upcoming due dates
            if days_until_due <= days_threshold:
                upcoming_due_dates.append({
                    'customer': customer,
                    'description': description,
                    'amount': amount,
                    'due_date': due_date,
                    'days_until_due': days_until_due
                })
        
        return upcoming_due_dates
    except Exception as e:
        conn.close()
        return []

def get_my_upcoming_due_dates(owner_username, days_threshold=7):
    """Get upcoming due dates for customers created by a specific owner"""
    # Get customers created by this owner
    my_customers = [acc["username"] for acc in list_my_accounts(owner_username) if acc["role"] == "Customer"]
    
    if not my_customers:
        return []
    
    all_upcoming = get_upcoming_due_dates(days_threshold)
    return [due for due in all_upcoming if due['customer'] in my_customers]

def get_overdue_transactions():
    """Get all overdue transactions - ONLY FOR UNPAID UTANG"""
    conn = get_connection()
    if not conn:
        return []
        
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT t.customer, t.description, t.amount, t.due_date 
            FROM transactions t
            WHERE t.type = 'utang' 
            AND t.confirmed = 1 
            AND t.due_date IS NOT NULL 
            AND t.due_date < ?
            AND EXISTS (
                SELECT 1 FROM accounts a 
                WHERE a.username = t.customer 
                AND (
                    SELECT COALESCE(SUM(
                        CASE WHEN t2.type = 'utang' THEN t2.amount ELSE -t2.amount END
                    ), 0)
                    FROM transactions t2 
                    WHERE t2.customer = t.customer AND t2.confirmed = 1
                ) > 0  -- Only include if customer has outstanding balance
            )
            ORDER BY t.due_date ASC
        ''', (get_current_date(),))
        
        rows = cursor.fetchall()
        conn.close()
        
        overdue = []
        for row in rows:
            customer, description, amount, due_date = row
            due_date_obj = datetime.strptime(due_date, '%Y-%m-%d').date()
            today = datetime.now().date()
            days_overdue = (today - due_date_obj).days
            
            overdue.append({
                'customer': customer,
                'description': description,
                'amount': amount,
                'due_date': due_date,
                'days_overdue': days_overdue
            })
        
        return overdue
    except Exception as e:
        conn.close()
        return []

def get_my_overdue_transactions(owner_username):
    """Get overdue transactions for customers created by a specific owner"""
    # Get customers created by this owner
    my_customers = [acc["username"] for acc in list_my_accounts(owner_username) if acc["role"] == "Customer"]
    
    if not my_customers:
        return []
    
    all_overdue = get_overdue_transactions()
    return [overdue for overdue in all_overdue if overdue['customer'] in my_customers]

# Alert System
def send_alert(username, message):
    """Send alert to user"""
    if not get_account(username):
        return False
    
    alert_id = generate_id()
    
    conn = get_connection()
    if not conn:
        return False
        
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO alerts (id, username, date, timestamp, message, read)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (alert_id, username, get_current_date(), get_current_datetime(), message, False))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        return False

def get_alerts(username):
    """Get user alerts"""
    conn = get_connection()
    if not conn:
        return []
        
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT * FROM alerts WHERE username = ? ORDER BY timestamp DESC LIMIT 50
        ''', (username,))
        
        rows = cursor.fetchall()
        conn.close()
        
        alerts = []
        for row in rows:
            alerts.append({
                "id": row[0],
                "username": row[1],
                "date": row[2],
                "timestamp": row[3],
                "message": row[4],
                "read": bool(row[5])
            })
        
        return alerts
    except Exception as e:
        conn.close()
        return []

def mark_alerts_read(username):
    """Mark all alerts as read"""
    conn = get_connection()
    if not conn:
        return False
        
    cursor = conn.cursor()
    
    try:
        cursor.execute('UPDATE alerts SET read = 1 WHERE username = ?', (username,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        return False

def delete_alert(alert_id):
    """Delete an alert"""
    conn = get_connection()
    if not conn:
        return False
        
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM alerts WHERE id = ?', (alert_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        return False

# Balance and Reporting
def calculate_balance(username):
    """Calculate customer balance with comprehensive None handling"""
    try:
        transactions = get_customer_transactions(username)
        
        total_debt = 0
        total_payment = 0
        total_interest_paid = 0
        
        for tx in transactions:
            if not tx.get("confirmed"):
                continue
                
            amount = tx.get("amount")
            if amount is None:
                continue
                
            try:
                amount_float = float(amount)
            except (TypeError, ValueError):
                continue
                
            if tx.get("type") == "utang":
                total_debt += amount_float
                # Add interest amount for utang transactions
                interest_amount = tx.get("interest_amount")
                if interest_amount is not None:
                    try:
                        total_interest_paid += float(interest_amount)
                    except (TypeError, ValueError):
                        pass
            elif tx.get("type") == "payment":
                total_payment += amount_float
                # Add interest amount for payment transactions
                interest_amount = tx.get("interest_amount")
                if interest_amount is not None:
                    try:
                        total_interest_paid += float(interest_amount)
                    except (TypeError, ValueError):
                        pass
        
        outstanding = round(total_debt - total_payment, 2)
        account = get_account(username)
        debt_limit = account.get("debtLimit", 0) if account else 0
        
        return {
            "total_debt": total_debt,
            "total_payment": total_payment,
            "outstanding": outstanding,
            "debt_limit": debt_limit,
            "available_credit": max(0, debt_limit - outstanding),
            "total_interest_paid": total_interest_paid
        }
    except Exception as e:
        print(f"Error calculating balance for {username}: {e}")
        return {
            "total_debt": 0,
            "total_payment": 0,
            "outstanding": 0,
            "debt_limit": 0,
            "available_credit": 0,
            "total_interest_paid": 0
        }

def get_top_debtors(limit=5):
    """Get customers with highest outstanding balances"""
    try:
        customers = list_accounts("Customer")
        
        debtor_balances = []
        for account in customers:
            balance = calculate_balance(account["username"])
            if balance["outstanding"] > 0:
                debtor_balances.append((account["username"], balance["outstanding"]))
        
        debtor_balances.sort(key=lambda x: x[1], reverse=True)
        return debtor_balances[:limit]
    except Exception as e:
        return []

def get_my_top_debtors(owner_username, limit=5):
    """Get customers created by specific owner with highest outstanding balances"""
    try:
        customers = list_my_accounts(owner_username)
        
        debtor_balances = []
        for account in customers:
            if account["role"] == "Customer":
                balance = calculate_balance(account["username"])
                if balance["outstanding"] > 0:
                    debtor_balances.append((account["username"], balance["outstanding"]))
        
        debtor_balances.sort(key=lambda x: x[1], reverse=True)
        return debtor_balances[:limit]
    except Exception as e:
        return []

# Settings Management
def get_setting(key, default=None):
    """Get system setting"""
    conn = get_connection()
    if not conn:
        return default
        
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT value FROM system_settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return default
        
        value = row[0]
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            return value
    except Exception as e:
        conn.close()
        return default

def update_setting(key, value):
    """Update system setting"""
    conn = get_connection()
    if not conn:
        return False
        
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO system_settings (key, value) VALUES (?, ?)
        ''', (key, str(value)))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        return False

def reset_all_data():
    """Reset all application data"""
    conn = get_connection()
    if not conn:
        return False, "Database connection failed"
        
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM accounts')
        cursor.execute('DELETE FROM transactions')
        cursor.execute('DELETE FROM alerts')
        
        default_settings = [
            ('currencySymbol', '₱'),
            ('appName', 'IUMS'),
            ('customerCreditLimit', '10000.00'),
            ('interestRate', '3.0'),
            ('dueDateReminderDays', '7,3,1,0')
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO system_settings (key, value) VALUES (?, ?)
        ''', default_settings)
        
        conn.commit()
        conn.close()
        return True, "All data has been reset successfully"
    except Exception as e:
        conn.close()
        return False, f"Error resetting data: {str(e)}"

# Utility Functions
def format_currency(amount):
    """Format amount as currency with comprehensive None handling"""
    symbol = get_setting("currencySymbol", "₱")
    try:
        # Handle None values and empty strings
        if amount is None:
            amount = 0.0
        elif isinstance(amount, str) and amount.strip() == "":
            amount = 0.0
        
        amount_float = float(amount)
        return f"{symbol} {amount_float:,.2f}"
    except (ValueError, TypeError):
        return f"{symbol} 0.00"

def get_customer_list():
    """Get list of all customer usernames"""
    try:
        return [acc["username"] for acc in list_accounts("Customer")]
    except Exception as e:
        return []

def get_my_customer_list(owner_username=None):
    """Get list of customer usernames created by specific owner"""
    if owner_username is None:
        owner_username = st.session_state.get("username")
        if not owner_username:
            return []
    
    try:
        accounts = list_my_accounts(owner_username)
        return [acc["username"] for acc in accounts if acc["role"] == "Customer"]
    except Exception as e:
        print(f"Error getting customer list: {e}")
        return []

def validate_amount(amount):
    """Validate amount input with comprehensive None handling"""
    try:
        if amount is None:
            return False, "Amount cannot be empty"
        
        if isinstance(amount, str):
            amount = amount.strip()
            if amount == "":
                return False, "Amount cannot be empty"
        
        amount_float = float(amount)
        if amount_float <= 0:
            return False, "Amount must be greater than 0"
        if amount_float > 1000000:  # Reasonable upper limit
            return False, "Amount is too large"
            
        return True, amount_float
    except (ValueError, TypeError) as e:
        return False, f"Please enter a valid number: {str(e)}"

def get_personal_info_display(account):
    """Get formatted personal information for display without contact number"""
    try:
        personal_info = account.get("personalInfo", {})
        full_name = personal_info.get("full_name", "Not provided")
        email = personal_info.get("email", "Not provided")
        address = personal_info.get("address", "Not provided")
        
        info_lines = []
        if full_name and full_name != "Not provided":
            info_lines.append(f"Name: {full_name}")
        if email and email != "Not provided":
            info_lines.append(f"Email: {email}")
        if address and address != "Not provided":
            info_lines.append(f"Address: {address}")
        
        return "\n".join(info_lines) if info_lines else "No personal information"
    except Exception as e:
        return "Error loading personal information"

def calculate_interest(principal, interest_rate):
    """Calculate interest amount with comprehensive None handling"""
    try:
        if principal is None:
            return 0.0
        
        if isinstance(principal, str) and principal.strip() == "":
            return 0.0
            
        principal_float = float(principal)
        interest_rate_float = float(interest_rate)
        return round(principal_float * (interest_rate_float / 100), 2)
    except (ValueError, TypeError):
        return 0.0

def get_interest_rate():
    """Get the current interest rate from settings"""
    return get_setting("interestRate", 3.0)

def get_transaction_statistics():
    """Get comprehensive transaction statistics"""
    try:
        transactions = get_all_transactions()
        accounts = list_accounts("Customer")
        
        confirmed_transactions = [t for t in transactions if t.get("confirmed")]
        pending_transactions = [t for t in transactions if not t.get("confirmed")]
        
        utang_transactions = [t for t in confirmed_transactions if t.get("type") == "utang"]
        payment_transactions = [t for t in confirmed_transactions if t.get("type") == "payment"]
        
        total_utang = sum(t.get("amount", 0) for t in utang_transactions)
        total_payments = sum(t.get("amount", 0) for t in payment_transactions)
        total_interest = sum(t.get("interest_amount", 0) for t in utang_transactions)
        
        # Due date statistics
        upcoming_due_dates = get_upcoming_due_dates(7)
        overdue_transactions = get_overdue_transactions()
        
        # Count customers with debt
        customers_with_debt = 0
        for acc in accounts:
            balance = calculate_balance(acc["username"])
            if balance["outstanding"] > 0:
                customers_with_debt += 1
        
        return {
            "total_transactions": len(transactions),
            "confirmed_transactions": len(confirmed_transactions),
            "pending_transactions": len(pending_transactions),
            "utang_transactions": len(utang_transactions),
            "payment_transactions": len(payment_transactions),
            "total_utang_amount": total_utang,
            "total_payment_amount": total_payments,
            "total_interest_amount": total_interest,
            "net_outstanding": total_utang - total_payments,
            "active_customers": len(accounts),
            "customers_with_debt": customers_with_debt,
            "upcoming_due_dates": len(upcoming_due_dates),
            "overdue_transactions": len(overdue_transactions)
        }
    except Exception as e:
        print(f"Error getting transaction statistics: {e}")
        return {
            "total_transactions": 0,
            "confirmed_transactions": 0,
            "pending_transactions": 0,
            "utang_transactions": 0,
            "payment_transactions": 0,
            "total_utang_amount": 0,
            "total_payment_amount": 0,
            "total_interest_amount": 0,
            "net_outstanding": 0,
            "active_customers": 0,
            "customers_with_debt": 0,
            "upcoming_due_dates": 0,
            "overdue_transactions": 0
        }

def get_my_transaction_statistics(owner_username):
    """Get transaction statistics for customers created by specific owner"""
    try:
        # Get my customers
        my_customers = [acc["username"] for acc in list_my_accounts(owner_username) if acc["role"] == "Customer"]
        
        if not my_customers:
            return {
                "total_transactions": 0,
                "confirmed_transactions": 0,
                "pending_transactions": 0,
                "utang_transactions": 0,
                "payment_transactions": 0,
                "total_utang_amount": 0,
                "total_payment_amount": 0,
                "total_interest_amount": 0,
                "net_outstanding": 0,
                "active_customers": 0,
                "customers_with_debt": 0,
                "upcoming_due_dates": 0,
                "overdue_transactions": 0
            }
        
        # Get transactions for my customers
        transactions = get_my_transactions(owner_username)
        
        confirmed_transactions = [t for t in transactions if t.get("confirmed")]
        pending_transactions = [t for t in transactions if not t.get("confirmed")]
        
        utang_transactions = [t for t in confirmed_transactions if t.get("type") == "utang"]
        payment_transactions = [t for t in confirmed_transactions if t.get("type") == "payment"]
        
        total_utang = sum(t.get("amount", 0) for t in utang_transactions)
        total_payments = sum(t.get("amount", 0) for t in payment_transactions)
        total_interest = sum(t.get("interest_amount", 0) for t in utang_transactions)
        
        # Due date statistics for my customers
        upcoming_due_dates = get_my_upcoming_due_dates(owner_username, 7)
        overdue_transactions = get_my_overdue_transactions(owner_username)
        
        # Count my customers with debt
        customers_with_debt = 0
        for customer in my_customers:
            balance = calculate_balance(customer)
            if balance["outstanding"] > 0:
                customers_with_debt += 1
        
        return {
            "total_transactions": len(transactions),
            "confirmed_transactions": len(confirmed_transactions),
            "pending_transactions": len(pending_transactions),
            "utang_transactions": len(utang_transactions),
            "payment_transactions": len(payment_transactions),
            "total_utang_amount": total_utang,
            "total_payment_amount": total_payments,
            "total_interest_amount": total_interest,
            "net_outstanding": total_utang - total_payments,
            "active_customers": len(my_customers),
            "customers_with_debt": customers_with_debt,
            "upcoming_due_dates": len(upcoming_due_dates),
            "overdue_transactions": len(overdue_transactions)
        }
    except Exception as e:
        print(f"Error getting my transaction statistics: {e}")
        return {
            "total_transactions": 0,
            "confirmed_transactions": 0,
            "pending_transactions": 0,
            "utang_transactions": 0,
            "payment_transactions": 0,
            "total_utang_amount": 0,
            "total_payment_amount": 0,
            "total_interest_amount": 0,
            "net_outstanding": 0,
            "active_customers": 0,
            "customers_with_debt": 0,
            "upcoming_due_dates": 0,
            "overdue_transactions": 0
        }

def update_due_date_status(customer):
    """Update due date status when payments are made - automatically removes paid due dates"""
    conn = get_connection()
    if not conn:
        return False
        
    cursor = conn.cursor()
    
    try:
        # Get customer's current balance
        balance = calculate_balance(customer)
        outstanding_balance = balance["outstanding"]
        
        if outstanding_balance <= 0:
            # Customer has no outstanding balance - clear ALL due dates
            cursor.execute('''
                UPDATE transactions 
                SET due_date = NULL 
                WHERE customer = ? AND type = 'utang' AND confirmed = 1
            ''', (customer,))
            
            # Send alert to customer
            send_alert(customer, "🎉 All utang fully paid! Due dates have been cleared.")
            
        else:
            # Customer has outstanding balance - apply FIFO payment logic
            # Get all unpaid utang ordered by date (oldest first)
            cursor.execute('''
                SELECT id, amount, due_date, description 
                FROM transactions 
                WHERE customer = ? AND type = 'utang' AND confirmed = 1 AND due_date IS NOT NULL
                ORDER BY date ASC
            ''', (customer,))
            
            utang_rows = cursor.fetchall()
            
            remaining_balance = outstanding_balance
            cleared_utang = []
            
            # Work backwards from newest to oldest to find which utang are still unpaid
            for utang_row in reversed(utang_rows):
                utang_id, utang_amount, due_date, description = utang_row
                
                if remaining_balance >= utang_amount:
                    # This utang is fully paid - clear due date
                    cursor.execute('UPDATE transactions SET due_date = NULL WHERE id = ?', (utang_id,))
                    cleared_utang.append(description)
                    remaining_balance -= utang_amount
                else:
                    # This utang is partially paid or unpaid - keep due date
                    break
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        conn.close()
        print(f"Error updating due date status: {e}")
        return False

# Customer-specific due date functions
def get_upcoming_due_dates_for_customer(username, days_threshold=7):
    """Get upcoming due dates for a specific customer - ONLY FOR UNPAID UTANG"""
    transactions = get_customer_transactions(username)
    
    upcoming_due_dates = []
    today = datetime.now().date()
    
    # Calculate current outstanding balance
    balance = calculate_balance(username)
    has_outstanding_balance = balance["outstanding"] > 0
    
    # If no outstanding balance, return empty list immediately
    if not has_outstanding_balance:
        return []
    
    for transaction in transactions:
        # Only show due dates for UNPAID utang with due dates
        if (transaction["type"] == "utang" and 
            transaction["confirmed"] and 
            transaction.get("due_date") and
            has_outstanding_balance):
            
            due_date = datetime.strptime(transaction["due_date"], '%Y-%m-%d').date()
            days_until_due = (due_date - today).days
            
            if days_until_due <= days_threshold:
                upcoming_due_dates.append({
                    'description': transaction['description'],
                    'amount': transaction['amount'],
                    'due_date': transaction['due_date'],
                    'days_until_due': days_until_due
                })
    
    return upcoming_due_dates

def get_overdue_transactions_for_customer(username):
    """Get overdue transactions for a specific customer - ONLY FOR UNPAID UTANG"""
    transactions = get_customer_transactions(username)
    
    overdue = []
    today = datetime.now().date()
    
    # Calculate current outstanding balance
    balance = calculate_balance(username)
    has_outstanding_balance = balance["outstanding"] > 0
    
    # If no outstanding balance, return empty list immediately
    if not has_outstanding_balance:
        return []
    
    for transaction in transactions:
        # Only show overdue for UNPAID utang with due dates
        if (transaction["type"] == "utang" and 
            transaction["confirmed"] and 
            transaction.get("due_date") and
            has_outstanding_balance):
            
            due_date = datetime.strptime(transaction["due_date"], '%Y-%m-%d').date()
            days_overdue = (today - due_date).days
            
            if days_overdue > 0:
                overdue.append({
                    'description': transaction['description'],
                    'amount': transaction['amount'],
                    'due_date': transaction['due_date'],
                    'days_overdue': days_overdue
                })
    
    return overdue

def verify_transaction_exists(transaction_id):
    """Verify if a transaction exists in the database"""
    conn = get_connection()
    if not conn:
        return False
        
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT id FROM transactions WHERE id = ?', (transaction_id,))
        row = cursor.fetchone()
        conn.close()
        return row is not None
    except Exception as e:
        conn.close()
        return False