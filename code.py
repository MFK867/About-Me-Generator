import streamlit as st
import requests
import json
from datetime import datetime
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =============================
# Configuration - USING GROQ (NOT GROK!)
# =============================

# Groq API Configuration
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"  # Fast and good quality
MAX_TOKENS = 300

# Get API key from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

def check_groq_connection():
    """Check if Groq API is accessible"""
    if not GROQ_API_KEY:
        return False, "API key not configured. Please set GROQ_API_KEY in your environment variables."
    
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        test_payload = {
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 5
        }
        response = requests.post(GROQ_API_URL, headers=headers, json=test_payload, timeout=10)
        
        if response.status_code == 200:
            return True, "Connected"
        else:
            return False, f"Status: {response.status_code} - {response.text[:100]}"
    except requests.exceptions.Timeout:
        return False, "Connection timeout"
    except requests.exceptions.ConnectionError:
        return False, "Connection error"
    except Exception as e:
        return False, f"Error: {str(e)}"

def generate_with_groq(prompt, system_prompt, temperature=0.9):
    """Generate text using Groq API with temperature for variation"""
    if not GROQ_API_KEY:
        st.error("❌ GROQ_API_KEY not configured")
        return None
    
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": MAX_TOKENS,
            "temperature": temperature,
            "top_p": 0.95  # Add nucleus sampling for more variety
        }
        
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        else:
            st.error(f"Groq API returned status code: {response.status_code}")
            st.error(f"Response: {response.text}")
            return None
    except requests.exceptions.Timeout:
        st.error("⏱️ Generation timed out")
        return None
    except requests.exceptions.ConnectionError:
        st.error("🔌 Cannot connect to Groq API")
        return None
    except Exception as e:
        st.error(f"❌ Error generating content: {str(e)}")
        return None

def generate_cv_sections(data, variation_number=0):
    """Generate CV summaries from form data with variations"""
    
    # Determine target market based on aspiration
    aspiration = data.get('aspiration', '')
    if aspiration in ["Interested in studying abroad", "Work as a freelancer"]:
        target_market = "International"
    else:
        target_market = "Pakistan"
    
    # Create aspiration-specific guidance with variation prompts
    aspiration_guidance = ""
    
    # Expanded variation styles with more diversity
    variation_styles = [
        "Lead with achievements and quantifiable results. Start with your strongest accomplishment.",
        "Open with your passion and what drives you. Emphasize commitment and enthusiasm.",
        "Begin by highlighting your unique competitive advantages and specialized skills.",
        "Start with your adaptability and how you embrace new challenges and learning.",
        "Open with a problem you solved or impact you created. Focus on outcomes.",
        "Lead with your professional identity and what makes you stand out in your field.",
        "Begin with your career goals and how your background prepares you for them.",
        "Start by describing your professional journey and key milestones.",
        "Open with your technical expertise and how you apply it effectively.",
        "Lead with your collaborative strengths and team contributions."
    ]
    
    # Select variation style based on variation number
    variation_style = variation_styles[variation_number % len(variation_styles)]
    
    if aspiration == "Interested in studying abroad":
        aspiration_guidance = "Emphasize academic achievements, research interests, international aspirations, adaptability, and desire for global education. Highlight qualifications that make them a strong candidate for international universities."
    elif aspiration == "Want to serve Family Business":
        aspiration_guidance = "Focus on family business values, loyalty, entrepreneurial mindset, relevant skills for business growth, and commitment to continuing family legacy. Show blend of tradition and innovation."
    elif aspiration == "New Start-up (Business)":
        aspiration_guidance = "Highlight entrepreneurial spirit, innovation, problem-solving skills, leadership qualities, risk-taking abilities, and vision for creating new ventures. Show passion for building something new."
    elif aspiration == "Work as a freelancer":
        aspiration_guidance = "Emphasize self-motivation, diverse skill set, flexibility, client management abilities, independent work style, and track record of delivering projects. Show versatility and reliability."
    elif aspiration == "Interested in Job":
        aspiration_guidance = "Focus on professional qualifications, team collaboration, career growth mindset, organizational skills, and readiness to contribute to company success. Show you're a valuable employee."
    elif aspiration == "Want to continue studies in Pakistan":
        aspiration_guidance = "Highlight academic dedication, research interests, commitment to local education system, desire for advanced knowledge, and contributions to Pakistan's academic community."
    
    # Add variation instruction to aspiration guidance
    aspiration_guidance += f" {variation_style}"
    
    system_prompt = f"""You are an expert CV writer for {target_market} job markets. 
Always write exactly 70 words. Write in first person perspective.
Create a unique and compelling narrative each time, varying sentence structure and emphasis.
Variation #{variation_number + 1} - Make this version distinctly different from previous versions."""

    prompt = f"""
Generate a professional CV "About Me" section for someone with the following profile:

TARGET MARKET: {target_market}
CAREER ASPIRATION: {aspiration}
{aspiration_guidance}

EDUCATION:
University: {data.get('university', 'N/A')}
Major Subject: {data.get('major_subject', 'N/A')}
Status: {data.get('degree_status', '')}
Pass out: {data.get('passout_session', 'N/A')}
Final Year Project: {data.get('final_year_project', 'N/A')}

EXPERIENCE:
Organization: {data.get('organization', 'N/A')}
Designation: {data.get('designation', '')}
Years: {data.get('experience_years', '')}
Status: {data.get('experience_status', '')}
Industry: {data.get('industry', '')}
Work Detail: {data.get('work_detail', 'N/A')}

SKILLS & INTERESTS:
Technical Skills: {data.get('technical_skills', '')}
IT Skills: {data.get('it_skills', 'N/A')}
Interests: {data.get('interests', 'N/A')}
Certifications: {data.get('certifications', 'N/A')}
Awards: {data.get('medal_holder', 'N/A')}

ACHIEVEMENTS:
{data.get('achievements', '')}

HONOURS:
{data.get('honours', 'N/A')}

REFERENCES:
Name: {data.get('ref_name', 'N/A')}
Designation: {data.get('ref_designation', 'N/A')}
Organization: {data.get('ref_organization', 'N/A')}

CRITICAL REQUIREMENTS:
1. Write exactly 70 words
2. Write in first person perspective
3. Tailor the content specifically for {target_market} market
4. Make the aspiration ({aspiration}) clear and central to the narrative
5. Use appropriate tone for {target_market} market (Pakistan: formal and respectful, International: direct and results-focused)
6. Create a UNIQUE version - vary the opening, structure, and emphasis from typical CV summaries

VARIATION INSTRUCTION: This is variation #{variation_number + 1}. Make it distinctly different by using alternative phrasing and different angle of emphasis.
"""
    
    # Use higher temperature for more variation
    temperature = 0.85 + (random.random() * 0.15)  # Random between 0.85 and 1.0
    text = generate_with_groq(prompt, system_prompt, temperature)
    
    if text:
        return {
            "text": text,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "designation": data.get('designation', ''),
            "market": target_market,
            "aspiration": aspiration,
            "university": data.get('university', ''),
            "variation": variation_number + 1
        }
    
    return None

def get_random_sample_data():
    """Return random sample data for testing"""
    sample_universities = ["LUMS", "NUST", "FAST", "UET", "COMSATS"]
    sample_majors = ["Computer Science", "Software Engineering", "Data Analytics", "Marketing", "Finance"]
    sample_orgs = ["TechSol", "DataCorp", "InnovateTech", "SoftSolutions", "Digital Dynamics"]
    sample_designations = ["Software Engineer", "Data Analyst", "Product Manager", "Web Developer", "Business Analyst"]
    sample_industries = ["Information Technology", "Software Development", "E-commerce", "Banking", "Telecommunications"]
    sample_skills = ["Python, JavaScript, SQL", "Java, C++, React", "Data Analysis, Machine Learning", "Marketing, SEO, Content", "Finance, Excel, PowerBI"]
    sample_achievements = [
        "Developed a full-stack web application with 1000+ active users",
        "Led a team of 5 developers to deliver project 2 weeks ahead of schedule",
        "Increased company revenue by 15% through data-driven marketing strategies",
        "Published research paper on AI applications in healthcare",
        "Won best performer award for 3 consecutive quarters"
    ]
    
    return {
        'university': random.choice(sample_universities),
        'major_subject': random.choice(sample_majors),
        'degree_status': random.choice(["Completed", "In Progress"]),
        'passout_session': str(random.randint(2020, 2024)),
        'final_year_project': f"Smart {random.choice(['Attendance', 'Inventory', 'Learning', 'Health'])} System using AI",
        'organization': random.choice(sample_orgs),
        'designation': random.choice(sample_designations),
        'experience_years': f"{random.randint(1, 5)} years",
        'experience_status': random.choice(["Current", "Previous"]),
        'industry': random.choice(sample_industries),
        'work_detail': f"Responsible for {random.choice(['developing', 'managing', 'analyzing', 'designing'])} {random.choice(['web applications', 'data pipelines', 'business processes', 'user interfaces'])}",
        'technical_skills': random.choice(sample_skills),
        'it_skills': f"Microsoft Office, {random.choice(['Photoshop', 'Figma', 'Tableau', 'PowerBI'])}",
        'interests': f"{random.choice(['Reading', 'Sports', 'Music', 'Traveling', 'Photography'])}, {random.choice(['Technology', 'Business', 'Innovation', 'Research'])}",
        'certifications': f"{random.choice(['AWS Certified', 'Google Certified', 'Microsoft Certified', 'PMP'])} - {random.choice(['Cloud Practitioner', 'Data Analyst', 'Azure Fundamentals', 'Project Management'])}",
        'medal_holder': random.choice(["Dean's List", "Gold Medalist", "Merit Scholarship", "Best Graduate Award"]),
        'achievements': random.choice(sample_achievements),
        'honours': f"Graduated with {random.choice(['Distinction', 'Honors', 'High GPA'])}",
        'ref_name': "Dr. " + random.choice(["Sarah", "John", "Michael", "Emma", "David"]) + " " + random.choice(["Khan", "Ahmad", "Hassan", "Sheikh"]),
        'ref_designation': random.choice(["Professor", "Senior Manager", "Director", "Team Lead"]),
        'ref_organization': random.choice(sample_universities + sample_orgs)
    }

# Streamlit UI
st.set_page_config(
    page_title="About Me Generator",
    page_icon="📝",
    layout="wide"
)

st.title("📝 Professional CV About Me Generator")
st.markdown("Generate compelling 'About Me' sections for your CV using AI")

# Check API connection
if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY not found in environment variables")
    st.info("🔧 **To set up on Streamlit Cloud:**")
    st.code("""
1. Go to your app settings on Streamlit Cloud
2. Click on "Secrets" in the left sidebar
3. Add the following:
   GROQ_API_KEY = "your-api-key-here"
4. Save and redeploy your app
    """)
    st.markdown("For local development, create a `.streamlit/secrets.toml` file:")
    st.code('GROQ_API_KEY = "your-api-key-here"')
    st.stop()
else:
    connected, status = check_groq_connection()
    if not connected:
        st.error(f"❌ Groq API Error: {status}")
        st.warning("Please check your API configuration")

# Initialize session state
if 'generated_section' not in st.session_state:
    st.session_state.generated_section = None
if 'form_data' not in st.session_state:
    st.session_state.form_data = {}
if 'variation_count' not in st.session_state:
    st.session_state.variation_count = 0

# Autofill button
col1, col2 = st.columns([1, 3])
with col1:
    if st.button("🎲 Autofill Sample Data"):
        st.session_state.autofill_data = get_random_sample_data()
        st.rerun()

# Initialize form data
if 'autofill_data' not in st.session_state:
    st.session_state.autofill_data = {}

# Main form
with st.form("cv_form"):
    st.header("👤 Personal Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        university = st.text_input("University", value=st.session_state.autofill_data.get('university', ''), placeholder="Your university name")
        major_subject = st.text_input("Major Subject", value=st.session_state.autofill_data.get('major_subject', ''), placeholder="Your major subject")
        degree_status = st.selectbox("Degree Status", ["Completed", "In Progress", "Expected"],
                                    index=["Completed", "In Progress", "Expected"].index(st.session_state.autofill_data.get('degree_status', 'Completed')))
        passout_session = st.text_input("Pass Out Session", value=st.session_state.autofill_data.get('passout_session', ''), placeholder="e.g., 2023")
    
    with col2:
        final_year_project = st.text_input("Final Year Project", value=st.session_state.autofill_data.get('final_year_project', ''), placeholder="Your FYP title")
        organization = st.text_input("Current/Most Recent Organization", value=st.session_state.autofill_data.get('organization', ''), placeholder="Company name")
        designation = st.text_input("Designation", value=st.session_state.autofill_data.get('designation', ''), placeholder="Your job title")
        experience_years = st.text_input("Experience Years", value=st.session_state.autofill_data.get('experience_years', ''), placeholder="e.g., 2 years")
    
    st.header("💼 Experience Details")
    
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        experience_status = st.selectbox("Experience Status", ["Current", "Previous", "None"],
                                        index=["Current", "Previous", "None"].index(st.session_state.autofill_data.get('experience_status', 'None')))
        industry = st.text_input("Industry", value=st.session_state.autofill_data.get('industry', ''), placeholder="e.g., IT, Finance")
    
    with col_exp2:
        work_detail = st.text_area("Work Detail", value=st.session_state.autofill_data.get('work_detail', ''), placeholder="Brief description of your work")
    
    st.header("🛠️ Skills & Achievements")
    
    col3, col4 = st.columns(2)
    
    with col3:
        technical_skills = st.text_area("Technical Skills", value=st.session_state.autofill_data.get('technical_skills', ''), placeholder="List your technical skills")
        it_skills = st.text_area("IT Skills", value=st.session_state.autofill_data.get('it_skills', ''), placeholder="Software, tools you know")
        interests = st.text_area("Interests", value=st.session_state.autofill_data.get('interests', ''), placeholder="Your professional interests")
        certifications = st.text_area("Certifications", value=st.session_state.autofill_data.get('certifications', ''), placeholder="Professional certifications")
        medal_holder = st.text_area("Awards/Honors", value=st.session_state.autofill_data.get('medal_holder', ''), placeholder="Any awards or honors")
    
    with col4:
        achievements = st.text_area("Achievements*", value=st.session_state.autofill_data.get('achievements', ''), placeholder="Your key achievements")
        honours = st.text_area("Honours", value=st.session_state.autofill_data.get('honours', ''), placeholder="Academic honors")
        ref_name = st.text_input("Reference Name", value=st.session_state.autofill_data.get('ref_name', ''), placeholder="Reference person name")
        ref_designation = st.text_input("Reference Designation", value=st.session_state.autofill_data.get('ref_designation', ''), placeholder="Reference person designation")
        ref_organization = st.text_input("Reference Organization", value=st.session_state.autofill_data.get('ref_organization', ''), placeholder="Reference person organization")
    
    st.header("🎯 Career Aspiration")
    aspiration = st.selectbox(
        "What is your career aspiration?*",
        [
            "Interested in Job",
            "Interested in studying abroad",
            "Want to serve Family Business",
            "New Start-up (Business)",
            "Work as a freelancer",
            "Want to continue studies in Pakistan"
        ]
    )
    
    submitted = st.form_submit_button("🚀 Generate About Me Section", type="primary")
    
    if submitted:
        if not achievements:
            st.error("Please fill in all required fields (marked with *)")
        else:
            # Prepare data
            form_data = {
                'university': university,
                'major_subject': major_subject,
                'degree_status': degree_status,
                'passout_session': passout_session,
                'final_year_project': final_year_project,
                'organization': organization,
                'designation': designation,
                'experience_years': experience_years,
                'experience_status': experience_status,
                'industry': industry,
                'work_detail': work_detail,
                'technical_skills': technical_skills,
                'it_skills': it_skills,
                'interests': interests,
                'certifications': certifications,
                'medal_holder': medal_holder,
                'achievements': achievements,
                'honours': honours,
                'ref_name': ref_name,
                'ref_designation': ref_designation,
                'ref_organization': ref_organization,
                'aspiration': aspiration
            }
            
            # Check if form data changed (especially aspiration)
            form_changed = st.session_state.form_data.get('aspiration') != aspiration or st.session_state.form_data != form_data
            
            # Store form data in session state
            st.session_state.form_data = form_data
            
            # Reset variation count if form changed
            if form_changed:
                st.session_state.variation_count = 0
            
            # Generate section
            with st.spinner("Generating your About Me section..."):
                generated_section = generate_cv_sections(form_data, st.session_state.variation_count)
                
                if generated_section:
                    st.session_state.generated_section = generated_section
                    st.session_state.variation_count += 1
                    st.rerun()

# Display generated section
if st.session_state.generated_section:
    st.success("✅ About Me section generated successfully!")
    
    section = st.session_state.generated_section
    
    st.header("📝 Generated About Me Section")
    
    # Create columns for better layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.text_area(
            "Your Professional About Me",
            value=section['text'],
            height=200,
            key=f"generated_section_v{section['variation']}"
        )
    
    with col2:
        st.info("**Target Market:** " + section['market'])
        st.info("**Aspiration:** " + section['aspiration'])
        st.info(f"**Version:** {section['variation']}")
        st.caption(f"Generated: {section['timestamp']}")
    
    # Action buttons
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    
    with col_btn1:
        if st.button("📋 Copy Text", use_container_width=True):
            st.info("💡 Select the text above and copy manually (Ctrl+C or Cmd+C)")
    
    with col_btn2:
        if st.button("🔄 Regenerate", use_container_width=True):
            if st.session_state.form_data:
                with st.spinner("Regenerating with new variation..."):
                    # Generate with incremented variation number
                    new_section = generate_cv_sections(st.session_state.form_data, st.session_state.variation_count)
                    if new_section:
                        st.session_state.generated_section = new_section
                        st.session_state.variation_count += 1
                        st.rerun()
            else:
                st.warning("Please fill and submit the form first")

# Footer
st.markdown("---")
st.markdown("💡 **Tip**: Fill in as much detail as possible for better results. The AI will tailor the content based on your target market and career aspirations.")

st.markdown("🔄 **Note**: Each regeneration creates a unique variation with different emphasis and structure.")
