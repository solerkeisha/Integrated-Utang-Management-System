import streamlit as st
from utils import get_account, create_account, ensure_session_state
import base64, os

def _get_base64_image(file_path):
    """Convert image to base64 for HTML embedding"""
    if not os.path.exists(file_path):
        return ""
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def show_login_page():
    """Show login/signup page with professional web-app layout"""
    ensure_session_state()

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
        --card-bg: rgba(30, 41, 59, 0.8);
        --hover-bg: rgba(51, 65, 85, 0.4);
    }

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--navy-dark) 100%);
        color: var(--text-primary);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .main {
        padding: 0 !important;
    }

    section[data-testid="stSidebar"] {
        display: none;
    }

    #MainMenu, header, footer {
        visibility: hidden;
    }

    /* --- MAIN LAYOUT --- */
    .login-container {
        display: flex;
        justify-content: center;
        align-items: stretch;
        height: 100vh;
        gap: 0;
    }

    /* --- LEFT PANEL --- */
    .left-panel {
        background: linear-gradient(135deg, var(--navy-dark), var(--navy-medium));
        color: var(--text-primary);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        flex: 1.2;
        padding: 4rem 3rem;
        border-radius: 0 16px 16px 0;
        box-shadow: 8px 0 24px rgba(0,0,0,0.2);
        height: 100vh;
        position: relative;
        overflow: hidden;
    }

    .left-panel::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 0%, rgba(59, 130, 246, 0.1) 100%);
        z-index: 1;
    }

    .left-panel > * {
        position: relative;
        z-index: 2;
    }

    /* --- RIGHT PANEL --- */
    .right-panel {
        flex: 1;
        background: var(--bg-primary);
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding: 3rem 2.5rem;
        position: relative;
    }

    /* --- TITLE --- */
    .title {
        text-align: center;
        color: var(--text-primary);
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        background: linear-gradient(135deg, var(--text-primary), var(--accent-blue));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* --- FORM STYLING --- */
    .stTextInput > div > div > input,
    .stPassword > div > div > input,
    .stTextArea > div > div > textarea {
        background: var(--card-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        color: var(--text-primary) !important;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        backdrop-filter: blur(10px);
    }

    .stTextInput > div > div > input:focus,
    .stPassword > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-blue) !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1) !important;
        transform: translateY(-1px);
    }

    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, var(--accent-blue), var(--navy-light));
        color: white;
        border: none;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, var(--accent-blue), #2563eb);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }

    /* Fix form labels */
    .stTextInput label,
    .stPassword label,
    .stTextArea label {
        color: var(--text-primary) !important;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }

    /* Professional Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: transparent;
        padding: 0;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background: var(--card-bg);
        border-radius: 8px 8px 0 0;
        padding: 0.75rem 1.5rem;
        margin: 0 2px;
        border: 1px solid var(--border-color);
        border-bottom: none;
        color: var(--text-secondary) !important;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .stTabs [aria-selected="true"] {
        background: var(--navy-light) !important;
        color: var(--text-primary) !important;
        border-color: var(--accent-blue);
        box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
    }

    /* Form container */
    .form-container {
        background: var(--card-bg);
        backdrop-filter: blur(10px);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--navy-light);
        border-radius: 3px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-blue);
    }
    </style>
    """, unsafe_allow_html=True)

    # Layout columns
    col1, col2 = st.columns([1, 1])

    with col1:
        img_base64 = _get_base64_image("logo.png")
        st.markdown(f"""
        <div class="left-panel">
            {'<img src="data:image/png;base64,' + img_base64 + '" alt="Logo" style="max-width: 200px; margin-bottom: 2rem;"/>' if img_base64 else ''}
            <h1 style="text-align: center; font-size: 2.5rem; margin-bottom: 1rem; background: linear-gradient(135deg, #f1f5f9, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">IUMS</h1>
            <p style="text-align: center; font-size: 1.2rem; opacity: 0.9; max-width: 400px; line-height: 1.6;">Integrated Utang Management System</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "👤 Create Account"])
        with tab1:
            show_login_form()
        with tab2:
            show_owner_signup()
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_login_form():
    """Show login form with professional styling"""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2 style="color: var(--text-primary); margin-bottom: 0.5rem;">Welcome Back</h2>
        <p style="color: var(--text-secondary);">Sign in to your account</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form", clear_on_submit=True):
        username = st.text_input("👤 Username", placeholder="Enter your username", key="login_username")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", key="login_password")

        login_btn = st.form_submit_button("Sign In", use_container_width=True)
        if login_btn:
            if not username or not password:
                st.error("❌ Please enter both username and password")
                return

            account = get_account(username)
            if not account:
                st.error("❌ Account not found")
                return

            if account["role"] not in ["Owner", "Customer"]:
                st.error("❌ Invalid user role")
                return

            if account["password"] != password:
                st.error("❌ Incorrect password")
                return

            # Successful login
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = account["role"]
            st.session_state.current_page = "Dashboard"
            st.success(f"🎉 Welcome back, {username}!")
            st.rerun()

def show_owner_signup():
    """Show owner account creation form with professional styling"""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2 style="color: var(--text-primary); margin-bottom: 0.5rem;">Create Account</h2>
        <p style="color: var(--text-secondary);">Set up your owner account</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("owner_signup_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Account Details**")
            username = st.text_input("Username", placeholder="Choose a username", key="signup_username")
            password = st.text_input("Password", type="password", placeholder="Create a password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", key="signup_confirm_password")

        with col2:
            st.markdown("**Personal Information**")
            full_name = st.text_input("Full Name *", placeholder="Enter your full name", key="signup_full_name")
            email = st.text_input("Email Address *", placeholder="Enter your email address", key="signup_email")
            address = st.text_area("Address", placeholder="Enter your address", height=80, key="signup_address")

        submit_btn = st.form_submit_button("Create Account", use_container_width=True)

        if submit_btn:
            if not username or not password:
                st.error("❌ Please enter username and password")
                return

            if password != confirm_password:
                st.error("❌ Passwords do not match")
                return

            if len(password) < 4:
                st.error("❌ Password must be at least 4 characters")
                return

            if not full_name:
                st.error("❌ Please enter your full name")
                return

            if not email:
                st.error("❌ Please enter your email address")
                return

            # Basic email validation
            if "@" not in email or "." not in email:
                st.error("❌ Please enter a valid email address")
                return

            personal_info = {
                "full_name": full_name,
                "email": email,
                "address": address
            }

            # Owner creates their own account, so they are their own creator
            success, message = create_account(username, password, "Owner", personal_info, created_by=username)

            if success:
                st.success("✅ Account created successfully! Please login with your new credentials.")
                st.rerun()
            else:
                st.error(f"❌ {message}")

def logout():
    """Logout user"""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.current_page = "Dashboard"
    st.success("✅ Logged out successfully!")
    st.rerun()