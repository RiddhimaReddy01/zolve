"""Zolve MVP - Streamlit Frontend with Behavioral UX Design."""

import streamlit as st
import requests
from typing import Optional
from datetime import datetime, timedelta
import json

st.set_page_config(
    page_title="Zolve - Behavioral Finance",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_BASE_URL = "http://localhost:8000"
DEMO_USER_ID = 1

if "user_id" not in st.session_state:
    st.session_state.user_id = DEMO_USER_ID
if "api_base" not in st.session_state:
    st.session_state.api_base = API_BASE_URL


def inject_styles() -> None:
    """Inject enhanced light theme with animations."""
    css = """
    <style>
    :root {
        --bg-primary: #FFFFFF;
        --bg-secondary: #F8F9FA;
        --bg-card: rgba(139, 92, 246, 0.04);
        --bg-card-hover: rgba(139, 92, 246, 0.08);
        --accent-gold: #D97706;
        --accent-purple: #7C3AED;
        --text-primary: #1F2937;
        --text-muted: #6B7280;
        --border-color: rgba(139, 92, 246, 0.15);
        --success-green: #10B981;
        --error-red: #EF4444;
        --warning-orange: #F97316;
    }

    * {
        box-sizing: border-box;
    }

    html, body {
        background-color: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    }

    .stApp {
        background-color: var(--bg-secondary) !important;
    }

    /* ============== ANIMATIONS ============== */
    @keyframes coin-burst {
        0% {
            opacity: 1;
            transform: scale(1) translateY(0);
        }
        100% {
            opacity: 0;
            transform: scale(0.5) translateY(-100px);
        }
    }

    @keyframes glow-pulse {
        0%, 100% {
            box-shadow: 0 0 20px rgba(217, 119, 6, 0.2);
        }
        50% {
            box-shadow: 0 0 40px rgba(217, 119, 6, 0.4);
        }
    }

    @keyframes slide-up {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes bounce {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }

    @keyframes shimmer {
        0% {
            background-position: -1000px 0;
        }
        100% {
            background-position: 1000px 0;
        }
    }

    /* ============== CARD STYLES ============== */
    .card {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
        margin: 12px 0;
        transition: all 0.3s ease;
        animation: slide-up 0.4s ease;
    }

    .card:hover {
        background: var(--bg-secondary);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
        border-color: rgba(217, 119, 6, 0.3);
    }

    .hero-card {
        background: linear-gradient(135deg, rgba(124, 58, 237, 0.06) 0%, rgba(217, 119, 6, 0.06) 100%);
        border: 1px solid rgba(217, 119, 6, 0.2);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 32px;
        box-shadow: 0 4px 16px rgba(217, 119, 6, 0.08);
    }

    .metric-hero {
        text-align: center;
        animation: slide-up 0.5s ease;
    }

    .metric-value {
        font-size: 2.5em;
        font-weight: 800;
        color: var(--accent-gold);
        margin: 8px 0;
        letter-spacing: -1px;
    }

    .metric-label {
        font-size: 0.9em;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 4px;
    }

    /* ============== PROGRESS BAR ============== */
    .progress-container {
        margin: 20px 0;
    }

    .progress-bar {
        background: rgba(217, 119, 6, 0.1);
        border-radius: 20px;
        height: 12px;
        overflow: hidden;
        border: 1px solid rgba(217, 119, 6, 0.2);
    }

    .progress-fill {
        background: linear-gradient(90deg, var(--accent-gold), var(--accent-purple));
        height: 100%;
        transition: width 0.6s ease;
        box-shadow: 0 0 10px rgba(217, 119, 6, 0.3);
    }

    .progress-text {
        display: flex;
        justify-content: space-between;
        font-size: 0.85em;
        margin-top: 8px;
        color: var(--text-muted);
    }

    /* ============== TIER BADGES ============== */
    .tier-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.9em;
        letter-spacing: 0.5px;
    }

    .tier-basic {
        background: rgba(107, 114, 128, 0.1);
        border: 1px solid rgba(107, 114, 128, 0.3);
        color: #4B5563;
    }

    .tier-silver {
        background: rgba(192, 192, 192, 0.1);
        border: 1px solid rgba(192, 192, 192, 0.3);
        color: #6B7280;
    }

    .tier-gold {
        background: rgba(217, 119, 6, 0.1);
        border: 1px solid rgba(217, 119, 6, 0.3);
        color: var(--accent-gold);
        animation: glow-pulse 2s ease-in-out infinite;
    }

    .tier-platinum {
        background: rgba(124, 58, 237, 0.1);
        border: 1px solid rgba(124, 58, 237, 0.3);
        color: var(--accent-purple);
        animation: glow-pulse 2s ease-in-out infinite;
    }

    /* ============== BUTTONS ============== */
    .stButton button {
        background: linear-gradient(135deg, var(--accent-gold), #B45309) !important;
        color: white !important;
        border-radius: 12px;
        font-weight: 700;
        border: none !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.9em !important;
    }

    .stButton button:hover {
        background: linear-gradient(135deg, var(--accent-purple), #6D28D9) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(217, 119, 6, 0.3) !important;
    }

    .stButton button:active {
        transform: translateY(0);
    }

    /* ============== ACTION CARDS ============== */
    .action-card {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 16px;
        margin: 8px 0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .action-card:hover {
        background: var(--bg-secondary);
        border-color: rgba(217, 119, 6, 0.3);
        transform: translateX(4px);
    }

    .action-card.limited {
        border-left: 4px solid var(--warning-orange);
    }

    .action-card.verified {
        border-left: 4px solid var(--success-green);
    }

    .scarcity-badge {
        display: inline-block;
        background: var(--warning-orange);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75em;
        font-weight: 700;
        margin: 4px 0;
        animation: bounce 1s ease-in-out infinite;
    }

    .reward-badge {
        display: inline-block;
        background: var(--success-green);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75em;
        font-weight: 700;
        margin: 4px 0;
    }

    /* ============== DEAL CARDS ============== */
    .deal-card {
        background: linear-gradient(135deg, rgba(124, 58, 237, 0.05) 0%, rgba(217, 119, 6, 0.05) 100%);
        border: 1px solid rgba(217, 119, 6, 0.15);
        backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 16px;
        margin: 12px 0;
        position: relative;
        transition: all 0.3s ease;
    }

    .deal-card:hover {
        border-color: rgba(217, 119, 6, 0.3);
        box-shadow: 0 8px 24px rgba(217, 119, 6, 0.1);
    }

    .deal-header {
        display: flex;
        justify-content: space-between;
        align-items: start;
        margin-bottom: 12px;
    }

    .deal-title {
        font-size: 1.1em;
        font-weight: 700;
        color: var(--text-primary);
    }

    .discount-badge {
        background: var(--accent-gold);
        color: white;
        padding: 8px 12px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 0.85em;
    }

    .timer-badge {
        background: var(--error-red);
        color: white;
        padding: 6px 12px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 0.8em;
        animation: bounce 1s ease-in-out infinite;
    }

    .coin-badge {
        display: inline-block;
        background: rgba(217, 119, 6, 0.1);
        border: 1px solid var(--accent-gold);
        color: var(--accent-gold);
        padding: 6px 12px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 0.9em;
    }

    /* ============== TEXT & ACCENTS ============== */
    .accent-gold {
        color: var(--accent-gold);
    }

    .accent-purple {
        color: var(--accent-purple);
    }

    .accent-green {
        color: var(--success-green);
    }

    .accent-red {
        color: var(--error-red);
    }

    .urgency-text {
        color: var(--warning-orange);
        font-weight: 700;
        animation: bounce 1s ease-in-out infinite;
    }

    /* ============== INPUTS ============== */
    .stTextInput input,
    .stSelectbox select,
    .stNumberInput input {
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        padding: 10px 12px !important;
    }

    .stTextInput input:focus,
    .stSelectbox select:focus,
    .stNumberInput input:focus {
        border-color: var(--accent-gold) !important;
        box-shadow: 0 0 0 2px rgba(217, 119, 6, 0.2) !important;
    }

    /* ============== NAVIGATION ============== */
    .sidebar-nav {
        padding: 20px;
        border-bottom: 1px solid var(--border-color);
    }

    .nav-item {
        padding: 12px 16px;
        border-radius: 8px;
        margin: 8px 0;
        cursor: pointer;
        transition: all 0.3s ease;
        color: var(--text-muted);
    }

    .nav-item:hover {
        background: rgba(217, 119, 6, 0.1);
        color: var(--accent-gold);
    }

    .nav-item.active {
        background: rgba(217, 119, 6, 0.15);
        color: var(--accent-gold);
        border-left: 3px solid var(--accent-gold);
    }

    /* ============== RESPONSIVE ============== */
    @media (max-width: 768px) {
        .metric-value {
            font-size: 2em;
        }
        .hero-card {
            padding: 20px;
        }
    }

    /* ============== UTILITY ============== */
    .divider-accent {
        border-top: 1px solid var(--border-color);
        margin: 20px 0;
    }

    .section-header {
        font-size: 1.3em;
        font-weight: 700;
        color: var(--text-primary);
        margin: 24px 0 16px 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        position: relative;
        padding-bottom: 12px;
    }

    .section-header::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 40px;
        height: 3px;
        background: linear-gradient(90deg, var(--accent-gold), var(--accent-purple));
        border-radius: 2px;
    }

    .info-box {
        background: rgba(59, 130, 246, 0.08);
        border-left: 3px solid rgb(59, 130, 246);
        padding: 12px 16px;
        border-radius: 8px;
        margin: 12px 0;
        font-size: 0.9em;
        color: var(--text-primary);
    }

    .success-box {
        background: rgba(16, 185, 129, 0.08);
        border-left: 3px solid var(--success-green);
        padding: 12px 16px;
        border-radius: 8px;
        margin: 12px 0;
        font-size: 0.9em;
        color: var(--text-primary);
    }

    .warning-box {
        background: rgba(249, 115, 22, 0.08);
        border-left: 3px solid var(--warning-orange);
        padding: 12px 16px;
        border-radius: 8px;
        margin: 12px 0;
        font-size: 0.9em;
        color: var(--text-primary);
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def api_get(endpoint: str) -> Optional[dict]:
    try:
        url = f"{st.session_state.api_base}{endpoint}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None


def api_post(endpoint: str, data: dict) -> Optional[dict]:
    try:
        url = f"{st.session_state.api_base}{endpoint}"
        response = requests.post(url, json=data, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None


def get_user_data() -> Optional[dict]:
    return api_get(f"/api/user/{st.session_state.user_id}")


def display_hero_metric(label: str, value: str, unit: str = ""):
    st.markdown(
        f"""
        <div class='metric-hero'>
            <div class='metric-label'>{label}</div>
            <div class='metric-value'>{value} {unit}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_progress_bar(current: float, target: float, label: str = ""):
    pct = min((current / target) * 100, 100) if target > 0 else 0
    st.markdown(
        f"""
        <div class='progress-container'>
            <div class='progress-bar'>
                <div class='progress-fill' style='width: {pct}%'></div>
            </div>
            <div class='progress-text'>
                <span>{label}</span>
                <span><span class='accent-gold'>{current:,.0f}</span> / {target:,.0f}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_tier_badge(tier: str):
    badge_class = f"tier-{tier.lower()}"
    st.markdown(
        f"<span class='tier-badge {badge_class}'>{tier} Tier</span>",
        unsafe_allow_html=True,
    )


inject_styles()

# Get user data
user_data = get_user_data()
z_world_data = api_get(f"/api/z-world/dashboard/{st.session_state.user_id}") if user_data else None

# Main page layout
st.markdown(
    "<div style='text-align: center; padding: 20px 0;'><h1 style='margin: 0; font-size: 2.5em;'>🎮 Zolve</h1><p style='color: #6B7280; margin: 8px 0; font-size: 0.95em;'>Behavioral Finance Gamification</p></div>",
    unsafe_allow_html=True,
)

st.markdown("<div class='divider-accent'></div>", unsafe_allow_html=True)

# Quick stats bar
if user_data:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        display_hero_metric("Coins", f"{user_data['balance']:,}", "💰")
    with col2:
        display_hero_metric("Tier", user_data["tier"], "")
    with col3:
        display_hero_metric("Credit Score", user_data.get("credit_score", "N/A"), "")
    with col4:
        display_hero_metric("Behaviors", user_data["verified_behaviors_count"], "✓")

st.markdown("<div class='divider-accent'></div>", unsafe_allow_html=True)

# Navigation tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(
    ["📊 Dashboard", "🏦 Bank", "💸 Earn", "🛒 Z-Kart", "🎮 Games", "⚡ Deals", "👥 Clubs", "👤 Profile"]
)

# ============== DASHBOARD ==============
with tab1:
    st.markdown(
        "<div class='section-header'>Dashboard</div>",
        unsafe_allow_html=True,
    )

    if user_data:
        if z_world_data:
            st.markdown(
                "<div class='section-header'>Z-World</div>",
                unsafe_allow_html=True,
            )
            intro = api_get("/api/z-world/intro")
            if z_world_data["onboarding"]["required"]:
                st.markdown(
                    f"<div class='info-box'><strong>{intro['value_proposition'] if intro else 'Earn rewards for financial behavior'}</strong></div>",
                    unsafe_allow_html=True,
                )
                with st.form("z_world_onboarding_form"):
                    club_name = st.text_input("Create a Z-Club", value="Credit Builders")
                    accepted = st.checkbox("I accept the Z-Coin rules")
                    submitted = st.form_submit_button("Enter Z-World", use_container_width=True)
                    if submitted:
                        result = api_post(
                            "/api/z-world/onboarding/complete",
                            {
                                "user_id": st.session_state.user_id,
                                "club_action": "create",
                                "club_name": club_name,
                                "accepted_coin_rules": accepted,
                            },
                        )
                        if result and result.get("success"):
                            st.markdown(
                                "<div class='success-box'><strong>Z-World activated.</strong> Signup bonus and your first scratch card are ready.</div>",
                                unsafe_allow_html=True,
                            )
                            st.balloons()
                            st.rerun()
            else:
                loop = z_world_data["daily_loop"]
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    display_hero_metric("Earned Spins", loop["spins_available"], "")
                with col_b:
                    display_hero_metric("Scratch Cards", loop["scratch_cards_available"], "")
                with col_c:
                    if st.button("Grant Today's Spin", use_container_width=True):
                        result = api_post(f"/api/z-world/daily-engagement/{st.session_state.user_id}", {})
                        if result:
                            st.rerun()

                notification = loop.get("latest_notification")
                if notification:
                    st.markdown(
                        f"<div class='success-box'><strong>{notification['title']}</strong><br/>{notification['message']}</div>",
                        unsafe_allow_html=True,
                    )

                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("Use Earned Spin", use_container_width=True):
                        result = api_post("/api/games/spin", {"user_id": st.session_state.user_id})
                        if result:
                            cost = "earned spin" if result.get("used_earned_spin") else f"{result.get('cost_paid', 0)} coins"
                            st.markdown(
                                f"<div class='success-box'><strong>Won {result['coins_won']} coins.</strong><br/>Used {cost}.</div>",
                                unsafe_allow_html=True,
                            )
                with col_b:
                    if st.button("Simulate On-Time Payment", use_container_width=True):
                        result = api_post(
                            "/api/z-world/financial-events",
                            {
                                "user_id": st.session_state.user_id,
                                "event_type": "payment_completed_on_time",
                                "metadata": {"source": "streamlit_demo"},
                            },
                        )
                        if result:
                            st.markdown(
                                f"<div class='success-box'><strong>Payment rewarded.</strong><br/>+{result['coins_awarded']} coins and {result['spins_unlocked']} spins unlocked.</div>",
                                unsafe_allow_html=True,
                            )
                            st.rerun()

                for action in loop["next_actions"][:3]:
                    st.markdown(
                        f"<div class='action-card'><strong>{action['label']}</strong></div>",
                        unsafe_allow_html=True,
                    )

            st.markdown("<div class='divider-accent'></div>", unsafe_allow_html=True)

        # Tier progress section
        tier_data = api_get(f"/api/tier-progress/{st.session_state.user_id}")
        if tier_data:
            st.markdown(
                "<div class='section-header'>Tier Progress</div>",
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns([3, 1])
            with col1:
                if tier_data["next_tier"]:
                    st.markdown(
                        f"<p style='margin: 0; color: #D97706; font-weight: 700;'>Progress to <span class='accent-purple'>{tier_data['next_tier']}</span> Tier</p>",
                        unsafe_allow_html=True,
                    )
                    display_progress_bar(
                        tier_data.get("current_progress", 0),
                        tier_data.get("progress_needed", 100),
                        "Near-completion magic 🚀",
                    )
                    col_a, col_b = st.columns(2)
                    col_a.markdown(
                        f"<span class='coin-badge'>+{tier_data.get('coins_needed', 0)} coins</span>",
                        unsafe_allow_html=True,
                    )
                    col_b.markdown(
                        f"<span class='reward-badge'>+{tier_data.get('behaviors_needed', 0)} behaviors</span>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        "<div class='success-box'><strong>🏆 Maximum Tier Reached!</strong> You're at the highest level.</div>",
                        unsafe_allow_html=True,
                    )

        st.markdown("<div class='divider-accent'></div>", unsafe_allow_html=True)

        # Action prompts
        st.markdown(
            "<div class='section-header'>Quick Actions</div>",
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                "<div class='action-card verified'><strong>💳 Pay Your Bills On Time</strong><br/><span style='color: #6B7280;'>Earn 500 coins + credit score boost</span><br/><span class='reward-badge'>Verified Action</span></div>",
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                "<div class='action-card limited'><strong>🎫 Daily Scratch Card</strong><br/><span style='color: #6B7280;'>Free play, unlimited wins</span><br/><span class='scarcity-badge'>Daily Reward</span></div>",
                unsafe_allow_html=True,
            )

        st.markdown("<div class='divider-accent'></div>", unsafe_allow_html=True)

        # Recent activity
        st.markdown(
            "<div class='section-header'>Recent Activity</div>",
            unsafe_allow_html=True,
        )

        if user_data.get("activity_feed"):
            for activity in user_data.get("activity_feed", [])[:5]:
                emoji = "📈" if activity["amount"] > 0 else "📉"
                direction_class = "accent-green" if activity["amount"] > 0 else "accent-red"
                st.markdown(
                    f"""
                    <div class='action-card'>
                        <strong>{emoji} {activity['event_type'].replace('_', ' ').title()}</strong>
                        <div style='color: #6B7280; font-size: 0.85em; margin-top: 4px;'>{activity['created_at'][:10]}</div>
                        <div style='font-size: 1.1em; font-weight: 700; margin-top: 8px;'><span class='{direction_class}'>{activity['amount']:+d}</span> coins</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                "<div class='info-box'><strong>No activity yet.</strong> Complete actions to start earning coins!</div>",
                unsafe_allow_html=True,
            )


# ============== LINK BANK ==============
with tab2:
    st.markdown(
        "<div class='section-header'>Link Your Bank Account</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='info-box'>Connect your bank to verify financial behaviors and earn coins automatically. Your data is secured by bank-level encryption.</div>",
        unsafe_allow_html=True,
    )

    with st.form("bank_link_form"):
        bank = st.selectbox("Select Your Bank", ["HDFC Bank", "ICICI Bank", "Axis Bank", "Other"])
        account = st.text_input("Account Number (last 4 digits)")
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Link Account", use_container_width=True)

        if submitted and account:
            result = api_post(
                "/api/bank/link",
                {
                    "user_id": st.session_state.user_id,
                    "bank_name": bank,
                    "account_number": account,
                },
            )
            if result and result.get("success"):
                st.markdown(
                    "<div class='success-box'><strong>✅ Account Linked!</strong> Your financial behaviors are now being tracked.</div>",
                    unsafe_allow_html=True,
                )
                st.balloons()
                st.rerun()


# ============== EARN ==============
with tab3:
    st.markdown(
        "<div class='section-header'>Ways to Earn Z-Coins</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='info-box'><strong>Verified Financial Behaviors:</strong> Detected automatically by our bank APIs. Zero friction earning.</div>",
        unsafe_allow_html=True,
    )

    verified_actions = [
        ("on_time_payment", "💳 On-Time Payment", 500, "Pay bills before the due date", True),
        ("credit_score_up", "📈 Credit Score Improvement", 400, "Increase your credit score by 10+ points", True),
        ("savings_milestone", "🎯 Savings Goal Milestone", 350, "Hit a savings target", True),
        ("direct_deposit", "💼 Regular Income Received", 200, "Consistent salary or income deposits", True),
    ]

    for action_id, label, coins, desc, verified in verified_actions:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown(
                f"""
                <div class='action-card verified'>
                    <strong>{label}</strong>
                    <div style='color: #6B7280; font-size: 0.85em; margin-top: 4px;'>{desc}</div>
                    <span class='reward-badge'>Verified</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f"<div style='text-align: center; padding: 16px;'><div style='font-size: 1.4em; font-weight: 700; color: #D97706;'>{coins}</div><div style='color: #6B7280; font-size: 0.8em; margin-top: 4px;'>Coins</div></div>",
                unsafe_allow_html=True,
            )
        with col3:
            if st.button("Claim", key=f"v_{action_id}", use_container_width=True):
                result = api_post(
                    "/api/coins/earn",
                    {"user_id": st.session_state.user_id, "action_type": action_id},
                )
                if result and result.get("success"):
                    st.markdown(
                        f"<div class='success-box'><strong>✨ Earned {result['coins_earned']} coins!</strong> Your tier progress just updated.</div>",
                        unsafe_allow_html=True,
                    )
                    st.balloons()
                    st.rerun()
                elif result and "Daily earning cap" in result.get("detail", ""):
                    st.markdown(
                        "<div class='warning-box'><strong>Daily Cap Reached.</strong> Try again tomorrow for this action.</div>",
                        unsafe_allow_html=True,
                    )

    st.markdown("<div class='divider-accent'></div>", unsafe_allow_html=True)

    st.markdown(
        "<div class='info-box'><strong>Engagement Actions:</strong> Build habits. Each action has daily limits.</div>",
        unsafe_allow_html=True,
    )

    engagement_actions = [
        ("daily_checkin", "☀️ Daily Check-In", 50, "Log in daily", False),
        ("education_module", "📚 Financial Education", 150, "Complete a learning module", False),
        ("ad_watch", "📺 Watch Advertisement", 10, "View a sponsored video (30 sec)", False),
    ]

    for action_id, label, coins, desc, _ in engagement_actions:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown(
                f"""
                <div class='action-card limited'>
                    <strong>{label}</strong>
                    <div style='color: #6B7280; font-size: 0.85em; margin-top: 4px;'>{desc}</div>
                    <span class='scarcity-badge'>Daily Limit</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f"<div style='text-align: center; padding: 16px;'><div style='font-size: 1.4em; font-weight: 700; color: #D97706;'>{coins}</div><div style='color: #6B7280; font-size: 0.8em; margin-top: 4px;'>Coins</div></div>",
                unsafe_allow_html=True,
            )
        with col3:
            if st.button("Claim", key=f"e_{action_id}", use_container_width=True):
                result = api_post(
                    "/api/coins/earn",
                    {"user_id": st.session_state.user_id, "action_type": action_id},
                )
                if result and result.get("success"):
                    st.markdown(
                        f"<div class='success-box'><strong>✨ Earned {result['coins_earned']} coins!</strong> {coins} coins gained.</div>",
                        unsafe_allow_html=True,
                    )
                    st.balloons()
                    st.rerun()
                elif result and "Daily earning cap" in result.get("detail", ""):
                    st.markdown(
                        "<div class='warning-box'><strong>Daily Cap Reached.</strong> Try again tomorrow for this action.</div>",
                        unsafe_allow_html=True,
                    )


# ============== Z-KART ==============
with tab4:
    st.markdown(
        "<div class='section-header'>Z-Kart Marketplace</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='info-box'><strong>Spend Your Coins on Real Products</strong> from top brands. Limited stock. Flash deals daily.</div>",
        unsafe_allow_html=True,
    )

    products = api_get("/api/zkart/products")
    if products:
        categories = sorted(set(p["category"] for p in products))
        category = st.selectbox("Filter by Category", ["All"] + categories)

        filtered = products if category == "All" else [p for p in products if p["category"] == category]

        st.markdown(
            f"<div class='section-header'>{len(filtered)} Products Available</div>",
            unsafe_allow_html=True,
        )

        for idx, product in enumerate(filtered):
            col1, col2 = st.columns([3, 1])

            with col1:
                discount = product.get("coin_discount_pct", 0)
                st.markdown(
                    f"""
                    <div class='deal-card'>
                        <div class='deal-header'>
                            <div>
                                <div class='deal-title'>{product['name']}</div>
                                <div style='color: #6B7280; font-size: 0.85em; margin-top: 4px;'>{product['category']}</div>
                            </div>
                            <div class='discount-badge'>+{discount}% Boost</div>
                        </div>
                        <div style='margin-top: 12px; display: flex; gap: 12px;'>
                            <div>
                                <div style='color: #6B7280; font-size: 0.8em;'>Price</div>
                                <div style='font-weight: 700; font-size: 1.1em;'>₹{product['base_price']}</div>
                            </div>
                            <div>
                                <div style='color: #6B7280; font-size: 0.8em;'>Coins Required</div>
                                <div style='font-weight: 700; font-size: 1.1em; color: #D97706;'>{product['coins_required']}</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col2:
                if st.button("Buy Now", key=f"buy_{product['id']}", use_container_width=True):
                    balance = api_get(f"/api/coins/balance/{st.session_state.user_id}")
                    if balance and balance["balance"] >= product["coins_required"]:
                        result = api_post(
                            "/api/zkart/purchase",
                            {
                                "user_id": st.session_state.user_id,
                                "product_id": product["id"],
                                "coins_to_spend": product["coins_required"],
                            },
                        )
                        if result and result.get("success"):
                            st.markdown(
                                f"<div class='success-box'><strong>🎉 Purchased!</strong> {product['name']} is being sent to your email.</div>",
                                unsafe_allow_html=True,
                            )
                            st.balloons()
                            st.rerun()
                    else:
                        needed = product["coins_required"] - (balance["balance"] if balance else 0)
                        st.markdown(
                            f"<div class='warning-box'><strong>Insufficient Coins.</strong> You need {needed} more coins.</div>",
                            unsafe_allow_html=True,
                        )


# ============== GAMES ==============
with tab5:
    st.markdown(
        "<div class='section-header'>Games & Rewards</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='info-box'><strong>Play Daily Games</strong> to win coins. Different mechanics, different rewards. Zero cost to play.</div>",
        unsafe_allow_html=True,
    )

    game_tab1, game_tab2 = st.tabs(["🎫 Scratch Card", "🎡 Spin Wheel"])

    with game_tab1:
        st.markdown(
            "<div style='padding: 20px; text-align: center;'><p style='color: #6B7280; margin: 0;'>Scratch to reveal your prize. Unlimited daily plays.</p></div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div class='info-box'><strong>Odds:</strong> 40% Try Again • 35% +50 Coins • 20% +150 Coins • 5% +500 Coins</div>",
            unsafe_allow_html=True,
        )

        if st.button("🎫 Play Scratch Card", use_container_width=True, key="scratch"):
            result = api_post(
                "/api/games/scratch",
                {"user_id": st.session_state.user_id},
            )
            if result:
                if result["coins_won"] > 0:
                    st.markdown(
                        f"""
                        <div class='hero-card'>
                            <div style='font-size: 2em; margin-bottom: 12px;'>✨ You Won!</div>
                            <div style='font-size: 2.5em; font-weight: 800; color: #D97706; margin: 16px 0;'>{result['coins_won']} Coins</div>
                            <div style='color: #6B7280;'>{result['message']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.balloons()
                else:
                    st.markdown(
                        f"<div class='warning-box'><strong>Try Again!</strong> {result['message']}</div>",
                        unsafe_allow_html=True,
                    )

    with game_tab2:
        st.markdown(
            "<div style='padding: 20px; text-align: center;'><p style='color: #6B7280; margin: 0;'>Costs 100 coins per spin. High risk, high reward.</p></div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div class='info-box'><strong>Segments:</strong> 50 • 100 • 200 • 300 • 500 • 1000 Coins</div>",
            unsafe_allow_html=True,
        )

        balance = api_get(f"/api/coins/balance/{st.session_state.user_id}")
        if balance and balance["balance"] >= 100:
            if st.button("🎡 Spin the Wheel", use_container_width=True, key="wheel"):
                result = api_post(
                    "/api/games/spin",
                    {"user_id": st.session_state.user_id},
                )
                if result:
                    st.markdown(
                        f"""
                        <div class='hero-card'>
                            <div style='font-size: 2em; margin-bottom: 12px;'>🎡 Spinning...</div>
                            <div style='font-size: 1.2em; font-weight: 700; color: #D97706; margin: 16px 0;'>Segment {result['segment_number']}</div>
                            <div style='font-size: 2em; font-weight: 800; color: #D97706; margin: 16px 0;'>{result['coins_won']} Coins</div>
                            <div style='color: #6B7280;'>{result['message']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.balloons()
        else:
            st.markdown(
                f"<div class='warning-box'><strong>Need 100 Coins to Spin.</strong> You have {balance['balance'] if balance else 0}. Earn more coins first!</div>",
                unsafe_allow_html=True,
            )


# ============== FLASH DEALS ==============
with tab6:
    st.markdown(
        "<div class='section-header'>Flash Deals</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='warning-box'><strong>⚠️ Limited Time Offers</strong> — These deals expire fast. Scarcity creates value.</div>",
        unsafe_allow_html=True,
    )

    # Simulated flash deals
    flash_deals = [
        {
            "title": "Premium Headphones",
            "original_price": 4999,
            "discount_pct": 35,
            "coins_needed": 1500,
            "quantity_left": 2,
            "minutes_left": 47,
        },
        {
            "title": "Wireless Charger",
            "original_price": 1999,
            "discount_pct": 25,
            "coins_needed": 400,
            "quantity_left": 5,
            "minutes_left": 23,
        },
        {
            "title": "Smart Watch Band",
            "original_price": 599,
            "discount_pct": 40,
            "coins_needed": 150,
            "quantity_left": 1,
            "minutes_left": 12,
        },
    ]

    for deal in flash_deals:
        col1, col2 = st.columns([3, 1])

        with col1:
            final_price = deal["original_price"] * (1 - deal["discount_pct"] / 100)
            st.markdown(
                f"""
                <div class='deal-card'>
                    <div class='deal-header'>
                        <div>
                            <div class='deal-title'>{deal['title']}</div>
                            <div style='color: #6B7280; font-size: 0.85em; margin-top: 4px;'>
                                <span style='text-decoration: line-through;'>₹{deal['original_price']}</span> →
                                <span style='color: #10B981; font-weight: 700;'>₹{final_price:.0f}</span>
                            </div>
                        </div>
                        <div class='discount-badge'>{deal['discount_pct']}% OFF</div>
                    </div>
                    <div style='margin-top: 12px; display: flex; gap: 12px;'>
                        <div style='flex: 1;'>
                            <div style='color: #6B7280; font-size: 0.8em;'>Coins Needed</div>
                            <div class='coin-badge' style='display: block; text-align: center; padding: 8px;'>{deal['coins_needed']}</div>
                        </div>
                        <div style='flex: 1;'>
                            <div style='color: #6B7280; font-size: 0.8em;'>Stock Left</div>
                            <div class='scarcity-badge' style='display: block; text-align: center;'>Only {deal['quantity_left']}</div>
                        </div>
                        <div style='flex: 1;'>
                            <div style='color: #6B7280; font-size: 0.8em;'>Expires In</div>
                            <div class='timer-badge' style='display: block; text-align: center;'>{deal['minutes_left']}m</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            if st.button("Buy", key=f"flash_{deal['title']}", use_container_width=True):
                st.markdown(
                    "<div class='success-box'><strong>Deal Locked!</strong> Proceeding to checkout...</div>",
                    unsafe_allow_html=True,
                )


# ============== Z-CLUBS ==============
with tab7:
    st.markdown(
        "<div class='section-header'>Z-Clubs</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='info-box'><strong>Join or Create Clubs</strong> to earn together. Unlock exclusive deals when your club reaches milestones.</div>",
        unsafe_allow_html=True,
    )

    # Simulated clubs
    clubs = [
        {
            "name": "Gold Savers Club",
            "members": 12,
            "tier": "Gold",
            "pool_coins": 5000,
            "progress": 75,
        },
        {
            "name": "Early Birds",
            "members": 8,
            "tier": "Silver",
            "pool_coins": 2000,
            "progress": 45,
        },
        {
            "name": "Finance Hackers",
            "members": 20,
            "tier": "Basic",
            "pool_coins": 1500,
            "progress": 30,
        },
    ]

    for club in clubs:
        st.markdown(
            f"""
            <div class='deal-card'>
                <div class='deal-header'>
                    <div>
                        <div class='deal-title'>{club['name']}</div>
                        <span class='tier-badge tier-{club['tier'].lower()}'>{club['tier']} Club</span>
                    </div>
                </div>
                <div style='margin-top: 16px; display: flex; gap: 16px;'>
                    <div>
                        <div style='color: #6B7280; font-size: 0.8em;'>Members</div>
                        <div style='font-weight: 700; font-size: 1.2em;'>{club['members']}</div>
                    </div>
                    <div>
                        <div style='color: #6B7280; font-size: 0.8em;'>Club Pool</div>
                        <div style='font-weight: 700; font-size: 1.2em; color: #D97706;'>{club['pool_coins']:,}</div>
                    </div>
                </div>
                <div style='margin-top: 12px;'>
                    <div style='color: #6B7280; font-size: 0.8em; margin-bottom: 4px;'>Progress to Next Tier</div>
                    <div class='progress-bar'>
                        <div class='progress-fill' style='width: {club['progress']}%'></div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)
        with col1:
            st.button("Join Club", use_container_width=True, key=f"join_{club['name']}")
        with col2:
            st.button("View Members", use_container_width=True, key=f"members_{club['name']}")

    st.markdown("<div class='divider-accent'></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-header'>Create Your Club</div>", unsafe_allow_html=True)

    with st.form("create_club_form"):
        club_name = st.text_input("Club Name", placeholder="e.g., My Savings Squad")
        club_desc = st.text_area("Description", placeholder="What's your club about?", height=80)
        submitted = st.form_submit_button("Create Club", use_container_width=True)

        if submitted and club_name:
            st.markdown(
                f"<div class='success-box'><strong>✅ Club Created!</strong> '{club_name}' is now live. Invite friends to join!</div>",
                unsafe_allow_html=True,
            )


# ============== PROFILE ==============
with tab8:
    st.markdown(
        "<div class='section-header'>My Profile</div>",
        unsafe_allow_html=True,
    )

    if user_data:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                f"""
                <div class='card'>
                    <div class='section-header' style='font-size: 1.1em; margin-bottom: 16px;'>Personal Info</div>
                    <div style='margin: 12px 0;'><span style='color: #6B7280;'>Name</span><br/><strong>{user_data['name']}</strong></div>
                    <div style='margin: 12px 0;'><span style='color: #6B7280;'>Email</span><br/><strong>{user_data['email']}</strong></div>
                    <div style='margin: 12px 0;'><span style='color: #6B7280;'>Member Since</span><br/><strong>{user_data['created_at'][:10]}</strong></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"""
                <div class='card'>
                    <div class='section-header' style='font-size: 1.1em; margin-bottom: 16px;'>Financial Metrics</div>
                    <div style='margin: 12px 0;'><span style='color: #6B7280;'>Credit Score</span><br/><strong style='font-size: 1.3em;'>{user_data.get('credit_score', 'N/A')}</strong></div>
                    <div style='margin: 12px 0;'><span style='color: #6B7280;'>Total Coins</span><br/><strong style='font-size: 1.3em; color: #D97706;'>{user_data['balance']:,}</strong></div>
                    <div style='margin: 12px 0;'><span style='color: #6B7280;'>Verified Behaviors</span><br/><strong style='font-size: 1.3em; color: #10B981;'>{user_data['verified_behaviors_count']}</strong></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div class='divider-accent'></div>", unsafe_allow_html=True)

        # Verified behaviors
        verified = api_get(f"/api/verified-behaviors/{st.session_state.user_id}")
        if verified and verified.get("verified_behaviors"):
            st.markdown(
                "<div class='section-header'>Verified Behaviors</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<p style='color: #6B7280; margin: 0 0 16px 0;'>You have <strong>{verified['total_count']}</strong> verified financial behaviors</p>",
                unsafe_allow_html=True,
            )

            for behavior in verified["verified_behaviors"][:5]:
                st.markdown(
                    f"""
                    <div class='action-card verified'>
                        <strong>{behavior['behavior_type'].replace('_', ' ').title()}</strong>
                        <div style='color: #6B7280; font-size: 0.85em; margin-top: 4px;'>Via {behavior['verification_source']}</div>
                        <div style='color: #6B7280; font-size: 0.85em;'>{behavior['completed_at'][:10]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                "<div class='info-box'><strong>No Verified Behaviors Yet.</strong> Link your bank account to start verifying financial behaviors.</div>",
                unsafe_allow_html=True,
            )

        st.markdown("<div class='divider-accent'></div>", unsafe_allow_html=True)

        # Transaction history
        st.markdown(
            "<div class='section-header'>Transaction History</div>",
            unsafe_allow_html=True,
        )

        history = api_get(f"/api/coins/history/{st.session_state.user_id}?limit=20")
        if history:
            for txn in history[:10]:
                emoji = "📈" if txn["amount"] > 0 else "📉"
                color_class = "accent-green" if txn["amount"] > 0 else "accent-red"
                st.markdown(
                    f"""
                    <div class='action-card'>
                        <div style='display: flex; justify-content: space-between; align-items: start;'>
                            <div>
                                <strong>{emoji} {txn['event_type'].replace('_', ' ').title()}</strong>
                                <div style='color: #6B7280; font-size: 0.85em; margin-top: 4px;'>{txn['created_at'][:10]} • {txn['description']}</div>
                            </div>
                            <div style='text-align: right;'>
                                <div style='font-weight: 700; font-size: 1.1em;'><span class='{color_class}'>{txn['amount']:+d}</span></div>
                                <div style='color: #6B7280; font-size: 0.8em;'>coins</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                "<div class='info-box'>No transaction history yet.</div>",
                unsafe_allow_html=True,
            )

st.markdown("<div class='divider-accent'></div>", unsafe_allow_html=True)

# Footer
st.markdown(
    "<div style='text-align: center; color: var(--text-muted); font-size: 0.85em; padding: 20px 0;'><p style='margin: 0;'>© 2026 Zolve • Behavioral Finance Gamification</p><p style='margin: 0; margin-top: 4px;'>Made with ❤️ for better financial habits</p></div>",
    unsafe_allow_html=True,
)
