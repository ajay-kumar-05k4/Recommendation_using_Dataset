from config import get_database
import pandas as pd
import ast
import re
from collections import Counter

# Connect to MongoDB Atlas
db = get_database()
collection = db["app"]

# Load data into DataFrame
data = list(collection.find({}, {"_id": 0}))
df = pd.DataFrame(data)

print("Data Loaded Successfully")
print("Total Rows:", len(df))

# ----------------------------
# Parse Purchase History
# ----------------------------
def parse_purchase(history):
    try:
        if isinstance(history, str):
            # If it's a string, try to convert to list format
            history = history.strip()
            
            # If it doesn't start with '[', wrap it
            if not history.startswith('['):
                history = '[' + history + ']'
            
            return ast.literal_eval(history)
        return history if isinstance(history, list) else []
    except Exception as e:
        print(f"Failed to parse: {history[:50]}... Error: {e}")
        return []

df["Purchase History"] = df["Purchase History"].apply(parse_purchase)

# ----------------------------
# Extract Ratings
# ----------------------------
def extract_rating(review):
    try:
        if isinstance(review, str):
            # JSON review case
            if "Rating" in review:
                parsed = ast.literal_eval(review)
                if isinstance(parsed, dict):
                    return float(parsed.get("Rating", 0))

            # Text case like "5 stars"
            match = re.search(r'(\d+(\.\d+)?)', review)
            if match:
                return float(match.group(1))

        return None
    except Exception as e:
        print(f"Warning: Rating extraction failed - {e}")
        return None

df["Rating"] = df["Product Reviews"].apply(extract_rating)

# ----------------------------
# Hybrid Recommendation Function
# ----------------------------
def recommend(customer_id):

    user_data = df[df["Customer ID"] == customer_id]

    if user_data.empty:
        return {"error": "User not found"}

    # 1️⃣ Find Favorite Category
    purchases = []

    for history in user_data["Purchase History"]:
        if isinstance(history, list):
            for item in history:
                # Handle both 'Product Category' and 'Category' keys
                category = item.get("Product Category") or item.get("Category")
                if category:
                    purchases.append(category)

    if not purchases:
        return {"message": "No purchase history found for this customer"}

    favorite_category = Counter(purchases).most_common(1)[0][0]

    # 2️⃣ Find Similar Users (same category buyers) 
    similar_users = df[df["Customer ID"] != customer_id]

    def has_category(history_list):
        if not isinstance(history_list, list):
            return False
        for item in history_list:
            cat = item.get("Product Category") or item.get("Category")
            if cat == favorite_category:
                return True
        return False

    category_users = similar_users[similar_users["Purchase History"].apply(has_category)]

    if category_users.empty:
        return {
            "Favorite Category": favorite_category,
            "Top Recommendations": [],
            "message": "No other customers found in this category"
        }

    # 3️⃣ Sort by Highest Rating - recommend top customers in favorite category
    top_rated = category_users.sort_values(
        by="Rating",
        ascending=False,
        na_position='last'
    ).head(3)

    recommendations = []

    for _, row in top_rated.iterrows():
        recommendations.append({
            "Customer ID": int(row["Customer ID"]),
            "Rating": row["Rating"],
            "Income": int(row.get("Annual Income", 0))
        })

    return {
        "Favorite Category": favorite_category,
        "Top Recommendations": recommendations,
        "Recommendation Type": "Top Customers in Your Favorite Category"
    }
