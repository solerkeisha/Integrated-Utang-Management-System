import streamlit as st
from utils import (
    calculate_balance, get_customer_transactions, get_pending_transactions,
    get_alerts, mark_alerts_read, format_currency, get_account,
    update_account_password, update_account_username, delete_transaction, delete_alert,
    get_upcoming_due_dates_for_customer, get_overdue_transactions_for_customer
)
from datetime import datetime

def show_customer_dashboard():
    """Show customer dashboard with organized message containers"""
    
    # Apply dark navy blue styles with improved message containers
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
    
    # Dashboard Overview
    if st.session_state.current_page == "Dashboard":
        show_customer_overview()
    elif st.session_state.current_page == "Balance":
        show_balance_page()
    elif st.session_state.current_page == "Transaction History":
        show_transaction_history()
    elif st.session_state.current_page == "Pending Transactions":
        show_pending_transactions()
    elif st.session_state.current_page == "Alerts":
        show_alerts_page()
    elif st.session_state.current_page == "Profile Settings":
        show_profile_settings()

def show_customer_overview():
    """Show customer overview with organized message containers"""
    st.markdown("## Customer Dashboard")
    
    username = st.session_state.username
    
    # Due Date Alerts Container
    with st.container():
        st.markdown("""
        <div class="message-container">
            <div class="message-header">
                <span>📅 Due Date Alerts</span>
            </div>
        """, unsafe_allow_html=True)
        
        upcoming_due_dates = get_upcoming_due_dates_for_customer(username, 7)
        overdue_transactions = get_overdue_transactions_for_customer(username)
        
        # Show overdue alerts
        if overdue_transactions:
            for overdue in overdue_transactions:
                st.markdown(f"""
                <div class="due-date-alert-customer due-date-critical-customer">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div style="flex: 1;">
                            <h4 style="margin: 0; color: var(--text-primary);">🚨 OVERDUE UTANG</h4>
                            <p style="margin: 0.5rem 0 0 0; color: var(--text-primary); opacity: 0.8;">
                                {overdue['description']} - {format_currency(overdue['amount'])}
                            </p>
                            <p style="margin: 0.5rem 0 0 0; color: var(--accent-red); font-weight: bold;">
                                Was due on {overdue['due_date']} ({overdue['days_overdue']} days ago)
                            </p>
                        </div>
                        <div style="font-size: 2rem;">⚠️</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Show upcoming due date alerts
        if upcoming_due_dates:
            for due_info in upcoming_due_dates:
                if due_info['days_until_due'] <= 3:
                    alert_class = "due-date-critical-customer"
                    icon = "⏰"
                    title = "URGENT: Due Soon"
                elif due_info['days_until_due'] <= 7:
                    alert_class = "due-date-warning-customer"
                    icon = "📅"
                    title = "Due Date Approaching"
                else:
                    alert_class = "due-date-info-customer"
                    icon = "📝"
                    title = "Upcoming Due Date"
                
                st.markdown(f"""
                <div class="due-date-alert-customer {alert_class}">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div style="flex: 1;">
                            <h4 style="margin: 0; color: var(--text-primary);">{icon} {title}</h4>
                            <p style="margin: 0.5rem 0 0 0; color: var(--text-primary); opacity: 0.8;">
                                {due_info['description']} - {format_currency(due_info['amount'])}
                            </p>
                            <p style="margin: 0.5rem 0 0 0; color: var(--text-primary);">
                                Due on {due_info['due_date']} ({due_info['days_until_due']} days from now)
                            </p>
                        </div>
                        <div style="font-size: 2rem;">{icon}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        if not overdue_transactions and not upcoming_due_dates:
            st.markdown("""
            <div class="empty-state">
                <h4 class="empty-state-title">No Due Date Alerts</h4>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Balance Summary Container
    with st.container():
        balance = calculate_balance(username)
        account = get_account(username)
        
        st.markdown("""
        <div class="message-container">
            <div class="message-header">
                <span>💰 Balance Summary</span>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Active Utang</div>
                <div class="metric-value" style="color: var(--accent-red) !important;">{format_currency(balance["outstanding"])}</div>
                <div style="font-size: 0.8rem; opacity: 0.8; color: var(--text-primary);">Total amount due</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Credit Limit</div>
                <div class="metric-value" style="color: var(--accent-blue) !important;">{format_currency(account["debtLimit"])}</div>
                <div style="font-size: 0.8rem; opacity: 0.8; color: var(--text-primary);">Maximum credit allowed</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Available Credit</div>
                <div class="metric-value" style="color: var(--accent-green) !important;">{format_currency(balance["available_credit"])}</div>
                <div style="font-size: 0.8rem; opacity: 0.8; color: var(--text-primary);">Remaining credit</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Interest</div>
                <div class="metric-value" style="color: var(--accent-amber) !important;">{format_currency(balance["total_interest_paid"])}</div>
                <div style="font-size: 0.8rem; opacity: 0.8; color: var(--text-primary);">Total interest</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Credit utilization - FIXED: Handle negative values
        st.markdown("### Credit Utilization")
        
        # Ensure utilization is between 0 and 100
        if account["debtLimit"] > 0:
            utilization = (balance["outstanding"] / account["debtLimit"]) * 100
            # Clamp utilization between 0 and 100
            utilization = max(0, min(100, utilization))
        else:
            utilization = 0
        
        col1, col2 = st.columns([3, 1])
        with col1:
            # Only show progress bar if utilization is valid
            if utilization >= 0:
                st.progress(utilization / 100, text=f"{utilization:.1f}% used")
            else:
                st.info("No credit utilization data available")
        
        with col2:
            if utilization > 90:
                status_style = "color: var(--accent-red); font-weight: bold;"
                status_text = "High Usage"
            elif utilization > 70:
                status_style = "color: var(--accent-amber); font-weight: bold;"
                status_text = "Moderate Usage"
            elif utilization > 0:
                status_style = "color: var(--accent-green); font-weight: bold;"
                status_text = "Good Standing"
            else:
                status_style = "color: var(--accent-blue); font-weight: bold;"
                status_text = "No Balance"
            
            st.markdown(f'<div style="{status_style}">{status_text}</div>', unsafe_allow_html=True)
        
        if utilization > 90:
            st.warning("Your credit utilization is very high. Please consider making a payment.")
        elif utilization > 70:
            st.info("Your credit utilization is moderate.")
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Recent Transactions Container
    with st.container():
        st.markdown("""
        <div class="message-container">
            <div class="message-header">
                <span>📊 Recent Transactions</span>
            </div>
        """, unsafe_allow_html=True)
        
        transactions = get_customer_transactions(username)[:5]
        
        if transactions:
            for transaction in transactions:
                if transaction["confirmed"]:
                    display_transaction_item(transaction, show_delete=True)
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📊</div>
                <h4 class="empty-state-title">No Transactions Yet</h4>
                <p>Your transaction history will appear here</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Recent Alerts Container
    with st.container():
        alerts = get_alerts(username)[:3]
        unread_count = sum(1 for alert in alerts if not alert["read"])
        
        st.markdown("""
        <div class="message-container">
            <div class="message-header">
                <span>🔔 Recent Alerts</span>
                <div class="alert-badge">{unread_count} Unread</div>
            </div>
        """.format(unread_count=unread_count), unsafe_allow_html=True)
        
        if alerts:
            for alert in alerts:
                display_alert_item(alert)
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">🔔</div>
                <h4 class="empty-state-title">No Alerts</h4>
                <p>You're all caught up!</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Quick Actions Container
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Refresh Dashboard", use_container_width=True, key="refresh_dash"):
                st.rerun()
        
        with col2:
            if st.button("👤 Profile Settings", use_container_width=True, key="profile_settings"):
                st.session_state.current_page = "Profile Settings"
                st.rerun()
        
        with col3:
            if st.button("📋 View All Transactions", use_container_width=True, key="view_transactions"):
                st.session_state.current_page = "Transaction History"
                st.rerun()
        
        st.markdown("</div></div>", unsafe_allow_html=True)

def display_transaction_item(transaction, show_interest_details=True, show_delete=False):
    """Display a single transaction item in a clean, separated layout"""
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
    
    # Status styling
    if transaction["confirmed"]:
        status_text = "CONFIRMED"
        status_color = "var(--accent-green)"
    else:
        status_text = "PENDING"
        status_color = "var(--accent-amber)"

    # Create the container with columns
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
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Show interest details if applicable
            if show_interest_details and transaction.get("interest_rate", 0) > 0 and transaction["type"] == "utang":
                col1a, col2a, col3a = st.columns(3)
                with col1a:
                    st.metric("Interest Rate", f"{transaction['interest_rate']}%")
                with col2a:
                    st.metric("Interest Amount", format_currency(transaction.get('interest_amount', 0)))
                with col3a:
                    st.metric("Principal", format_currency(transaction.get('principal_amount', transaction['amount'])))
            
            # Due date information
            if (transaction.get("due_date") and 
                transaction["type"] == "utang" and 
                transaction["confirmed"]):
                
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
            
            st.markdown("</div>", unsafe_allow_html=True)  # Close the container
        
        with col2:
            # Right side - Amount and delete button inside the same styled container
            st.markdown(f"""
            <div style="border-left: 4px solid {border_color}; background: var(--bg-secondary); padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border: 1px solid var(--border-color); height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
                <div style="text-align: center;">
                    <div style="font-size: 1.3rem; font-weight: bold; color: {amount_color}; margin-bottom: 1rem;">
                        {amount_prefix}{format_currency(transaction['amount'])}
                    </div>
            """, unsafe_allow_html=True)
            
            # Delete button - this will appear inside the right container
            if show_delete:
                if st.button("🗑️ Delete", key=f"del_trans_{transaction['id']}", use_container_width=True):
                    if delete_transaction(transaction['id']):
                        st.success("Transaction deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to delete transaction")
            
            st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Separator between transactions
    st.markdown("---")

def display_alert_item(alert):
    """Display a single alert item with delete button"""
    alert_border = "var(--accent-blue)" if alert["read"] else "var(--accent-red)"
    alert_bg = "rgba(59, 130, 246, 0.1)" if alert["read"] else "rgba(239, 68, 68, 0.1)"
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        st.markdown(f"""
        <div class="alert-container" style="border-left-color: {alert_border}; background: {alert_bg};">
            <div style="display: flex; align-items: flex-start; gap: 0.75rem;">
                <div style="font-size: 1.2rem; margin-top: 0.1rem;">{'🔔' if not alert['read'] else '📭'}</div>
                <div style="flex: 1;">
                    <div style="color: var(--text-primary); font-weight: {'600' if not alert['read'] else '400'}; margin-bottom: 0.5rem; line-height: 1.4;">
                        {alert['message']}
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.75rem;">
                        <div style="font-size: 0.75rem; color: var(--text-secondary);">
                            📅 {alert['date']} • 🕒 {alert['timestamp'][11:16]}
                        </div>
                        <div style="font-size: 0.7rem; color: {alert_border}; font-weight: 500;">
                            {'UNREAD' if not alert['read'] else 'READ'}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🗑️", key=f"del_alert_{alert['id']}", help="Delete alert", use_container_width=True):
            if delete_alert(alert['id']):
                st.success("Alert deleted successfully!")
                st.rerun()
            else:
                st.error("Failed to delete alert")

def show_balance_page():
    """Show detailed balance information"""
    st.markdown("## 💰 Balance Details")
    
    username = st.session_state.username
    balance = calculate_balance(username)
    account = get_account(username)
    
    # Account Summary Container
    with st.container():
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Total Debt</div>
                <div class="metric-value" style="color: var(--accent-red) !important;">{format_currency(balance["total_debt"])}</div>
                <div style="font-size: 0.8rem; color: var(--text-primary); opacity: 0.7;">All time borrowed</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Total Payments</div>
                <div class="metric-value" style="color: var(--accent-green) !important;">{format_currency(balance["total_payment"])}</div>
                <div style="font-size: 0.8rem; color: var(--text-primary); opacity: 0.7;">All time paid</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Active Utang</div>
                <div class="metric-value" style="color: var(--accent-red) !important;">{format_currency(balance["outstanding"])}</div>
                <div style="font-size: 0.8rem; color: var(--text-primary); opacity: 0.7;">Current amount due</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Available Credit</div>
                <div class="metric-value" style="color: var(--accent-green) !important;">{format_currency(balance["available_credit"])}</div>
                <div style="font-size: 0.8rem; color: var(--text-primary); opacity: 0.7;">Remaining credit limit</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Interest Paid</div>
                <div class="metric-value" style="color: var(--accent-amber) !important;">{format_currency(balance["total_interest_paid"])}</div>
                <div style="font-size: 0.8rem; color: var(--text-primary); opacity: 0.7;">Total interest paid</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Credit Information Container
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Credit Limit</div>
                <div class="metric-value" style="color: var(--accent-blue) !important;">{format_currency(account['debtLimit'])}</div>
                <div style="font-size: 0.8rem; color: var(--text-primary); opacity: 0.7;">Maximum borrowing limit</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            utilization = (balance["outstanding"] / account["debtLimit"]) * 100 if account["debtLimit"] > 0 else 0
            utilization_color = "var(--accent-red)" if utilization > 90 else "var(--accent-amber)" if utilization > 70 else "var(--accent-green)"
            
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Credit Utilization</div>
                <div class="metric-value" style="color: {utilization_color} !important;">{utilization:.1f}%</div>
                <div style="font-size: 0.8rem; color: var(--text-primary); opacity: 0.7;">Percentage of limit used</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Recent Balance Changes Container
    with st.container():
        st.markdown("""
        <div class="message-container">
            <div class="message-header">
                <span>📊 Recent Balance Changes</span>
            </div>
        """, unsafe_allow_html=True)
        
        transactions = get_customer_transactions(username)[:10]
        
        if transactions:
            for transaction in transactions:
                if transaction["confirmed"]:
                    display_transaction_item(transaction, show_interest_details=True, show_delete=True)
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">💳</div>
                <h4 class="empty-state-title">No Transaction History</h4>
                <p>Your transaction history will appear here once you have activity.</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Back to dashboard button
    with st.container():
        if st.button("← Back to Dashboard", use_container_width=True):
            st.session_state.current_page = "Dashboard"
            st.rerun()
        
        st.markdown("</div></div>", unsafe_allow_html=True)

def show_transaction_history():
    """Show customer transaction history with due dates"""
    st.markdown("## 📊 Transaction History")
    
    username = st.session_state.username
    transactions = get_customer_transactions(username)
    
    # Filter Options Container
    with st.container():        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            show_confirmed = st.checkbox("Show Confirmed Only", value=True)
        
        with col2:
            transaction_type = st.selectbox("Filter by Type", ["All", "Utang", "Payment"])
        
        with col3:
            sort_order = st.selectbox("Sort Order", ["Newest First", "Oldest First"])
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Transactions Container
    with st.container():
        st.markdown("""
        <div class="message-container">
            <div class="message-header">
                <span>📋 All Transactions</span>
            </div>
        """, unsafe_allow_html=True)
        
        if not transactions:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📊</div>
                <h4 class="empty-state-title">No Transactions Found</h4>
                <p>You don't have any transactions yet.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Filter and display transactions with due dates
            filtered_transactions = []
            for transaction in transactions:
                if show_confirmed and not transaction["confirmed"]:
                    continue
                
                if transaction_type == "Utang" and transaction["type"] != "utang":
                    continue
                
                if transaction_type == "Payment" and transaction["type"] != "payment":
                    continue
                
                filtered_transactions.append(transaction)
            
            # Sort transactions
            if sort_order == "Newest First":
                filtered_transactions.sort(key=lambda x: x["date"], reverse=True)
            else:
                filtered_transactions.sort(key=lambda x: x["date"])
            
            # Display transactions with due date information
            for transaction in filtered_transactions:
                display_transaction_item(transaction, show_delete=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Back to dashboard button
    with st.container(): 
        if st.button("← Back to Dashboard", use_container_width=True):
            st.session_state.current_page = "Dashboard"
            st.rerun()
        
        st.markdown("</div></div>", unsafe_allow_html=True)

def show_pending_transactions():
    """Show pending transactions waiting for customer OTP confirmation"""
    st.markdown("## ⏳ Pending Transactions")
    
    username = st.session_state.username
    pending_transactions = get_pending_transactions(username)
    
    # Main Container
    with st.container():
        st.markdown("""
        <div class="message-container">
            <div class="message-header">
                <span> Pending Transactions</span>
                <div class="alert-badge">{count} Pending</div>
            </div>
        """.format(count=len(pending_transactions)), unsafe_allow_html=True)
        
        st.info("These transactions are waiting for your OTP confirmation.")
        
        if not pending_transactions:
            st.markdown("""
            <div class="empty-state">
                <h4 class="empty-state-title">No Pending Transactions</h4>
            </div>
            """, unsafe_allow_html=True)
        else:
            for transaction in pending_transactions:
                display_transaction_item(transaction, show_interest_details=True, show_delete=True)
                st.divider()
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Instructions Container
    with st.container():
        st.markdown("""
        <div class="message-container">
            <div class="message-header">
                <span>📋 Confirmation Instructions</span>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        1. **Staff/Owner will inform you** about a new transaction
        2. **They will ask for the OTP** shown above
        3. **Provide them with the 6-digit OTP** code
        4. **They will enter the OTP** to confirm the transaction
        5. **Once confirmed**, the transaction will appear in your history
        6. **You will receive an alert** when confirmed
        """)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Back to dashboard button
    with st.container():      
        if st.button("← Back to Dashboard", use_container_width=True):
            st.session_state.current_page = "Dashboard"
            st.rerun()
        
        st.markdown("</div></div>", unsafe_allow_html=True)

def show_alerts_page():
    """Show customer alerts and notifications"""
    st.markdown("## 🔔 Alerts & Notifications")
    
    username = st.session_state.username
    alerts = get_alerts(username)
    unread_count = sum(1 for alert in alerts if not alert["read"])
    
    # Header Container
    with st.container():
        st.markdown("""
        <div class="message-container">
            <div class="message-header">
                <span>📨 Message</span>
                <div class="alert-badge">{unread_count} Unread</div>
            </div>
        """.format(unread_count=unread_count), unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if unread_count > 0:
                st.markdown(f"### 📬 You have {unread_count} unread message(s)")
            else:
                st.markdown("### 📭 All messages read")
        
        with col2:
            if unread_count > 0:
                if st.button("Mark All as Read", use_container_width=True):
                    if mark_alerts_read(username):
                        st.success("All messages marked as read!")
                        st.rerun()
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Messages Container
    with st.container():
        if not alerts:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📭</div>
                <h4 class="empty-state-title">No Messages</h4>
                <p>You don't have any alerts or notifications.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Display alerts in message format
            for alert in alerts:
                display_alert_item(alert)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Statistics Container
    with st.container():
        st.markdown("""
        <div class="message-container">
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Messages", len(alerts))
        
        with col2:
            st.metric("Unread", unread_count)
        
        with col3:
            st.metric("Read", len(alerts) - unread_count)
        
        with col4:
            today_count = sum(1 for alert in alerts if alert['date'] == datetime.now().strftime("%Y-%m-%d"))
            st.metric("Today", today_count)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Quick Actions Container
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Refresh Messages", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("← Back to Dashboard", use_container_width=True):
                st.session_state.current_page = "Dashboard"
                st.rerun()
        
        st.markdown("</div></div>", unsafe_allow_html=True)

def show_profile_settings():
    """Show customer profile settings with email field and without contact number"""
    st.markdown("## 👤 Profile Settings")
    
    username = st.session_state.username
    account = get_account(username)
    
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
                    <span style="color: var(--text-secondary);">Credit Limit:</span>
                    <span style="color: var(--text-primary); font-weight: bold; margin-left: 0.5rem;">{format_currency(account['debtLimit'])}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            personal_info = account.get("personalInfo", {})
            st.markdown(f"""
            <div class="profile-section">
                <h4 style="color: var(--text-primary); margin-bottom: 1rem;">Personal Information</h4>
                <div style="margin-bottom: 0.5rem;">
                    <span style="color: var(--text-secondary);">Full Name:</span>
                    <span style="color: var(--text-primary); font-weight: bold; margin-left: 0.5rem;">{personal_info.get('full_name', 'Not provided')}</span>
                </div>
                <div style="margin-bottom: 0.5rem;">
                    <span style="color: var(--text-secondary);">Email Address:</span>
                    <span style="color: var(--text-primary); font-weight: bold; margin-left: 0.5rem;">{personal_info.get('email', 'Not provided')}</span>
                </div>
                <div style="margin-bottom: 0.5rem;">
                    <span style="color: var(--text-secondary);">Address:</span>
                    <span style="color: var(--text-primary); margin-left: 0.5rem;">{personal_info.get('address', 'Not provided')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Update Personal Information Form
    with st.container():
        st.markdown("""
        <div class="message-container">
            <div class="message-header">
                <span>✏️ Update Personal Information</span>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("update_personal_info_form"):
            personal_info = account.get("personalInfo", {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                full_name = st.text_input(
                    "Full Name *", 
                    value=personal_info.get('full_name', ''),
                    placeholder="Enter your full name",
                    key="update_full_name"
                )
                email = st.text_input(
                    "Email Address *",
                    value=personal_info.get('email', ''),
                    placeholder="Enter your email address",
                    key="update_email"
                )
            
            with col2:
                address = st.text_area(
                    "Address",
                    value=personal_info.get('address', ''),
                    placeholder="Enter your address",
                    height=100,
                    key="update_address"
                )
            
            update_btn = st.form_submit_button("Update Personal Information", use_container_width=True)
            
            if update_btn:
                if not full_name.strip():
                    st.error("❌ Full name is required")
                elif not email.strip():
                    st.error("❌ Email address is required")
                else:
                    # Basic email validation
                    if "@" not in email or "." not in email:
                        st.error("❌ Please enter a valid email address")
                    else:
                        # Update personal information
                        updated_personal_info = {
                            "full_name": full_name.strip(),
                            "email": email.strip(),
                            "address": address.strip()
                        }
                        
                        # Update account in database
                        conn = get_connection()
                        if conn:
                            cursor = conn.cursor()
                            try:
                                cursor.execute(
                                    'UPDATE accounts SET personal_info = ? WHERE username = ?',
                                    (json.dumps(updated_personal_info), username)
                                )
                                conn.commit()
                                conn.close()
                                st.success("✅ Personal information updated successfully!")
                                st.rerun()
                            except Exception as e:
                                conn.close()
                                st.error(f"❌ Error updating personal information: {str(e)}")
        
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
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
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
            current_password_username = st.text_input("Current Password for Verification", type="password")
            new_username = st.text_input("New Username", value=username)
            
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
    
    # Back to Dashboard button
    with st.container():        
        if st.button("← Back to Dashboard", use_container_width=True):
            st.session_state.current_page = "Dashboard"
            st.rerun()
        
        st.markdown("</div></div>", unsafe_allow_html=True)