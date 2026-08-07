import streamlit as st
import PyPDF2
import pandas as pd
import re

# ---------------- Page Configuration ----------------
st.set_page_config(
    page_title="CareerAI",
    page_icon="🎓",
    layout="wide"
)

# ---------------- Session State ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- LOGIN PAGE ----------------
if not st.session_state.logged_in:

    st.title("🎓 CareerAI")
    st.subheader("AI Internship Recommendation Platform")

    st.markdown("---")

    left, right = st.columns([2, 1])

    with left:
        st.header("Welcome to CareerAI")
        st.write("""
        ✅ Build Professional Resume

        ✅ AI Internship Recommendation

        ✅ Skill Gap Analysis

        ✅ Career Roadmap

        ✅ AI Interview Practice

        ✅ Career Readiness Score
        """)

    with right:

        st.subheader("Login")

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

           if "@" in email and "." in email and len(password) >= 4:

              st.session_state.logged_in = True
              st.session_state.email = email
              st.rerun()

           else:

             st.error("Please enter a valid email and password.")

# ---------------- DASHBOARD ----------------
# ---------------- DASHBOARD ----------------
else:

    # Sidebar
    st.sidebar.title("🎓 CareerAI")

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

    # Dashboard Page
    if page == "🏠 Dashboard":
       
        st.title("🏠 CareerAI Dashboard")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Resume Score", "82%")

        with col2:
            st.metric("Career Readiness", "74%")

        with col3:
            st.metric("Internships", "15")
        st.markdown("---")

        st.subheader("Welcome to CareerAI")

        st.write("""
        CareerAI helps students to:

        ✅ Upload Resume

        ✅ Get AI Internship Recommendation

        ✅ Analyze Skill Gap

        ✅ Generate Career Roadmap

        ✅ Improve Career Readiness
        """)


    elif page == "📄 Upload Resume":

        st.title("📄 Upload Resume")

        uploaded_file = st.file_uploader(
            "Choose Resume",
            type=["pdf"]
        )

        if uploaded_file:
            st.success("✅ Resume Uploaded Successfully!")
            st.write("File Name:", uploaded_file.name)
            st.write(
                "File Size:",
                round(uploaded_file.size/1024,2),
                "KB"
            )
            pdf_reader = PyPDF2.PdfReader(uploaded_file)

            total_pages = len(pdf_reader.pages)

            st.write("Total Pages:", total_pages)
            text = ""

            for page in pdf_reader.pages:
              text += page.extract_text()
            st.markdown("---")

            st.subheader("📄 Extracted Resume Text")

            st.write(text)
            skills = [
             "Python",
             "Java",
             "C",
             "C++",
             "HTML",
             "CSS",
             "JavaScript",
             "SQL",
             "React",
             "Docker",
             "AWS",
             "Machine Learning",
              "Communication",
             "Git",
             "Flask",
             "Django"
            ]
            found_skills = []
            for skill in skills:

             if skill.lower() in text.lower():

              found_skills.append(skill)
            st.session_state["found_skills"] = found_skills
            st.markdown("---")

            st.subheader("✅ Skills Found")

            for skill in found_skills:

             st.success(skill)
            resume_score = len(found_skills) * 10
            if resume_score > 100:
              resume_score = 100
            st.markdown("---")

            st.subheader("📊 Resume Score")
            st.metric("Score", f"{resume_score}%")
            st.progress(resume_score)
            if resume_score >= 80:
              st.success("Excellent Resume! 🎉")

            elif resume_score >= 60:
              st.info("Good Resume. Add a few more skills.")

            else:
              st.warning("Your resume needs improvement.")

        if uploaded_file: 

         if st.button("Analyze Resume"):

                st.subheader("Resume Analysis")

                st.metric("Resume Score","82%")

                st.progress(82)

                st.write("### Skills Found")

                st.write("✅ Python")

                st.write("✅ HTML")

                st.write("✅ CSS")

                st.write("✅ SQL")

                st.write("✅ Communication")


    elif page == "🤖 AI Recommendation":

        st.title("🤖 AI Internship Recommendation")
        found_skills = st.session_state.get("found_skills", [])
        if not found_skills:

         st.warning("⚠ Please upload your resume first.")

         st.stop()
        data = pd.read_csv("internships.csv")

        st.subheader("Available Internships")

        st.dataframe(data)
        st.markdown("---")

        st.subheader("🎯 Recommended Internships")
        for index, row in data.iterrows():
               required_skills = row["Skills"]
               match = 0
               for skill in found_skills:

                if skill.lower() in required_skills.lower():

                  match += 1
        total_required = len(required_skills.split(","))

        match_score = int((match / total_required) * 100)
        if match_score >= 50:

         st.write("###", row["Company"])

         st.write("Role:", row["Role"])

         st.progress(match_score)

         st.write("Match Score:", f"{match_score}%")

         st.markdown("---")
    elif page == "📈 Skill Gap":

     st.title("📈 Skill Gap Analysis")

     found_skills = st.session_state.get("found_skills", [])

     if not found_skills:

        st.warning("⚠ Please upload your resume first.")

        st.stop()

     data = pd.read_csv("internships.csv")

     st.subheader("Recommended Skill Improvements")

     for index, row in data.iterrows():

        required_skills = row["Skills"].split(",")

        have = []

        missing = []

        for skill in required_skills:

            skill = skill.strip()

            if skill in found_skills:

                have.append(skill)

            else:

                missing.append(skill)

        st.markdown("---")

        st.subheader(row["Company"])

        st.write("### ✅ Skills You Have")

        for skill in have:
            st.success(skill)

        st.write("### ❌ Skills You Need")

        for skill in missing:
            st.error(skill)

        if len(missing) == 0:
            st.success("🎉 You already meet the skill requirements!")

        else:
            st.info("Learn the missing skills to improve your chances.")
    

         

        st.title("🛣 Career Roadmap")

        st.success("Week 1")

        st.write("Learn HTML & CSS")

        st.success("Week 2")

        st.write("Learn Python")

        st.success("Week 3")
    
        st.write("Learn SQL")

        st.success("Week 4")

        st.write("Learn React")

        st.success("Week 5")

        st.write("Build Full Stack Project")

        st.success("Week 6")

        st.write("Apply Internship")
    elif page == "⭐ Career Impact":

         st.title("⭐ Career Impact Simulator")

         skill = st.selectbox(
        "Select Skill",
        [
            "React",
            "Docker",
            "AWS",
            "Machine Learning"
        ]
        )

         if st.button("Predict"):

           st.metric("Current Match","74%")

           st.metric("Future Match","91%")

           st.success("12 More Internship Opportunities")

    elif page == "👤 Profile":

        st.title("👤 Student Profile")

        st.write("Name: Suthiksha")
        st.write("Resume Score: 82%")
        st.write("Career Readiness: 74%")

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
