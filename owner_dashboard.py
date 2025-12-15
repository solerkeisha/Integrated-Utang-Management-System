import streamlit as st
from utils import (
    calculate_balance, get_customer_transactions, get_pending_transactions,
    confirm_transaction_with_otp, get_alerts, mark_alerts_read, format_currency,
    send_alert, get_account, get_personal_info_display, update_account_password, 
    update_account_username, get_setting, list_my_accounts, create_account,
    delete_account, create_pending_transaction_with_due_date, get_all_transactions,
    get_my_top_debtors, update_setting, reset_all_data, get_my_customer_list,
    validate_amount, calculate_interest, get_interest_rate, get_transaction_statistics,
    get_my_transaction_statistics, delete_transaction, delete_alert, check_due_dates, 
    get_upcoming_due_dates, get_overdue_transactions, verify_transaction_exists,
    get_my_upcoming_due_dates, get_my_overdue_transactions, get_my_transactions
)
from datetime import datetime, timedelta

def debug_transaction_state():
    """Debug function to check transaction state"""
    print("🔧 DEBUG: Current transaction state:")
    if 'current_transaction' in st.session_state:
        for key, value in st.session_state.current_transaction.items():
            print(f"   {key}: {value}")
    else:
        print("   No current transaction in session state")

def show_owner_dashboard():
    """Show owner dashboard with organized message containers"""
    
    if st.session_state.current_page == "Dashboard":
        show_owner_overview()
    elif st.session_state.current_page == "Manage Account":
        show_account_management()
    elif st.session_state.current_page == "Add Utang":
        show_add_utang()
    elif st.session_state.current_page == "Record Payment":
        show_record_payment()
    elif st.session_state.current_page == "Reports":
        show_reports()
    elif st.session_state.current_page == "Settings":
        show_settings()
    elif st.session_state.current_page == "Pending Confirmations":
        show_pending_confirmations()
    elif st.session_state.current_page == "Owner Profile":
        show_owner_profile()

def show_owner_overview():
    """Show owner overview with organized message containers"""
    st.markdown("## Owner Dashboard")
    
    # Custom CSS for organized message containers
    st.markdown("""
    <style>
    .owner-metric-box {
        background: var(--bg-secondary);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        text-align: center;
        transition: transform 0.2s ease;
    }
    .owner-metric-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.15);
    }
    .owner-metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
        color: var(--text-primary) !important;
    }
    .owner-metric-label {
        font-size: 0.9rem;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
        font-weight: 500;
        opacity: 0.9;
    }
    
    .message-container {
        background: var(--bg-secondary);
        border-radius: 12px;
        border: 1px solid var(--border-color);
        margin: 1rem 0;
        overflow: hidden;
    }
    .message-header {
        background: var(--navy-dark);
        padding: 1rem 1.5rem;
        font-weight: 600;
        color: var(--text-primary);
        border-bottom: 1px solid var(--border-color);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .message-content {
        padding: 1.5rem;
    }
    
    .due-date-alert {
        background: var(--bg-secondary);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 6px solid;
        margin: 1rem 0;
        border: 1px solid var(--border-color);
    }
    .due-date-critical { border-left-color: var(--accent-red); background: rgba(239, 68, 68, 0.1); }
    .due-date-warning { border-left-color: var(--accent-amber); background: rgba(245, 158, 11, 0.1); }
    .due-date-info { border-left-color: var(--accent-blue); background: rgba(59, 130, 246, 0.1); }
    
    .debtor-item {
        background: var(--bg-secondary);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid;
        margin: 0.5rem 0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        border: 1px solid var(--border-color);
    }
    
    .action-buttons {
        display: flex;
        gap: 0.5rem;
        margin-top: 1rem;
        flex-wrap: wrap;
    }
    
    .action-button {
        flex: 1;
        min-width: 120px;
    }
    
    .alert-badge {
        background: var(--accent-red);
        color: white;
        border-radius: 12px;
        padding: 0.25rem 0.75rem;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .empty-state {
        text-align: center;
        padding: 3rem 2rem;
        color: var(--text-secondary);
    }
    
    .empty-state-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }
    
    .empty-state-title {
        color: var(--text-primary);
        margin-bottom: 0.5rem;
        font-size: 1.2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Get current owner's username
    owner_username = st.session_state.username
    
    # Quick stats in organized containers - ONLY SHOW OWNER'S DATA
    accounts = list_my_accounts(owner_username)
    transactions = get_my_transactions(owner_username)
    
    total_customers = len([acc for acc in accounts if acc.get("role") == "Customer"])
    total_transactions = len(transactions)
    
    # Calculate total outstanding and interest for owner's customers
    total_outstanding = 0
    total_interest = 0
    
    for account in accounts:
        if account.get("role") == "Customer":
            balance = calculate_balance(account["username"])
            total_outstanding += balance["outstanding"]
            total_interest += balance["total_interest_paid"]
    
    # Due date statistics for owner's customers
    upcoming_due_dates = get_my_upcoming_due_dates(owner_username, 7)
    overdue_transactions = get_my_overdue_transactions(owner_username)
    
    # Metrics Container
    with st.container():
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f"""
            <div class="owner-metric-box">
                <div class="owner-metric-label">My Customers</div>
                <div class="owner-metric-value" style="color: var(--accent-blue) !important;">{total_customers}</div>
                <div style="font-size: 0.8rem; color: var(--text-primary); opacity: 0.7;">Customers I created</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="owner-metric-box">
                <div class="owner-metric-label">My Transactions</div>
                <div class="owner-metric-value" style="color: var(--navy-light) !important;">{total_transactions}</div>
                <div style="font-size: 0.8rem; color: var(--text-primary); opacity: 0.7;">Transactions with my customers</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="owner-metric-box">
                <div class="owner-metric-label">Total Outstanding</div>
                <div class="owner-metric-value" style="color: var(--accent-red) !important;">{format_currency(total_outstanding)}</div>
                <div style="font-size: 0.8rem; color: var(--text-primary); opacity: 0.8;">Amount due from my customers</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="owner-metric-box">
                <div class="owner-metric-label">Total Interest</div>
                <div class="owner-metric-value" style="color: var(--accent-amber) !important;">{format_currency(total_interest)}</div>
                <div style="font-size: 0.8rem; color: var(--text-primary); opacity: 0.7;">Interest from my customers</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div class="owner-metric-box">
                <div class="owner-metric-label">Due Dates</div>
                <div class="owner-metric-value" style="color: var(--accent-teal) !important;">{len(upcoming_due_dates)}</div>
                <div style="font-size: 0.8rem; color: var(--text-primary); opacity: 0.7;">Upcoming in 7 days (my customers)</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Alerts Container - ORGANIZED MESSAGES
    with st.container():
        alert_count = 0
        
        # Due Date Alerts for owner's customers
        if overdue_transactions:
            alert_count += 1
            st.markdown(f"""
            <div class="due-date-alert due-date-critical">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div style="flex: 1;">
                        <h4 style="margin: 0; color: var(--text-primary);">🚨 Overdue Utang (My Customers)</h4>
                        <p style="margin: 0.5rem 0 0 0; color: var(--text-primary); opacity: 0.8;">
                            There are {len(overdue_transactions)} utang(s) from my customers that are overdue!
                        </p>
                    </div>
                    <div style="font-size: 2rem;">⚠️</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if upcoming_due_dates:
            critical_due = len([d for d in upcoming_due_dates if d['days_until_due'] <= 3])
            if critical_due > 0:
                alert_count += 1
                st.markdown(f"""
                <div class="due-date-alert due-date-warning">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div style="flex: 1;">
                            <h4 style="margin: 0; color: var(--text-primary);">⏰ Critical Due Dates (My Customers)</h4>
                            <p style="margin: 0.5rem 0 0 0; color: var(--text-primary); opacity: 0.8;">
                                {critical_due} utang(s) from my customers due within 3 days!
                            </p>
                        </div>
                        <div style="font-size: 2rem;">🔔</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Pending transactions alert for owner's customers
        pending_count = len(get_pending_transactions())
        if pending_count > 0:
            alert_count += 1
            st.markdown(f"""
            <div class="due-date-alert due-date-info">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div style="flex: 1;">
                        <h4 style="margin: 0; color: var(--text-primary);">📋 Pending Transactions (My Customers)</h4>
                        <p style="margin: 0.5rem 0 0 0; color: var(--text-primary); opacity: 0.8;">
                            There are {pending_count} transactions with my customers waiting for OTP confirmation
                        </p>
                    </div>
                    <div style="font-size: 2rem;">📋</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("View Pending Confirmations", use_container_width=True, key="view_pending"):
                st.session_state.current_page = "Pending Confirmations"
                st.rerun()
        
        if alert_count == 0:
            st.markdown("""
            <div class="empty-state">
                <p>No urgent alerts at this time</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Quick Actions Container
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔄 Refresh Dashboard", use_container_width=True, key="refresh_owner"):
                st.rerun()
        
        with col2:
            # Fixed Check Due Dates button with proper feedback
            if st.button("📅 Check Due Dates", use_container_width=True, key="check_due_dates_overview"):
                with st.spinner("🔍 Checking due dates and sending reminders..."):
                    try:
                        success, message = check_due_dates()
                        if success:
                            st.success(f"✅ {message}")
                            
                            # Show detailed results for owner's customers
                            overdue_count = len(get_my_overdue_transactions(owner_username))
                            upcoming_count = len(get_my_upcoming_due_dates(owner_username, 7))
                            
                            if overdue_count > 0:
                                st.error(f"🚨 {overdue_count} overdue utang(s) found for my customers")
                            if upcoming_count > 0:
                                st.info(f"📅 {upcoming_count} upcoming due date(s) in the next 7 days for my customers")
                            if overdue_count == 0 and upcoming_count == 0:
                                st.success("🎉 No due date issues found for my customers! All utang are either paid or not due soon.")
                                
                        else:
                            st.error(f"❌ {message}")
                    except Exception as e:
                        st.error(f"❌ Error checking due dates: {str(e)}")
        
        with col3:
            if st.button("👤 My Profile", use_container_width=True, key="owner_profile"):
                st.session_state.current_page = "Owner Profile"
                st.rerun()
        
        with col4:
            if st.button("📊 View Reports", use_container_width=True, key="view_reports"):
                st.session_state.current_page = "Reports"
                st.rerun()
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Top Debtors Container - ONLY OWNER'S CUSTOMERS
    with st.container():
        st.markdown("""
        <div class="message-container">
            <div class="message-header">
                <span>Top Debtors (My Customers)</span>
            </div>
        """, unsafe_allow_html=True)
        
        top_debtors = get_my_top_debtors(owner_username, 5)
        
        if top_debtors:
            for i, (username, amount) in enumerate(top_debtors, 1):
                rank_color = "var(--accent-red)" if i == 1 else "var(--accent-amber)" if i == 2 else "var(--accent-green)" if i == 3 else "var(--accent-blue)"
                
                st.markdown(f"""
                <div class="debtor-item" style="border-left-color: {rank_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: flex; align-items: center; gap: 1rem;">
                            <div style="background: {rank_color}; color: white; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold;">{i}</div>
                            <div>
                                <div style="font-weight: bold; color: var(--text-primary);">{username}</div>
                                <div style="font-size: 0.8rem; color: var(--text-primary); opacity: 0.7;">Outstanding Balance</div>
                            </div>
                        </div>
                        <div style="font-weight: bold; color: {rank_color}; font-size: 1.1rem;">{format_currency(amount)}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">💰</div>
                <h4 class="empty-state-title">No Outstanding Debts</h4>
                <p>All my customers have paid their balances</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)

def show_account_management():
    """Show account management in organized containers - ONLY SHOW OWNER'S ACCOUNTS"""
    st.markdown("## Manage My Accounts")
    
    # Get current owner's username
    owner_username = st.session_state.username
    
    # Create new account form in a container
    with st.container():
        st.markdown("""
        <div class="message-container">
            <div class="message-header">
                <span>Create New Account</span>
            </div>
            <div class="message-content">
        """, unsafe_allow_html=True)
        
        with st.form("create_account_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Account Details**")
                username = st.text_input("Username", placeholder="Enter username", key="create_username")
                password = st.text_input("Password", type="password", placeholder="Enter password", key="create_password")
                role = st.selectbox("Role", ["Customer"], key="create_role")
            
            with col2:
                st.markdown("**Personal Information**")
                full_name = st.text_input("Full Name *", placeholder="Enter full name", key="create_full_name")
                email = st.text_input("Email Address *", placeholder="Enter email address", key="create_email")
                address = st.text_area("Address", placeholder="Enter address", height=80, key="create_address")
            
            submitted = st.form_submit_button("Create Account", use_container_width=True)
            
            if submitted:
                if not username or not password:
                    st.error("Username and password are required")
                    return
                
                # Personal info is required for customer accounts
                if not full_name or not email:
                    st.error("Full name and email address are required for customer accounts")
                    return
                
                # Basic email validation
                if "@" not in email or "." not in email:
                    st.error("Please enter a valid email address")
                    return
                
                personal_info = {
                    "full_name": full_name,
                    "email": email,
                    "address": address
                }
                
                # Pass the current owner as creator
                success, message = create_account(
                    username, 
                    password, 
                    role, 
                    personal_info,
                    created_by=owner_username
                )
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Existing accounts in containers - ONLY SHOW ACCOUNTS CREATED BY THIS OWNER
    st.markdown(f"## My Created Accounts")
    
    # Use the filtered function
    accounts = list_my_accounts(owner_username)
    
    if not accounts:
        st.markdown("""
        <div class="message-container">
            <div class="message-content">
                <div class="empty-state">
                    <div class="empty-state-icon">👥</div>
                    <h4 class="empty-state-title">No Accounts Yet</h4>
                    <p>You haven't created any accounts yet. Create your first account above.</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    for account in accounts:
        with st.container():
            st.markdown(f"""
            <div class="message-container">
                <div class="message-header">
                    <span>👤 {account['username']}</span>
                    <div class="alert-badge">{account['role']}</div>
                </div>
                <div class="message-content">
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
            
            with col1:
                st.write(f"**Username:** {account['username']}")
                st.write(f"**Role:** {account['role']}")
                personal_info = get_personal_info_display(account)
                if personal_info != "No personal information":
                    with st.expander("View Personal Info"):
                        st.text(personal_info)
            
            with col2:
                if account["role"] == "Customer":
                    balance = calculate_balance(account["username"])
                    st.write(f"**Balance:** {format_currency(balance['outstanding'])}")
                    st.write(f"**Available Credit:** {format_currency(balance['available_credit'])}")
                else:
                    st.write("**System Account**")
            
            with col3:
                if account["role"] == "Customer":
                    st.write(f"**Limit:** {format_currency(account['debtLimit'])}")
                else:
                    st.write("**No Limit**")
            
            with col4:
                st.write(f"**Created:** {account.get('created_date', 'Unknown')[:10]}")
            
            with col5:
                if account["username"] != st.session_state.username:
                    if st.button("Delete", key=f"del_{account['username']}", use_container_width=True):
                        success, message = delete_account(account["username"])
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                else:
                    st.write("**Current User**")
            
            st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Back to Dashboard
    with st.container():
        st.markdown("""
        <div class="message-container">
            <div class="message-content">
        """, unsafe_allow_html=True)
        
        if st.button("← Back to Dashboard", use_container_width=True):
            st.session_state.current_page = "Dashboard"
            st.rerun()
        
        st.markdown("</div></div>", unsafe_allow_html=True)

def show_add_utang():
    """Show add utang form with organized containers - ONLY SHOW OWNER'S CUSTOMERS"""
    st.markdown("##  Add Utang")
    
    # Get current owner's username
    owner_username = st.session_state.username
    
    # Get only customers created by this owner
    customers = get_my_customer_list(owner_username)
    
    if not customers:
        st.markdown("""
        <div class="message-container">
            <div class="message-content">
                <div class="empty-state">
                    <div class="empty-state-icon">👥</div>
                    <h4 class="empty-state-title">No Customer Accounts</h4>
                    <p>Create customer accounts first to add utang</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Back to Dashboard", use_container_width=True):
            st.session_state.current_page = "Dashboard"
            st.rerun()
        return
    
    # Initialize session state for this transaction
    if 'current_transaction' not in st.session_state:
        st.session_state.current_transaction = {
            'step': 1,
            'customer': '',
            'description': '',
            'amount': 1000.0,
            'due_date': None,
            'apply_interest': True,
            'interest_rate': 3.0,
            'total_amount': 0.0,
            'transaction_id': None
        }
    
    # Step 1: Create pending transaction in container
    if st.session_state.current_transaction['step'] == 1:
        with st.container():
            with st.form("add_utang_form_step1", clear_on_submit=False):
                customer = st.selectbox("Select Customer", customers, key="utang_customer")
                description = st.text_input("Description", placeholder="Item or reason for debt", key="utang_description")
                amount = st.number_input("Amount", min_value=1.0, value=1000.0, step=100.0, format="%.2f", key="utang_amount")
                
                # Custom Due Date Section
                st.markdown("### Due Date Settings")
                col1, col2 = st.columns(2)
                
                with col1:
                    today = datetime.now().date()
                    min_date = today + timedelta(days=1)
                    max_date = today + timedelta(days=365)
                    
                    due_date = st.date_input(
                        "Set Due Date *",
                        min_value=min_date,
                        max_value=max_date,
                        help="Select the date when this utang should be paid",
                        key="utang_due_date"
                    )
                    
                    if due_date:
                        st.info(f"**Selected Due Date:** {due_date.strftime('%B %d, %Y')}")
                    
                    if due_date and due_date <= today:
                        st.error("❌ Due date must be in the future")
                
                with col2:
                    if due_date:
                        days_until_due = (due_date - today).days
                        if days_until_due <= 7:
                            status_color = "var(--accent-red)"
                            status_text = "Urgent"
                            icon = "🔴"
                        elif days_until_due <= 30:
                            status_color = "var(--accent-amber)"
                            status_text = "Approaching"
                            icon = "🟠"
                        else:
                            status_color = "var(--accent-green)"
                            status_text = "Comfortable"
                            icon = "🟢"
                        
                        st.markdown(f"""
                        <div style="background: var(--bg-secondary); padding: 1rem; border-radius: 8px; border-left: 4px solid {status_color}; text-align: center;">
                            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{icon}</div>
                            <div style="font-size: 0.9rem; color: var(--text-primary); opacity: 0.9;">Days Until Due</div>
                            <div style="font-size: 1.5rem; font-weight: bold; color: {status_color}; margin: 0.5rem 0;">{days_until_due}</div>
                            <div style="font-size: 0.8rem; color: {status_color}; font-weight: 500;">{status_text}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Interest section
                st.markdown("###  Interest Settings")
                apply_interest = st.checkbox("Apply 3% Interest", value=True, key="apply_interest")
                interest_rate = 3.0 if apply_interest else 0.0
                
                if apply_interest:
                    if amount is not None:
                        interest_amount = calculate_interest(amount, interest_rate)
                        total_amount = amount + interest_amount
                        st.info(f"**Interest Amount:** {format_currency(interest_amount)}")
                        st.success(f"**Total with Interest:** {format_currency(total_amount)}")
                else:
                    st.info("**No interest applied**")
                    total_amount = amount if amount is not None else 0.0
                
                submitted = st.form_submit_button("📤 Send OTP to Customer", use_container_width=True)
                
                if submitted:
                    if not due_date:
                        st.error("❌ Please select a due date")
                        return
                    
                    if due_date <= today:
                        st.error("❌ Due date must be in the future")
                        return
                    
                    # Comprehensive amount validation
                    if amount is None:
                        st.error("❌ Please enter a valid amount")
                        return
                    
                    amount_str = str(amount).strip() if amount is not None else ""
                    if not amount_str:
                        st.error("❌ Please enter a valid amount")
                        return
                    
                    is_valid, validated_amount = validate_amount(amount)
                    if not is_valid:
                        st.error(validated_amount)
                        return
                    
                    if not description:
                        st.error("Please enter a description")
                        return
                    
                    if not customer:
                        st.error("Please select a customer")
                        return
                    
                    # Check credit limit
                    balance = calculate_balance(customer)
                    new_balance = balance["outstanding"] + validated_amount
                    credit_limit = get_account(customer)["debtLimit"]
                    
                    if new_balance > credit_limit:
                        st.warning(f"⚠️ **Credit Limit Warning**: This will exceed customer's credit limit!")
                        proceed = st.checkbox("I understand and want to proceed anyway")
                        if not proceed:
                            return
                    
                    # Create pending transaction FIRST
                    transaction, message = create_pending_transaction_with_due_date(
                        customer, "utang", description, validated_amount, st.session_state.username, 
                        interest_rate, due_date.strftime('%Y-%m-%d')
                    )
                    
                    if transaction:
                        # IMPORTANT: Update session state with ALL transaction data
                        st.session_state.current_transaction = {
                            'step': 2,
                            'customer': customer,
                            'description': description,
                            'amount': validated_amount,
                            'due_date': due_date.strftime('%Y-%m-%d'),
                            'apply_interest': apply_interest,
                            'interest_rate': interest_rate,
                            'total_amount': validated_amount + (calculate_interest(validated_amount, interest_rate) if apply_interest else 0),
                            'transaction_id': transaction["id"]
                        }
                        
                        debug_transaction_state()
                        
                        st.success("✅ OTP sent to customer! Please ask the customer for the OTP code.")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
            
            st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Step 2: Confirm with OTP
    elif st.session_state.current_transaction['step'] == 2:
        print("🔧 DEBUG: Entering OTP confirmation step")
        debug_transaction_state()
        
        with st.container():
            st.markdown("""
            <div class="message-container">
                <div class="message-header">
                    <span>🔐 OTP Confirmation</span>
                </div>
                <div class="message-content">
            """, unsafe_allow_html=True)
            
            # Check if transaction ID exists in session state
            transaction_id = st.session_state.current_transaction.get('transaction_id')
            if not transaction_id:
                st.error("❌ CRITICAL: Transaction ID is missing from session state!")
                st.info("This usually happens when the page refreshes. Please go back and create the transaction again.")
                
                if st.button("← Go Back to Create New Utang", use_container_width=True):
                    st.session_state.current_transaction = {'step': 1}
                    st.rerun()
                return
            
            # Verify transaction exists in database
            if not verify_transaction_exists(transaction_id):
                st.error("❌ Transaction not found in database! It may have been deleted or expired.")
                if st.button("← Go Back to Create New Utang", use_container_width=True):
                    st.session_state.current_transaction = {'step': 1}
                    st.rerun()
                return
            
            st.success("📱 OTP has been sent to the customer. Please ask them for the OTP code.")
            
            customer_info = get_account(st.session_state.current_transaction['customer'])
            customer_name = customer_info.get("personalInfo", {}).get("full_name", st.session_state.current_transaction['customer'])
            
            st.markdown("#### Transaction Details to Confirm")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Customer", customer_name)
                st.metric("Description", st.session_state.current_transaction['description'])
            
            with col2:
                st.metric("Amount", format_currency(st.session_state.current_transaction['total_amount']))
                st.metric("Due Date", st.session_state.current_transaction['due_date'])
            
            with col3:
                due_date = datetime.strptime(st.session_state.current_transaction['due_date'], '%Y-%m-%d').date()
                today = datetime.now().date()
                days_until_due = (due_date - today).days
                
                if days_until_due <= 7:
                    status_color = "var(--accent-red)"
                    status_icon = "🔴"
                elif days_until_due <= 30:
                    status_color = "var(--accent-amber)"
                    status_icon = "🟠"
                else:
                    status_color = "var(--accent-green)"
                    status_icon = "🟢"
                
                st.metric("Days Until Due", days_until_due)
                st.markdown(f"""
                <div style="background: {status_color}; color: white; padding: 0.5rem; border-radius: 6px; text-align: center; font-weight: bold;">
                    {status_icon} {days_until_due} days remaining
                </div>
                """, unsafe_allow_html=True)
            
            # OTP Section
            st.markdown("#### OTP Verification")
            st.info("🔒 Ask the customer to provide the 6-digit OTP they received")
            
            otp = st.text_input(
                "Enter OTP from Customer", 
                placeholder="Enter 6-digit OTP code",
                max_chars=6,
                key="otp_input_confirmation"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                confirm_btn = st.button(
                    "✅ Confirm Utang with OTP", 
                    use_container_width=True, 
                    key="confirm_otp_btn_final",
                    type="primary"
                )
            with col2:
                cancel_btn = st.button(
                    "❌ Cancel Transaction", 
                    use_container_width=True, 
                    key="cancel_otp_btn_final"
                )
            
            # OTP CONFIRMATION LOGIC
            if confirm_btn:
                if not otp:
                    st.error("❌ Please enter the OTP")
                    return
                
                if len(otp) != 6:
                    st.error("❌ OTP must be exactly 6 digits")
                    return
                
                print(f"🔧 Attempting to confirm transaction: {transaction_id}")
                
                success, message = confirm_transaction_with_otp(transaction_id, otp)

                if success:
                    st.success (f"✅ {message}")
                    # Reset transaction state
                    st.session_state.current_transaction = {'step': 1}
                    
                    # Add small delay and rerun
                    import time
                    time.sleep(2)
                    st.rerun()
                    
                else:
                    st.error(f"❌ {message}")
            
            # CANCEL LOGIC
            if cancel_btn:
                # Optional: Delete the pending transaction from database
                transaction_id = st.session_state.current_transaction.get('transaction_id')
                if transaction_id:
                    delete_transaction(transaction_id)
                
                # Reset transaction state
                st.session_state.current_transaction = {'step': 1}
                st.info("ℹ️ Transaction cancelled")
                st.rerun()
            
            st.markdown("</div></div>", unsafe_allow_html=True)

    # Due Date Management Section - ONLY FOR OWNER'S CUSTOMERS
    with st.container():
        st.markdown("""
        <div class="message-container">
            <div class="message-header">
                <span> Due Date Management (My Customers)</span>
            </div>
            <div class="message-content">
        """, unsafe_allow_html=True)
        
        upcoming_due_dates = get_my_upcoming_due_dates(owner_username)
        overdue_transactions = get_my_overdue_transactions(owner_username)
        
        # Overdue Section
        if overdue_transactions:
            st.error(f"🚨 **{len(overdue_transactions)} OVERDUE UTANG(S) FROM MY CUSTOMERS**")
            for overdue in overdue_transactions[:3]:
                st.markdown(f"""
                <div class="due-date-alert due-date-critical">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="flex: 1;">
                            <div style="font-weight: bold; color: var(--text-primary); font-size: 1.1rem;">{overdue['customer']}</div>
                            <div style="font-size: 0.9rem; color: var(--text-primary); opacity: 0.9; margin-bottom: 0.25rem;">
                                {overdue['description']}
                            </div>
                            <div style="font-size: 0.8rem; color: var(--text-secondary);">
                                💰 Amount: {format_currency(overdue['amount'])} • 📅 Due: {overdue['due_date']}
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 1rem; color: var(--accent-red); font-weight: bold; margin-bottom: 0.25rem;">
                                ⚠️ OVERDUE: {overdue['days_overdue']} days
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Upcoming Due Dates Section
        if upcoming_due_dates:
            urgent_due = [d for d in upcoming_due_dates if d['days_until_due'] <= 7]
            approaching_due = [d for d in upcoming_due_dates if 7 < d['days_until_due'] <= 30]
            comfortable_due = [d for d in upcoming_due_dates if d['days_until_due'] > 30]
            
            if urgent_due:
                st.warning(f"🔴 **{len(urgent_due)} URGENT** - Due within 7 days (My Customers)")
                for due_info in urgent_due[:3]:
                    display_due_date_item(due_info, "urgent")
            
            if approaching_due:
                st.info(f"🟠 **{len(approaching_due)} APPROACHING** - Due in 8-30 days (My Customers)")
                for due_info in approaching_due[:2]:
                    display_due_date_item(due_info, "approaching")
            
            if comfortable_due:
                st.success(f"🟢 **{len(comfortable_due)} COMFORTABLE** - Due in 31+ days (My Customers)")
                for due_info in comfortable_due[:2]:
                    display_due_date_item(due_info, "comfortable")
        
        # Manual due date check button
        col1, col2 = st.columns([2, 1])
        with col1:
            if st.button("🔄 Check Due Dates & Send Reminders", use_container_width=True, key="check_due_dates_utang"):
                success, message = check_due_dates()
                if success:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")
                st.rerun()
        with col2:
            if st.button("📈 View All Due Dates", use_container_width=True, key="view_all_due_dates"):
                st.session_state.current_page = "Reports"
                st.rerun()

        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Back to Dashboard button
    with st.container():
        st.markdown("""
        <div class="message-container">
            <div class="message-content">
        """, unsafe_allow_html=True)
        
        if st.button("← Back to Dashboard", use_container_width=True, key="back_to_dashboard_utang"):
            # Reset transaction state
            if 'current_transaction' in st.session_state:
                st.session_state.current_transaction = {'step': 1}
            st.session_state.current_page = "Dashboard"
            st.rerun()
        
        st.markdown("</div></div>", unsafe_allow_html=True)

def display_due_date_item(due_info, urgency_level):
    """Display a due date item with appropriate styling - ONLY FOR UNPAID UTANG"""
    if urgency_level == "urgent":
        border_color = "var(--accent-red)"
        bg_color = "rgba(239, 68, 68, 0.1)"
        icon = "🔴"
    elif urgency_level == "approaching":
        border_color = "var(--accent-amber)"
        bg_color = "rgba(245, 158, 11, 0.1)"
        icon = "🟠"
    else:
        border_color = "var(--accent-green)"
        bg_color = "rgba(16, 185, 129, 0.1)"
        icon = "🟢"
    
    # Check if this utang is still outstanding
    customer_balance = calculate_balance(due_info['customer'])
    has_outstanding_balance = customer_balance["outstanding"] > 0
    
    if not has_outstanding_balance:
        # This utang has been paid - don't display it
        return
    
    st.markdown(f"""
    <div class="due-date-alert" style="border-left-color: {border_color}; background: {bg_color};">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="flex: 1;">
                <div style="font-weight: bold; color: var(--text-primary);">{icon} {due_info['customer']}</div>
                <div style="font-size: 0.9rem; color: var(--text-primary); opacity: 0.9; margin-bottom: 0.25rem;">
                    {due_info['description']}
                </div>
                <div style="font-size: 0.8rem; color: var(--text-secondary);">
                    💰 Amount: {format_currency(due_info['amount'])} • 📅 Due: {due_info['due_date']}
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 1rem; color: {border_color}; font-weight: bold; margin-bottom: 0.25rem;">
                    {due_info['days_until_due']} days
                </div>
                <div style="font-size: 0.7rem; color: var(--text-secondary);">
                    Balance: {format_currency(customer_balance['outstanding'])}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_owner_transaction_item(transaction, show_interest_details=True, show_delete=False):
    """Display a single transaction item for owner with consistent layout in one container"""
    # Determine colors based on transaction type
    if transaction["type"] == "payment":
        border_color = "var(--accent-green)"
        amount_color = "var(--accent-green)"
        amount_prefix = "-"
        type_icon = "💰"
        type_label = "Payment"
        type_bg = "rgba(16, 185, 129, 0.1)"
    else:  # utang
        border_color = "var(--accent-red)"
        amount_color = "var(--accent-red)"
        amount_prefix = "+"
        type_icon = "📝"
        type_label = "Utang"
        type_bg = "rgba(239, 68, 68, 0.1)"
    
    # Status styling
    if transaction["confirmed"]:
        status_text = "CONFIRMED"
        status_color = "var(--accent-green)"
        status_bg = "rgba(16, 185, 129, 0.1)"
    else:
        status_text = "PENDING"
        status_color = "var(--accent-amber)"
        status_bg = "rgba(245, 158, 11, 0.1)"
    
    # Check if this utang is still outstanding
    customer_balance = calculate_balance(transaction['customer'])
    has_outstanding_balance = customer_balance["outstanding"] > 0
    
    # Create the main transaction container
    st.markdown(f"""
    <div class="message-item" style="border-left-color: {border_color};">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem;">
            <!-- Left Section: Transaction Details -->
            <div style="flex: 1;">
                <!-- Header Row -->
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                        <div style="font-size: 1.8rem; background: {type_bg}; padding: 0.5rem; border-radius: 8px;">{type_icon}</div>
                        <div>
                            <div style="font-weight: 600; color: var(--text-primary); font-size: 1.2rem; margin-bottom: 0.25rem;">
                                {transaction['customer']} - {transaction['description']}
                            </div>
                            <div style="display: flex; align-items: center; gap: 1rem; font-size: 0.85rem; color: var(--text-secondary);">
                                <span>📅 {transaction['date']}</span>
                                <span style="background: {type_bg}; color: {border_color}; padding: 0.2rem 0.6rem; border-radius: 12px; font-weight: 500;">{type_label}</span>
                                <span style="background: {status_bg}; color: {status_color}; padding: 0.2rem 0.6rem; border-radius: 12px; font-weight: 500;">{status_text}</span>
                                <span style="background: rgba(59, 130, 246, 0.1); color: var(--accent-blue); padding: 0.2rem 0.6rem; border-radius: 12px; font-weight: 500;">
                                    👤 {transaction.get('created_by', 'System')}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Details Row -->
                <div style="display: flex; flex-wrap: wrap; gap: 1rem; margin-top: 0.75rem;">
    """, unsafe_allow_html=True)
    
    # Interest information if applicable
    if show_interest_details and transaction.get("interest_rate", 0) > 0 and transaction["type"] == "utang":
        st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 0.5rem; background: rgba(245, 158, 11, 0.1); padding: 0.5rem 0.75rem; border-radius: 6px;">
                        <div style="font-size: 1rem;">⚡</div>
                        <div>
                            <div style="font-size: 0.75rem; color: var(--text-secondary);">Interest Rate</div>
                            <div style="font-size: 0.9rem; color: var(--accent-amber); font-weight: 500;">{transaction['interest_rate']}%</div>
                        </div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.5rem; background: rgba(245, 158, 11, 0.1); padding: 0.5rem 0.75rem; border-radius: 6px;">
                        <div style="font-size: 1rem;">💰</div>
                        <div>
                            <div style="font-size: 0.75rem; color: var(--text-secondary);">Interest Amount</div>
                            <div style="font-size: 0.9rem; color: var(--accent-amber); font-weight: 500;">{format_currency(transaction.get('interest_amount', 0))}</div>
                        </div>
                    </div>
        """, unsafe_allow_html=True)
    
    # Principal amount for utang with interest
    if transaction["type"] == "utang" and transaction.get("interest_rate", 0) > 0:
        st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 0.5rem; background: rgba(59, 130, 246, 0.1); padding: 0.5rem 0.75rem; border-radius: 6px;">
                        <div style="font-size: 1rem;">📊</div>
                        <div>
                            <div style="font-size: 0.75rem; color: var(--text-secondary);">Principal</div>
                            <div style="font-size: 0.9rem; color: var(--accent-blue); font-weight: 500;">{format_currency(transaction.get('principal_amount', transaction['amount']))}</div>
                        </div>
                    </div>
        """, unsafe_allow_html=True)
    
    # Due date information - ONLY SHOW FOR UNPAID UTANG
    if (transaction.get("due_date") and 
        transaction["type"] == "utang" and 
        transaction["confirmed"]):
        
        if has_outstanding_balance:
            due_date = datetime.strptime(transaction["due_date"], '%Y-%m-%d').date()
            today = datetime.now().date()
            days_until_due = (due_date - today).days
            
            if days_until_due < 0:
                due_status = f"OVERDUE: {abs(days_until_due)} days"
                due_color = "var(--accent-red)"
                due_icon = "⚠️"
                due_bg = "rgba(239, 68, 68, 0.1)"
            elif days_until_due == 0:
                due_status = "DUE TODAY"
                due_color = "var(--accent-red)"
                due_icon = "⏰"
                due_bg = "rgba(239, 68, 68, 0.1)"
            elif days_until_due <= 7:
                due_status = f"Due in {days_until_due} days"
                due_color = "var(--accent-amber)"
                due_icon = "📅"
                due_bg = "rgba(245, 158, 11, 0.1)"
            else:
                due_status = f"Due in {days_until_due} days"
                due_color = "var(--accent-blue)"
                due_icon = "📝"
                due_bg = "rgba(59, 130, 246, 0.1)"
            
            st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 0.5rem; background: {due_bg}; padding: 0.5rem 0.75rem; border-radius: 6px;">
                        <div style="font-size: 1rem;">{due_icon}</div>
                        <div>
                            <div style="font-size: 0.75rem; color: var(--text-secondary);">Due Date</div>
                            <div style="font-size: 0.9rem; color: {due_color}; font-weight: 500;">{transaction['due_date']}</div>
                            <div style="font-size: 0.7rem; color: {due_color};">{due_status}</div>
                        </div>
                    </div>
            """, unsafe_allow_html=True)
        else:
            # Utang is paid - show paid status
            st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 0.5rem; background: rgba(16, 185, 129, 0.1); padding: 0.5rem 0.75rem; border-radius: 6px;">
                        <div style="font-size: 1rem;">✅</div>
                        <div>
                            <div style="font-size: 0.75rem; color: var(--text-secondary);">Status</div>
                            <div style="font-size: 0.9rem; color: var(--accent-green); font-weight: 500;">PAID - Due date cleared</div>
                        </div>
                    </div>
            """, unsafe_allow_html=True)
    
    # Status if not confirmed
    if not transaction["confirmed"]:
        st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 0.5rem; background: rgba(245, 158, 11, 0.1); padding: 0.5rem 0.75rem; border-radius: 6px;">
                        <div style="font-size: 1rem;">⏳</div>
                        <div>
                            <div style="font-size: 0.75rem; color: var(--text-secondary);">Status</div>
                            <div style="font-size: 0.9rem; color: var(--accent-amber); font-weight: 500;">Waiting for OTP Confirmation</div>
                        </div>
                    </div>
        """, unsafe_allow_html=True)
    
    # Current balance info for owner
    st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 0.5rem; background: rgba(148, 163, 184, 0.1); padding: 0.5rem 0.75rem; border-radius: 6px;">
                        <div style="font-size: 1rem;">📈</div>
                        <div>
                            <div style="font-size: 0.75rem; color: var(--text-secondary);">Current Balance</div>
                            <div style="font-size: 0.9rem; color: var(--text-primary); font-weight: 500;">{format_currency(customer_balance['outstanding'])}</div>
                        </div>
                    </div>
    """, unsafe_allow_html=True)
    
    # Close the details row and left section
    st.markdown("""
                </div>
            </div>
            
            <!-- Right Section: Amount and Actions -->
            <div style="text-align: right; min-width: 140px;">
                <div style="font-weight: bold; color: %s; font-size: 1.5rem; margin-bottom: 0.75rem;">
                    %s %s
                </div>
    """ % (amount_color, amount_prefix, format_currency(transaction['amount'])), unsafe_allow_html=True)
    
    # Delete button if enabled
    if show_delete:
        st.markdown("""
                <div style="margin-top: 0.5rem;">
        """, unsafe_allow_html=True)
        
        if st.button("🗑️ Delete", key=f"del_trans_{transaction['id']}", help="Delete transaction", use_container_width=True):
            if delete_transaction(transaction['id']):
                st.success("Transaction deleted successfully!")
                st.rerun()
            else:
                st.error("Failed to delete transaction")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Close the container
    st.markdown("""
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_record_payment():
    """Show record payment form with OTP workflow - ONLY SHOW OWNER'S CUSTOMERS"""
    st.markdown("## Record Payment")
    
    # Get current owner's username
    owner_username = st.session_state.username
    
    # Initialize payment_amount if not set
    if 'payment_amount' not in st.session_state:
        st.session_state.payment_amount = 1000.0
    
    # Get only customers created by this owner
    customers = get_my_customer_list(owner_username)
    
    if not customers:
        st.markdown("""
        <div class="message-container">
            <div class="message-content">
                <div class="empty-state">
                    <div class="empty-state-icon">👥</div>
                    <h4 class="empty-state-title">No Customer Accounts</h4>
                    <p>Create customer accounts first to record payments</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Back to Dashboard", use_container_width=True):
            st.session_state.current_page = "Dashboard"
            st.rerun()
        return
    
    # Step 1: Select payment type and amount
    if not st.session_state.get('payment_pending_otp'):
        with st.container():
            selected_customer = st.selectbox("Select Customer", customers, key="payment_customer")
            
            if selected_customer:
                customer_balance = calculate_balance(selected_customer)
                outstanding_balance = customer_balance["outstanding"]
                customer_account = get_account(selected_customer)
                customer_name = customer_account.get("personalInfo", {}).get("full_name", selected_customer)
                
                # Show total utang
                st.markdown(f"""
                <div style="background: var(--bg-secondary); padding: 1.5rem; border-radius: 12px; border: 2px solid var(--accent-red); margin: 1rem 0; text-align: center;">
                    <div style="font-size: 0.9rem; color: var(--text-primary); opacity: 0.9;">TOTAL UTANG</div>
                    <div style="font-size: 2rem; font-weight: bold; color: var(--accent-red); margin: 0.5rem 0;">{format_currency(outstanding_balance)}</div>
                    <div style="font-size: 0.8rem; color: var(--text-primary); opacity: 0.7;">{customer_name}</div>
                </div>
                """, unsafe_allow_html=True)
                
                if outstanding_balance <= 0:
                    st.success("This customer has no outstanding balance!")
                    if st.button("Back to Dashboard", use_container_width=True):
                        st.session_state.current_page = "Dashboard"
                        st.rerun()
                    return
                
                # Payment type selection
                st.markdown("#### Select Payment Type")    
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Full Payment", use_container_width=True, 
                               type="primary" if st.session_state.get('payment_type') == 'Full Payment' else "secondary",
                               key="full_payment_btn"):
                        st.session_state.payment_type = "Full Payment"
                        st.session_state.payment_amount = float(outstanding_balance)
                        st.session_state.payment_description = f"Full payment for {customer_name}'s outstanding balance"
                        st.session_state.partial_payment_confirmed = False
                        st.rerun()
                
                with col2:
                    if st.button("Partial Payment", use_container_width=True,
                               type="primary" if st.session_state.get('payment_type') == 'Partial Payment' else "secondary",
                               key="partial_payment_btn"):
                        st.session_state.payment_type = "Partial Payment"
                        st.session_state.partial_payment_confirmed = False
                        st.rerun()
                
                payment_type = st.session_state.get('payment_type')
                
                if payment_type == "Full Payment":
                    st.markdown("---")
                    st.markdown("#### Full Payment Details")
                    
                    st.success("**Full Payment Selected**")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Payment Amount", format_currency(outstanding_balance))
                        st.metric("Customer", customer_name)
                    
                    with col2:
                        st.metric("Previous Balance", format_currency(outstanding_balance))
                        st.metric("New Balance", "₱ 0.00")
                    
                    st.success("✅ This payment will fully settle the customer's balance!")
                    
                    # Send OTP button
                    if st.button("Send OTP to Customer", use_container_width=True, type="primary", key="send_otp_full"):
                        # Validate payment_amount before sending
                        if st.session_state.payment_amount is None:
                            st.error("Payment amount is invalid. Please try again.")
                            return
                            
                        try:
                            payment_amount_float = float(st.session_state.payment_amount)
                        except (ValueError, TypeError):
                            st.error("Invalid payment amount format.")
                            return
                            
                        transaction, message = create_pending_transaction_with_due_date(
                            selected_customer, "payment", 
                            st.session_state.payment_description, 
                            payment_amount_float,
                            st.session_state.username
                        )
                        
                        if transaction:
                            st.session_state.payment_pending_otp = True
                            st.session_state.pending_transaction_id = transaction["id"]
                            st.session_state.pending_customer = selected_customer
                            st.session_state.outstanding_balance = outstanding_balance
                            st.success("✅ OTP sent to customer! Please ask customer for the OTP.")
                            st.rerun()
                        else:
                            st.error(message)
                
                elif payment_type == "Partial Payment":
                    st.markdown("---")
                    st.markdown("#### Partial Payment Details")
                    st.info(f"**Enter the payment amount below.** Maximum: {format_currency(outstanding_balance)}")
                    
                    if not st.session_state.get('partial_payment_confirmed'):
                        # Use a form for the partial payment input
                        with st.form("partial_payment_form"):
                            default_amount = min(1000.0, float(outstanding_balance))
                            if default_amount < 1.0:
                                default_amount = 1.0
                            
                            # Ensure payment_amount is properly initialized
                            if 'payment_amount' not in st.session_state or st.session_state.payment_amount is None:
                                st.session_state.payment_amount = default_amount
                            
                            amount = st.number_input(
                                "Payment Amount *", 
                                min_value=1.0, 
                                max_value=float(outstanding_balance),
                                value=float(st.session_state.payment_amount),
                                step=100.0, 
                                format="%.2f",
                                key="partial_payment_amount"
                            )
                            
                            description = st.text_input(
                                "Payment Description *", 
                                value=st.session_state.get('payment_description', f"Partial payment from {customer_name}"),
                                key="partial_payment_description"
                            )
                            
                            if amount > 0:
                                remaining_balance = outstanding_balance - amount
                                payment_percentage = (amount / outstanding_balance) * 100
                                
                                st.markdown("#### Payment Summary")
                                
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.metric("Payment Amount", format_currency(amount))
                                
                                with col2:
                                    st.metric("Remaining Balance", format_currency(remaining_balance))
                                
                                with col3:
                                    st.metric("Payment %", f"{payment_percentage:.1f}%")
                            
                            submitted = st.form_submit_button("Add Payment", use_container_width=True)
                            
                            if submitted:
                                if amount is None or amount <= 0:
                                    st.error("Please enter a valid payment amount")
                                    return
                                
                                if amount > outstanding_balance:
                                    st.error("Payment amount cannot exceed outstanding balance")
                                    return
                                
                                # SAFELY store the amount as float with validation
                                try:
                                    validated_amount = float(amount)
                                    if validated_amount <= 0:
                                        st.error("Amount must be greater than 0")
                                        return
                                    st.session_state.payment_amount = validated_amount
                                except (ValueError, TypeError) as e:
                                    st.error(f"Invalid amount format: {e}")
                                    return
                                
                                if not description.strip():
                                    st.error("Please enter a payment description")
                                    return
                                    
                                st.session_state.payment_description = description
                                st.session_state.partial_payment_confirmed = True
                                st.rerun()
                    
                    else:
                        st.markdown("#### Partial Payment Ready")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Payment Amount", format_currency(st.session_state.payment_amount))
                            st.metric("Customer", customer_name)
                        
                        with col2:
                            remaining = outstanding_balance - st.session_state.payment_amount
                            st.metric("Previous Balance", format_currency(outstanding_balance))
                            st.metric("New Balance", format_currency(remaining))
                        
                        # OTP send buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Send OTP to Customer", use_container_width=True, type="primary", key="send_otp_partial"):
                                # COMPREHENSIVE validation before sending OTP
                                if st.session_state.payment_amount is None:
                                    st.error("Payment amount is None. Please enter a valid amount.")
                                    st.session_state.partial_payment_confirmed = False
                                    st.rerun()
                                    return
                                    
                                try:
                                    payment_amount_float = float(st.session_state.payment_amount)
                                    if payment_amount_float <= 0:
                                        st.error("Payment amount must be greater than 0.")
                                        st.session_state.partial_payment_confirmed = False
                                        st.rerun()
                                        return
                                        
                                    if payment_amount_float > outstanding_balance:
                                        st.error("Payment amount cannot exceed outstanding balance.")
                                        st.session_state.partial_payment_confirmed = False
                                        st.rerun()
                                        return
                                except (ValueError, TypeError) as e:
                                    st.error(f"Invalid payment amount: {e}")
                                    st.session_state.partial_payment_confirmed = False
                                    st.rerun()
                                    return
                                    
                                transaction, message = create_pending_transaction_with_due_date(
                                    selected_customer, "payment", 
                                    st.session_state.payment_description, 
                                    payment_amount_float,
                                    st.session_state.username
                                )
                                
                                if transaction:
                                    st.session_state.payment_pending_otp = True
                                    st.session_state.pending_transaction_id = transaction["id"]
                                    st.session_state.pending_customer = selected_customer
                                    st.session_state.outstanding_balance = outstanding_balance
                                    st.session_state.partial_payment_confirmed = False
                                    st.success("✅ OTP sent to customer! Please ask customer for the OTP.")
                                    st.rerun()
                                else:
                                    st.error(message)
                        
                        with col2:
                            if st.button("Edit Payment Amount", use_container_width=True, key="edit_partial_amount"):
                                st.session_state.partial_payment_confirmed = False
                                st.rerun()
            
            st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Step 2: Confirm payment with OTP
    else:
        with st.container():
            st.markdown("""
            <div class="message-container">
                <div class="message-header">
                    <span>🔐 Payment Confirmation</span>
                </div>
                <div class="message-content">
            """, unsafe_allow_html=True)
            
            st.success("📱 OTP has been sent to the customer. Please ask them for the OTP code.")
            
            customer_name = get_account(st.session_state.pending_customer).get("personalInfo", {}).get("full_name", st.session_state.pending_customer)
            
            # Display payment details
            st.markdown("#### Payment Details to Confirm")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Customer", customer_name)
                st.metric("Payment Amount", format_currency(st.session_state.payment_amount))
            
            with col2:
                remaining = st.session_state.outstanding_balance - st.session_state.payment_amount
                st.metric("Previous Balance", format_currency(st.session_state.outstanding_balance))
                st.metric("New Balance", format_currency(remaining))
            
            st.markdown("---")
            
            # OTP Section
            st.markdown("#### OTP Verification")
            st.info("🔒 Ask the customer to provide the 6-digit OTP they received")
            
            otp = st.text_input(
                "Enter OTP from Customer", 
                placeholder="Enter 6-digit OTP code", 
                max_chars=6, 
                key="payment_otp_input"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                confirm_btn = st.button(
                    "✅ Confirm Payment with OTP", 
                    use_container_width=True, 
                    key="confirm_payment_btn",
                    type="primary"
                )
            with col2:
                cancel_btn = st.button(
                    "❌ Cancel Payment", 
                    use_container_width=True, 
                    key="cancel_payment_btn"
                )
            
            # PAYMENT OTP CONFIRMATION LOGIC
            if confirm_btn:
                if not otp:
                    st.error("❌ Please enter the OTP")
                    st.stop()
                
                if len(otp) != 6:
                    st.error("❌ OTP must be exactly 6 digits")
                    st.stop()
                
                success, message = confirm_transaction_with_otp(st.session_state.pending_transaction_id, otp)
                if success:
                    st.success(f"✅ Payment of {format_currency(st.session_state.payment_amount)} confirmed successfully!")
                    
                    new_balance = calculate_balance(st.session_state.pending_customer)
                    remaining_balance = new_balance["outstanding"]
                    
                    if remaining_balance > 0:
                        st.info(f"Remaining balance: {format_currency(remaining_balance)}")
                    else:
                        st.success(f"🎉 Excellent! {customer_name} has fully paid their balance!")
                    
                    # Clear all session state
                    payment_state_keys = [
                        'payment_pending_otp', 'pending_transaction_id', 'pending_customer',
                        'payment_amount', 'outstanding_balance', 'payment_type', 
                        'payment_description', 'partial_payment_confirmed'
                    ]
                    for key in payment_state_keys:
                        if key in st.session_state:
                            del st.session_state[key]
                    
                    st.rerun()
                    
                else:
                    st.error(f"❌ {message}")
            
            # PAYMENT CANCEL LOGIC
            if cancel_btn:
                payment_state_keys = [
                    'payment_pending_otp', 'pending_transaction_id', 'pending_customer',
                    'payment_amount', 'outstanding_balance', 'payment_type', 
                    'payment_description', 'partial_payment_confirmed'
                ]
                for key in payment_state_keys:
                    if key in st.session_state:
                        del st.session_state[key]
                st.info("ℹ️ Payment transaction cancelled.")
                st.rerun()
            
            st.markdown("</div></div>", unsafe_allow_html=True)

    # Transaction History Section - ONLY FOR SELECTED CUSTOMER
    selected_customer = st.session_state.get('pending_customer') or (customers[0] if customers else None)
    
    if selected_customer:
        with st.container():
            st.markdown("""
            <div class="message-container">
                <div class="message-header">
                    <span>📊 Recent Payment History</span>
                </div>
                <div class="message-content">
            """, unsafe_allow_html=True)
            
            try:
                transactions = get_customer_transactions(selected_customer)
                
                if not transactions:
                    st.info("No transaction history found for this customer.")
                else:
                    # Filter only payment transactions that are confirmed
                    payment_transactions = [tx for tx in transactions if tx["type"] == "payment" and tx.get("confirmed")]
                    
                    if not payment_transactions:
                        st.info("No payment history found for this customer.")
                    else:
                        # Sort by date (newest first) and get last 5
                        payment_transactions.sort(key=lambda x: x.get("date", ""), reverse=True)
                        recent_payments = payment_transactions[:5]
                        
                        for transaction in recent_payments:
                            date_str = transaction.get("date", "Unknown date")
                            description = transaction.get("description", "No description")
                            amount = transaction.get("amount", 0)
                            
                            st.markdown(f"""
                            <div class="message-item" style="border-left-color: var(--accent-green);">
                                <div style="display: flex; justify-content: space-between; align-items: start;">
                                    <div style="flex: 1;">
                                        <div style="font-weight: bold; color: var(--text-primary);">{description}</div>
                                        <div style="font-size: 0.8rem; color: var(--text-primary); opacity: 0.7; margin-top: 0.25rem;">
                                             {date_str}
                                        </div>
                                    </div>
                                    <div style="text-align: right;">
                                        <div style="font-weight: bold; color: var(--accent-green); font-size: 1.1rem;">
                                            - {format_currency(amount)}
                                        </div>
                                        <div style="font-size: 0.7rem; color: var(--text-primary); opacity: 0.7;">
                                            Recorded by: {transaction.get('created_by', 'System')}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error loading payment history: {str(e)}")
            
            st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Back to Dashboard button
    with st.container():
        st.markdown("""
        <div class="message-container">
            <div class="message-content">
        """, unsafe_allow_html=True)
        
        if st.button("← Back to Dashboard", use_container_width=True, key="back_to_dashboard_payment"):
            # Clean up all session state
            payment_state_keys = [
                'payment_pending_otp', 'pending_transaction_id', 'pending_customer',
                'payment_amount', 'outstanding_balance', 'payment_type', 
                'payment_description', 'partial_payment_confirmed'
            ]
            for key in payment_state_keys:
                if key in st.session_state:
                    del st.session_state[key]
            
            st.session_state.current_page = "Dashboard"
            st.rerun()
        
        st.markdown("</div></div>", unsafe_allow_html=True)

def show_pending_confirmations():
    """Show pending transactions in organized message containers - matching customer dashboard style"""
    st.markdown("## Pending Confirmations (My Customers)")
    
    # Get current owner's username
    owner_username = st.session_state.username
    
    # Get pending transactions for owner's customers
    pending_transactions = []
    all_pending = get_pending_transactions()
    
    # Filter to only show pending transactions for owner's customers
    my_customers = get_my_customer_list(owner_username)
    for transaction in all_pending:
        if transaction['customer'] in my_customers:
            pending_transactions.append(transaction)
    
    if not pending_transactions:
        st.markdown("""
        <div class="message-container">
            <div class="message-content">
                <div class="empty-state">
                    <h4 class="empty-state-title">No Pending Transactions</h4>
                    <p>All transactions with my customers have been confirmed</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Back to Dashboard", use_container_width=True, key="back_from_empty_pending"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
        return
    
    # Main Pending Transactions Container
    with st.container():
        st.markdown("""
        <div class="message-container">
            <div class="message-header">
                <span>📋 Pending Transactions (My Customers)</span>
                <div class="alert-badge">{count} Pending</div>
            </div>
            <div class="message-content">
        """.format(count=len(pending_transactions)), unsafe_allow_html=True)
        
        st.info("The following transactions with my customers are waiting for OTP confirmation.")
        
        for transaction in pending_transactions:
            # Use the exact same display function as customer dashboard
            display_pending_transaction_item(transaction, show_delete=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Instructions Container
    with st.container():
        st.markdown("""
        <div class="message-container">
            <div class="message-header">
                <span>📋 Confirmation Instructions</span>
            </div>
            <div class="message-content">
        """, unsafe_allow_html=True)
        
        st.markdown("""
        ### How to Confirm Transactions
        
        1. **Inform the customer** about the pending transaction
        2. **Ask the customer for the OTP** they received
        3. **Enter the 6-digit OTP** in the transaction details
        4. **Click Confirm** to complete the transaction
        5. **Transaction will be recorded** in the customer's history
        6. **Customer will receive a confirmation** alert
        """)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Back to dashboard button
    with st.container():
        st.markdown("""
        <div class="message-container">
            <div class="message-content">
        """, unsafe_allow_html=True)
        
        if st.button("← Back to Dashboard", use_container_width=True, key="back_from_pending"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
        
        st.markdown("</div></div>", unsafe_allow_html=True)

def display_pending_transaction_item(transaction, show_delete=False):
    """Display a single pending transaction item in customer dashboard style"""
    # Determine colors based on transaction type
    if transaction["type"] == "payment":
        border_color = "var(--accent-green)"
        amount_color = "var(--accent-green)"
        amount_prefix = "-"
        type_icon = "💰"
        type_label = "Payment"
    else:  # utang
        border_color = "var(--accent-red)"
        amount_color = "var(--accent-red)"
        amount_prefix = "+"
        type_icon = "📝"
        type_label = "Utang"
    
    # Status styling for pending transactions
    status_text = "PENDING"
    status_color = "var(--accent-amber)"

    # Create the container with columns - matching customer dashboard layout
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Left side - Transaction details
            st.markdown(f"""
            <div style="border-left: 4px solid {border_color}; background: var(--bg-secondary); padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border: 1px solid var(--border-color);">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <div style="font-size: 1.5rem;">{type_icon}</div>
                    <div>
                        <h4 style="margin: 0; color: var(--text-primary);">{transaction['description']}</h4>
                        <div style="display: flex; gap: 0.5rem; margin-top: 0.25rem;">
                            <span style="font-size: 0.8rem; color: var(--text-secondary);">📅 {transaction['date']}</span>
                            <span style="font-size: 0.8rem; background: {border_color}20; color: {border_color}; padding: 0.1rem 0.5rem; border-radius: 10px;">{type_label}</span>
                            <span style="font-size: 0.8rem; background: {status_color}20; color: {status_color}; padding: 0.1rem 0.5rem; border-radius: 10px;">{status_text}</span>
                            <span style="font-size: 0.8rem; color: var(--text-secondary);">👤 {transaction['customer']}</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Show interest details if applicable
            if transaction.get("interest_rate", 0) > 0 and transaction["type"] == "utang":
                col1a, col2a, col3a = st.columns(3)
                with col1a:
                    st.metric("Interest Rate", f"{transaction['interest_rate']}%")
                with col2a:
                    st.metric("Interest Amount", format_currency(transaction.get('interest_amount', 0)))
                with col3a:
                    st.metric("Principal", format_currency(transaction.get('principal_amount', transaction['amount'])))
            
            # Due date information for utang
            if (transaction.get("due_date") and 
                transaction["type"] == "utang"):
                
                due_date = datetime.strptime(transaction["due_date"], '%Y-%m-%d').date()
                today = datetime.now().date()
                days_until_due = (due_date - today).days
                
                if days_until_due < 0:
                    due_status = f"OVERDUE ({abs(days_until_due)} days)"
                    status_emoji = "⚠️"
                elif days_until_due == 0:
                    due_status = "DUE TODAY"
                    status_emoji = "⏰"
                elif days_until_due <= 7:
                    due_status = f"Due in {days_until_due} days"
                    status_emoji = "📅"
                else:
                    due_status = f"Due in {days_until_due} days"
                    status_emoji = "📝"
                
                st.write(f"{status_emoji} **Due Date:** {transaction['due_date']} - *{due_status}*")
            
        
        with col2:
            # Right side - Amount and actions inside the same styled container
            st.markdown(f"""
            <div style="border-left: 4px solid {border_color}; background: var(--bg-secondary); padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border: 1px solid var(--border-color); height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
                <div style="text-align: center;">
                    <div style="font-size: 1.3rem; font-weight: bold; color: {amount_color}; margin-bottom: 1rem;">
                        {amount_prefix}{format_currency(transaction['amount'])}
                    </div>
            """, unsafe_allow_html=True)
            
            # Action buttons
            col_action1, col_action2 = st.columns(2)
            
            with col_action1:
                # Confirm button
                if st.button("✅ Confirm", key=f"confirm_{transaction['id']}", use_container_width=True):
                    # Show OTP input for confirmation
                    st.session_state[f"confirming_{transaction['id']}"] = True
            
            with col_action2:
                # Delete button
                if show_delete:
                    if st.button("🗑️ Delete", key=f"del_trans_{transaction['id']}", use_container_width=True):
                        if delete_transaction(transaction['id']):
                            st.success("Transaction deleted successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to delete transaction")
            
            st.markdown("</div></div>", unsafe_allow_html=True)
    
    # OTP Confirmation Section (appears when Confirm button is clicked)
    if st.session_state.get(f"confirming_{transaction['id']}"):
        with st.container():
            st.markdown("""
            <div class="message-container">
                <div class="message-header">
                    <span>🔐 Confirm Transaction</span>
                </div>
                <div class="message-content">
            """, unsafe_allow_html=True)
            
            st.warning("⚠️ **Important**: Make sure you have received the OTP from the customer before confirming!")
            
            # OTP input
            otp_input = st.text_input(
                "Enter OTP from Customer",
                placeholder="Enter 6-digit OTP",
                max_chars=6,
                key=f"otp_confirm_{transaction['id']}"
            )
            
            col_confirm, col_cancel = st.columns(2)
            
            with col_confirm:
                if st.button("✅ Confirm with OTP", key=f"final_confirm_{transaction['id']}", use_container_width=True, type="primary"):
                    if not otp_input:
                        st.error("❌ Please enter the OTP")
                    elif len(otp_input) != 6:
                        st.error("❌ OTP must be exactly 6 digits")
                    else:
                        success, message = confirm_transaction_with_otp(transaction['id'], otp_input)
                        if success:
                            st.success("✅ Transaction confirmed successfully!")
                            # Clear the confirming state
                            if f"confirming_{transaction['id']}" in st.session_state:
                                del st.session_state[f"confirming_{transaction['id']}"]
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
            
            with col_cancel:
                if st.button("❌ Cancel", key=f"cancel_confirm_{transaction['id']}", use_container_width=True):
                    if f"confirming_{transaction['id']}" in st.session_state:
                        del st.session_state[f"confirming_{transaction['id']}"]
                    st.rerun()
            
            st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Separator between transactions
    st.markdown("---")

def show_reports():
    """Show reports with due date analytics - ONLY SHOW OWNER'S DATA"""
    st.markdown("## Reports & Analytics (My Customers)")
    
    # Get current owner's username
    owner_username = st.session_state.username
    
    # Due Date Analytics Section for owner's customers
    with st.container():
        st.markdown("""
        <div class="message-container">
            <div class="message-header">
                <span>📅 Due Date Analytics (My Customers)</span>
            </div>
            <div class="message-content">
        """, unsafe_allow_html=True)
        
        upcoming_due_dates = get_my_upcoming_due_dates(owner_username, 30)
        overdue_transactions = get_my_overdue_transactions(owner_username)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Overdue Utang", len(overdue_transactions))
        
        with col2:
            due_this_week = len([d for d in upcoming_due_dates if d['days_until_due'] <= 7])
            st.metric("Due This Week", due_this_week)
        
        with col3:
            due_next_week = len([d for d in upcoming_due_dates if 7 < d['days_until_due'] <= 14])
            st.metric("Due Next Week", due_next_week)
        
        with col4:
            total_upcoming = len(upcoming_due_dates)
            st.metric("Total Upcoming", total_upcoming)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Transaction summary for owner's customers
    with st.container():
        st.markdown("""
        <div class="message-container">
            <div class="message-header">
                <span>💰 Transaction Summary (My Customers)</span>
            </div>
            <div class="message-content">
        """, unsafe_allow_html=True)
        
        stats = get_my_transaction_statistics(owner_username)
        
        if stats:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Debt Issued", format_currency(stats['total_utang_amount']))
            
            with col2:
                st.metric("Total Payments", format_currency(stats['total_payment_amount']))
            
            with col3:
                st.metric("Total Interest", format_currency(stats['total_interest_amount']))
            
            with col4:
                st.metric("Net Balance", format_currency(stats['net_outstanding']))
            
            # Additional statistics
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div style="background: var(--bg-secondary); padding: 1rem; border-radius: 8px; border-left: 4px solid var(--accent-teal);">
                    <div style="font-weight: bold; color: var(--text-primary);">Transaction Statistics (My Customers)</div>
                    <div style="display: flex; justify-content: space-between; margin-top: 0.5rem;">
                        <span style="color: var(--text-secondary);">Total Transactions:</span>
                        <span style="color: var(--text-primary); font-weight: bold;">{stats['total_transactions']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-secondary);">Confirmed:</span>
                        <span style="color: var(--accent-green); font-weight: bold;">{stats['confirmed_transactions']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-secondary);">Pending:</span>
                        <span style="color: var(--accent-amber); font-weight: bold;">{stats['pending_transactions']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="background: var(--bg-secondary); padding: 1rem; border-radius: 8px; border-left: 4px solid var(--accent-blue);">
                    <div style="font-weight: bold; color: var(--text-primary);">Customer Statistics (My Customers)</div>
                    <div style="display: flex; justify-content: space-between; margin-top: 0.5rem;">
                        <span style="color: var(--text-secondary);">Total Customers:</span>
                        <span style="color: var(--text-primary); font-weight: bold;">{stats['active_customers']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-secondary);">With Outstanding Debt:</span>
                        <span style="color: var(--accent-red); font-weight: bold;">{stats['customers_with_debt']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📊</div>
                <h4 class="empty-state-title">No Transaction Data</h4>
                <p>No transactions have been recorded yet with your customers</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Top debtors - ONLY OWNER'S CUSTOMERS
    with st.container():
        st.markdown("""
        <div class="message-container">
            <div class="message-header">
                <span>Top Debtors (My Customers)</span>
            </div>
            <div class="message-content">
        """, unsafe_allow_html=True)
        
        top_debtors = get_my_top_debtors(owner_username, 10)
        
        if top_debtors:
            for i, (username, amount) in enumerate(top_debtors, 1):
                rank_color = "var(--accent-red)" if i == 1 else "var(--accent-amber)" if i == 2 else "var(--accent-green)" if i == 3 else "var(--accent-blue)"
                
                st.markdown(f"""
                <div class="debtor-item" style="border-left-color: {rank_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: flex; align-items: center; gap: 1rem;">
                            <div style="background: {rank_color}; color: white; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold;">{i}</div>
                            <div>
                                <div style="font-weight: bold; color: var(--text-primary); font-size: 1.1rem;">{username}</div>
                                <div style="font-size: 0.8rem; color: var(--text-primary); opacity: 0.7;">Outstanding Balance</div>
                            </div>
                        </div>
                        <div style="font-weight: bold; color: {rank_color}; font-size: 1.2rem;">{format_currency(amount)}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">💰</div>
                <h4 class="empty-state-title">No Outstanding Debts</h4>
                <p>All my customers have paid their balances</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Back button
    with st.container():
        st.markdown("""
        <div class="message-container">
            <div class="message-content">
        """, unsafe_allow_html=True)
        
        if st.button("← Back to Dashboard", use_container_width=True):
            st.session_state.current_page = "Dashboard"
            st.rerun()
        
        st.markdown("</div></div>", unsafe_allow_html=True)

def show_settings():
    """Show system settings"""
    st.markdown("## System Settings")
    
    # System settings
    with st.container():
        st.markdown("""
        <div class="message-container">
            <div class="message-header">
                <span>System Configuration</span>
            </div>
            <div class="message-content">
        """, unsafe_allow_html=True)
        
        with st.form("system_settings"):
            currency_symbol = st.text_input("Currency Symbol", value=get_setting("currencySymbol", "₱"))
            app_name = st.text_input("Application Name", value=get_setting("appName", "IUMS"))
            interest_rate = st.number_input("Default Interest Rate (%)", 
                                         min_value=0.0, 
                                         max_value=50.0, 
                                         value=float(get_setting("interestRate", 3.0)),
                                         step=0.5)
            customer_credit_limit = st.number_input("Default Customer Credit Limit", 
                                                  min_value=1000.0, 
                                                  value=float(get_setting("customerCreditLimit", 10000.0)),
                                                  step=1000.0)
            
            # Due Date Settings
            st.markdown("### Due Date Settings")
            reminder_days = st.text_input("Reminder Days", 
                                        value=get_setting("dueDateReminderDays", "7,3,1,0"),
                                        help="Comma-separated days before due date to send reminders")
            
            if st.form_submit_button("Save Settings", use_container_width=True):
                update_setting("currencySymbol", currency_symbol)
                update_setting("appName", app_name)
                update_setting("interestRate", interest_rate)
                update_setting("customerCreditLimit", customer_credit_limit)
                update_setting("dueDateReminderDays", reminder_days)
                st.success("Settings saved successfully!")
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Danger zone
    with st.container():
        st.markdown("""
        <div class="message-container">
            <div class="message-header">
                <span>⚠️ Data Management</span>
            </div>
            <div class="message-content">
        """, unsafe_allow_html=True)
        
        st.warning("This will delete all accounts and transactions. This action cannot be undone.")
        
        if st.button("Reset All Data", use_container_width=True):
            if st.checkbox("I understand this will delete ALL data"):
                if st.button("Confirm Reset", type="primary", use_container_width=True):
                    success, message = reset_all_data()
                    if success:
                        st.success(message)
                        st.rerun()
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Back to Dashboard
    with st.container():
        st.markdown("""
        <div class="message-container">
            <div class="message-content">
        """, unsafe_allow_html=True)
        
        if st.button("← Back to Dashboard", use_container_width=True):
            st.session_state.current_page = "Dashboard"
            st.rerun()
        
        st.markdown("</div></div>", unsafe_allow_html=True)

def show_owner_profile():
    """Show owner profile settings with organized message containers"""
    st.markdown("## 👤 Owner Profile Settings")
    
    username = st.session_state.username
    account = get_account(username)
    
    # Apply the same dark navy blue styles as customer profile
    st.markdown("""
    <style>
    .main-container {
        background: var(--bg-secondary);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .metric-box {
        background: var(--bg-secondary);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        text-align: center;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 0.9rem;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
        font-weight: 500;
        opacity: 0.9;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        margin: 0.5rem 0;
        color: var(--text-primary) !important;
    }
    
    .message-container {
        background: var(--bg-secondary);
        border-radius: 12px;
        border: 1px solid var(--border-color);
        margin: 1rem 0;
        overflow: hidden;
    }
    .message-header {
        background: var(--navy-dark);
        padding: 1rem 1.5rem;
        font-weight: 600;
        color: var(--text-primary);
        border-bottom: 1px solid var(--border-color);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .message-content {
        padding: 1.5rem;
    }
    
    .message-item {
        background: var(--bg-secondary);
        padding: 1.5rem;
        border-left: 4px solid;
        margin: 0.75rem 0;
        border-radius: 8px;
        transition: background-color 0.2s ease;
        border: 1px solid var(--border-color);
    }
    .message-item:hover {
        background: var(--navy-dark);
        transform: translateX(4px);
    }
    
    .alert-container {
        background: var(--bg-secondary);
        padding: 1.5rem;
        border-left: 4px solid;
        margin: 0.75rem 0;
        border-radius: 8px;
        transition: background-color 0.2s ease;
        border: 1px solid var(--border-color);
    }
    .alert-container:hover {
        background: var(--navy-dark);
    }
    
    .due-date-alert-customer {
        background: var(--bg-secondary);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 6px solid;
        margin: 1rem 0;
        border: 1px solid var(--border-color);
    }
    .due-date-critical-customer { border-left-color: var(--accent-red); background: rgba(239, 68, 68, 0.1); }
    .due-date-warning-customer { border-left-color: var(--accent-amber); background: rgba(245, 158, 11, 0.1); }
    .due-date-info-customer { border-left-color: var(--accent-blue); background: rgba(59, 130, 246, 0.1); }
    
    .empty-state {
        text-align: center;
        padding: 3rem 2rem;
        color: var(--text-secondary);
    }
    .empty-state-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }
    .empty-state-title {
        color: var(--text-primary);
        margin-bottom: 0.5rem;
        font-size: 1.2rem;
    }
    
    .profile-section {
        background: var(--bg-secondary);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        margin: 1rem 0;
    }
    
    .action-buttons {
        display: flex;
        gap: 0.5rem;
        margin-top: 1rem;
        flex-wrap: wrap;
    }
    
    .action-button {
        flex: 1;
        min-width: 120px;
    }
    
    .alert-badge {
        background: var(--accent-red);
        color: white;
        border-radius: 12px;
        padding: 0.25rem 0.75rem;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .status-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        margin-left: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Current Profile Information Container
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="profile-section">
                <h4 style="color: var(--text-primary); margin-bottom: 1rem;">Account Details</h4>
                <div style="margin-bottom: 0.5rem;">
                    <span style="color: var(--text-secondary);">Username:</span>
                    <span style="color: var(--text-primary); font-weight: bold; margin-left: 0.5rem;">{account['username']}</span>
                </div>
                <div style="margin-bottom: 0.5rem;">
                    <span style="color: var(--text-secondary);">Role:</span>
                    <span style="color: var(--text-primary); font-weight: bold; margin-left: 0.5rem;">{account['role']}</span>
                </div>
                <div style="margin-bottom: 0.5rem;">
                    <span style="color: var(--text-secondary);">Account Created:</span>
                    <span style="color: var(--text-primary); margin-left: 0.5rem;">{account.get('created_date', 'Unknown')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Get owner's personal information
            personal_info = account.get("personalInfo", {})
            full_name = personal_info.get('full_name', 'Not provided')
            address = personal_info.get('address', 'Not provided')
            email = personal_info.get('email', 'Not provided')
            
            st.markdown(f"""
            <div class="profile-section">
                <h4 style="color: var(--text-primary); margin-bottom: 1rem;">👤 Personal Information</h4>
                <div style="margin-bottom: 0.5rem;">
                    <span style="color: var(--text-secondary);">Full Name:</span>
                    <span style="color: var(--text-primary); font-weight: bold; margin-left: 0.5rem;">{full_name}</span>
                </div>
                <div style="margin-bottom: 0.5rem;">
                    <span style="color: var(--text-secondary);">Email Address:</span>
                    <span style="color: var(--text-primary); font-weight: bold; margin-left: 0.5rem;">{email}</span>
                </div>
                <div style="margin-bottom: 0.5rem;">
                    <span style="color: var(--text-secondary);">Address:</span>
                    <span style="color: var(--text-primary); margin-left: 0.5rem;">{address}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    

    # Change Password Container
    with st.container():
        st.markdown("""
        <div class="message-container">
            <div class="message-header">
                <span>🔒 Change Password</span>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("change_password_form"):
            current_password = st.text_input("Current Password", type="password", 
                                           placeholder="Enter your current password")
            new_password = st.text_input("New Password", type="password", 
                                       placeholder="Enter your new password")
            confirm_password = st.text_input("Confirm New Password", type="password", 
                                           placeholder="Confirm your new password")
            
            change_pass_btn = st.form_submit_button("Change Password", use_container_width=True)
            
            if change_pass_btn:
                if not current_password or not new_password or not confirm_password:
                    st.error("❌ Please fill in all password fields")
                elif new_password != confirm_password:
                    st.error("❌ New passwords do not match")
                elif len(new_password) < 4:
                    st.error("❌ Password must be at least 4 characters long")
                elif current_password != account["password"]:
                    st.error("❌ Current password is incorrect")
                else:
                    success, message = update_account_password(username, new_password)
                    if success:
                        st.success("✅ Password updated successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Change Username Container
    with st.container():
        st.markdown("""
        <div class="message-container">
            <div class="message-header">
                <span>👤 Change Username</span>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("change_username_form"):
            current_password_username = st.text_input("Current Password for Verification", type="password",
                                                    placeholder="Enter your current password to verify")
            new_username = st.text_input("New Username", value=username,
                                       placeholder="Enter your new username")
            
            change_user_btn = st.form_submit_button("Change Username", use_container_width=True)
            
            if change_user_btn:
                if not current_password_username or not new_username:
                    st.error("❌ Please fill in all fields")
                elif current_password_username != account["password"]:
                    st.error("❌ Current password is incorrect")
                elif new_username == username:
                    st.error("❌ New username is the same as current username")
                elif len(new_username) < 3:
                    st.error("❌ Username must be at least 3 characters long")
                else:
                    success, message = update_account_username(username, new_username)
                    if success:
                        st.success("✅ Username updated successfully!")
                        st.session_state.username = new_username
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Security Tips Container
    with st.container():
        st.markdown("""
        <div class="profile-section">
            <h4 style="color: var(--text-primary); margin-bottom: 1rem;">Security Tips</h4>
            <ul style="color: var(--text-primary); line-height: 1.6;">
                <li>Use a strong password with at least 8 characters</li>
                <li>Include numbers, letters, and special characters</li>
                <li>Don't use the same password for multiple accounts</li>
                <li>Never share your password with anyone</li>
                <li>Change your password regularly</li>
                <li>Log out after each session, especially on shared devices</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Quick Actions Container
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Refresh Profile", use_container_width=True, key="refresh_profile"):
                st.rerun()
        
        with col2:
            if st.button("⚙️ System Settings", use_container_width=True, key="system_settings"):
                st.session_state.current_page = "Settings"
                st.rerun()
        
        with col3:
            if st.button("📊 View Reports", use_container_width=True, key="view_reports_profile"):
                st.session_state.current_page = "Reports"
                st.rerun()
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Back to Dashboard Container
    with st.container():        
        if st.button("← Back to Dashboard", use_container_width=True):
            st.session_state.current_page = "Dashboard"
            st.rerun()
        
        st.markdown("</div></div>", unsafe_allow_html=True)