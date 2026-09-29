import streamlit as st
import PyPDF2
import pandas as pd
import re

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="CareerAI",
    page_icon="🎓",
    layout="wide"
)

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

if "resume_score" not in st.session_state:
    st.session_state.resume_score = 0


# =========================================================
# SKILLS DATABASE
# =========================================================

SKILLS = [
    "Python",
    "Java",
    "C",
    "C++",
    "HTML",
    "CSS",
    "JavaScript",
    "SQL",
    "Excel",
    "React",
    "Docker",
    "AWS",
    "Machine Learning",
    "Communication",
    "Git",
    "Flask",
    "Django",
    "REST API",
    "MongoDB",
    "MySQL",
    "Data Structures",
    "Data Analysis"
]


# =========================================================
# LOGIN PAGE
# =========================================================

if not st.session_state.logged_in:

    st.title("🎓 CareerAI")
    st.subheader(
        "AI-Powered Resume, Job & Internship Career Platform"
    )

    st.markdown("---")

    left, right = st.columns([2, 1])

    with left:

        st.header("Welcome to CareerAI")

        st.write("""
        CareerAI helps students improve their career readiness.

        ✅ Build Professional Resume

        ✅ AI Resume Analysis

        ✅ Job & Internship Matching

        ✅ Skill Gap Analysis

        ✅ Personalized Career Roadmap

        ✅ Career Impact Analysis

        ✅ Career Readiness Score
        """)

    with right:

        st.subheader("Login")

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

    st.sidebar.title("🎓 CareerAI")

    st.sidebar.write(
        f"Logged in as: {st.session_state.email}"
    )

    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "📄 Upload Resume",
            "🤖 AI Recommendation",
            "💼 Job Matcher",
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

        st.title("🏠 CareerAI Dashboard")

        # Check whether resume is uploaded
        resume_uploaded = bool(
            st.session_state.resume_text.strip()
        )

        # -----------------------------------------
        # BEFORE RESUME UPLOAD
        # -----------------------------------------

        if not resume_uploaded:

            score = 0
            readiness = 0
            internship_count = 0

        # -----------------------------------------
        # AFTER RESUME UPLOAD
        # -----------------------------------------

        else:

            score = st.session_state.resume_score

            # Career readiness
            if score >= 80:
                readiness = 80

            elif score >= 60:
                readiness = 65

            elif score > 0:
                readiness = 45

            else:
                readiness = 0

            # Count suitable internships
            internship_count = 0

            try:

                data = pd.read_csv(
                    "internships.csv"
                )

                for _, row in data.iterrows():

                    required_skills = str(
                        row["Skills"]
                    ).split(",")

                    required_skills = [
                        skill.strip()
                        for skill in required_skills
                    ]

                    matched = any(
                        required.lower()
                        == user_skill.lower()
                        for required in required_skills
                        for user_skill in st.session_state.found_skills
                    )

                    if matched:
                        internship_count += 1

            except Exception:

                internship_count = 0

        # -----------------------------------------
        # DASHBOARD METRICS
        # -----------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Resume Score",
                f"{score}%"
            )

        with col2:

            st.metric(
                "Career Readiness",
                f"{readiness}%"
            )

        with col3:

            st.metric(
                "Internships",
                internship_count
            )

        st.markdown("---")

        st.subheader("👋 Welcome to CareerAI")

        if not resume_uploaded:

            st.info(
                "📄 Please upload your resume to start your CareerAI analysis."
            )

        else:

            st.success(
                "✅ Resume uploaded and analyzed successfully!"
            )

            st.write(
                "Your dashboard has been updated based on your resume."
            )


    # =====================================================
    # UPLOAD RESUME
    # =====================================================

    elif page == "📄 Upload Resume":

        st.title("📄 Resume Upload & Analysis")

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
                round(
                    uploaded_file.size / 1024,
                    2
                ),
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

                    # Save resume text
                    st.session_state.resume_text = text

                    # ---------------------------------
                    # SKILL EXTRACTION
                    # ---------------------------------

                    found_skills = []

                    for skill in SKILLS:

                        pattern = (
                            r"\b"
                            + re.escape(skill)
                            + r"\b"
                        )

                        if re.search(
                            pattern,
                            text,
                            re.IGNORECASE
                        ):

                            found_skills.append(skill)

                    st.session_state.found_skills = found_skills

                    # ---------------------------------
                    # RESUME SCORE
                    # ---------------------------------

                    score = min(
                        len(found_skills) * 5,
                        100
                    )

                    text_lower = text.lower()

                    if "education" in text_lower:
                        score += 5

                    if "project" in text_lower:
                        score += 5

                    if "experience" in text_lower:
                        score += 5

                    if "certification" in text_lower:
                        score += 5

                    score = min(
                        score,
                        100
                    )

                    st.session_state.resume_score = score

                    # ---------------------------------
                    # EXTRACTED TEXT
                    # ---------------------------------

                    st.markdown("---")

                    st.subheader(
                        "📄 Extracted Resume Text"
                    )

                    with st.expander(
                        "View Resume Text"
                    ):

                        st.text(text)

                    # ---------------------------------
                    # SKILLS
                    # ---------------------------------

                    st.markdown("---")

                    st.subheader(
                        "🧠 Skills Found"
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
                            "No predefined skills were detected."
                        )

                    # ---------------------------------
                    # RESUME SCORE
                    # ---------------------------------

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

                    st.markdown("---")

                    st.success(
                        "✅ Resume data saved. "
                        "Go to Dashboard to see the updated score."
                    )

            except Exception as e:

                st.error(
                    f"Error reading PDF: {e}"
                )


    # =====================================================
    # AI INTERNSHIP RECOMMENDATION
    # =====================================================

    elif page == "🤖 AI Recommendation":

        st.title(
            "🤖 AI Internship Recommendation"
        )

        found_skills = st.session_state.found_skills

        if not found_skills:

            st.warning(
                "⚠ Please upload your resume first."
            )

            st.stop()

        try:

            data = pd.read_csv(
                "internships.csv"
            )

        except FileNotFoundError:

            st.error(
                "❌ internships.csv not found."
            )

            st.stop()

        except pd.errors.EmptyDataError:

            st.error(
                "❌ internships.csv is empty."
            )

            st.stop()

        except Exception as e:

            st.error(
                f"Error reading internship data: {e}"
            )

            st.stop()

        st.subheader(
            "🎯 Recommended Internships"
        )

        recommendations = []

        for _, row in data.iterrows():

            required_skills = str(
                row["Skills"]
            ).split(",")

            required_skills = [
                skill.strip()
                for skill in required_skills
            ]

            matched = []

            for required in required_skills:

                for user_skill in found_skills:

                    if (
                        required.lower()
                        == user_skill.lower()
                    ):

                        matched.append(required)
                        break

            if required_skills:

                match_score = int(
                    (
                        len(matched)
                        / len(required_skills)
                    ) * 100
                )

            else:

                match_score = 0

            missing = [
                skill
                for skill in required_skills
                if skill not in matched
            ]

            recommendations.append(
                {
                    "Company": row["Company"],
                    "Role": row["Role"],
                    "Skills": row["Skills"],
                    "Match": match_score,
                    "Matched": matched,
                    "Missing": missing
                }
            )

        # Sort recommendations
        recommendations.sort(
            key=lambda x: x["Match"],
            reverse=True
        )

        for item in recommendations:

            st.markdown("---")

            st.subheader(
                f"🏢 {item['Company']}"
            )

            st.write(
                "Role:",
                item["Role"]
            )

            st.write(
                "Required Skills:",
                item["Skills"]
            )

            st.progress(
                item["Match"]
            )

            st.write(
                f"🎯 Match Score: {item['Match']}%"
            )

            if item["Matched"]:

                st.write(
                    "✅ Matched Skills:",
                    ", ".join(
                        item["Matched"]
                    )
                )

            if item["Missing"]:

                st.write(
                    "❌ Missing Skills:",
                    ", ".join(
                        item["Missing"]
                    )
                )

            else:

                st.success(
                    "🎉 You meet all listed skill requirements!"
                )


    # =====================================================
    # JOB MATCHER
    # =====================================================

    elif page == "💼 Job Matcher":

        st.title(
            "💼 Job Matcher"
        )

        st.info(
            "🚧 Advanced TF-IDF job matching will be added in the next stage."
        )

        st.write("""
        Planned process:

        Resume
        ↓
        Job Description
        ↓
        TF-IDF
        ↓
        Cosine Similarity
        ↓
        Job Match Score
        """)


    # =====================================================
    # SKILL GAP
    # =====================================================

    elif page == "📈 Skill Gap":

        st.title(
            "📈 Skill Gap Analysis"
        )

        found_skills = st.session_state.found_skills

        if not found_skills:

            st.warning(
                "⚠ Please upload your resume first."
            )

            st.stop()

        try:

            data = pd.read_csv(
                "internships.csv"
            )

        except Exception as e:

            st.error(
                f"Could not load internship data: {e}"
            )

            st.stop()

        st.subheader(
            "🎯 Skill Requirements by Internship"
        )

        for _, row in data.iterrows():

            required_skills = str(
                row["Skills"]
            ).split(",")

            required_skills = [
                skill.strip()
                for skill in required_skills
            ]

            have = []
            missing = []

            for skill in required_skills:

                found = any(
                    skill.lower()
                    == user_skill.lower()
                    for user_skill in found_skills
                )

                if found:

                    have.append(skill)

                else:

                    missing.append(skill)

            st.markdown("---")

            st.subheader(
                f"🏢 {row['Company']} — {row['Role']}"
            )

            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    "### ✅ Skills You Have"
                )

                if have:

                    for skill in have:

                        st.success(skill)

                else:

                    st.write(
                        "No matching skills."
                    )

            with col2:

                st.write(
                    "### ❌ Skills You Need"
                )

                if missing:

                    for skill in missing:

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
            "🛣 Personalized Career Roadmap"
        )

        st.write(
            "Your current roadmap prototype:"
        )

        roadmap = [
            (
                "Step 1",
                "Learn HTML & CSS"
            ),
            (
                "Step 2",
                "Strengthen Python"
            ),
            (
                "Step 3",
                "Learn SQL"
            ),
            (
                "Step 4",
                "Learn Git & GitHub"
            ),
            (
                "Step 5",
                "Learn React"
            ),
            (
                "Step 6",
                "Build a Full-Stack Project"
            ),
            (
                "Step 7",
                "Apply for Internships"
            )
        ]

        for step, description in roadmap:

            st.success(
                f"{step} → {description}"
            )

        st.info(
            "🤖 Personalized LLM-generated roadmap "
            "with real course recommendations will be added next."
        )


    # =====================================================
    # CAREER IMPACT
    # =====================================================

    elif page == "⭐ Career Impact":

        st.title(
            "⭐ Career Impact Simulator"
        )

        skill = st.selectbox(
            "Select a skill you want to learn",
            [
                "React",
                "Docker",
                "AWS",
                "Machine Learning",
                "REST API"
            ]
        )

        if st.button(
            "Analyze Career Impact",
            key="career_impact_button"
        ):

            current_score = (
                st.session_state.resume_score
            )

            future_score = min(
                current_score + 10,
                100
            )

            st.metric(
                "Current Resume Score",
                f"{current_score}%"
            )

            st.metric(
                f"Future Score with {skill}",
                f"{future_score}%"
            )

            st.success(
                f"Learning {skill} can strengthen your profile."
            )


    # =====================================================
    # PROFILE
    # =====================================================

    elif page == "👤 Profile":

        st.title(
            "👤 Student Profile"
        )

        st.write(
            "Email:",
            st.session_state.email
        )

        st.write(
            "Resume Score:",
            f"{st.session_state.resume_score}%"
        )

        st.write(
            "Skills Found:",
            len(st.session_state.found_skills)
        )

        if st.session_state.found_skills:

            st.write(
                "Skills:",
                ", ".join(
                    st.session_state.found_skills
                )
            )

        st.markdown("---")

        if st.button(
            "Logout",
            key="logout_button"
        ):

            st.session_state.logged_in = False
            st.session_state.email = ""
            st.session_state.resume_text = ""
            st.session_state.found_skills = []
            st.session_state.resume_score = 0

            st.rerun()
