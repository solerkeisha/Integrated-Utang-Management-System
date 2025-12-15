import sqlite3
import json
import os
from datetime import datetime, timedelta

def get_connection():
    """Get database connection"""
    try:
        conn = sqlite3.connect('iums.db', check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def init_database():
    """Initialize database tables with proper default values"""
    conn = get_connection()
    if not conn:
        return False
        
    cursor = conn.cursor()
    
    try:
        # Create accounts table WITH created_by field
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                debt_limit REAL DEFAULT 0,
                personal_info TEXT,
                created_date TEXT,
                created_by TEXT  -- Track who created the account
            )
        ''')
        
        # Create transactions table with proper defaults
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                customer TEXT NOT NULL,
                type TEXT NOT NULL,
                description TEXT,
                amount REAL NOT NULL DEFAULT 0,
                date TEXT NOT NULL,
                confirmed INTEGER DEFAULT 0,
                otp TEXT,
                created_by TEXT,
                created_at TEXT,
                confirmed_at TEXT,
                status TEXT DEFAULT 'pending',
                interest_rate REAL DEFAULT 0,
                interest_amount REAL DEFAULT 0,
                principal_amount REAL DEFAULT 0,
                due_date TEXT,
                FOREIGN KEY (customer) REFERENCES accounts (username)
            )
        ''')
        
        # Create alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                date TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                message TEXT NOT NULL,
                read INTEGER DEFAULT 0,
                FOREIGN KEY (username) REFERENCES accounts (username)
            )
        ''')
        
        # Create system settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # Insert default settings
        default_settings = [
            ('currencySymbol', '₱'),
            ('appName', 'IUMS'),
            ('customerCreditLimit', '10000.00'),
            ('interestRate', '3.0'),
            ('dueDateReminderDays', '7,3,1,0')
        ]
        
        cursor.executemany('INSERT OR IGNORE INTO system_settings (key, value) VALUES (?, ?)', default_settings)
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully with created_by field")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        if conn:
            conn.close()
        return False

def add_missing_columns():
    """Add missing columns to existing tables including created_by"""
    conn = get_connection()
    if not conn:
        return False
        
    cursor = conn.cursor()
    
    try:
        # Check accounts table columns
        cursor.execute("PRAGMA table_info(accounts)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add created_by column if missing
        if 'created_by' not in columns:
            cursor.execute('ALTER TABLE accounts ADD COLUMN created_by TEXT')
            # Set default for existing records
            cursor.execute("UPDATE accounts SET created_by = 'system' WHERE created_by IS NULL")
            print("✅ Added created_by column to accounts table")
        
        # Check transactions table columns
        cursor.execute("PRAGMA table_info(transactions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add missing columns to transactions table
        missing_columns = []
        if 'interest_rate' not in columns:
            cursor.execute('ALTER TABLE transactions ADD COLUMN interest_rate REAL DEFAULT 0')
            missing_columns.append('interest_rate')
        
        if 'interest_amount' not in columns:
            cursor.execute('ALTER TABLE transactions ADD COLUMN interest_amount REAL DEFAULT 0')
            missing_columns.append('interest_amount')
        
        if 'principal_amount' not in columns:
            cursor.execute('ALTER TABLE transactions ADD COLUMN principal_amount REAL DEFAULT 0')
            missing_columns.append('principal_amount')
        
        if 'status' not in columns:
            cursor.execute('ALTER TABLE transactions ADD COLUMN status TEXT DEFAULT "pending"')
            missing_columns.append('status')
        
        if 'due_date' not in columns:
            cursor.execute('ALTER TABLE transactions ADD COLUMN due_date TEXT')
            missing_columns.append('due_date')
        
        if missing_columns:
            print(f"✅ Added missing columns to transactions: {', '.join(missing_columns)}")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error adding columns: {e}")
        if conn:
            conn.close()
        return False

def migrate_created_by_field():
    """Ensure all accounts have a created_by value"""
    conn = get_connection()
    if not conn:
        return False
        
    cursor = conn.cursor()
    
    try:
        # Update any NULL created_by fields to 'system'
        cursor.execute("UPDATE accounts SET created_by = 'system' WHERE created_by IS NULL")
        
        conn.commit()
        conn.close()
        print("✅ Migrated created_by field for all accounts")
        return True
    except Exception as e:
        print(f"❌ Error migrating created_by field: {e}")
        if conn:
            conn.close()
        return False

def migrate_from_json():
    """Migrate data from old JSON format to database"""
    if not os.path.exists('data.json'):
        return True
        
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            old_data = json.load(f)
        
        conn = get_connection()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Migrate accounts
        if 'accounts' in old_data:
            for username, account_data in old_data['accounts'].items():
                personal_info = account_data.get('personalInfo', {})
                personal_info_json = json.dumps(personal_info)
                created_by = account_data.get('created_by', 'system')
                
                cursor.execute('''
                    INSERT OR IGNORE INTO accounts 
                    (username, password, role, debt_limit, personal_info, created_date, created_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    username,
                    account_data.get('password', ''),
                    account_data.get('role', 'Customer'),
                    account_data.get('debtLimit', 10000.00),
                    personal_info_json,
                    account_data.get('created_date', datetime.now().isoformat()),
                    created_by
                ))
        
        # Migrate transactions
        if 'transactions' in old_data:
            for transaction_id, transaction_data in old_data['transactions'].items():
                due_date = transaction_data.get('due_date') or (datetime.strptime(transaction_data.get('date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d') + timedelta(days=30)).strftime('%Y-%m-%d')
                
                cursor.execute('''
                    INSERT OR IGNORE INTO transactions 
                    (id, customer, type, description, amount, date, confirmed, otp, created_by, created_at, confirmed_at, status, interest_rate, interest_amount, principal_amount, due_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    transaction_id,
                    transaction_data.get('customer', ''),
                    transaction_data.get('type', 'utang'),
                    transaction_data.get('description', ''),
                    transaction_data.get('amount', 0),
                    transaction_data.get('date', datetime.now().strftime('%Y-%m-%d')),
                    int(transaction_data.get('confirmed', False)),
                    transaction_data.get('otp', ''),
                    transaction_data.get('created_by', 'system'),
                    transaction_data.get('created_at', datetime.now().isoformat()),
                    transaction_data.get('confirmed_at', ''),
                    transaction_data.get('status', 'confirmed' if transaction_data.get('confirmed') else 'pending'),
                    transaction_data.get('interest_rate', 0),
                    transaction_data.get('interest_amount', 0),
                    transaction_data.get('principal_amount', transaction_data.get('amount', 0)),
                    due_date
                ))
        
        conn.commit()
        conn.close()
        
        # Backup old file
        os.rename('data.json', 'data.json.backup')
        print("✅ Successfully migrated data from data.json to database")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def check_database_health():
    """Check database health and fix issues"""
    conn = get_connection()
    if not conn:
        return False, "Cannot connect to database"
    
    try:
        cursor = conn.cursor()
        
        # Check if all tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        required_tables = ['accounts', 'transactions', 'alerts', 'system_settings']
        
        missing_tables = [table for table in required_tables if table not in tables]
        if missing_tables:
            conn.close()
            return False, f"Missing tables: {', '.join(missing_tables)}"
        
        # Check accounts table structure
        cursor.execute("PRAGMA table_info(accounts)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'created_by' not in columns:
            conn.close()
            add_missing_columns()
            return True, "Added created_by column to accounts table"
        
        # Check transactions table structure
        cursor.execute("PRAGMA table_info(transactions)")
        columns = [column[1] for column in cursor.fetchall()]
        required_columns = ['interest_rate', 'interest_amount', 'principal_amount', 'status', 'due_date']
        
        missing_columns = [col for col in required_columns if col not in columns]
        if missing_columns:
            conn.close()
            add_missing_columns()
            return True, f"Added missing columns to transactions: {', '.join(missing_columns)}"
        
        conn.close()
        return True, "Database is healthy"
        
    except Exception as e:
        if conn:
            conn.close()
        return False, f"Database health check failed: {str(e)}"