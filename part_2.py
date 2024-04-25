from openai import OpenAI
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)


# A Conditional Recommender System
def recommend_fruits(answers):
    allowed_fruits = ['oranges', 'apples', 'pears', 'grapes', 'watermelon', 'lemon', 'lime']

    # Apply rules based on answers
    if answers['party_on_weekends'] == 'yes':
        allowed_fruits = list(set(allowed_fruits) & set(['apples', 'pears', 'grapes', 'watermelon']))

    if answers['flavours'] == 'cider':
        allowed_fruits = list(set(allowed_fruits) & set(['apples', 'oranges', 'lemon', 'lime']))
    elif answers['flavours'] == 'sweet':
        allowed_fruits = list(set(allowed_fruits) & set(['watermelon', 'oranges']))
    elif answers['flavours'] == 'waterlike':
        allowed_fruits = list(set(allowed_fruits) & set(['watermelon']))

    if 'grapes' in allowed_fruits:
        allowed_fruits.remove('watermelon')

    if answers['texture_dislike'] == 'smooth':
        allowed_fruits.remove('pears')
    elif answers['texture_dislike'] == 'slimy':
        allowed_fruits = list(set(allowed_fruits) - set(['watermelon', 'lime', 'grapes']))
    elif answers['texture_dislike'] == 'waterlike':
        allowed_fruits.remove('watermelon')

    price_range = int(answers['price_range'].replace('$', ''))
    if price_range < 3:
        allowed_fruits = list(set(allowed_fruits) - set(['lime', 'watermelon']))
    elif 4 < price_range < 7:
        allowed_fruits = list(set(allowed_fruits) - set(['pears', 'apples']))

    return allowed_fruits

# gpt3 prompting
# Prompt template
prompt_template = """
You have been tasked with creating a recommendation system for fruits based on certain criteria provided by the user. The system will recommend a list of fruits that match the user's preferences.

The system should ask the user the following questions:
1. Do you go out to party on weekends? (yes or no)
2. What flavors do you like? (cider, sweet, waterlike)
3. What texture do you dislike? (smooth, slimy, rough)
4. What price range will you buy a drink for? ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)

Based on the user's answers, the system should apply the following rules to generate the list of recommended fruits:

1. If the user goes out to party on weekends, include apples, pears, grapes, and watermelon.
2. If the user likes cider, include apples, oranges, lemon, and lime.
3. If the user likes sweet flavors, include watermelon and oranges.
4. If the user likes waterlike flavors, include watermelon.
5. If the user chooses grapes, remove watermelon from the list.
6. If the user dislikes smooth texture, remove pears.
7. If the user dislikes slimy texture, remove watermelon, lime, and grapes.
8. If the user dislikes waterlike texture, remove watermelon.
9. If the user's price range is less than $3, remove lime and watermelon.
10. If the user's price range is between $4 and $7, remove pears and apples.

Now, please generate a list of recommended fruits based on the user's responses to the questions. Please the response should be correct.

User Responses:
{user_response}

Recommended Fruits:
"""

os.environ['OPENAI_API_KEY'] = os.getenv('openai_api_key')

client = OpenAI()

# GPT-3.5 API recommendation

def gpt_recommend(user_response):
    #Todo: Should be generoted with the context/contexts we find by doing semantaic search
    response = client.chat.completions.create(
    model="gpt-3.5-turbo-16k",
    messages = [
    {
        "role": "system",
        "content": prompt_template.format(**user_response),
    }
],
    )
    return response.choices[0].message.content

# Route to get recommendations
@app.route('/recommend_fruits', methods=['POST'])
def get_recommendations():
    data = request.get_json()
    answers = {
        'user_response': data['user_response']
    }
    # using gpt recommendation
    recommended_fruits = gpt_recommend(answers)
    return recommended_fruits


if __name__ == "__main__":
  app.run(host="0.0.0.0", 
    port=4000,
    debug=True,
    threaded=True)