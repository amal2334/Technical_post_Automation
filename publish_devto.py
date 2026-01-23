import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
from groq import Groq
import requests
import time
import random



load_dotenv()



GROQ_API_KEY = os.getenv('GROQ_API_KEY')
DEVTO_API_KEY = os.getenv('DEVTO_API_KEY')



def classify_topic(topic):
    """Classify topic as technical or soft skills."""
    soft_keywords = [
        'english', 'communication', 'soft skills', 'presentation', 
        'stakeholder', 'leadership', 'interview', 'career', 'resume',
        'business english', 'teamwork', 'negotiation'
    ]
    topic_lower = topic.lower()
    return "soft_skills" if any(keyword in topic_lower for keyword in soft_keywords) else "technical"



def get_topic_prompt(topic, topic_type):
    """Generate topic-specific prompt."""
    
    if topic_type == "soft_skills":
        return f"""Write professional DEV.TO career article: "Data Analyst Guide: Mastering {topic}"

SOFT SKILLS - NO CODE BLOCKS NEEDED (4500+ characters):

# Data Analyst Guide: Mastering {topic}

## The Critical Question Every Analyst Faces
Compelling question + industry statistic (e.g., "68% of projects fail due to...")

## Real-World Case Study
Detailed story: Analyst struggled → applied framework → promotion/success (800+ chars)

## Proven 7-Step Framework
Practical methodology with templates/examples:
1. Self-assessment
2. Daily practice routine  
3. Stakeholder mapping
4. Presentation structure
5. Feedback loops
6. Advanced techniques
7. Measurement/Milestones

## Career Impact & ROI
- Salary increase data
- Promotion statistics  
- Interview success rates
- Business outcomes

## 30-Day Action Plan
Daily checklist + resources (courses/books/communities)

Professional tone. Actionable. Recruiter-focused. NO technical code."""
    
    else:  # technical
        return f"""Write technical DEV.TO tutorial: "Data Analyst Guide: Mastering {topic}"

COMPLETE CODE IMPLEMENTATION (4500+ chars):

# Data Analyst Guide: Mastering {topic}

## Business Problem Statement
Real scenario + ROI impact

## Step-by-Step Technical Solution
1. Data preparation (pandas/SQL)
2. Analysis pipeline
3. Model/visualization code
4. Performance evaluation
5. Production deployment

Include:
- Full working Python (pandas/sklearn)
- SQL queries  
- Metrics/ROI calculations
- Edge cases
- Scaling tips"""



def post_devto(title, body_markdown):
    """Publish article to DEV.TO API."""
    headers = {
        'api-key': DEVTO_API_KEY,
        'Content-Type': 'application/json',
    }
    data = {
        "article": {
            "title": title,
            "body_markdown": body_markdown,
            "published": True,
            "tag_list": ["DataScience", "DataAnalysis", "Python", "Analytics", "Career"]
        }
    }
    
    response = requests.post('https://dev.to/api/articles', headers=headers, json=data)
    
    if response.status_code in [200, 201]:
        result = response.json()
        print(f"Success! Status: {response.status_code}")
        return result['url'], result['id']
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None, None



def main():
    if not all([GROQ_API_KEY, DEVTO_API_KEY]):
        print("Missing API keys.")
        return
    
    print(f"\nData Analytics Publishing - {datetime.now().strftime('%Y-%m-%d %H:%M CET')}")
    
    df = pd.read_excel('topics.xlsx')
    topic_row = df.sample(1).reset_index(drop=True)
    topic = topic_row.iloc[0]['topic'].strip()
    print(f"Topic: {topic}")
    
    # 🔑 SMART CLASSIFICATION
    topic_type = classify_topic(topic)
    print(f"Type: {topic_type}")
    
    title = f"Data Analyst Guide: Mastering {topic}"  # ✅ title defined here
    
    client = Groq(api_key=GROQ_API_KEY)
    prompt = get_topic_prompt(topic, topic_type)
    
    # 🔑 ADAPTED SYSTEM PROMPT
    system_content = (
        "Senior career coach for data professionals. "
        "NO code blocks. Focus: frameworks, case studies, checklists, ROI data."
        if topic_type == "soft_skills" else
        "Expert data engineer. Complete working Python/SQL code examples required."
    )
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=5000
    )
    
    content = response.choices[0].message.content.strip()
    
    print(f"Content: {len(content)} characters ({topic_type} mode)")
    print(f"Preview:\n{content[:600]}...")
    
    # ✅ AUTO-PUBLISH FOR GITHUB ACTIONS
    print("Auto-publishing to DEV.TO...")
    url, article_id = post_devto(title, content)  # ✅ Now title IS defined
    if url:
        print(f"✅ Published: {url}")
        print(f"ID: {article_id}")
    else:
        print("Failed to publish.")
        exit(1)


if __name__ == "__main__":
    main()


