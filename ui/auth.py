import streamlit as st
from config import PERSONAS, INTERESTS, AVOID_SUGGESTIONS, PERSONA_FOCUS
from core.auth import authenticate, register_user
from core.db import list_users

def render():
    # Session state initialization
    ss = st.session_state
    if "auth_mode" not in ss:
        ss.auth_mode = "🔑 Log In"

    # Newspaper Editorial Header / Masthead
    st.markdown(
        """
        <style>
        .auth-container {
            max-width: 580px;
            margin: 0 auto;
            padding: 2.2rem 2.5rem;
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.06);
            border: 1px solid #e5e7eb;
        }
        .auth-masthead {
            text-align: center;
            font-family: Georgia, 'Times New Roman', serif;
            font-size: 2.6rem;
            font-weight: 700;
            color: #111827;
            letter-spacing: -0.5px;
            margin-bottom: 0.2rem;
        }
        .auth-subhead {
            text-align: center;
            font-size: 1.05rem;
            color: #6b7280;
            font-style: italic;
            margin-bottom: 1.8rem;
        }
        .auth-card-title {
            font-size: 1.3rem;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 0.3rem;
        }
        .auth-card-subtitle {
            font-size: 0.9rem;
            color: #6b7280;
            margin-bottom: 1.2rem;
        }
        .auth-demo-badge {
            display: inline-block;
            background: #f3f4f6;
            color: #374151;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 500;
            margin-left: 6px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Center column layout
    _, col, _ = st.columns([1, 2.2, 1])

    with col:
        st.markdown(
            """
            <div class="auth-masthead">☕ THE DAILY BREW</div>
            <div class="auth-subhead">Your Personal AI-Curated Morning Intelligence Briefing</div>
            """,
            unsafe_allow_html=True,
        )

        # Tab / Mode selector
        mode = st.segmented_control(
            "Account Options",
            options=["🔑 Log In", "✨ Create Account"],
            default=ss.auth_mode,
            key="auth_selector",
            label_visibility="collapsed",
        )
        if mode and mode != ss.auth_mode:
            ss.auth_mode = mode
            st.rerun()

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        if ss.auth_mode == "🔑 Log In":
            _render_login()
        else:
            _render_signup()


def _render_login():
    ss = st.session_state
    st.markdown('<div class="auth-card-title">Welcome Back</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-card-subtitle">Sign in to read today\'s personalized edition.</div>', unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input(
            "Username or Reader Name",
            value=ss.get("prefill_username", ""),
            placeholder="e.g. Alex or Maheen",
            help="Case-insensitive name used when you registered",
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            help="For accounts created before passwords were required, you can enter a new password to protect your account.",
        )

        submitted = st.form_submit_button("Log In to Daily Brew 🗞️", type="primary", use_container_width=True)

    if submitted:
        user, err = authenticate(username, password)
        if err:
            st.error(err)
        else:
            ss.user_id = user["id"]
            st.query_params["uid"] = str(user["id"])
            ss.pop("prefill_username", None)
            st.toast(f"Welcome back, {user['name']}!", icon="☕")
            st.rerun()

    # Switch to signup quick link
    st.markdown("<div style='text-align: center; margin-top: 1rem; font-size: 0.9rem; color: #6b7280;'>", unsafe_allow_html=True)
    if st.button("New reader? Create an account here →", key="switch_to_signup"):
        ss.auth_mode = "✨ Create Account"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Demo / Existing Readers Quick-Helper for hackathon testing
    existing_users = list_users()
    if existing_users:
        with st.expander("👥 Existing Readers (Quick Demo Access)"):
            st.caption("Click any reader below to autofill and log in directly:")
            for u in existing_users:
                p_text = f" ({u.get('persona', 'Reader')})" if u.get("persona") else ""
                col1, col2 = st.columns([3, 1])
                col1.write(f"**{u['name']}** {p_text}")
                if col2.button("Log In", key=f"demo_login_{u['id']}", use_container_width=True):
                    ss.user_id = u["id"]
                    st.query_params["uid"] = str(u["id"])
                    st.rerun()


def _render_signup():
    ss = st.session_state
    st.markdown('<div class="auth-card-title">Create Your Reader Account</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-card-subtitle">Set up your profile to generate your customized morning newspaper.</div>', unsafe_allow_html=True)

    with st.form("signup_form"):
        st.markdown("##### 1. Account Details")
        name = st.text_input("Your Name / Username", placeholder="e.g. Alex Hunter", help="Unique identifier for your morning paper")
        
        c1, c2 = st.columns(2)
        password = c1.text_input("Password", type="password", placeholder="Min 4 characters")
        confirm_password = c2.text_input("Confirm Password", type="password", placeholder="Repeat password")

        persona = st.selectbox(
            "Your Primary Role / Persona",
            PERSONAS,
            index=0,
            help="Our AI editor balances topics and depth tailored to your professional focus.",
        )

        st.markdown("<hr style='margin: 1.2rem 0; border: none; border-top: 1px solid #e5e7eb;'>", unsafe_allow_html=True)
        st.markdown("##### 2. What do you want to read about?")
        st.caption("Select at least 2 interests. You can tune these later as you read.")

        # Default interests focus based on chosen persona
        default_interests = PERSONA_FOCUS.get(persona, ["Tech & AI", "Science"])
        interests = st.pills(
            "Interests",
            INTERESTS,
            selection_mode="multi",
            default=default_interests,
        ) or []

        custom_interests = st.text_input(
            "Other topics of interest (optional, comma-separated)",
            placeholder="e.g. Quantum Computing, Formula 1, Biotechnology",
        )

        st.markdown("<hr style='margin: 1.2rem 0; border: none; border-top: 1px solid #e5e7eb;'>", unsafe_allow_html=True)
        st.markdown("##### 3. Topics to Keep Out (Optional)")
        st.caption("We will filter out stories focused primarily on these topics.")

        avoid = st.pills(
            "Avoid",
            AVOID_SUGGESTIONS,
            selection_mode="multi",
            default=["Celebrity Gossip"],
        ) or []

        custom_avoid = st.text_input(
            "Other topics to avoid (optional, comma-separated)",
            placeholder="e.g. Reality TV, Tabloid Drama",
        )

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Create My Account & Brew Paper 🗞️", type="primary", use_container_width=True)

    if submitted:
        # Pre-validation
        name_clean = name.strip()
        if not name_clean:
            st.error("Please enter a name or username.")
            return

        if not password:
            st.error("Please choose a password.")
            return

        if len(password) < 4:
            st.error("Password must be at least 4 characters long.")
            return

        if password != confirm_password:
            st.error("Passwords do not match. Please verify both password fields.")
            return

        # Combine selected interests and custom extras
        extra_interests = [x.strip() for x in custom_interests.split(",") if x.strip()]
        all_interests = list(dict.fromkeys(interests + extra_interests))

        if len(all_interests) < 2:
            st.error("Please select at least 2 topics of interest.")
            return

        extra_avoid = [x.strip() for x in custom_avoid.split(",") if x.strip()]
        all_avoid = list(dict.fromkeys(avoid + extra_avoid))

        # Register user in database
        user, err = register_user(name_clean, password, persona, all_interests, all_avoid)
        if err:
            st.error(err)
        else:
            ss.user_id = user["id"]
            st.query_params["uid"] = str(user["id"])
            st.toast(f"Welcome aboard, {user['name']}!", icon="🗞️")
            st.rerun()

    st.markdown("<div style='text-align: center; margin-top: 1rem; font-size: 0.9rem; color: #6b7280;'>", unsafe_allow_html=True)
    if st.button("Already have an account? Log in here →", key="switch_to_login"):
        ss.auth_mode = "🔑 Log In"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
