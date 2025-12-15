import streamlit as st
from auth import show_login_page, logout
from customer_dashboard import show_customer_dashboard
from owner_dashboard import show_owner_dashboard
from utils import ensure_session_state, get_setting
from database import init_database, migrate_from_json, add_missing_columns, check_database_health, migrate_created_by_field

# Page configuration
st.set_page_config(
    page_title="IUMS",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply professional web-app theme
def apply_custom_styles():
    st.markdown("""
    <style>
    :root {
        --navy-dark: #0f172a;
        --navy-medium: #1e293b;
        --navy-light: #334155;
        --accent-blue: #3b82f6;
        --accent-teal: #0d9488;
        --accent-green: #10b981;
        --accent-amber: #f59e0b;
        --accent-red: #ef4444;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --bg-primary: #0a0f1c;
        --bg-secondary: #1e293b;
        --border-color: #334155;
        --card-bg: rgba(30, 41, 59, 0.95);
    }
    
    .main-header {
        font-size: 2.8rem;
        background: linear-gradient(135deg, var(--text-primary), var(--accent-blue));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
        letter-spacing: -1px;
    }
    
    .user-info-card {
        background: var(--card-bg);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .footer {
        text-align: center;
        padding: 2rem;
        color: var(--text-secondary);
        margin-top: 3rem;
        border-top: 1px solid var(--border-color);
    }
    </style>
    """, unsafe_allow_html=True)

def show_header():
    """Show application header"""
    app_name = get_setting("appName", "IUMS")
    
    st.markdown(f"""
    <div class="main-header">
        {app_name}
    </div>
    """, unsafe_allow_html=True)

def show_sidebar():
    """Show sidebar navigation with due date alerts"""
    # Only show user info if logged in
    if st.session_state.logged_in:
        # User info card
        st.sidebar.markdown(f"""
        <div class="user-info-card">
            <div style="width: 70px; height: 70px; background: linear-gradient(135deg, var(--accent-blue), var(--accent-teal)); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; font-size: 1.8rem; color: white; font-weight: bold; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);">
                {st.session_state.username[0].upper()}
            </div>
            <h3 style="margin: 0; color: var(--text-primary); font-size: 1.2rem;">{st.session_state.username}</h3>
            <p style="margin: 0.5rem 0 0 0; color: var(--text-secondary); font-size: 0.85rem; background: rgba(30, 41, 59, 0.6); padding: 0.4rem 1rem; border-radius: 20px; display: inline-block; border: 1px solid var(--border-color);">
                {st.session_state.role}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation based on role
        if st.session_state.role == "Owner":
            menu_options = [
                ("Dashboard", "Dashboard"),
                ("Manage My Accounts", "Manage Account"), 
                ("Add Utang", "Add Utang"),
                ("Record Payment", "Record Payment"),
                ("Pending Confirmations", "Pending Confirmations"),
                ("Reports & Analytics", "Reports"),
                ("System Settings", "Settings"),
                ("Owner Profile", "Owner Profile")
            ]
        else:  # Customer
            menu_options = [
                ("Dashboard", "Dashboard"),
                ("Balance Details", "Balance"),
                ("Transaction History", "Transaction History"),
                ("Pending Transactions", "Pending Transactions"),
                ("Messages & Alerts", "Alerts"),
                ("Profile Settings", "Profile Settings")
            ]
        
        # Create navigation buttons
        st.sidebar.markdown("### Navigation")
        for display_name, page_name in menu_options:
            is_selected = st.session_state.current_page == page_name
            
            if st.sidebar.button(
                display_name, 
                key=f"nav_{page_name}",
                use_container_width=True,
                type="primary" if is_selected else "secondary"
            ):
                st.session_state.current_page = page_name
                st.rerun()
        
        # System actions
        st.sidebar.markdown("---")
        st.sidebar.markdown("### System Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.sidebar.button("Refresh", key="refresh_btn", use_container_width=True):
                st.rerun()
        
        # Auto-check due dates for owners (ONLY when logged in as Owner)
        if st.session_state.role == "Owner":
            if st.sidebar.button("Check Due Dates", key="check_due_dates_sidebar", use_container_width=True):
                from utils import check_due_dates
                success, message = check_due_dates()
                if success:
                    st.sidebar.success(message)
                else:
                    st.sidebar.error(message)
                st.rerun()
    else:
        # Show login message or basic info when not logged in
        st.sidebar.markdown("""
        <div class="user-info-card">
            <div style="width: 70px; height: 70px; background: var(--navy-medium); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; font-size: 1.8rem; color: white; font-weight: bold;">
                👤
            </div>
            <h3 style="margin: 0; color: var(--text-primary); font-size: 1.2rem;">Not Logged In</h3>
            <p style="margin: 0.5rem 0 0 0; color: var(--text-secondary); font-size: 0.85rem;">
                Please log in to continue
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Logout button (only show when logged in)
    if st.session_state.logged_in:
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Logout", key="logout_btn", type="primary", use_container_width=True):
            logout()

def initialize_system():
    """Initialize the system and database"""
    if "system_initialized" not in st.session_state:
        with st.spinner("🔧 Initializing system..."):
            # Initialize database
            if not init_database():
                st.error("❌ Failed to initialize database")
                return False
            
            # Add missing columns including due_date and created_by
            add_missing_columns()
            
            # Migrate created_by field
            migrate_created_by_field()
            
            # Migrate from old formats
            migrate_from_json()
            
            # Check database health
            health_status, health_message = check_database_health()
            if not health_status:
                st.warning(f"Database health check: {health_message}")
            
            st.session_state.system_initialized = True
            
            # Initialize email service
            try:
                from email_utils import email_service
                email_service.set_currency_symbol(get_setting("currencySymbol", "₱"))
            except ImportError:
                pass
                
            return True
    return True

def main():
    """Main application function"""
    apply_custom_styles()
    ensure_session_state()
    
    # Initialize system
    if not initialize_system():
        st.error("System initialization failed. Please refresh the page.")
        return
    
    # Show header
    show_header()
    
    # Show sidebar
    show_sidebar()
    
    # Authentication check - show login page if not logged in
    if not st.session_state.logged_in:
        show_login_page()
        return
    
    # Show appropriate dashboard based on role
    try:
        if st.session_state.role == "Owner":
            show_owner_dashboard()
        elif st.session_state.role == "Customer":
            show_customer_dashboard()
        else:
            st.error("❌ Unknown user role")
    except Exception as e:
        st.info("Please refresh the page or contact support if the issue persists.")

    # Footer
    st.markdown("""
    <div class="footer">
        <p style="margin: 0; font-weight: 500;">IUMS - Integrated Utang Management System</p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.8rem; opacity: 0.8;">Secure • Professional • Efficient • With Due Date Tracking</p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.7rem; opacity: 0.6;">v2.1 • Built with Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()