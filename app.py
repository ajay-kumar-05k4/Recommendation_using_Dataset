from flask import Flask, render_template, request
from recommender import recommend

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        try:
            customer_id = int(request.form["customer_id"])
            result = recommend(customer_id)
        except ValueError:
            result = {"error": "Customer ID must be a number"}
        except Exception as e:
            result = {"error": f"Server error: {str(e)}"}

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
