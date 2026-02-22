import streamlit as st
from pymongo import MongoClient

def get_database():
    """
    Get MongoDB database connection.
    Works on both local development and Streamlit Cloud.
    
    On Streamlit Cloud, add secret via app settings:
    mongodb_connection_string = "your_connection_string"
    
    Locally, can use hardcoded string for development.
    """
    try:
        # Try to read from Streamlit secrets (works on both local and cloud)
        CONNECTION_STRING = st.secrets.get("mongodb_connection_string")
        if not CONNECTION_STRING:
            # Fallback if secret not configured
            raise KeyError("MongoDB connection string not found in secrets")
    except (FileNotFoundError, KeyError):
        # Local development fallback
        CONNECTION_STRING = "mongodb+srv://ajaymedaboina9676381509_db_user:Bl9k5WV0RAasxeE0@cluster0.0txhl9g.mongodb.net/"
    
    client = MongoClient(CONNECTION_STRING)
    return client["Ecommerce"]
