
import json
import html
import streamlit as st
from pathlib import Path

# ============================================================
# SENTINEL | SECURITY INTELLIGENCE
# ============================================================

st.set_page_config(
    page_title="SENTINEL | Security Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


# ============================================================
# DATA LAYER — EXISTING JSON CONTRACTS PRESERVED
# ============================================================

def load_json(filename, default):
    path = DATA_DIR / filename

    if not path.exists():
        return default

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        st.error(f"Unable to read {filename}.")
        return default


alerts = load_json("alerts.json", [])
evidence_data = load_json("evidence.json", {})
verification_data = load_json("verification.json", [])
llm_data = load_json("llm_analysis.json", [])

if not isinstance(alerts, list):
    alerts = []

if not isinstance(verification_data, list):
    verification_data = []

if not isinstance(llm_data, list):
    llm_data = []

evidence_records = evidence_data.get("records", [])

evidence_by_id = {
    record["event_id"]: record
    for record in evidence_records
    if isinstance(record, dict) and "event_id" in record
}

verification_by_user = {
    item["alert"]["username"]: item["verified_claims"]
    for item in verification_data
    if isinstance(item, dict)
    and isinstance(item.get("alert"), dict)
    and "username" in item["alert"]
}

llm_by_user = {
    item["username"]: item
    for item in llm_data
    if isinstance(item, dict) and "username" in item
}


# ============================================================
# VISUAL DESIGN SYSTEM
# ============================================================

st.markdown("""
<style>
:root {
    --bg: #080b0d;
    --surface: #101715;
    --surface-soft: #141e1a;
    --surface-raised: #1a2721;
    --green: #00e5a0;
    --green-soft: #83f5c8;
    --text: #eff8f3;
    --muted: #899b91;
    --line: rgba(177, 208, 190, .10);
    --red: #ff667d;
    --amber: #ffc477;
    --blue: #74cfff;
}

.stApp {
    color: var(--text);
    background:
        radial-gradient(ellipse at 76% -8%, rgba(0,229,160,.13), transparent 34%),
        radial-gradient(ellipse at 0% 48%, rgba(24,105,76,.10), transparent 36%),
        radial-gradient(ellipse at 100% 88%, rgba(0,229,160,.045), transparent 30%),
        #080b0d;
}
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    opacity: .13;
    background-image: radial-gradient(rgba(180,220,195,.22) .55px, transparent .55px);
    background-size: 5px 5px;
    mask-image: linear-gradient(to bottom, black, transparent 78%);
}
.main .block-container {
    max-width: 1600px;
    padding: 1.65rem 3.1rem 4.5rem;
    position: relative;
    z-index: 1;
}
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: rgba(8,11,13,.55); }
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
h1, h2, h3 { color: var(--text) !important; }
h1 {
    font-size: 2.45rem !important;
    font-weight: 850 !important;
    letter-spacing: -1.7px !important;
}
h2 {
    font-size: 1.5rem !important;
    font-weight: 760 !important;
    letter-spacing: -.7px !important;
}
h3 { font-size: 1.05rem !important; font-weight: 700 !important; }
p { color: #afbeb5; }

/* Sidebar: darker glass rail, soft active navigation */
section[data-testid="stSidebar"] {
    background:
        radial-gradient(ellipse at 18% 0%, rgba(0,229,160,.11), transparent 42%),
        linear-gradient(180deg, #111a16 0%, #0b110e 62%, #090d0b 100%);
    border-right: 1px solid rgba(0,229,160,.12);
}
section[data-testid="stSidebar"] > div { padding-top: 1.35rem; }
section[data-testid="stSidebar"] [data-testid="stRadio"] > label {
    color: #788b80;
    font-size: .66rem;
    font-weight: 850;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    margin: 0 0 12px 5px;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] > div { gap: 7px; }
section[data-testid="stSidebar"] [data-testid="stRadio"] label {
    padding: 12px 14px;
    border-radius: 17px;
    border: 1px solid transparent;
    background: transparent;
    transition: background .2s ease, border-color .2s ease, transform .2s ease;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(0,229,160,.055);
    border-color: rgba(0,229,160,.13);
    transform: translateX(2px);
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background: linear-gradient(110deg, rgba(0,229,160,.17), rgba(0,229,160,.035));
    border-color: rgba(0,229,160,.24);
    box-shadow: inset 3px 0 0 var(--green), 0 8px 24px rgba(0,0,0,.13);
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child { display: none; }
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color: #728579; }
.brand { padding: 17px 12px 22px; }
.brand-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 43px;
    height: 43px;
    border-radius: 15px 15px 15px 5px;
    color: #06150f;
    font-size: 1.45rem;
    font-weight: 900;
    background: linear-gradient(145deg, #8affd1, #00bd86);
    box-shadow: 0 8px 28px rgba(0,229,160,.18);
    margin-bottom: 13px;
}
.brand-name { color: #f3faf5; font-size: 1.65rem; font-weight: 900; letter-spacing: -1.4px; }
.brand-name span { color: var(--green); }
.brand-subtitle { color: #71867a; font-size: .61rem; font-weight: 800; letter-spacing: 2px; margin-top: 6px; }
.brand-accent {
    height: 1px;
    margin: 12px 10px 23px;
    background: linear-gradient(90deg, rgba(0,229,160,.55), rgba(0,229,160,0));
}
.sidebar-status {
    background: linear-gradient(135deg, rgba(0,229,160,.09), rgba(0,229,160,.025));
    border: 1px solid rgba(0,229,160,.17);
    border-radius: 20px 20px 20px 7px;
    padding: 15px;
    margin-top: 10px;
    box-shadow: 0 12px 28px rgba(0,0,0,.12);
}
.sidebar-status-title { color: var(--green); font-size: .69rem; font-weight: 850; letter-spacing: 1px; }
.sidebar-status-sub { color: #7d9285; font-size: .69rem; margin-top: 5px; }

/* Top navigation capsule */
.topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    padding: 11px 17px;
    border: 1px solid rgba(177,208,190,.10);
    border-radius: 100px;
    background: linear-gradient(110deg, rgba(20,30,25,.86), rgba(13,20,16,.72));
    box-shadow: 0 12px 32px rgba(0,0,0,.13), inset 0 1px 0 rgba(255,255,255,.025);
    margin-bottom: 36px;
    backdrop-filter: blur(18px);
}
.topbar-left { color: #a1b4a8; font-size: .67rem; font-weight: 800; letter-spacing: 1.3px; }
.topbar-right { color: var(--green); font-size: .67rem; font-weight: 850; letter-spacing: 1px; }

/* Page title hierarchy */
.eyebrow { color: var(--green); font-size: .67rem; font-weight: 850; letter-spacing: 2.2px; margin-bottom: 11px; }
.hero-title {
    color: #f4faf6;
    font-size: clamp(2.2rem, 4vw, 3.05rem);
    font-weight: 900;
    letter-spacing: -2.3px;
    line-height: 1.04;
    margin-bottom: 12px;
    text-shadow: 0 8px 35px rgba(0,0,0,.18);
}
.hero-description { color: #82968a; font-size: .88rem; line-height: 1.7; margin-bottom: 31px; max-width: 760px; }
.section-heading { color: #eaf4ed; font-size: 1.04rem; font-weight: 820; letter-spacing: -.35px; }
.section-subtitle { color: #7e9185; font-size: .75rem; margin-top: 5px; margin-bottom: 15px; }

/* Floating metric surfaces */
.kpi {
    position: relative;
    isolation: isolate;
    overflow: hidden;
    min-height: 151px;
    padding: 23px 24px 21px;
    border-radius: 27px 27px 27px 9px;
    background:
        radial-gradient(circle at 100% 0%, var(--glow, rgba(0,229,160,.12)), transparent 47%),
        linear-gradient(145deg, rgba(27,40,33,.97), rgba(13,21,17,.98));
    border: 1px solid rgba(177,208,190,.105);
    box-shadow: 0 17px 42px rgba(0,0,0,.20), inset 0 1px 0 rgba(255,255,255,.035);
    transition: transform .25s ease, border-color .25s ease, box-shadow .25s ease;
}
.kpi::after {
    content: "";
    position: absolute;
    z-index: -1;
    width: 125px;
    height: 125px;
    right: -62px;
    bottom: -80px;
    border-radius: 50%;
    border: 1px solid rgba(0,229,160,.11);
    box-shadow: 0 0 0 13px rgba(0,229,160,.018), 0 0 0 27px rgba(0,229,160,.012);
}
.kpi:hover {
    transform: translateY(-4px);
    border-color: rgba(0,229,160,.28);
    box-shadow: 0 22px 45px rgba(0,0,0,.25), 0 0 25px rgba(0,229,160,.045);
}
.kpi-label { color: #8da297; font-size: .66rem; font-weight: 850; letter-spacing: 1.5px; }
.kpi-value { color: #f1f8f3; font-size: 2.25rem; font-weight: 900; letter-spacing: -1.5px; margin-top: 14px; line-height: 1.1; }
.kpi-note { color: #788c80; font-size: .7rem; margin-top: 7px; }

/* Large panels and incident identity */
.soft-panel {
    background:
        radial-gradient(ellipse at 100% 0%, rgba(0,229,160,.055), transparent 38%),
        linear-gradient(145deg, rgba(25,38,30,.92), rgba(13,21,17,.97));
    border: 1px solid rgba(177,208,190,.095);
    border-radius: 27px 27px 27px 9px;
    padding: 23px;
    margin-bottom: 15px;
    box-shadow: 0 16px 38px rgba(0,0,0,.14), inset 0 1px 0 rgba(255,255,255,.025);
}
.identity {
    position: relative;
    overflow: hidden;
    background:
        radial-gradient(circle at 95% 5%, rgba(0,229,160,.18), transparent 37%),
        radial-gradient(circle at 0% 100%, rgba(0,229,160,.055), transparent 40%),
        linear-gradient(135deg, #1a2b22, #101913 76%);
    border: 1px solid rgba(0,229,160,.20);
    border-radius: 30px 30px 30px 10px;
    padding: 28px 30px;
    margin-bottom: 20px;
    box-shadow: 0 20px 48px rgba(0,0,0,.20), inset 0 1px 0 rgba(255,255,255,.035);
}
.identity::after {
    content: "";
    position: absolute;
    width: 230px;
    height: 230px;
    right: -105px;
    top: -145px;
    border-radius: 50%;
    border: 1px solid rgba(0,229,160,.16);
    box-shadow: 0 0 0 18px rgba(0,229,160,.025), 0 0 0 38px rgba(0,229,160,.018);
}
.identity-label { color: var(--green); font-size: .66rem; font-weight: 850; letter-spacing: 1.7px; }
.identity-name { color: #f4faf5; font-size: 2.05rem; font-weight: 900; letter-spacing: -1.5px; margin-top: 8px; }
.identity-details { color: #93a79a; font-size: .76rem; margin-top: 7px; }

/* Status pills */
.pill { display: inline-block; border-radius: 100px; padding: 6px 11px; font-size: .64rem; font-weight: 900; letter-spacing: .8px; }
.green { color: #00e5a0; background: rgba(0,229,160,.10); border: 1px solid rgba(0,229,160,.22); }
.red { color: #ff7287; background: rgba(255,102,125,.10); border: 1px solid rgba(255,102,125,.22); }
.amber { color: #ffc477; background: rgba(255,196,119,.10); border: 1px solid rgba(255,196,119,.22); }
.blue { color: #74cfff; background: rgba(116,207,255,.10); border: 1px solid rgba(116,207,255,.22); }

/* Streamlit-native surfaces harmonised with the theme */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(177,208,190,.10);
    border-radius: 20px;
    overflow: hidden;
    background: rgba(15,23,18,.72);
}
.stSelectbox div[data-baseweb="select"] > div,
.stTextInput input, .stTextArea textarea {
    background: #121c16;
    border: 1px solid #29392f;
    border-radius: 15px;
    color: #eff8f3;
}
.stSelectbox div[data-baseweb="select"] > div:focus-within {
    border-color: var(--green);
    box-shadow: 0 0 0 1px rgba(0,229,160,.15);
}
.stButton button {
    background: linear-gradient(135deg,#00d69a,#009d75);
    border: 1px solid rgba(0,229,160,.4);
    border-radius: 100px;
    color: #04140e !important;
    font-weight: 850;
    padding: .55rem 1.3rem;
    transition: .2s ease;
}
.stButton button:hover { background: #00e5a0; box-shadow: 0 0 22px rgba(0,229,160,.2); transform: translateY(-2px); }
[data-testid="stExpander"] {
    background: linear-gradient(145deg, rgba(18,28,22,.94), rgba(13,20,16,.96));
    border: 1px solid rgba(177,208,190,.095);
    border-radius: 19px 19px 19px 7px;
    overflow: hidden;
}
[data-testid="stAlert"] { border-radius: 17px; }
[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(145deg, rgba(20,31,24,.80), rgba(12,19,15,.84));
    border: 1px solid rgba(177,208,190,.085) !important;
    border-radius: 23px 23px 23px 8px;
    box-shadow: 0 12px 30px rgba(0,0,0,.10);
}
[data-testid="stCodeBlock"] { border: 1px solid rgba(0,229,160,.18); border-radius: 16px; overflow: hidden; }
[data-testid="stFileUploader"] {
    background: linear-gradient(145deg, rgba(17,26,20,.9), rgba(12,19,15,.95));
    border: 1px dashed #42634f;
    border-radius: 22px 22px 22px 8px;
    padding: 14px;
}
hr { border-color: rgba(177,208,190,.09); }
::-webkit-scrollbar { width: 7px; }
::-webkit-scrollbar-track { background: #080b0d; }
::-webkit-scrollbar-thumb { background: #2c4134; border-radius: 100px; }
::-webkit-scrollbar-thumb:hover { background: #00b982; }
::selection { background: rgba(0,229,160,.3); color: white; }

@media (max-width: 900px) {
    .main .block-container { padding: 1.2rem 1.1rem 3rem; }
    .hero-title { font-size: 2.2rem; }
    .topbar { border-radius: 20px; align-items: flex-start; flex-direction: column; }
    .kpi { min-height: 130px; padding: 19px; }
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# UI HELPERS
# ============================================================

def safe(value):
    return html.escape(str(value))


def page_header(eyebrow, title, description):
    st.markdown(
        f"""
        <div class="eyebrow">{safe(eyebrow)}</div>
        <div class="hero-title">{safe(title)}</div>
        <div class="hero-description">{safe(description)}</div>
        """,
        unsafe_allow_html=True
    )


def section_heading(title, subtitle=None):
    st.markdown(
        f"""
        <div style="margin:27px 0 14px;">
            <div class="section-heading">{safe(title)}</div>
            {f'<div class="section-subtitle">{safe(subtitle)}</div>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True
    )


def kpi_card(label, value, note, glow="rgba(0,229,160,.12)"):
    st.markdown(
        f"""
        <div class="kpi" style="--glow:{glow}">
            <div class="kpi-label">{safe(label)}</div>
            <div class="kpi-value">{safe(value)}</div>
            <div class="kpi-note">{safe(note)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def severity_pill(severity):
    severity = str(severity).upper()

    if severity in ("HIGH", "CRITICAL"):
        return f'<span class="pill red">{safe(severity)}</span>'

    if severity == "MEDIUM":
        return f'<span class="pill amber">{safe(severity)}</span>'

    return f'<span class="pill blue">{safe(severity)}</span>'


def verification_pill(status):
    if status == "SUPPORTED":
        return '<span class="pill green">SUPPORTED</span>'

    if status == "PARTIALLY_SUPPORTED":
        return '<span class="pill amber">PARTIALLY SUPPORTED</span>'

    return '<span class="pill red">UNSUPPORTED</span>'


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="brand">
            <div class="brand-icon">◈</div>
            <div class="brand-name">SENTINEL<span>.</span></div>
            <div class="brand-subtitle">SECURITY INTELLIGENCE</div>
        </div>
        <div class="brand-accent"></div>
        """,
        unsafe_allow_html=True
    )

    page = st.radio(
        "WORKSPACE",
        ["Overview", "Investigate", "Evidence Vault"]
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="brand-accent"></div>
        <div class="brand-subtitle">ENVIRONMENT</div>
        <div class="sidebar-status">
            <div class="sidebar-status-title">
                ● DASHBOARD ONLINE
            </div>
            <div class="sidebar-status-sub">
                Local demonstration environment
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.caption(f"ALERTS  /  {len(alerts)}")
    st.caption(f"EVIDENCE  /  {len(evidence_records)}")
    st.caption(f"LLM REPORTS  /  {len(llm_data)}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("SENTINEL · PROTOTYPE")


# ============================================================
# TOP BAR
# ============================================================

st.markdown(
    """
    <div class="topbar">
        <div class="topbar-left">
            SENTINEL / SECURITY INTELLIGENCE PLATFORM
        </div>
        <div class="topbar-right">
            ● LOCAL DEMO ENVIRONMENT
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# OVERVIEW
# ============================================================

if page == "Overview":

    page_header(
        "COMMAND OVERVIEW / 01",
        "Security, in focus.",
        "A consolidated view of detected incidents, investigation coverage and evidence integrity."
    )

    total_alerts = len(alerts)

    high_severity = sum(
        1 for alert in alerts
        if alert.get("severity") in ("HIGH", "CRITICAL")
    )

    investigated = len(verification_data)

    all_claims = [
        claim
        for item in verification_data
        for claim in item.get("verified_claims", [])
    ]

    supported = sum(
        1 for claim in all_claims
        if claim.get("status") == "SUPPORTED"
    )

    supported_pct = (
        supported / len(all_claims) * 100
        if all_claims else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi_card(
            "TOTAL ALERTS",
            total_alerts,
            "Detected incidents",
            "rgba(116,207,255,.12)"
        )

    with c2:
        kpi_card(
            "HIGH / CRITICAL",
            high_severity,
            "Require analyst attention",
            "rgba(255,102,125,.12)"
        )

    with c3:
        kpi_card(
            "INVESTIGATED",
            investigated,
            "Verification records",
            "rgba(0,229,160,.12)"
        )

    with c4:
        kpi_card(
            "SUPPORTED CLAIMS",
            f"{supported_pct:.1f}%",
            f"{supported} of {len(all_claims)} claims",
            "rgba(255,196,119,.12)"
        )

    section_heading(
        "Incident intelligence",
        "Security alerts currently available for investigation."
    )

    if alerts:

        for index, alert in enumerate(alerts, start=1):

            username = alert.get("username", "Unknown")
            alert_type = alert.get("alert_type", "Unknown")
            severity = alert.get("severity", "UNKNOWN")
            source_ip = alert.get("source_ip", "Unknown")
            attempts = alert.get("failed_attempts", 0)

            has_llm = username in llm_by_user

            with st.container(border=True):

                col1, col2, col3 = st.columns([3, 2, 1])

                with col1:
                    st.markdown(
                        f"**INC-{index:03d} · {safe(username)}**"
                    )
                    st.caption(alert_type)

                with col2:
                    st.markdown(
                        severity_pill(severity),
                        unsafe_allow_html=True
                    )
                    st.caption(
                        f"{attempts} failed attempts · {safe(source_ip)}"
                    )

                with col3:
                    if has_llm:
                        st.markdown(
                            '<span class="pill green">ANALYSED</span>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            '<span class="pill amber">PENDING</span>',
                            unsafe_allow_html=True
                        )

    else:
        st.info("No security alerts available.")

    section_heading(
        "Analysis coverage",
        "Current state of generated reports and independent verification."
    )

    a, b = st.columns(2)

    with a:
        kpi_card(
            "LLM REPORTS",
            len(llm_data),
            f"Out of {total_alerts} alerts",
            "rgba(0,229,160,.12)"
        )

    with b:
        kpi_card(
            "VERIFIED CLAIMS",
            len(all_claims),
            "Independent Python verification",
            "rgba(116,207,255,.12)"
        )

    st.caption(
        "The current verification module checks predefined claims. "
        "It does not automatically verify every sentence generated by Gemini."
    )


# ============================================================
# INVESTIGATE
# ============================================================

elif page == "Investigate":

    page_header(
        "THREAT INVESTIGATION / 02",
        "Understand the incident.",
        "Inspect original events, AI-generated findings and independent evidence verification."
    )

    if not alerts:

        st.warning("No alerts found. Run the ingestion pipeline first.")

    else:

        selected_alert = st.selectbox(
            "SELECT INCIDENT",
            alerts,
            format_func=lambda alert: (
                f"{alert['username']} · "
                f"{alert['alert_type']} · "
                f"{alert['severity']}"
            )
        )

        username = selected_alert["username"]
        alert_type = selected_alert.get("alert_type", "Unknown")
        severity = selected_alert.get("severity", "UNKNOWN")
        source_ip = selected_alert.get("source_ip", "Unknown")
        attempts = selected_alert.get("failed_attempts", 0)

        st.markdown(
            f"""
            <div class="identity">
                <div class="identity-label">ACTIVE INVESTIGATION</div>
                <div class="identity-name">{safe(username)}</div>
                <div class="identity-details">
                    {safe(alert_type)} &nbsp; · &nbsp;
                    {attempts} failed login attempts &nbsp; · &nbsp;
                    {safe(source_ip)}
                </div>
                <div style="margin-top:15px;">
                    {severity_pill(severity)}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # INCIDENT METRICS

        a, b, c = st.columns(3)

        with a:
            kpi_card(
                "ACCOUNT",
                username,
                "Observed username"
            )

        with b:
            kpi_card(
                "FAILED LOGINS",
                attempts,
                "Recorded attempts",
                "rgba(255,102,125,.12)"
            )

        with c:
            kpi_card(
                "LINKED EVENTS",
                len(selected_alert.get("evidence_ids", [])),
                "Evidence references",
                "rgba(116,207,255,.12)"
            )

        # LLM

        section_heading(
            "AI intelligence",
            "Gemini-generated incident assessment."
        )

        llm_result = llm_by_user.get(username)

        if llm_result:

            st.markdown(
                '<span class="pill green">ANALYSIS AVAILABLE</span>',
                unsafe_allow_html=True
            )

            analysis = llm_result.get("analysis", "")

            with st.container(border=True):

                if analysis:
                    st.markdown(analysis)
                else:
                    st.warning("Analysis file is empty.")

            llm_ids = llm_result.get("evidence_ids", [])

            st.caption("Evidence supplied to the model")

            if llm_ids:
                st.code(" · ".join(llm_ids), language="text")
            else:
                st.warning("No evidence IDs recorded.")

        else:

            st.markdown(
                '<span class="pill amber">ANALYSIS PENDING</span>',
                unsafe_allow_html=True
            )

            st.info(
                "No LLM analysis has been saved for this incident. "
                "The remaining investigation sections are available."
            )

        # EVIDENCE

        section_heading(
            "Evidence trail",
            "Original records linked to this incident."
        )

        required_ids = selected_alert.get("evidence_ids", [])

        matching_evidence = [
            evidence_by_id[event_id]
            for event_id in required_ids
            if event_id in evidence_by_id
        ]

        if matching_evidence:

            for record in matching_evidence:

                with st.container(border=True):

                    left, right = st.columns([1, 5])

                    with left:
                        st.markdown(
                            f"**{safe(record.get('event_id', 'EVT'))}**"
                        )
                        st.caption(
                            str(record.get("timestamp", ""))
                        )

                    with right:
                        st.markdown(
                            f"**{safe(record.get('event_type', 'Unknown'))}**"
                        )
                        st.caption(
                            safe(record.get("raw_line", ""))
                        )

            with st.expander("Open evidence table"):
                st.dataframe(
                    matching_evidence,
                    use_container_width=True,
                    hide_index=True
                )

        else:
            st.warning("No matching evidence found.")

        # VERIFICATION

        section_heading(
            "Claim verification",
            "Independent rule-based checks against original evidence."
        )

        claims = verification_by_user.get(username, [])

        if claims:

            supported_count = sum(
                1 for claim in claims
                if claim.get("status") == "SUPPORTED"
            )

            partial_count = sum(
                1 for claim in claims
                if claim.get("status") == "PARTIALLY_SUPPORTED"
            )

            unsupported_count = sum(
                1 for claim in claims
                if claim.get("status") == "UNSUPPORTED"
            )

            x, y, z = st.columns(3)

            with x:
                kpi_card(
                    "SUPPORTED",
                    supported_count,
                    "Evidence matches"
                )

            with y:
                kpi_card(
                    "PARTIAL",
                    partial_count,
                    "Incomplete evidence",
                    "rgba(255,196,119,.12)"
                )

            with z:
                kpi_card(
                    "UNSUPPORTED",
                    unsupported_count,
                    "Not established",
                    "rgba(255,102,125,.12)"
                )

            for index, claim in enumerate(claims, start=1):

                with st.container(border=True):

                    st.caption(f"CLAIM {index:02d}")

                    st.write(
                        claim.get("claim", "Claim unavailable")
                    )

                    st.markdown(
                        verification_pill(
                            claim.get("status", "UNSUPPORTED")
                        ),
                        unsafe_allow_html=True
                    )

                    ids = claim.get("evidence_ids", [])

                    st.caption(
                        "Evidence references: "
                        + (
                            ", ".join(ids)
                            if ids else "No supporting evidence"
                        )
                    )

        else:

            st.warning(
                "Verification results unavailable. "
                "Run python -m verification.checker."
            )

        # RESPONSE GUIDANCE

        section_heading(
            "Analyst guidance",
            "Advisory response actions. Nothing is automatically executed."
        )

        actions = [
            "Review subsequent authentication activity.",
            "Confirm whether the source IP is expected.",
            "Review access to sensitive resources.",
            "Escalate findings to a security analyst."
        ]

        for index, action in enumerate(actions, start=1):
            st.markdown(f"**{index:02d}** · {action}")

        st.caption(
            "The IP addresses in this synthetic demonstration are "
            "reserved documentation addresses, not confirmed real attackers."
        )

    # UPLOAD

    section_heading(
        "Evidence intake",
        "File selection is available; automatic processing is not connected."
    )

    uploaded_file = st.file_uploader(
        "Choose a security log",
        type=["txt", "log", "csv", "json"]
    )

    if uploaded_file:
        st.success(f"Selected: {uploaded_file.name}")
        st.info(
            "Automatic ingestion of uploaded files has not yet been implemented."
        )


# ============================================================
# EVIDENCE VAULT
# ============================================================

elif page == "Evidence Vault":

    page_header(
        "FORENSIC REPOSITORY / 03",
        "Evidence, preserved.",
        "Inspect original records, integrity fingerprints and verification history."
    )

    if evidence_data:

        source_file = evidence_data.get("source_file", "Unknown")
        sha256 = evidence_data.get("sha256", "Unavailable")

        a, b = st.columns([1, 2])

        with a:
            kpi_card(
                "STORED RECORDS",
                len(evidence_records),
                "Original parsed events",
                "rgba(116,207,255,.12)"
            )

        with b:
            st.markdown(
                f"""
                <div class="soft-panel">
                    <div class="kpi-label">SOURCE FILE</div>
                    <div style="
                        color:#f1f8f3;
                        font-size:1.1rem;
                        font-weight:800;
                        margin-top:12px;
                    ">
                        {safe(source_file)}
                    </div>
                    <div class="kpi-note">
                        Evidence repository source
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        section_heading(
            "Integrity fingerprint",
            "SHA-256 hash stored for the source evidence file."
        )

        st.code(sha256, language="text")

        st.caption(
            "SHA-256 helps detect changes to the hashed file. "
            "It does not independently prove provenance, collection time "
            "or chain of custody."
        )

        section_heading(
            "Original evidence",
            "Stored records and their event identifiers."
        )

        if evidence_records:
            st.dataframe(
                evidence_records,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No evidence records found.")

    else:

        st.warning(
            "Evidence store not found. "
            "Run python -m ingestion.evidence."
        )

    # VERIFICATION HISTORY

    section_heading(
        "Verification history",
        "Previously recorded claim assessments."
    )

    if verification_data:

        for item in verification_data:

            alert = item.get("alert", {})
            username = alert.get("username", "Unknown")
            alert_type = alert.get("alert_type", "Unknown")

            with st.expander(f"{username} · {alert_type}"):

                for claim in item.get("verified_claims", []):

                    st.write(
                        claim.get("claim", "Claim unavailable")
                    )

                    st.markdown(
                        verification_pill(
                            claim.get("status", "UNSUPPORTED")
                        ),
                        unsafe_allow_html=True
                    )

                    ids = claim.get("evidence_ids", [])

                    st.caption(
                        "Evidence: "
                        + (
                            ", ".join(ids)
                            if ids else "None"
                        )
                    )

    else:

        st.info("No verification history available.")

    # LLM ARCHIVE

    section_heading(
        "AI assessment archive",
        "Generated incident reports and their recorded evidence references."
    )

    if llm_data:

        for item in llm_data:

            username = item.get("username", "Unknown")

            with st.expander(f"Assessment · {username}"):

                st.markdown(
                    item.get("analysis", "Analysis unavailable")
                )

                ids = item.get("evidence_ids", [])

                st.caption(
                    "Evidence IDs: "
                    + (
                        ", ".join(ids)
                        if ids else "None recorded"
                    )
                )

    else:

        st.info("No AI-generated reports have been saved yet.")


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div style="
        margin-top:48px;
        padding-top:18px;
        border-top:1px solid rgba(177,208,190,.09);
        color:#64776b;
        font-size:.65rem;
        font-weight:750;
        letter-spacing:1.5px;
        text-align:center;
    ">
        SENTINEL SECURITY INTELLIGENCE
        &nbsp; · &nbsp;
        INCIDENT RESPONSE PROTOTYPE
    </div>
    """,
    unsafe_allow_html=True
)
