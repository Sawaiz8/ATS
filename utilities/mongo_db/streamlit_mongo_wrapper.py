import streamlit as st
from main.database import mongo_store
import asyncio
import pandas as pd
import streamlit as st

@st.cache_data(ttl=300)
def get_all_session_names():
    return asyncio.run(mongo_store.get_all_session_names())

@st.cache_data(ttl=300)
def get_session_data(session_name: str):
    return asyncio.run(mongo_store.get_session_data(session_name))


def upsert_volunteers_data(df, session_name, category):
    for index, row in df.iterrows():
        # Get all columns that weren't renamed
        department_specific_columns = {col: row[col] for col in row.index if col not in [
            'timestamp', 'email', 'name', 'age', 'gender', 'phone_number', 'transport',
            'ngo_work', 'city', 'city_address', 'occupation', 'institute', 'CV',
            'insta_id', 'linkedin_id', 'has_discord', 'path_to_pdf'
        ]}
        
        applicant_data = {
            "session_name": session_name,
            "category": category,
            "name": row["name"],
            "age": row["age"], 
            "phone_number": row["phone_number"],
            "email": row["email"],
            "gender": row["gender"],
            "transport": row["transport"],
            "ngo_work": row["ngo_work"],
            "city": row["city"],
            "city_address": row["city_address"],
            "occupation": row["occupation"],
            "institute": row["institute"],
            "department_questions": department_specific_columns,
            "socials_data": {
                "insta_id": row["insta_id"],
                "linkedin_id": row["linkedin_id"],
                "has_discord": row["has_discord"]
            },
            "CV": row["CV"],
            "path_to_pdf": row["path_to_pdf"],
            "timestamp": row["timestamp"],
            "applicant_status": "Under Review"
        }
        asyncio.run(mongo_store.upsert_volunteer_data(applicant_data))


def get_volunteer_data_as_csv(session_name: str, category: str):
    # Get volunteer data from MongoDB
    volunteer_data = asyncio.run(mongo_store.get_all_volunteers_data(session_name, category))
    
    if not volunteer_data:
        return pd.DataFrame()
        
    # Flatten nested dictionaries
    flattened_data = []
    for volunteer in volunteer_data:
        flat_record = {
            "session_name": volunteer["session_name"],
            "category": volunteer["category"], 
            "name": volunteer["name"],
            "age": volunteer["age"],
            "phone_number": volunteer["phone_number"],
            "email": volunteer["email"],
            "gender": volunteer["gender"],
            "transport": volunteer["transport"],
            "ngo_work": volunteer["ngo_work"],
            "city": volunteer["city"],
            "city_address": volunteer["city_address"],
            "occupation": volunteer["occupation"],
            "institute": volunteer["institute"],
            "CV": volunteer["CV"],
            "path_to_pdf": volunteer["path_to_pdf"],
            "timestamp": volunteer["timestamp"],
            "insta_id": volunteer["socials_data"]["insta_id"],
            "linkedin_id": volunteer["socials_data"]["linkedin_id"],
            "has_discord": volunteer["socials_data"]["has_discord"]
        }
        
        # Add department specific questions
        if "department_questions" in volunteer:
            for key, value in volunteer["department_questions"].items():
                flat_record[key] = value

        flat_record["applicant_status"] = volunteer["applicant_status"]
            
        flattened_data.append(flat_record)
    
    # Convert to DataFrame
    df = pd.DataFrame(flattened_data)
    return df

