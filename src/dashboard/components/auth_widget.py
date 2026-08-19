"""
Authentication & Session Header Component for Streamlit.
"""

import streamlit as st

from src.dashboard.api_client import api_client


def init_session_auth():
    """Ensure session state variables exist."""
    if "jwt_token" not in st.session_state:
        st.session_state["jwt_token"] = None
    if "username" not in st.session_state:
        st.session_state["username"] = None
    if "user_role" not in st.session_state:
        st.session_state["user_role"] = None
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False


def render_auth_sidebar():
    """Renders login/logout controls in the sidebar."""
    init_session_auth()

    st.sidebar.markdown("### 🔐 User Session")

    if st.session_state["authenticated"]:
        role_color = "#38BDF8" if st.session_state["user_role"] == "Admin" else "#34D399"
        st.sidebar.markdown(
            f"""
            <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 0.75rem; margin-bottom: 0.75rem;">
                <div style="color: #94A3B8; font-size: 0.75rem; text-transform: uppercase;">Active User</div>
                <div style="color: #F8FAFC; font-weight: 700; font-size: 1.05rem;">{st.session_state['username']}</div>
                <div style="margin-top: 0.25rem;">
                    <span style="background: rgba(56, 189, 248, 0.15); color: {role_color}; border: 1px solid {role_color}; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">
                        Role: {st.session_state['user_role']}
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.sidebar.button("🚪 Log Out", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["jwt_token"] = None
            st.session_state["username"] = None
            st.session_state["user_role"] = None
            api_client.set_token(None)
            st.rerun()
    else:
        st.sidebar.info("💡 Log in with demo account (`admin` / `admin123`).")
        with st.sidebar.form("login_form"):
            username = st.text_input("Username", value="admin")
            password = st.text_input("Password", value="admin123", type="password")
            submit = st.form_submit_button("Sign In 🔓", use_container_width=True)

            if submit:
                try:
                    res = api_client.login(username=username, password=password)
                    st.session_state["jwt_token"] = res.get("access_token")
                    st.session_state["username"] = res.get("username")
                    st.session_state["user_role"] = res.get("role")
                    st.session_state["authenticated"] = True
                    api_client.set_token(res.get("access_token"))
                    st.sidebar.success("Logged in successfully!")
                    st.rerun()
                except Exception as e:
                    st.sidebar.error(f"Login failed: {e}")
