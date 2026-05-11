import os
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__) 
# Flask defaults to 'templates' and 'static' (lowercase) in the same directory as this file.
# app.template_folder = r'C:\Users\gabri\OneDrive\Glacier Watch\templates'
# app.static_folder = r'C:\Users\gabri\OneDrive\Glacier Watch\Static'




QUIZ_QS = [
    {
        'id': 1,
        'question': 'Which country has the most glaciers in the Alps?',
        'options': ['Italy', 'Switzerland', 'France', 'Austria'],
        'correct': 1  
    },
    {
        'id': 2,
        'question': 'What percentage of Alpine glaciers have disappeared since 1850?',
        'options': ['30%', '50%', '80%', '95%'],
        'correct': 2  
    },
    {
        'id': 3,
        'question': 'What do you call a large crack in a Glacier?',
        'options': ['A hollow', 'A crack', 'A crevasse', 'A ravine'],
        'correct': 2  
    },
    {
        'id': 4,
        'question': 'How much has global temperature increased since pre-industrial times?',
        'options': ['0.5°C', '1.1°C', '2.5°C', '5°C'],
        'correct': 1  
    },
    {
        'id': 5,
        'question': 'What is the main impact of glacier melting on local communities?',
        'options': ['Decreased tourism', 'Water supply problems', 'Increased water supply', 'Better agriculture'],
        'correct': 1  
    },
    {
        'id': 6,
        'question': 'What do you call the process where a glacier loses mass due to melting?',
        'options': ['Ablation', 'Flux', 'Thawing', 'De-massification'],
        'correct': 0  
    }
]

#home page route
@app.route('/')
def home():
    return render_template('home-page.html')

#quiz page route
@app.route('/quiz')
def quiz():
    return render_template('Quiz.html')

#quiz submitting route
@app.route('/submit-quiz', methods=['POST'])
def submit_quiz():
    answers = request.form
    score = 0
    results = []
    
    #checking answers
    for question in QUIZ_QS:
        q_id = str(question['id'])
        user_answer_index = answers.get(f'question_{q_id}')
        
        if user_answer_index is not None:
            user_answer_index = int(user_answer_index)
            is_correct = user_answer_index == question['correct']
            
            if is_correct:
                score += 1
            
            results.append({
                'question': question['question'],
                'user_answer': question['options'][user_answer_index],
                'correct_answer': question['options'][question['correct']],
                'correct': is_correct
            })
    
    #percentage correct
    total_questions = len(QUIZ_QS)
    percentage = round((score / total_questions) * 100, 1)
    
    #message
    if percentage >= 80:
        message = "Excellent! You really know your stuff!"
    elif percentage >= 60:
        message = "Good job! You have solid knowledge about this topic."
    elif percentage >= 40:
        message = "Not bad! Keep learning more about glaciers and climate change and see how you can make a difference."
    else:
        message = "Keep studying! There's a lot to learn about glaciers and climate."
    
    return render_template('results.html', 
                          score=score, 
                          total_questions=total_questions,
                          percentage=percentage,
                          message=message,
                          results=results)

# Results
@app.route('/results')
def results():
    return render_template('results.html')

# 404
@app.errorhandler(404)
def page_not_found(e):
    return "Page not found", 404

# Run

#ROUTE FOR DATA DISPLAY 
@app.route('/data')
def data():
    conn = sqlite3.connect('alpinewatch.db')
    cursor = conn.cursor()
    
    #glacier data by country
    cursor.execute('''
        SELECT c.country_name, COUNT(DISTINCT g.glacier_id) as glacier_count, 
               AVG(gd.net_mass_balance) as avg_mass_balance
        FROM countries c
        LEFT JOIN glaciers g ON c.country_id = g.country_id
        LEFT JOIN glacier_data gd ON g.glacier_id = gd.glacier_id
        WHERE c.country_name IN ('Switzerland', 'Italy', 'France')
        GROUP BY c.country_name
    ''')
    #small letter calls data by shorter name 
    #First JOIN: Connects countries to glaciers using country_id
    #Second JOIN: Connects glaciers to glacier_data using glacier_id
    #LEFT JOIN specifically keeps all countries even if they have no glaciers
    #Where means only data from the 
    #One row per country thanks to GROUP BY c.country_name
    glacier_stats = cursor.fetchall()
    
    #ghg data
    cursor.execute('''
    SELECT c.country_name, ge.year, ge.emissions_index
    FROM ghg_emissions ge
    JOIN countries c ON ge.country_id = c.country_id
    WHERE c.country_name IN ('Switzerland', 'Italy', 'France')
    ORDER BY c.country_name, ge.year
''')

    ghg_data = cursor.fetchall()
    
    conn.close()
    
    return render_template('data.html', glacier_stats=glacier_stats, ghg_data=ghg_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)


