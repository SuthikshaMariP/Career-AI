import streamlit as st
import PyPDF2
import pandas as pd
import re
import ollama


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="CareerAI",
    page_icon="🎓",
    layout="wide"
)


# =========================================================
# OLLAMA
# =========================================================

# If an Ollama API key is available in Streamlit Secrets, use
# Ollama Cloud. Otherwise, keep using the local Ollama server.
try:
    OLLAMA_API_KEY = st.secrets.get("OLLAMA_API_KEY", "")
except Exception:
    OLLAMA_API_KEY = ""

if OLLAMA_API_KEY:
    OLLAMA_MODEL = "gpt-oss:20b-cloud"
    ollama_client = ollama.Client(
        host="https://ollama.com",
        headers={"Authorization": f"Bearer {OLLAMA_API_KEY}"}
    )
else:
    OLLAMA_MODEL = "llama3.2:3b"
    ollama_client = ollama.Client(host="http://localhost:11434")


# =========================================================
# PREMIUM UI / UX THEME
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root{
  --bg:#f5f7fb; --surface:#ffffff; --surface2:#f8fafc; --ink:#0f172a; --muted:#64748b;
  --line:#e2e8f0; --blue:#4f46e5; --blue2:#2563eb; --cyan:#06b6d4; --purple:#7c3aed;
}
*{box-sizing:border-box}
.stApp{background:var(--bg);font-family:'Inter',sans-serif;color:var(--ink)}
[data-testid="stAppViewContainer"]{background:radial-gradient(circle at 85% 0%,rgba(99,102,241,.08),transparent 25%),linear-gradient(180deg,#f8faff 0%,#f4f7fb 100%)}
.block-container{max-width:1500px;padding:1.8rem 2.4rem 4rem}
#MainMenu,footer,header{visibility:hidden}
h1{font-weight:800!important;letter-spacing:-1.7px!important;color:#0b1220!important}
h2,h3{font-weight:750!important;letter-spacing:-.55px!important;color:#111827!important}
p,label{color:#475569}

/* SIDEBAR */
[data-testid="stSidebar"]{background:linear-gradient(180deg,#f7f9ff 0%,#eef4ff 55%,#f7fbff 100%);border-right:1px solid #dfe7f5;box-shadow:8px 0 28px rgba(71,85,105,.05)}
[data-testid="stSidebar"] *{font-family:'Inter',sans-serif}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p{color:#64748b}
[data-testid="stSidebar"] .stRadio>label{display:none}
[data-testid="stSidebar"] .stRadio [role="radiogroup"]{gap:.28rem}
[data-testid="stSidebar"] .stRadio [role="radiogroup"] label{border-radius:13px;padding:.72rem .82rem;margin:0;color:#64748b!important;border:1px solid transparent;transition:.18s ease}
[data-testid="stSidebar"] .stRadio [role="radiogroup"] label:hover{background:#eef2ff;color:#4338ca!important;border-color:#dbe3ff;transform:translateX(2px)}
[data-testid="stSidebar"] .stRadio [role="radiogroup"] label:has(input:checked){background:linear-gradient(90deg,#eef2ff,#f0f9ff);color:#3730a3!important;border-color:#cfd8ff;box-shadow:inset 3px 0 0 #6366f1}
[data-testid="stSidebar"] .stRadio [role="radiogroup"] label p{color:inherit!important;font-weight:600}
[data-testid="stSidebar"] .stButton button{width:100%;background:#fff!important;color:#334155!important;border:1px solid #dbe4f2!important;border-radius:12px!important}

/* CONTROLS */
.stButton>button,.stLinkButton>a{border-radius:12px!important;font-weight:700!important;min-height:45px;border:1px solid #d9e2ef!important;transition:.2s ease;box-shadow:0 3px 8px rgba(15,23,42,.03)}
.stButton>button:hover,.stLinkButton>a:hover{transform:translateY(-2px);box-shadow:0 12px 25px rgba(37,99,235,.14)}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,#4f46e5,#2563eb)!important;color:#fff!important;border:0!important;box-shadow:0 10px 25px rgba(79,70,229,.25)!important}
.stTextInput input,.stTextArea textarea,.stSelectbox div[data-baseweb="select"]>div,.stMultiSelect div[data-baseweb="select"]>div{border-radius:12px!important;border-color:#d8e1ee!important;background:#fff!important;min-height:45px}
[data-testid="stFileUploader"]{background:#fff;border:1.5px dashed #b7c4d8;border-radius:18px;padding:.65rem;box-shadow:0 8px 22px rgba(15,23,42,.035)}
[data-testid="stMetric"]{background:rgba(255,255,255,.9);border:1px solid #e3e8f1;border-radius:20px;padding:1.2rem 1.25rem;box-shadow:0 12px 30px rgba(15,23,42,.055);min-height:126px}
[data-testid="stMetricLabel"]{color:#64748b!important;font-weight:650!important}
[data-testid="stMetricValue"]{color:#0f172a!important;font-weight:800!important;letter-spacing:-1px}
[data-testid="stAlert"]{border-radius:14px;border:1px solid #e1e8f2}
details[data-testid="stExpander"]{background:#fff;border:1px solid #e3e8f1;border-radius:16px;margin-bottom:.7rem;box-shadow:0 7px 20px rgba(15,23,42,.035)}
.stProgress>div>div>div>div{border-radius:999px}

/* PREMIUM COMPONENTS */
.cai-hero{position:relative;overflow:hidden;background:linear-gradient(135deg,#ffffff 0%,#f3f7ff 55%,#eef9ff 100%);color:#172033;border-radius:30px;padding:2.35rem 2.6rem;margin-bottom:1.5rem;box-shadow:0 20px 55px rgba(71,85,105,.10);border:1px solid #dfe7f5;min-height:245px}
.cai-hero:before{content:'';position:absolute;width:430px;height:430px;border-radius:50%;right:-145px;top:-220px;background:radial-gradient(circle,rgba(129,140,248,.18),rgba(99,102,241,0) 67%);pointer-events:none}
.cai-hero:after{content:'';position:absolute;width:260px;height:260px;border-radius:50%;right:20%;bottom:-190px;background:rgba(14,165,233,.08);filter:blur(5px);pointer-events:none}
.cai-hero h1,.cai-hero h2,.cai-hero h3,.cai-hero p{color:#172033!important;position:relative;z-index:1}
.cai-hero h1{font-size:clamp(2rem,4vw,3.25rem)!important;line-height:1.05!important;max-width:760px}
.cai-hero p{color:#64748b!important}
.cai-eyebrow{color:#6366f1!important;font-size:.69rem;font-weight:800;letter-spacing:1.8px;text-transform:uppercase;margin-bottom:.55rem}
/* animated study / motivation scene */
.study-scene{position:absolute;right:35px;top:28px;width:310px;height:190px;z-index:2;pointer-events:none}
.study-glow{position:absolute;right:0;top:0;width:185px;height:185px;border-radius:50%;background:radial-gradient(circle,rgba(129,140,248,.20),rgba(186,230,253,0) 68%);animation:glowPulse 4s ease-in-out infinite}
.study-desk{position:absolute;right:5px;bottom:22px;width:245px;height:12px;border-radius:10px;background:#cbd5e1;box-shadow:0 10px 20px rgba(71,85,105,.10)}
.study-laptop{position:absolute;right:58px;bottom:35px;width:125px;height:78px;border:7px solid #334155;border-bottom-width:9px;border-radius:10px 10px 4px 4px;background:linear-gradient(135deg,#eef2ff,#dbeafe);transform:perspective(200px) rotateX(-3deg);box-shadow:0 10px 18px rgba(51,65,85,.12)}
.study-laptop:after{content:'';position:absolute;left:-16px;bottom:-17px;width:155px;height:12px;border-radius:0 0 14px 14px;background:#64748b}
.study-screen{position:absolute;inset:10px;border-radius:3px;background:linear-gradient(180deg,#ffffff,#eef2ff);overflow:hidden}
.study-line{height:5px;border-radius:5px;background:#a5b4fc;margin:10px 9px 0;animation:typing 2.8s ease-in-out infinite}
.study-line:nth-child(2){width:68%;background:#bae6fd;animation-delay:.35s}.study-line:nth-child(3){width:48%;background:#c4b5fd;animation-delay:.7s}
.study-book{position:absolute;left:32px;bottom:37px;width:68px;height:44px;border-radius:5px 8px 8px 5px;background:#e0e7ff;box-shadow:inset 34px 0 #c7d2fe,0 8px 16px rgba(71,85,105,.12);transform:rotate(-7deg);animation:bookFloat 3.5s ease-in-out infinite}
.study-pencil{position:absolute;left:88px;bottom:51px;width:72px;height:7px;border-radius:8px;background:#fbbf24;transform:rotate(-22deg);animation:pencilFloat 3s ease-in-out infinite}
.study-plant{position:absolute;right:12px;bottom:35px;width:45px;height:52px}.study-pot{position:absolute;bottom:0;left:8px;width:30px;height:23px;background:#bfdbfe;border-radius:4px 4px 12px 12px}.leaf{position:absolute;width:24px;height:35px;background:#86efac;border-radius:24px 2px 24px 2px;transform-origin:bottom center;animation:leafSway 3s ease-in-out infinite}.leaf.one{left:7px;top:1px;transform:rotate(-28deg)}.leaf.two{left:18px;top:0;transform:rotate(25deg);animation-delay:.5s}.leaf.three{left:14px;top:-8px;transform:rotate(2deg);animation-delay:1s}
.study-star{position:absolute;color:#f59e0b;font-size:20px;animation:twinkle 2.2s ease-in-out infinite}.study-star.s1{right:55px;top:22px}.study-star.s2{right:205px;top:35px;font-size:13px;animation-delay:.7s}.study-star.s3{right:172px;bottom:28px;font-size:11px;animation-delay:1.2s}
@keyframes glowPulse{50%{transform:scale(1.08);opacity:.72}}@keyframes typing{0%,100%{opacity:.45;transform:scaleX(.72);transform-origin:left}50%{opacity:1;transform:scaleX(1)}}@keyframes bookFloat{50%{transform:rotate(-5deg) translateY(-5px)}}@keyframes pencilFloat{50%{transform:rotate(-17deg) translateY(-4px)}}@keyframes leafSway{50%{rotate:4deg;translate:2px 0}}@keyframes twinkle{0%,100%{opacity:.35;transform:scale(.8) rotate(0)}50%{opacity:1;transform:scale(1.15) rotate(18deg)}}
.cai-card{background:rgba(255,255,255,.97);border:1px solid #e3e8f1;border-radius:20px;padding:1.35rem;box-shadow:0 12px 32px rgba(15,23,42,.055);height:100%;transition:.2s ease}
.cai-card:hover{transform:translateY(-2px);box-shadow:0 17px 38px rgba(15,23,42,.075)}
.cai-card-title{color:#111827;font-size:1rem;font-weight:800;margin-bottom:.28rem}
.cai-muted{color:#64748b;font-size:.88rem}
.cai-pill{display:inline-block;padding:.38rem .72rem;border-radius:999px;background:#eef2ff;color:#4338ca;font-size:.73rem;font-weight:750;margin:.16rem .12rem}
.cai-section{margin-top:1.7rem;margin-bottom:.7rem}
.cai-section h3{margin-bottom:.12rem}
.cai-pagehead{display:flex;align-items:center;justify-content:space-between;gap:1rem;margin:0 0 1.35rem;padding-bottom:1rem;border-bottom:1px solid #e5eaf3}
.cai-pagehead .title{font-size:1.9rem;font-weight:800;color:#0f172a;letter-spacing:-1.1px}
.cai-pagehead .desc{color:#64748b;margin-top:.22rem;font-size:.91rem}
.cai-kpi{background:#fff;border:1px solid #e3e8f1;border-radius:18px;padding:1.15rem;box-shadow:0 9px 26px rgba(15,23,42,.045)}
.cai-kpi .label{color:#64748b;font-size:.73rem;font-weight:750;text-transform:uppercase;letter-spacing:.65px}
.cai-kpi .value{color:#0f172a;font-size:1.9rem;font-weight:800;margin-top:.25rem;letter-spacing:-1px}
.cai-kpi .hint{color:#94a3b8;font-size:.76rem;margin-top:.15rem}
.cai-step{background:linear-gradient(180deg,#fff,#fbfcfe);border:1px solid #e5eaf2;border-radius:15px;padding:1rem 1.1rem;margin-bottom:.65rem;box-shadow:0 5px 16px rgba(15,23,42,.025)}
.cai-step strong{color:#111827}
.cai-login{background:rgba(255,255,255,.98);border:1px solid #e2e8f0;border-radius:24px;padding:1.55rem;box-shadow:0 24px 60px rgba(15,23,42,.10)}
.cai-feature{display:flex;gap:.85rem;align-items:flex-start;padding:.78rem 0;border-bottom:1px solid #edf1f6}
.cai-feature:last-child{border-bottom:0}
.cai-feature-icon{width:38px;height:38px;border-radius:12px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#eef2ff,#e0f2fe);font-size:1rem;flex:0 0 auto}
.cai-feature b{color:#172033;font-size:.92rem}
.cai-feature span{display:block;color:#64748b;font-size:.78rem;margin-top:.12rem}
@media(max-width:900px){.block-container{padding:1rem}.cai-hero{padding:1.7rem;border-radius:22px}.study-scene{opacity:.35;right:-45px;transform:scale(.8);transform-origin:right top}.cai-pagehead{display:block}.cai-hero h1{font-size:2rem!important}}
</style>
""", unsafe_allow_html=True)

# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "email" not in st.session_state:
    st.session_state.email = ""

if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

if "found_skills" not in st.session_state:
    st.session_state.found_skills = []

if "found_degrees" not in st.session_state:
    st.session_state.found_degrees = []

if "ai_resume_context" not in st.session_state:
    st.session_state.ai_resume_context = ""

if "resume_score" not in st.session_state:
    st.session_state.resume_score = 0

if "ai_resume_analysis" not in st.session_state:
    st.session_state.ai_resume_analysis = ""

if "career_roadmap" not in st.session_state:
    st.session_state.career_roadmap = ""


# =========================================================
# CSE / IT SKILLS DATABASE
# =========================================================

SKILLS = [

    # ---------------- PROGRAMMING LANGUAGES ----------------

    "C",
    "C++",
    "C#",
    "Java",
    "Python",
    "JavaScript",
    "TypeScript",
    "PHP",
    "Ruby",
    "Go",
    "Rust",
    "Kotlin",
    "Swift",
    "Dart",
    "R",
    "MATLAB",
    "Scala",
    "Perl",
    "Lua",
    "Objective-C",
    "Groovy",

    # ---------------- WEB ----------------

    "HTML",
    "CSS",
    "Bootstrap",
    "Tailwind CSS",
    "React",
    "Angular",
    "Vue",
    "Next.js",
    "Node.js",
    "Express.js",
    "REST API",
    "GraphQL",
    "Web Development",
    "Frontend Development",
    "Backend Development",
    "Full Stack Development",

    # ---------------- PYTHON ----------------

    "Django",
    "Flask",
    "FastAPI",
    "Pandas",
    "NumPy",
    "Matplotlib",
    "Seaborn",
    "Scikit-learn",

    # ---------------- JAVA ----------------

    "Spring",
    "Spring Boot",
    "Hibernate",
    "JDBC",
    "Maven",
    "Gradle",

    # ---------------- DATABASE ----------------

    "SQL",
    "MySQL",
    "PostgreSQL",
    "Oracle",
    "SQLite",
    "MongoDB",
    "Redis",
    "Firebase",
    "NoSQL",
    "Database Management",

    # ---------------- DATA STRUCTURES ----------------

    "Data Structures",
    "Algorithms",
    "Arrays",
    "Linked List",
    "Stack",
    "Queue",
    "Trees",
    "Binary Tree",
    "Binary Search Tree",
    "Graphs",
    "Hashing",
    "Searching",
    "Sorting",
    "Recursion",
    "Dynamic Programming",
    "Time Complexity",
    "Space Complexity",

    # ---------------- COMPUTER SCIENCE ----------------

    "Object Oriented Programming",
    "OOP",
    "Operating Systems",
    "DBMS",
    "Computer Networks",
    "Computer Architecture",
    "Software Engineering",
    "Compiler Design",
    "Distributed Systems",
    "System Design",

    # ---------------- AI / ML ----------------

    "Artificial Intelligence",
    "AI",
    "Machine Learning",
    "Deep Learning",
    "Natural Language Processing",
    "NLP",
    "Computer Vision",
    "Generative AI",
    "Large Language Models",
    "LLM",
    "Neural Networks",
    "TensorFlow",
    "PyTorch",
    "Keras",
    "OpenCV",
    "Hugging Face",
    "LangChain",

    # ---------------- DATA ----------------

    "Data Analysis",
    "Data Analytics",
    "Data Science",
    "Data Engineering",
    "Statistics",
    "Data Visualization",
    "Power BI",
    "Tableau",
    "Excel",
    "ETL",

    # ---------------- CLOUD ----------------

    "AWS",
    "Microsoft Azure",
    "Azure",
    "Google Cloud",
    "GCP",
    "Cloud Computing",
    "EC2",
    "S3",
    "Lambda",

    # ---------------- DEVOPS ----------------

    "Docker",
    "Kubernetes",
    "Git",
    "GitHub",
    "GitLab",
    "Bitbucket",
    "Jenkins",
    "CI/CD",
    "DevOps",
    "Linux",
    "Bash",
    "Shell Scripting",

    # ---------------- CYBERSECURITY ----------------

    "Cybersecurity",
    "Network Security",
    "Ethical Hacking",
    "Cryptography",
    "Web Security",
    "OWASP",
    "Penetration Testing",
    "Security Testing",
    "Authentication",
    "Authorization",

    # ---------------- MOBILE ----------------

    "Android",
    "Android Development",
    "Flutter",
    "React Native",
    "iOS Development",

    # ---------------- TESTING ----------------

    "Software Testing",
    "Manual Testing",
    "Automation Testing",
    "Selenium",
    "JUnit",
    "PyTest",
    "Quality Assurance",
    "QA",

    # ---------------- APIs / TOOLS ----------------

    "API",
    "REST",
    "JSON",
    "XML",
    "Postman",

    # ---------------- SOFT SKILLS ----------------

    "Communication",
    "Problem Solving",
    "Leadership",
    "Teamwork",
    "Time Management",
    "Critical Thinking"
]


# =========================================================
# CSE / IT DEGREES
# =========================================================

DEGREES = [

    "B.E",
    "B.Tech",
    "BCA",
    "B.Sc",
    "BSc",
    "M.E",
    "M.Tech",
    "MCA",
    "M.Sc",
    "MSc",

    "Computer Science",
    "Computer Science and Engineering",
    "CSE",

    "Information Technology",
    "Information Science",

    "Artificial Intelligence",
    "AI",
    "Artificial Intelligence and Machine Learning",
    "AI and ML",
    "AI & ML",

    "Data Science",
    "Data Analytics",

    "Cyber Security",
    "Cybersecurity",

    "Cloud Computing",

    "Software Engineering",

    "Information Systems",

    "Computer Applications",

    "Computer Engineering",

    "Information and Communication Technology",

    "Internet of Things",
    "IoT",

    "Machine Learning"
]


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def find_skills(text):

    found = []

    for skill in SKILLS:

        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(
            pattern,
            text,
            re.IGNORECASE
        ):

            found.append(skill)

    return found


def find_degrees(text):

    found = []

    for degree in DEGREES:

        pattern = r"(?<!\w)" + re.escape(degree) + r"(?!\w)"

        if re.search(
            pattern,
            text,
            re.IGNORECASE
        ):

            found.append(degree)

    return found


def extract_section(text, section_names):

    lines = text.splitlines()

    collected = []

    collecting = False

    for line in lines:

        clean_line = line.strip()

        lower_line = clean_line.lower()

        if any(
            section.lower() in lower_line
            for section in section_names
        ):

            collecting = True
            continue

        if collecting:

            if clean_line:

                if (
                    clean_line.isupper()
                    and len(clean_line) < 60
                ):
                    break

                collected.append(clean_line)

            if len(collected) >= 12:
                break

    return "\n".join(collected)


def build_ai_resume_context(text, skills, degrees):

    education = extract_section(
        text,
        [
            "education",
            "academic qualification",
            "educational qualification"
        ]
    )

    projects = extract_section(
        text,
        [
            "projects",
            "academic projects",
            "project"
        ]
    )

    experience = extract_section(
        text,
        [
            "experience",
            "work experience",
            "internship",
            "internships"
        ]
    )

    certifications = extract_section(
        text,
        [
            "certifications",
            "certification",
            "courses"
        ]
    )

    # Limit the amount of text sent to Ollama.
    education = education[:1200]
    projects = projects[:1600]
    experience = experience[:1400]
    certifications = certifications[:1000]

    context = f"""
CSE / IT STUDENT PROFILE

Detected Technical Skills:
{", ".join(skills) if skills else "None detected"}

Detected CSE / IT Education:
{", ".join(degrees) if degrees else "Not detected"}

Education Details:
{education if education else "Not available"}

Projects:
{projects if projects else "Not available"}

Experience / Internships:
{experience if experience else "Not available"}

Certifications / Courses:
{certifications if certifications else "Not available"}
"""

    return context[:7000]


# =========================================================
# LOGIN PAGE
# =========================================================

if not st.session_state.logged_in:

    st.markdown("""
    <div class="cai-hero">
        <div class="cai-eyebrow">AI CAREER INTELLIGENCE PLATFORM</div>
        <h1>Build your career with clarity.</h1>
        <div class="study-scene"><div class="study-glow"></div><div class="study-star s1">✦</div><div class="study-star s2">✦</div><div class="study-star s3">✦</div><div class="study-desk"></div><div class="study-book"></div><div class="study-pencil"></div><div class="study-laptop"><div class="study-screen"><div class="study-line"></div><div class="study-line"></div><div class="study-line"></div></div></div><div class="study-plant"><div class="leaf one"></div><div class="leaf two"></div><div class="leaf three"></div><div class="study-pot"></div></div></div>
            <p style="font-size:1.05rem;max-width:700px;">
            CareerAI analyzes your resume, discovers skill gaps, recommends internships,
            and creates a personalized learning roadmap for your next career step.
        </p>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([1.35, 0.85], gap="large")

    with left:
        st.markdown("""
        <div class="cai-card">
            <div class="cai-eyebrow" style="color:#4f46e5 !important;">WHAT YOU GET</div>
            <h2>One workspace for your career journey</h2>
            <p class="cai-muted">From resume analysis to internship discovery, everything is organized in one simple dashboard.</p>
            <div style="margin-top:1rem;">
                <span class="cai-pill">Resume Intelligence</span>
                <span class="cai-pill">AI Recommendations</span>
                <span class="cai-pill">Skill Gap Analysis</span>
                <span class="cai-pill">Career Roadmap</span>
                <span class="cai-pill">Career Impact</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown("""
        <div class="cai-card">
            <div class="cai-eyebrow" style="color:#4f46e5 !important;">GET STARTED</div>
            <h2>Welcome back</h2>
            <p class="cai-muted">Sign in to continue your CareerAI journey.</p>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("Sign in")

        email = st.text_input("Email")

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button(
            "Login",
            key="login_button"
        ):

            if (
                "@" in email
                and "." in email
                and len(password) >= 4
            ):

                st.session_state.logged_in = True
                st.session_state.email = email

                st.rerun()

            else:

                st.error(
                    "Please enter a valid email and password."
                )


# =========================================================
# MAIN APPLICATION
# =========================================================

else:

    # =====================================================
    # SIDEBAR
    # =====================================================

    st.sidebar.markdown("""
    <div style="padding:.7rem .35rem 1.2rem;">
        <div style="font-size:1.5rem;font-weight:850;letter-spacing:-.5px;">🎓 CareerAI</div>
        <div style="color:#94a3b8;font-size:.72rem;font-weight:700;letter-spacing:1.1px;text-transform:uppercase;margin-top:.25rem;">AI Career Intelligence</div>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown(
        f"<div style='background:rgba(255,255,255,.07);padding:.75rem;border-radius:12px;font-size:.82rem;color:#cbd5e1;'>Signed in as<br><b>{st.session_state.email}</b></div>",
        unsafe_allow_html=True
    )

    st.sidebar.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)
    st.sidebar.caption("WORKSPACE")

    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "📄 Upload Resume",
            "🤖 AI Recommendation",
            "📈 Skill Gap",
            "🛣 Career Roadmap",
            "⭐ Career Impact",
            "👤 Profile"
        ]
    )


    # =====================================================
    # DASHBOARD
    # =====================================================

    if page == "🏠 Dashboard":

        score = st.session_state.resume_score
        readiness = 80 if score >= 80 else 65 if score >= 60 else 45 if score > 0 else 0
        resume_done = bool(st.session_state.resume_text)
        ai_done = bool(st.session_state.ai_resume_analysis)
        roadmap_done = bool(st.session_state.career_roadmap)
        skills_done = len(st.session_state.found_skills) > 0
        completed = sum([resume_done, skills_done, ai_done, roadmap_done])
        overall = int(completed / 4 * 100)

        st.markdown(f"""
        <div class="cai-hero">
            <div class="study-scene"><div class="study-glow"></div><div class="study-star s1">✦</div><div class="study-star s2">✦</div><div class="study-star s3">✦</div><div class="study-desk"></div><div class="study-book"></div><div class="study-pencil"></div><div class="study-laptop"><div class="study-screen"><div class="study-line"></div><div class="study-line"></div><div class="study-line"></div></div></div><div class="study-plant"><div class="leaf one"></div><div class="leaf two"></div><div class="leaf three"></div><div class="study-pot"></div></div></div>
            <div class="cai-eyebrow">CAREERAI • AI CAREER INTELLIGENCE</div>
            <h1>Build your next career move with confidence.</h1>
            <p style="max-width:760px;color:#dbeafe!important;">Analyze your resume, understand your skill gaps, discover internship opportunities and follow a personalized roadmap — all from one workspace.</p>
            <div style="margin-top:1.2rem;"><span class="cai-pill" style="background:rgba(255,255,255,.12);color:#fff;">{overall}% workspace complete</span><span class="cai-pill" style="background:rgba(255,255,255,.12);color:#fff;">Llama AI powered</span></div>
        </div>
        """, unsafe_allow_html=True)

        k1,k2,k3,k4 = st.columns(4, gap="medium")
        with k1: st.metric("Resume Strength", f"{score}%", help="Current CareerAI resume score")
        with k2: st.metric("Career Readiness", f"{readiness}%")
        with k3: st.metric("Skills Detected", len(st.session_state.found_skills))
        with k4: st.metric("Education", len(st.session_state.found_degrees))

        st.markdown('<div class="cai-section"><h3>Career workspace</h3><div class="cai-muted">Your progress and the fastest next action are shown below.</div></div>', unsafe_allow_html=True)
        left,right = st.columns([1.15,.85], gap="large")
        with left:
            st.markdown('<div class="cai-card"><div class="cai-card-title">Your CareerAI progress</div><div class="cai-muted">Complete each stage to build a stronger career profile.</div></div>', unsafe_allow_html=True)
            st.progress(overall/100)
            stages=[("Resume analysis",resume_done),("Skill detection",skills_done),("AI analysis",ai_done),("Career roadmap",roadmap_done)]
            for name,done in stages:
                st.markdown(f'<div class="cai-step"><strong>{"✓" if done else "○"} {name}</strong><span style="float:right;color:{"#16a34a" if done else "#94a3b8"};font-size:.82rem;">{"Complete" if done else "Pending"}</span></div>',unsafe_allow_html=True)
        with right:
            st.markdown('<div class="cai-card"><div class="cai-card-title">Quick actions</div><div class="cai-muted">Jump directly to the next useful step.</div></div>', unsafe_allow_html=True)
            if not resume_done:
                if st.button("📄 Upload & analyze resume", use_container_width=True, type="primary"):
                    st.session_state._dashboard_hint="upload"; st.rerun()
            elif not ai_done:
                if st.button("🤖 Run AI resume analysis", use_container_width=True, type="primary"):
                    st.session_state._dashboard_hint="ai"; st.rerun()
            else:
                if st.button("🛣 Build my career roadmap", use_container_width=True, type="primary"):
                    st.session_state._dashboard_hint="roadmap"; st.rerun()
            st.markdown('<div style="height:.45rem"></div>',unsafe_allow_html=True)
            st.info("Use the sidebar to explore Internship Recommendations, Skill Gap and Career Impact.")

        st.markdown('<div class="cai-section"><h3>Profile snapshot</h3></div>', unsafe_allow_html=True)
        a,b = st.columns(2, gap="large")
        with a:
            st.markdown('<div class="cai-card"><div class="cai-card-title">Technical skills</div><div class="cai-muted">Detected from your uploaded resume.</div><div style="margin-top:.7rem;">'+("".join(f'<span class="cai-pill">{x}</span>' for x in st.session_state.found_skills) if st.session_state.found_skills else '<span class="cai-muted">Upload a resume to detect skills.</span>')+'</div></div>', unsafe_allow_html=True)
        with b:
            education = ", ".join(st.session_state.found_degrees) if st.session_state.found_degrees else "Not detected yet"
            st.markdown(f'<div class="cai-card"><div class="cai-card-title">Education</div><div class="cai-muted">CSE / IT education detected from your resume.</div><div style="margin-top:1rem;font-size:1.05rem;font-weight:700;color:#172033;">{education}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="cai-section"><h3>Next step</h3></div>', unsafe_allow_html=True)
        if not resume_done:
            st.info("Start by uploading a PDF resume. CareerAI will extract your skills and education.")
        elif not ai_done:
            st.info("Your resume is ready. Run AI Resume Analysis to get deeper feedback.")
        elif not roadmap_done:
            st.info("Your profile is analyzed. Build a personalized Career Roadmap next.")
        else:
            st.success("Your main CareerAI workflow is complete. Explore your recommendations and skill gap.")


    # =====================================================
    # UPLOAD RESUME
    # =====================================================

    elif page == "📄 Upload Resume":

        st.markdown('<div class="cai-pagehead"><div><div class="title">Resume Analysis</div><div class="desc">Upload your resume and turn it into an actionable career profile.</div></div><div class="cai-pill">PDF • AI analysis</div></div>', unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Upload your resume",
            type=["pdf"]
        )

        if uploaded_file:

            st.success(
                "✅ Resume uploaded successfully!"
            )

            st.write(
                "File Name:",
                uploaded_file.name
            )

            st.write(
                "File Size:",
                round(uploaded_file.size / 1024, 2),
                "KB"
            )

            try:

                pdf_reader = PyPDF2.PdfReader(
                    uploaded_file
                )

                total_pages = len(
                    pdf_reader.pages
                )

                st.write(
                    "Total Pages:",
                    total_pages
                )

                text = ""

                for page_data in pdf_reader.pages:

                    page_text = page_data.extract_text()

                    if page_text:

                        text += page_text + "\n"

                if not text.strip():

                    st.error(
                        "❌ Could not extract text from this PDF."
                    )

                    st.info(
                        "Please upload a text-based PDF resume."
                    )

                else:

                    # =====================================
                    # SAVE ORIGINAL RESUME
                    # =====================================

                    st.session_state.resume_text = text

                    st.session_state.ai_resume_analysis = ""

                    st.session_state.career_roadmap = ""


                    # =====================================
                    # DETECT CSE SKILLS
                    # =====================================

                    found_skills = find_skills(text)

                    st.session_state.found_skills = found_skills


                    # =====================================
                    # DETECT CSE / IT DEGREES
                    # =====================================

                    found_degrees = find_degrees(text)

                    st.session_state.found_degrees = found_degrees


                    # =====================================
                    # CREATE SHORT AI CONTEXT
                    # =====================================

                    st.session_state.ai_resume_context = (
                        build_ai_resume_context(
                            text,
                            found_skills,
                            found_degrees
                        )
                    )


                    # =====================================
                    # RESUME SCORE
                    # =====================================

                    score = min(
                        len(found_skills) * 3,
                        70
                    )

                    text_lower = text.lower()

                    if (
                        "education" in text_lower
                        or "b.tech" in text_lower
                        or "b.e" in text_lower
                        or "bca" in text_lower
                        or "mca" in text_lower
                    ):
                        score += 10

                    if "project" in text_lower:
                        score += 10

                    if (
                        "experience" in text_lower
                        or "internship" in text_lower
                    ):
                        score += 5

                    if (
                        "certification" in text_lower
                        or "certifications" in text_lower
                    ):
                        score += 5

                    score = min(
                        score,
                        100
                    )

                    st.session_state.resume_score = score


                    # =====================================
                    # DISPLAY RESUME TEXT
                    # =====================================

                    st.markdown("---")

                    st.subheader(
                        "📄 Extracted Resume Text"
                    )

                    with st.expander(
                        "View Original Resume Text"
                    ):

                        st.text(text)


                    # =====================================
                    # DISPLAY SKILLS
                    # =====================================

                    st.markdown("---")

                    st.subheader(
                        "🧠 CSE / IT Skills Found"
                    )

                    if found_skills:

                        cols = st.columns(3)

                        for i, skill in enumerate(
                            found_skills
                        ):

                            with cols[i % 3]:

                                st.success(
                                    f"✓ {skill}"
                                )

                    else:

                        st.warning(
                            "No predefined CSE skills detected."
                        )


                    # =====================================
                    # DISPLAY DEGREE
                    # =====================================

                    st.markdown("---")

                    st.subheader(
                        "🎓 CSE / IT Education Detected"
                    )

                    if found_degrees:

                        for degree in found_degrees:

                            st.info(
                                f"🎓 {degree}"
                            )

                    else:

                        st.warning(
                            "No predefined CSE / IT degree detected."
                        )


                    # =====================================
                    # AI CONTEXT PREVIEW
                    # =====================================

                    st.markdown("---")

                    st.subheader(
                        "⚡ AI Processing Profile"
                    )

                    st.caption(
                        "This is the shorter profile sent to Ollama. "
                        "Your original resume remains unchanged."
                    )

                    with st.expander(
                        "View AI Processing Profile"
                    ):

                        st.text(
                            st.session_state.ai_resume_context
                        )


                    # =====================================
                    # RESUME SCORE
                    # =====================================

                    st.markdown("---")

                    st.subheader(
                        "📊 Resume Strength"
                    )

                    st.metric(
                        "Resume Score",
                        f"{score}%"
                    )

                    st.progress(score)

                    if score >= 80:

                        st.success(
                            "Excellent Resume! 🎉"
                        )

                    elif score >= 60:

                        st.info(
                            "Good Resume. Some improvements are possible."
                        )

                    else:

                        st.warning(
                            "Your resume needs improvement."
                        )

                    st.success(
                        "✅ Resume data saved successfully!"
                    )


            except Exception as e:

                st.error(
                    f"❌ Error reading PDF: {e}"
                )


    # =====================================================
    # AI RESUME ANALYSIS
    # =====================================================

    if (
        st.session_state.resume_text
        and page == "🤖 AI Recommendation"
    ):

        st.title(
            "🤖 AI Resume Analysis"
        )

        st.caption(
            f"Powered locally by Ollama • Model: {OLLAMA_MODEL}"
        )

        st.info(
            "CareerAI sends a shortened CSE-focused profile "
            "to Ollama instead of the entire resume."
        )

        if st.button(
            "Analyze Resume with AI",
            key="ai_resume_button"
        ):

            with st.spinner(
                "🤖 Ollama is analyzing your resume..."
            ):

                prompt = f"""
You are CareerAI, an AI career advisor for CSE and IT college students.

Analyze the following SHORT CSE-focused student profile.

{st.session_state.ai_resume_context}

Give a concise report using these sections:

## 1. Resume Summary
Give a short summary.

## 2. Technical Skills
List the programming languages, technologies,
tools and computer science skills detected.

## 3. Education
Mention the detected CSE / IT degree and specialization.

## 4. Projects
Mention the projects available in the profile.

## 5. Experience
Mention internships or experience.
If unavailable, say "No professional experience found."

## 6. Resume Strength
Give a score from 0 to 100 and briefly explain it.

## 7. Strengths
Give 3-5 points.

## 8. Skill Gaps
Suggest important CSE/IT skills that may be useful
for suitable entry-level careers.

## 9. Improvement Suggestions
Give practical suggestions for a college student.

## 10. Suitable Career Roles
Suggest suitable CSE/IT career roles based on the profile.

Keep the answer under 500 words.

Do not invent qualifications, experience,
projects, marks, certifications or skills.
"""

                try:

                    response = ollama_client.chat(
                        model=OLLAMA_MODEL,
                        messages=[
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    )

                    st.session_state.ai_resume_analysis = (
                        response["message"]["content"]
                    )

                    st.success(
                        "✅ AI Resume Analysis Completed!"
                    )

                except Exception as e:

                    st.error(
                        "❌ Ollama request failed."
                    )

                    st.write(
                        "Please make sure Ollama is running."
                    )

                    st.code(
                        str(e)
                    )


        if st.session_state.ai_resume_analysis:

            st.markdown("---")

            st.subheader(
                "📊 AI Resume Report"
            )

            st.markdown(
                st.session_state.ai_resume_analysis
            )

    elif page == "🤖 AI Recommendation":

        st.warning(
            "⚠ Please upload your resume first."
        )


    # =====================================================
    # INTERNSHIP RECOMMENDATION
    # =====================================================

    if page == "🤖 AI Recommendation" and st.session_state.resume_text:

        st.markdown("---")
        st.markdown('<div class="cai-pagehead"><div><div class="title">Internship Recommendations</div><div class="desc">Discover opportunities matched to the skills in your resume.</div></div><div class="cai-pill">Skill matched</div></div>', unsafe_allow_html=True)

        found_skills = st.session_state.found_skills

        try:
            data = pd.read_csv("internships.csv")
        except FileNotFoundError:
            st.error("❌ internships.csv not found.")
            st.stop()
        except Exception as e:
            st.error(f"Error reading internship data: {e}")
            st.stop()

        required_columns = ["Company", "Role", "Skills"]
        missing_columns = [
            column for column in required_columns
            if column not in data.columns
        ]

        if missing_columns:
            st.error(
                "❌ internships.csv is missing these columns: "
                + ", ".join(missing_columns)
            )
            st.stop()

        # Normalize resume skills once for faster matching.
        user_skills = {
            str(skill).strip().lower()
            for skill in found_skills
            if str(skill).strip()
        }

        recommendations = []

        for _, row in data.iterrows():

            required_skills = [
                skill.strip()
                for skill in str(row["Skills"]).split(",")
                if skill.strip()
            ]

            # Remove duplicate required skills while keeping their order.
            required_skills = list(dict.fromkeys(required_skills))

            matched = [
                skill
                for skill in required_skills
                if skill.lower() in user_skills
            ]

            missing = [
                skill
                for skill in required_skills
                if skill.lower() not in user_skills
            ]

            match_score = (
                round((len(matched) / len(required_skills)) * 100)
                if required_skills else 0
            )

            recommendations.append({
                "Company": str(row["Company"]),
                "Role": str(row["Role"]),
                "Skills": required_skills,
                "Match": match_score,
                "Matched": matched,
                "Missing": missing
            })

        recommendations.sort(
            key=lambda item: (-item["Match"], item["Company"])
        )

        # Summary at the top.
        if recommendations:
            best_match = recommendations[0]["Match"]
            high_matches = sum(
                1 for item in recommendations
                if item["Match"] >= 60
            )

            col1, col2, col3 = st.columns(3)
            col1.metric("📋 Internships Checked", len(recommendations))
            col2.metric("🎯 Best Skill Match", f"{best_match}%")
            col3.metric("⭐ 60%+ Matches", high_matches)

        if not user_skills:
            st.warning(
                "⚠ No skills were detected from your resume. "
                "Upload a resume containing technical skills to get better recommendations."
            )

        st.info(
            "Recommendations are based on the skills detected from your uploaded resume. "
            "A higher percentage means more of the listed internship skills match your profile."
        )

        st.markdown("### 🎯 Recommended Internships")

        # Show every company, but place the strongest matches first.
        for index, item in enumerate(recommendations, start=1):

            st.markdown("---")

            st.subheader(
                f"{index}. 🏢 {item['Company']} — {item['Role']}"
            )

            score = item["Match"]
            st.progress(score / 100)

            if score >= 75:
                st.success(f"🎯 Skill Match: {score}%")
            elif score >= 50:
                st.info(f"🎯 Skill Match: {score}%")
            elif score > 0:
                st.warning(f"🎯 Skill Match: {score}%")
            else:
                st.error(f"🎯 Skill Match: {score}%")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**✅ Matched Skills**")
                if item["Matched"]:
                    st.write(", ".join(item["Matched"]))
                else:
                    st.write("No matching skills detected")

            with col2:
                st.markdown("**❌ Skills to Learn**")
                if item["Missing"]:
                    st.write(", ".join(item["Missing"]))
                else:
                    st.write("🎉 You have all listed skills!")

            with st.expander("📚 View internship skill details"):
                st.write(
                    "**Required Skills:** "
                    + ", ".join(item["Skills"])
                )

    # =====================================================
    # SKILL GAP
    # =====================================================

    elif page == "📈 Skill Gap":

        st.title(
            "📈 CSE Skill Gap Analysis"
        )

        st.write(
            "Compare your detected skills with the skills required by the internship dataset "
            "and identify the skills you can focus on next."
        )

        found_skills = st.session_state.found_skills

        if not st.session_state.resume_text:

            st.warning(
                "⚠ Please upload your resume first."
            )

            st.info(
                "Go to '📄 Upload Resume' first."
            )

            st.stop()

        if not found_skills:

            st.warning(
                "No predefined CSE/IT skills were detected in your resume."
            )

            st.info(
                "The analysis below will treat all internship skills as missing."
            )

        try:

            data = pd.read_csv(
                "internships.csv"
            )

        except FileNotFoundError:

            st.error(
                "❌ internships.csv not found. Keep it in the same folder as app.py."
            )

            st.stop()

        except Exception as e:

            st.error(
                f"Could not load internship data: {e}"
            )

            st.stop()


        # =================================================
        # CALCULATE OVERALL SKILL MATCH
        # =================================================

        user_skill_set = {
            skill.strip().lower()
            for skill in found_skills
        }

        company_results = []
        missing_frequency = {}
        matched_frequency = {}
        all_required_skills = set()

        for _, row in data.iterrows():

            required_skills = [
                skill.strip()
                for skill in str(row["Skills"]).split(",")
                if skill.strip()
            ]

            have = []
            missing = []

            for skill in required_skills:

                all_required_skills.add(skill)

                if skill.lower() in user_skill_set:
                    have.append(skill)
                    matched_frequency[skill] = matched_frequency.get(skill, 0) + 1
                else:
                    missing.append(skill)
                    missing_frequency[skill] = missing_frequency.get(skill, 0) + 1

            match_percentage = (
                int((len(have) / len(required_skills)) * 100)
                if required_skills
                else 0
            )

            company_results.append(
                {
                    "Company": row["Company"],
                    "Role": row["Role"],
                    "Required Skills": ", ".join(required_skills),
                    "Have": have,
                    "Missing": missing,
                    "Match": match_percentage
                }
            )


        total_required = sum(
            len(result["Have"]) + len(result["Missing"])
            for result in company_results
        )

        total_matched = sum(
            len(result["Have"])
            for result in company_results
        )

        overall_match = (
            int((total_matched / total_required) * 100)
            if total_required
            else 0
        )


        # =================================================
        # TOP SUMMARY
        # =================================================

        st.markdown("---")

        st.subheader("📊 Overall Skill Gap Summary")

        summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

        with summary_col1:

            st.metric(
                "🧠 Your Skills",
                len(found_skills)
            )

        with summary_col2:

            st.metric(
                "📋 Required Skills",
                len(all_required_skills)
            )

        with summary_col3:

            st.metric(
                "❌ Missing Skills",
                len(missing_frequency)
            )

        with summary_col4:

            st.metric(
                "🎯 Overall Skill Match",
                f"{overall_match}%"
            )

        st.progress(overall_match / 100)


        # =================================================
        # YOUR SKILLS / MOST NEEDED SKILLS
        # =================================================

        st.markdown("---")

        left_col, right_col = st.columns(2)

        with left_col:

            st.subheader("✅ Skills You Already Have")

            if found_skills:

                for skill in found_skills:
                    st.success(skill)

            else:

                st.info("No predefined skills detected.")

        with right_col:

            st.subheader("🎯 Most Frequently Missing Skills")

            if missing_frequency:

                top_missing = sorted(
                    missing_frequency.items(),
                    key=lambda item: item[1],
                    reverse=True
                )[:10]

                for skill, count in top_missing:

                    st.error(
                        f"{skill} — missing in {count} internship requirement(s)"
                    )

            else:

                st.success(
                    "🎉 No missing skills were found in the internship dataset."
                )


        # =================================================
        # COURSE RECOMMENDATIONS FOR MISSING SKILLS
        # =================================================

        st.markdown("---")

        st.subheader("📚 Courses for Your Missing Skills")

        if missing_frequency:

            try:

                courses_data = pd.read_csv("courses.csv")

                required_course_columns = [
                    "Course",
                    "Platform",
                    "Skill",
                    "Level",
                    "Duration",
                    "Study_Hours_Per_Week",
                    "Link",
                    "Cost"
                ]

                missing_course_columns = [
                    column
                    for column in required_course_columns
                    if column not in courses_data.columns
                ]

                if missing_course_columns:

                    st.warning(
                        "courses.csv is missing: "
                        + ", ".join(missing_course_columns)
                    )

                else:

                    missing_skill_names = [
                        skill.lower()
                        for skill in missing_frequency
                    ]

                    course_recommendations = []

                    for _, course in courses_data.iterrows():

                        course_skill = str(course["Skill"]).strip().lower()

                        matched_missing_skill = None

                        for missing_skill in missing_skill_names:

                            if (
                                missing_skill in course_skill
                                or course_skill in missing_skill
                            ):

                                matched_missing_skill = missing_skill
                                break

                        if matched_missing_skill:

                            original_skill = next(
                                skill
                                for skill in missing_frequency
                                if skill.lower() == matched_missing_skill
                            )

                            course_recommendations.append(
                                {
                                    "Missing Skill": original_skill,
                                    "Course": course["Course"],
                                    "Platform": course["Platform"],
                                    "Level": course["Level"],
                                    "Duration": course["Duration"],
                                    "Study Hours": course["Study_Hours_Per_Week"],
                                    "Cost": course["Cost"],
                                    "Link": course["Link"]
                                }
                            )

                    if course_recommendations:

                        # Keep the most relevant missing skills first.
                        course_recommendations.sort(
                            key=lambda item: missing_frequency.get(
                                item["Missing Skill"], 0
                            ),
                            reverse=True
                        )

                        displayed_courses = course_recommendations[:10]

                        for course in displayed_courses:

                            with st.expander(
                                f"📘 {course['Course']} — {course['Missing Skill']}"
                            ):

                                st.write(
                                    f"**Platform:** {course['Platform']}"
                                )

                                st.write(
                                    f"**Level:** {course['Level']}"
                                )

                                st.write(
                                    f"**Duration:** {course['Duration']}"
                                )

                                st.write(
                                    f"**Study Hours:** {course['Study Hours']}"
                                )

                                st.write(
                                    f"**Cost:** {course['Cost']}"
                                )

                                if str(course["Link"]).strip():

                                    st.link_button(
                                        "🔗 Open Course",
                                        str(course["Link"]).strip()
                                    )

                    else:

                        st.info(
                            "No course in courses.csv directly matches the missing skills found in the internship dataset."
                        )

            except FileNotFoundError:

                st.warning(
                    "courses.csv not found. Add courses.csv to enable course recommendations for skill gaps."
                )

            except Exception as e:

                st.warning(
                    f"Could not load course recommendations: {e}"
                )

        else:

            st.success(
                "🎉 You currently match all skills required by the internship dataset."
            )


        # =================================================
        # COMPANY-BY-COMPANY BREAKDOWN
        # =================================================

        st.markdown("---")

        st.subheader("🏢 Internship Skill Requirements")

        for result in company_results:

            with st.expander(
                f"{result['Company']} — {result['Role']} | Match: {result['Match']}%"
            ):

                st.write(
                    "**Required Skills:**",
                    result["Required Skills"]
                )

                company_col1, company_col2 = st.columns(2)

                with company_col1:

                    st.write("### ✅ Skills You Have")

                    if result["Have"]:

                        for skill in result["Have"]:
                            st.success(skill)

                    else:

                        st.write("No matching skills.")

                with company_col2:

                    st.write("### ❌ Skills You Need")

                    if result["Missing"]:

                        for skill in result["Missing"]:
                            st.error(skill)

                    else:

                        st.success(
                            "All required skills available!"
                        )

    # =====================================================
    # CAREER ROADMAP
    # =====================================================

    elif page == "🛣 Career Roadmap":

        st.title(
            "🛣 AI Personalized Career Roadmap"
        )

        st.write(
            "Choose your target CSE/IT career and build your own learning plan."
        )

        if not st.session_state.resume_text:

            st.warning(
                "⚠ Please upload your resume first."
            )

            st.info(
                "Go to '📄 Upload Resume' first."
            )

            st.stop()


        # =================================================
        # TARGET CAREER
        # =================================================

        career_options = [

            "Software Engineer",
            "Python Developer",
            "Java Developer",
            "C/C++ Developer",
            "Web Developer",
            "Frontend Developer",
            "Backend Developer",
            "Full-Stack Developer",

            "Data Analyst",
            "Data Scientist",
            "Data Engineer",

            "Machine Learning Engineer",
            "AI Engineer",
            "MLOps Engineer",

            "Cloud Engineer",
            "DevOps Engineer",

            "Cybersecurity Engineer",
            "Network Engineer",

            "Database Administrator",

            "Mobile App Developer",

            "UI/UX Designer",

            "QA / Software Tester",

            "Business Analyst",

            "Game Developer"
        ]


        career_goal = st.selectbox(
            "🎯 Select your target career",
            career_options
        )


        st.markdown("---")

        # =================================================
        # CURRENT LEVEL / TIME / LEARNING STYLE
        # =================================================

        level = st.selectbox(
            "📚 Select your current level",
            ["Beginner", "Intermediate", "Advanced"]
        )

        study_time = st.selectbox(
            "⏰ How much time can you study per week?",
            ["2 hours", "5 hours", "10 hours", "15 hours", "20+ hours"]
        )

        learning_style = st.selectbox(
            "🎓 Choose your learning style",
            ["Courses", "Projects", "Practice / DSA", "Combination"]
        )


        # =================================================
        # DETECTED SKILLS
        # =================================================

        st.subheader(
            "🧠 Your Detected Skills"
        )

        if st.session_state.found_skills:

            st.write(
                ", ".join(
                    st.session_state.found_skills
                )
            )

        else:

            st.write(
                "No predefined skills detected."
            )


        # =================================================
        # SKILLS USER WANTS TO LEARN
        # =================================================

        available_skills = [
            "Python", "Java", "C", "C++", "SQL", "HTML", "CSS",
            "JavaScript", "React", "Git", "Docker", "AWS",
            "Data Structures", "Algorithms", "Machine Learning",
            "REST API", "Cloud Computing", "Cybersecurity",
            "Data Analysis", "Data Science", "Power BI", "Excel",
            "Linux", "Kubernetes", "Django", "Flask", "FastAPI"
        ]

        selected_skills = st.multiselect(
            "🧠 Choose skills you want to learn",
            available_skills
        )

        if selected_skills:
            skills_for_courses = selected_skills
        else:
            skills_for_courses = [
                "Python", "SQL", "Git"
            ]

        st.caption(
            "If you do not select skills, Python, SQL and Git are used as default learning topics."
        )


        # =================================================
        # REAL COURSES FROM courses.csv
        # =================================================

        st.markdown("---")

        st.subheader(
            "🎓 Choose Real Courses"
        )

        st.write(
            "CareerAI reads the real-course information from your courses.csv file. "
            "You choose which courses you want to include in your roadmap."
        )

        try:

            courses_data = pd.read_csv(
                "courses.csv"
            )

            required_columns = [
                "Course",
                "Platform",
                "Skill",
                "Career",
                "Level",
                "Duration",
                "Study_Hours_Per_Week",
                "Link",
                "Cost"
            ]

            missing_columns = [
                column
                for column in required_columns
                if column not in courses_data.columns
            ]

            if missing_columns:

                st.error(
                    "❌ courses.csv is missing these columns: "
                    + ", ".join(missing_columns)
                )

                st.stop()


            # Clean empty values so the filters work safely.
            for column in required_columns:

                courses_data[column] = courses_data[column].fillna("").astype(str)


            # Match a course when either its career or one of its skills
            # is relevant to the student's selections.
            career_text = career_goal.lower()

            matching_rows = []

            for _, row in courses_data.iterrows():

                row_career = row["Career"].lower()
                row_skill = row["Skill"].lower()
                row_level = row["Level"].lower()

                career_match = (
                    career_text in row_career
                    or row_career in career_text
                )

                skill_match = any(
                    selected_skill.lower() in row_skill
                    or row_skill in selected_skill.lower()
                    for selected_skill in skills_for_courses
                )

                level_match = (
                    row_level == ""
                    or row_level == level.lower()
                    or row_level == "all"
                )

                if (career_match or skill_match) and level_match:
                    matching_rows.append(row)


            matching_courses = pd.DataFrame(
                matching_rows,
                columns=courses_data.columns
            )


            # If level filtering removes everything, show career/skill
            # matches instead of leaving the student with no courses.
            if matching_courses.empty:

                for _, row in courses_data.iterrows():

                    row_career = row["Career"].lower()
                    row_skill = row["Skill"].lower()

                    career_match = (
                        career_text in row_career
                        or row_career in career_text
                    )

                    skill_match = any(
                        selected_skill.lower() in row_skill
                        or row_skill in selected_skill.lower()
                        for selected_skill in skills_for_courses
                    )

                    if career_match or skill_match:
                        matching_rows.append(row)

                matching_courses = pd.DataFrame(
                    matching_rows,
                    columns=courses_data.columns
                )


            # Remove duplicate courses if the same course matched by
            # both career and skill.
            if not matching_courses.empty:

                matching_courses = matching_courses.drop_duplicates(
                    subset=["Course", "Platform", "Skill"]
                ).reset_index(drop=True)


            if matching_courses.empty:

                st.warning(
                    "⚠ No matching real courses were found in courses.csv for the selected career and skills."
                )

                selected_course_indexes = []

            else:

                course_options = []

                for index, row in matching_courses.iterrows():

                    label = (
                        f"{row['Course']} | "
                        f"{row['Platform']} | "
                        f"{row['Skill']}"
                    )

                    course_options.append(label)


                selected_course_labels = st.multiselect(
                    "📖 Select the real courses you want",
                    course_options,
                    key="real_course_selection"
                )

                selected_course_indexes = [
                    course_options.index(label)
                    for label in selected_course_labels
                ]


                # Show the real course information before the user selects
                # personal duration and weekly study hours.
                if selected_course_indexes:

                    st.markdown("### 📚 Selected Course Details")

                    for index in selected_course_indexes:

                        row = matching_courses.iloc[index]

                        st.markdown("---")

                        st.write(
                            f"**{row['Course']}**"
                        )

                        st.write(
                            f"Platform: **{row['Platform']}**"
                        )

                        st.write(
                            f"Skill: **{row['Skill']}**"
                        )

                        st.write(
                            f"Official Duration: **{row['Duration']}**"
                        )

                        st.write(
                            f"Official Study Time: **{row['Study_Hours_Per_Week']}**"
                        )

                        st.write(
                            f"Cost: **{row['Cost']}**"
                        )

                        if row["Link"].strip():

                            st.link_button(
                                "🔗 Open Course",
                                row["Link"].strip()
                            )


            # =================================================
            # PERSONAL COURSE PLAN
            # =================================================

            course_rows = []

            if selected_course_indexes:

                st.markdown("---")

                st.subheader(
                    "📝 Set Your Own Course Duration & Study Hours"
                )

                st.caption(
                    "The official course duration is shown above. "
                    "Your duration and weekly study hours are your personal plan."
                )

                duration_options = [
                    "2 weeks",
                    "4 weeks",
                    "6 weeks",
                    "8 weeks",
                    "12 weeks",
                    "16 weeks"
                ]

                hours_options = [
                    "2",
                    "4",
                    "6",
                    "8",
                    "10",
                    "15",
                    "20"
                ]

                for position, index in enumerate(selected_course_indexes):

                    row = matching_courses.iloc[index]

                    st.markdown("---")

                    st.write(
                        f"### {row['Course']}"
                    )

                    col1, col2 = st.columns(2)

                    with col1:

                        your_duration = st.selectbox(
                            "Your Duration",
                            duration_options,
                            index=1,
                            key=f"real_course_duration_{position}"
                        )

                    with col2:

                        your_hours = st.selectbox(
                            "Your Study Hours / Week",
                            hours_options,
                            index=1,
                            key=f"real_course_hours_{position}"
                        )

                    course_rows.append(
                        {
                            "Course": row["Course"],
                            "Platform": row["Platform"],
                            "Skill": row["Skill"],
                            "Official Duration": row["Duration"],
                            "Your Duration": your_duration,
                            "Your Study Time": f"{your_hours} hrs/week",
                            "Cost": row["Cost"],
                            "Link": row["Link"]
                        }
                    )


            if course_rows:

                st.markdown("---")

                st.subheader(
                    "📋 Your Selected Learning Plan"
                )

                course_table = pd.DataFrame(
                    course_rows
                )

                display_course_table = course_table.drop(
                    columns=["Link"]
                )

                st.dataframe(
                    display_course_table,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info(
                    "Select at least one real course to create your personal course plan."
                )


        except FileNotFoundError:

            st.error(
                "❌ courses.csv not found. Keep courses.csv in the same folder as app.py."
            )

            st.info(
                "Required file: courses.csv"
            )

            st.stop()

        except Exception as e:

            st.error(
                f"❌ Error reading courses.csv: {e}"
            )

            st.stop()


        # =================================================
        # ALTERNATIVE CAREER PATHS
        # =================================================

        selected_alternatives = {
            "Software Engineer": [
                "Backend Developer",
                "Full-Stack Developer",
                "Data Engineer"
            ],
            "Python Developer": [
                "Backend Developer",
                "Data Analyst",
                "Machine Learning Engineer"
            ],
            "Web Developer": [
                "Frontend Developer",
                "Full-Stack Developer",
                "UI/UX Designer"
            ],
            "Data Analyst": [
                "Data Scientist",
                "Business Analyst",
                "Data Engineer"
            ],
            "Data Scientist": [
                "Data Analyst",
                "Machine Learning Engineer",
                "AI Engineer"
            ],
            "Machine Learning Engineer": [
                "Data Scientist",
                "AI Engineer",
                "MLOps Engineer"
            ],
            "Cloud Engineer": [
                "DevOps Engineer",
                "MLOps Engineer",
                "Network Engineer"
            ],
            "DevOps Engineer": [
                "Cloud Engineer",
                "MLOps Engineer",
                "Software Engineer"
            ],
            "Cybersecurity Engineer": [
                "Network Engineer",
                "Cloud Engineer",
                "Security Analyst"
            ],
            "Java Developer": [
                "Software Engineer",
                "Backend Developer",
                "Android Developer"
            ],
            "C/C++ Developer": [
                "Embedded Systems Developer",
                "Software Engineer",
                "Game Developer"
            ],
            "Full-Stack Developer": [
                "Backend Developer",
                "Frontend Developer",
                "Software Engineer"
            ]
        }.get(
            career_goal,
            [
                "Software Engineer",
                "Data Analyst",
                "Web Developer"
            ]
        )


        st.markdown("---")

        st.subheader(
            "🔀 Alternative Career Paths"
        )

        for path in selected_alternatives:

            st.info(
                f"➡️ {path}"
            )


        # =================================================
        # GENERATE ROADMAP
        # =================================================

        st.markdown("---")

        if st.button(
            "🚀 Generate My Career Roadmap",
            key="career_roadmap_button"
        ):

            if not course_rows:

                st.warning(
                    "⚠ Please select at least one real course before generating the roadmap."
                )

            else:

                with st.spinner(
                    "🤖 Ollama is creating your roadmap..."
                ):

                    skills = ", ".join(
                        st.session_state.found_skills
                    )

                    selected_course_text = "\n".join(
                        [
                            f"- {row['Course']} | Platform: {row['Platform']} | "
                            f"Skill: {row['Skill']} | Official Duration: {row['Official Duration']} | "
                            f"Your Duration: {row['Your Duration']} | "
                            f"Your Study Time: {row['Your Study Time']} | Cost: {row['Cost']} | "
                            f"Link: {row['Link']}"
                            for row in course_rows
                        ]
                    )

                    alternative_text = "\n".join(
                        [
                            f"- {path}"
                            for path in selected_alternatives
                        ]
                    )

                    prompt = f"""
You are CareerAI, a practical career-planning assistant for CSE/IT students.
Create a clear, realistic roadmap using ONLY the information supplied below.
Do not invent courses, links, certifications, experience, marks, skills or achievements.

TARGET CAREER: {career_goal}
CURRENT LEVEL: {level}
WEEKLY STUDY TIME: {study_time}
LEARNING STYLE: {learning_style}
SKILLS TO LEARN: {", ".join(skills_for_courses)}
DETECTED SKILLS: {skills if skills else "None detected"}

RESUME PROFILE:
{st.session_state.ai_resume_context}

SELECTED REAL COURSES:
{selected_course_text}

ALTERNATIVE CAREER PATHS:
{alternative_text}

Write the roadmap in this exact order:

## 1. Current Profile
Give a short summary of the student's level, existing skills and target career.

## 2. Skill Gap
List the most important skills to develop. Separate existing skills from priority skills to learn.

## 3. Learning Roadmap
Create 5 phases. For every phase include:
- What to learn
- What to practice
- A small measurable outcome
Respect the student's weekly study time and learning style.

### Phase 1 - Foundation
### Phase 2 - Core Skills
### Phase 3 - Advanced Skills
### Phase 4 - Projects
### Phase 5 - Internship Readiness

## 4. Selected Real Courses
Use ONLY the supplied courses. For each course mention platform, skill, official duration,
the student's selected duration, and selected weekly study time. Never invent missing details.

## 5. Project Recommendations
Suggest exactly 3 beginner-to-intermediate projects relevant to {career_goal}.
Make each project practical and state the main skills it practices.

## 6. Weekly Study Plan
Give a simple Monday-to-Sunday plan that fits {study_time} per week.

## 7. Milestones
Give 4-6 measurable milestones the student can check off.

## 8. Alternative Career Paths
Use ONLY the supplied alternatives and briefly state what extra skills each may require.

## 9. Final Goal
State the concrete skills, projects and learning evidence the student should have before applying
for entry-level {career_goal} opportunities.

Keep the response around 500-650 words.
Use headings and bullet points. Keep explanations concise and actionable.
"""

                    try:

                        response = ollama_client.chat(
                            model=OLLAMA_MODEL,
                            messages=[
                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ]
                        )

                        st.session_state.career_roadmap = (
                            response["message"]["content"]
                        )

                        st.success(
                            "✅ Personalized Career Roadmap Generated!"
                        )

                    except Exception as e:

                        st.error(
                            "❌ Could not generate the career roadmap."
                        )

                        st.write(
                            "Please make sure Ollama is running."
                        )

                        st.code(
                            str(e)
                        )


        if st.session_state.career_roadmap:

            st.markdown("---")

            st.subheader(
                f"🎯 Roadmap for {career_goal}"
            )

            st.markdown(
                st.session_state.career_roadmap
            )



    # =====================================================
    # CAREER IMPACT
    # =====================================================

    elif page == "⭐ Career Impact":

        st.markdown('<div class="cai-pagehead"><div><div class="title">Career Impact Simulator</div><div class="desc">Explore hypothetical score changes from skills you plan to learn.</div></div><div class="cai-pill">Simulation</div></div>', unsafe_allow_html=True)

        st.write(
            "Simulate how adding selected skills could change your CareerAI "
            "readiness score. The points are hypothetical project values only; "
            "they are not predictions of hiring results or salary."
        )

        if not st.session_state.resume_text:

            st.warning(
                "⚠ Please upload your resume first so the simulator can use your current resume score."
            )
            st.info("Go to '📄 Upload Resume' first.")

        else:

            # These are intentionally hypothetical simulator values.
            skill_impact = {
                "Python": 8,
                "SQL": 7,
                "Git": 5,
                "Data Structures": 10,
                "Algorithms": 10,
                "REST API": 7,
                "React": 8,
                "Docker": 7,
                "AWS": 10,
                "Cloud Computing": 9,
                "Machine Learning": 12,
                "Cybersecurity": 9,
                "Java": 8,
                "JavaScript": 8,
                "C++": 8,
                "Linux": 6,
                "Django": 7,
                "Flask": 6,
                "FastAPI": 7,
                "Data Analysis": 8,
                "Power BI": 7,
                "Excel": 5
            }

            current_skills = {
                skill.lower()
                for skill in st.session_state.found_skills
            }

            available_impact_skills = [
                skill
                for skill in skill_impact
                if skill.lower() not in current_skills
            ]

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Current Resume Score",
                    f"{st.session_state.resume_score}%"
                )

            with col2:
                st.metric(
                    "Skills Already Detected",
                    len(st.session_state.found_skills)
                )

            st.markdown("---")

            if not available_impact_skills:
                st.success(
                    "🎉 Your resume already contains all skills available in this simulator."
                )
            else:

                st.subheader("🎯 Select Skills You Plan to Learn")

                selected_impact_skills = st.multiselect(
                    "Choose one or more skills",
                    available_impact_skills,
                    help="The simulator adds hypothetical points for the selected skills."
                )

                current_score = st.session_state.resume_score

                simulated_points = sum(
                    skill_impact[skill]
                    for skill in selected_impact_skills
                )

                projected_score = min(
                    current_score + simulated_points,
                    100
                )

                actual_improvement = projected_score - current_score

                st.markdown("---")
                st.subheader("📊 Career Readiness Simulation")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Current Score",
                        f"{current_score}%"
                    )

                with col2:
                    st.metric(
                        "Projected Simulator Score",
                        f"{projected_score}%",
                        delta=f"+{actual_improvement} points"
                    )

                with col3:
                    st.metric(
                        "Skills Selected",
                        len(selected_impact_skills)
                    )

                st.write("### Current Resume Score")
                st.progress(current_score / 100)
                st.write(f"**{current_score}%**")

                st.write("### Projected Simulator Score")
                st.progress(projected_score / 100)
                st.write(f"**{projected_score}%**")

                if selected_impact_skills:

                    st.markdown("---")
                    st.subheader("🧩 Selected Skill Impact")

                    impact_rows = []

                    for selected_skill in selected_impact_skills:
                        impact_rows.append({
                            "Skill": selected_skill,
                            "Simulator Points": f"+{skill_impact[selected_skill]}"
                        })

                    impact_table = pd.DataFrame(impact_rows)

                    st.dataframe(
                        impact_table,
                        use_container_width=True,
                        hide_index=True
                    )

                    st.success(
                        f"📈 In this hypothetical simulator, the selected skills add "
                        f"+{actual_improvement} points to the current score."
                    )

                    st.info(
                        "💡 The simulator is capped at 100%. The points are fixed "
                        "demo values and should not be interpreted as guaranteed "
                        "career, hiring, or salary outcomes."
                    )

                    st.markdown("---")
                    st.subheader("🛠 Suggested Learning Order")

                    ordered_skills = sorted(
                        selected_impact_skills,
                        key=lambda skill: skill_impact[skill],
                        reverse=True
                    )

                    for number, skill in enumerate(ordered_skills, start=1):
                        st.write(
                            f"**{number}. {skill}** — "
                            f"focus on this skill as part of your learning plan."
                        )

                    st.markdown("---")
                    st.subheader("🔗 Continue Your Career Plan")
                    st.write(
                        "Use these selected skills in the Career Roadmap to choose "
                        "courses, study hours, projects, and milestones."
                    )

                else:
                    st.info(
                        "Select one or more skills above to see the simulated impact."
                    )

                st.markdown("---")
                st.subheader("💡 How to Use This Simulator")
                st.write(
                    "1. Upload your resume.\n"
                    "2. Select skills you want to learn.\n"
                    "3. Compare your current score with the hypothetical projected score.\n"
                    "4. Use the selected skills when building your Career Roadmap."
                )



    # =====================================================
    # PROFILE
    # =====================================================

    elif page == "👤 Profile":

        st.markdown(
            '<div class="cai-pagehead"><div><div class="title">Your Profile</div><div class="desc">View your CareerAI account, resume progress and detected career information.</div></div><div class="cai-pill">Career Profile</div></div>',
            unsafe_allow_html=True
        )

        # Account information
        st.markdown('<div class="cai-section"><h3>👤 Account</h3></div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2, gap="large")

        with c1:
            st.markdown(
                f'<div class="cai-card"><div class="cai-card-title">Email</div><div style="margin-top:.6rem;font-size:1.05rem;font-weight:700;color:#172033;">{st.session_state.email}</div></div>',
                unsafe_allow_html=True
            )

        with c2:
            st.markdown(
                f'<div class="cai-card"><div class="cai-card-title">Resume Status</div><div style="margin-top:.6rem;font-size:1.05rem;font-weight:700;color:#172033;">{"Uploaded ✓" if st.session_state.resume_text else "Not uploaded yet"}</div></div>',
                unsafe_allow_html=True
            )

        # Career summary
        st.markdown('<div class="cai-section"><h3>📊 Career Summary</h3></div>', unsafe_allow_html=True)

        p1, p2, p3, p4 = st.columns(4, gap="medium")

        with p1:
            st.metric("Resume Score", f"{st.session_state.resume_score}%")
        with p2:
            st.metric("Skills Detected", len(st.session_state.found_skills))
        with p3:
            st.metric("Education", len(st.session_state.found_degrees))
        with p4:
            st.metric("AI Analysis", "Ready ✓" if st.session_state.ai_resume_analysis else "Pending")

        # Detected skills
        st.markdown('<div class="cai-section"><h3>💻 Technical Skills</h3></div>', unsafe_allow_html=True)

        if st.session_state.found_skills:
            skills_html = "".join(
                f'<span class="cai-pill">{skill}</span>'
                for skill in st.session_state.found_skills
            )
            st.markdown(
                f'<div class="cai-card">{skills_html}</div>',
                unsafe_allow_html=True
            )
        else:
            st.info("Upload a resume to detect your technical skills.")

        # Education
        st.markdown('<div class="cai-section"><h3>🎓 Education</h3></div>', unsafe_allow_html=True)

        if st.session_state.found_degrees:
            st.markdown(
                '<div class="cai-card">' +
                "".join(f'<div style="padding:.35rem 0;font-weight:600;color:#172033;">🎓 {degree}</div>' for degree in st.session_state.found_degrees) +
                '</div>',
                unsafe_allow_html=True
            )
        else:
            st.info("Education details will appear here after resume analysis.")

        # Workflow status
        st.markdown('<div class="cai-section"><h3>🚀 CareerAI Progress</h3></div>', unsafe_allow_html=True)

        progress_items = [
            ("Resume uploaded", bool(st.session_state.resume_text)),
            ("Skills detected", bool(st.session_state.found_skills)),
            ("AI resume analysis", bool(st.session_state.ai_resume_analysis)),
            ("Career roadmap", bool(st.session_state.career_roadmap)),
        ]

        for label, completed in progress_items:
            status = "✓ Complete" if completed else "○ Pending"
            status_color = "#16a34a" if completed else "#94a3b8"
            st.markdown(
                f'<div class="cai-step"><strong>{"✓" if completed else "○"} {label}</strong><span style="float:right;color:{status_color};font-size:.82rem;">{status}</span></div>',
                unsafe_allow_html=True
            )

        # Logout
        st.markdown('<div class="cai-section"><h3>🔐 Account Actions</h3></div>', unsafe_allow_html=True)

        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.email = ""
            st.session_state.resume_text = ""
            st.session_state.found_skills = []
            st.session_state.found_degrees = []
            st.session_state.resume_score = 0
            st.session_state.ai_resume_analysis = ""
            st.session_state.ai_resume_context = ""
            st.session_state.career_roadmap = ""
            st.rerun()


# =========================================================
# CAREERAI FOOTER
# =========================================================
if st.session_state.get("logged_in", False):
    st.markdown("<div style='text-align:center;color:#94a3b8;font-size:.76rem;margin-top:2.5rem;padding-top:1rem;border-top:1px solid #e5eaf3;'>CareerAI • AI Career Intelligence Platform • Built with Streamlit + Ollama</div>", unsafe_allow_html=True)
