import os

from flask import Flask, request, render_template
import pickle
from models import Session, Message
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression




app = Flask(__name__)

# Load initial model
vectorizer = None
model = None

def train_model():
    session = Session()
    messages = session.query(Message).all()

    X = [msg.user_message for msg in messages]
    y = [msg.bot_response for msg in messages]
    print(messages)
    if len(set(y)) < 2:
        return None, None

    vectorizer = TfidfVectorizer()
    X_vectors = vectorizer.fit_transform(X)

    model = LogisticRegression()
    model.fit(X_vectors, y)

    return vectorizer, model

def get_bot_response(user_input):
    global vectorizer, model

    if model is None or vectorizer is None:
        return "I'm not trained yet. Please teach me!"

    X = vectorizer.transform([user_input])
    prediction = model.predict(X)[0]

    return prediction

@app.route("/", methods=["GET", "POST"])
def home():
    global vectorizer, model
    session = Session()
    bot_response = ""

    if request.method == "POST":
        user_input = request.form["message"]

        if user_input.startswith("teach:"):
            try:
                # Teaching format: teach: question | answer
                _, teaching = user_input.split("teach:")
                question, answer = teaching.split("|")
                question = question.strip()
                answer = answer.strip()

                # Save to DB
                new_message = Message(user_message=question, bot_response=answer)
                session.add(new_message)
                session.commit()

                # Retrain model
                vectorizer, model = train_model()

                bot_response = f"Learned new pattern! '{question}' → '{answer}'"
            except:
                bot_response = "Wrong teaching format! Use: teach: question | answer"
        else:
            if model is None:
                bot_response = "I'm not trained yet. Please teach me!"
            else:
                bot_response = get_bot_response(user_input)

    return render_template("chat.html", bot_response=bot_response)

if __name__ == "__main__":
    # Initial training
    vectorizer, model = train_model()
    port = int(os.environ.get('PORT', 5000))  
app.run(host='0.0.0.0', port=port)
    # app.run(debug=True)
