### Comprehensive Health Management APP
import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import json
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Data persistence
DATA_FILE = "health_data.json"

def load_data():
    if Path(DATA_FILE).exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"profile": {}, "meals": [], "exercises": [], "goals": {}}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def get_gemini_response(input_text, image, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_text, image[0], prompt])
    return response.text

def get_text_response(prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text

def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        return [{"mime_type": uploaded_file.type, "data": bytes_data}]
    else:
        raise FileNotFoundError("No file uploaded")

def calculate_bmr(weight, height, age, gender):
    if gender == "Male":
        return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

def calculate_daily_calories(bmr, activity_level):
    multipliers = {
        "Sedentary": 1.2,
        "Lightly Active": 1.375,
        "Moderately Active": 1.55,
        "Very Active": 1.725,
        "Extremely Active": 1.9
    }
    return bmr * multipliers[activity_level]

# Initialize app
st.set_page_config(page_title="AI Health Manager", layout="wide")
data = load_data()

# Sidebar navigation
st.sidebar.title("🏥 AI Health Manager")
page = st.sidebar.selectbox("Navigate", ["Dashboard", "Profile Setup", "Food Analysis", "Exercise Tracker", "Progress Reports", "AI Health Coach"])

if page == "Profile Setup":
    st.header("👤 User Profile Setup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Name", value=data["profile"].get("name", ""))
        age = st.number_input("Age", min_value=1, max_value=120, value=data["profile"].get("age", 25))
        gender = st.selectbox("Gender", ["Male", "Female"], index=0 if data["profile"].get("gender") == "Male" else 1)
        
    with col2:
        weight = st.number_input("Weight (kg)", min_value=1.0, value=float(data["profile"].get("weight", 70.0)))
        height = st.number_input("Height (cm)", min_value=1.0, value=float(data["profile"].get("height", 170.0)))
        activity_level = st.selectbox("Activity Level", 
                                    ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extremely Active"],
                                    index=["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extremely Active"].index(data["profile"].get("activity_level", "Moderately Active")))
    
    goal = st.selectbox("Health Goal", ["Lose Weight", "Maintain Weight", "Gain Weight"], 
                       index=["Lose Weight", "Maintain Weight", "Gain Weight"].index(data["profile"].get("goal", "Maintain Weight")))
    
    if st.button("Save Profile"):
        bmr = calculate_bmr(weight, height, age, gender)
        daily_calories = calculate_daily_calories(bmr, activity_level)
        
        # Adjust calories based on goal
        if goal == "Lose Weight":
            target_calories = daily_calories - 500
        elif goal == "Gain Weight":
            target_calories = daily_calories + 500
        else:
            target_calories = daily_calories
            
        data["profile"] = {
            "name": name, "age": age, "gender": gender, "weight": weight,
            "height": height, "activity_level": activity_level, "goal": goal,
            "bmr": bmr, "daily_calories": daily_calories, "target_calories": target_calories
        }
        save_data(data)
        st.success("Profile saved successfully!")
        st.rerun()

elif page == "Food Analysis":
    st.header("🍽️ AI Food Analysis & Calorie Tracking")
    
    if not data["profile"]:
        st.warning("Please set up your profile first!")
        st.stop()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
        uploaded_file = st.file_uploader("Upload food image", type=["jpg", "jpeg", "png"])
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Food Image", use_column_width=True)
    
    with col2:
        additional_info = st.text_area("Additional Information (optional)", 
                                     placeholder="e.g., portion size, cooking method...")
        
        if st.button("Analyze Food") and uploaded_file:
            with st.spinner("Analyzing food..."):
                image_data = input_image_setup(uploaded_file)
                
                prompt = f"""
                Analyze this food image and provide:
                1. List each food item with estimated calories
                2. Total calories for the entire meal
                3. Nutritional breakdown (protein, carbs, fat, fiber)
                4. Health assessment (healthy/moderate/unhealthy)
                5. Suggestions for improvement
                
                Format as JSON:
                {{
                    "items": [{{"name": "item", "calories": number, "protein": "Xg", "carbs": "Xg", "fat": "Xg"}}],
                    "total_calories": number,
                    "health_score": "healthy/moderate/unhealthy",
                    "suggestions": "text"
                }}
                
                Additional context: {additional_info}
                """
                
                try:
                    response = get_gemini_response(prompt, image_data, "")
                    # Try to parse JSON response
                    import re
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        analysis = json.loads(json_match.group())
                        
                        st.subheader("📊 Analysis Results")
                        st.metric("Total Calories", f"{analysis['total_calories']} kcal")
                        st.metric("Health Score", analysis['health_score'].title())
                        
                        # Food items breakdown
                        if analysis['items']:
                            df = pd.DataFrame(analysis['items'])
                            st.dataframe(df, use_container_width=True)
                        
                        st.write("**Suggestions:**", analysis['suggestions'])
                        
                        # Save meal data
                        if st.button("Save to Daily Log"):
                            meal_data = {
                                "date": str(date.today()),
                                "meal_type": meal_type,
                                "items": analysis['items'],
                                "total_calories": analysis['total_calories'],
                                "health_score": analysis['health_score'],
                                "timestamp": str(datetime.now())
                            }
                            data["meals"].append(meal_data)
                            save_data(data)
                            st.success("Meal saved to daily log!")
                    else:
                        st.write(response)
                except Exception as e:
                    st.error(f"Error parsing response: {e}")
                    st.write(response)

elif page == "Exercise Tracker":
    st.header("🏃‍♂️ Exercise Tracker")
    
    if not data["profile"]:
        st.warning("Please set up your profile first!")
        st.stop()
    
    col1, col2 = st.columns(2)
    
    with col1:
        exercise_type = st.selectbox("Exercise Type", 
                                   ["Running", "Walking", "Cycling", "Swimming", "Weight Training", "Yoga", "Other"])
        duration = st.number_input("Duration (minutes)", min_value=1, value=30)
        intensity = st.selectbox("Intensity", ["Low", "Moderate", "High"])
        
    with col2:
        notes = st.text_area("Notes (optional)")
        
        if st.button("Calculate Calories Burned"):
            # Simplified calorie calculation based on MET values
            met_values = {
                "Running": {"Low": 8, "Moderate": 11, "High": 16},
                "Walking": {"Low": 3, "Moderate": 4, "High": 5},
                "Cycling": {"Low": 6, "Moderate": 8, "High": 12},
                "Swimming": {"Low": 6, "Moderate": 8, "High": 11},
                "Weight Training": {"Low": 3, "Moderate": 5, "High": 8},
                "Yoga": {"Low": 2, "Moderate": 3, "High": 4},
                "Other": {"Low": 3, "Moderate": 5, "High": 7}
            }
            
            met = met_values[exercise_type][intensity]
            weight = data["profile"]["weight"]
            calories_burned = (met * weight * duration) / 60
            
            st.metric("Calories Burned", f"{calories_burned:.0f} kcal")
            
            if st.button("Save Exercise"):
                exercise_data = {
                    "date": str(date.today()),
                    "type": exercise_type,
                    "duration": duration,
                    "intensity": intensity,
                    "calories_burned": calories_burned,
                    "notes": notes,
                    "timestamp": str(datetime.now())
                }
                data["exercises"].append(exercise_data)
                save_data(data)
                st.success("Exercise logged successfully!")

elif page == "Dashboard":
    st.header("📊 Health Dashboard")
    
    if not data["profile"]:
        st.warning("Please set up your profile first!")
        st.stop()
    
    # Today's summary
    today = str(date.today())
    today_meals = [m for m in data["meals"] if m["date"] == today]
    today_exercises = [e for e in data["exercises"] if e["date"] == today]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        calories_consumed = sum(m["total_calories"] for m in today_meals)
        st.metric("Calories Consumed", f"{calories_consumed:.0f}")
    
    with col2:
        calories_burned = sum(e["calories_burned"] for e in today_exercises)
        st.metric("Calories Burned", f"{calories_burned:.0f}")
    
    with col3:
        net_calories = calories_consumed - calories_burned
        st.metric("Net Calories", f"{net_calories:.0f}")
    
    with col4:
        target = data["profile"]["target_calories"]
        remaining = target - net_calories
        st.metric("Remaining", f"{remaining:.0f}")
    
    # Progress bar
    progress = min(net_calories / target, 1.0) if target > 0 else 0
    st.progress(progress)
    
    # Today's meals
    if today_meals:
        st.subheader("Today's Meals")
        for meal in today_meals:
            with st.expander(f"{meal['meal_type']} - {meal['total_calories']} kcal"):
                for item in meal['items']:
                    st.write(f"• {item['name']}: {item['calories']} kcal")
    
    # Today's exercises
    if today_exercises:
        st.subheader("Today's Exercises")
        for exercise in today_exercises:
            st.write(f"• {exercise['type']}: {exercise['duration']} min ({exercise['calories_burned']:.0f} kcal)")

elif page == "Progress Reports":
    st.header("📈 Progress Reports")
    
    if not data["meals"] and not data["exercises"]:
        st.info("No data available yet. Start logging meals and exercises!")
        st.stop()
    
    # Weekly calorie trend
    if data["meals"]:
        meals_df = pd.DataFrame(data["meals"])
        meals_df['date'] = pd.to_datetime(meals_df['date'])
        daily_calories = meals_df.groupby('date')['total_calories'].sum().reset_index()
        
        fig = px.line(daily_calories, x='date', y='total_calories', 
                     title='Daily Calorie Intake Trend')
        st.plotly_chart(fig, use_container_width=True)
    
    # Exercise frequency
    if data["exercises"]:
        exercises_df = pd.DataFrame(data["exercises"])
        exercise_counts = exercises_df['type'].value_counts()
        
        fig = px.pie(values=exercise_counts.values, names=exercise_counts.index,
                    title='Exercise Distribution')
        st.plotly_chart(fig, use_container_width=True)

elif page == "AI Health Coach":
    st.header("🤖 AI Health Coach")
    
    if not data["profile"]:
        st.warning("Please set up your profile first!")
        st.stop()
    
    st.write("Ask your AI health coach anything about nutrition, fitness, or wellness!")
    
    user_question = st.text_input("Your question:")
    
    if st.button("Get AI Advice") and user_question:
        with st.spinner("Thinking..."):
            context = f"""
            User Profile:
            - Age: {data['profile']['age']}
            - Gender: {data['profile']['gender']}
            - Weight: {data['profile']['weight']}kg
            - Height: {data['profile']['height']}cm
            - Goal: {data['profile']['goal']}
            - Activity Level: {data['profile']['activity_level']}
            - Target Calories: {data['profile']['target_calories']:.0f}
            
            Recent Activity:
            - Recent meals logged: {len(data['meals'][-5:])}
            - Recent exercises: {len(data['exercises'][-5:])}
            
            Question: {user_question}
            
            Provide personalized health advice based on the user's profile and question.
            """
            
            response = get_text_response(context)
            st.write(response)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("💡 **Tips:**")
st.sidebar.markdown("• Take clear photos of your meals")
st.sidebar.markdown("• Log exercises regularly")
st.sidebar.markdown("• Check your dashboard daily")
st.sidebar.markdown("• Ask the AI coach for advice")