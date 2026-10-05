import base64
from io import BytesIO
from flask import Flask, render_template, request

# CRITICAL FOR PYTHONANYWHERE: Use the non-interactive Agg backend
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import wordle_counts as wc

#--------------------------------------------------------------------------------------------
# Initial lists and counts
#--------------------------------------------------------------------------------------------
ans_list = wc.get_answers_for_year(2026)
counts = wc.get_letter_counts(ans_list)

def plot_graph(x_values, y_values, plot_title):
    plt.plot(x_values,y_values)
    # 3. Use plt.gca() to target the y-axis and set the major locator
    plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(10))

    plt.title(plot_title, color="darkblue")
    for x, y in zip(x_values, y_values):
        plt.annotate(f'({x},{y})', xy=(x,y), xytext=(x,y))
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close() # Clear the current figure memory
    buf.seek(0)
    plot_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return plot_base64

app = Flask(__name__)

@app.route('/')
def index():
    letter_counts = [sum(counts[index]) for index, letter in enumerate(wc.letters)]
    plot_title = f"Number of times a letter appeard (counts last updated on {wc.last_date_str}) "
    plot_base64 = plot_graph(wc.letters, letter_counts, plot_title)

    return render_template('index.html', plot_var=plot_base64)

@app.route('/load_custom_counts', methods=['POST'])
def load_custom_counts():
    custom_answers = wc.get_all_answers()
    custom_counts = wc.get_letter_counts(custom_answers)
    letter_counts = [custom_counts[index][0] for index, letter in enumerate(wc.letters)]
    plot_title = f"Number of words beginning with each letter (counts last updated on {wc.last_date_str})"
    plot_base64 = plot_graph(wc.letters, letter_counts, plot_title)

    return render_template('user_input.html', first_page_load="yes", begin_date='2021-06-19', last_date=wc.last_date_val, plot_var=plot_base64)

@app.route('/show_custom_counts', methods=['GET','POST'])
def start_and_end_dates():
    start_date = request.values.get('start_date')
    end_date = request.values.get('end_date')
    letter = request.values.get('letter')
    custom_answers = wc.get_answers_between_dates(start_date, end_date)
    custom_counts = wc.get_letter_counts(custom_answers)
    custom_letter_counts = custom_counts[wc.letters.index(letter)]
    positions = ['first', 'second', 'third', 'fourth', 'last']
    custom_title = f"Showing counts for letter {letter} between dates {start_date} and {end_date}"
    plot_base64 = plot_graph(positions, custom_letter_counts, custom_title)
    

    return render_template('user_input.html', first_page_load="no", begin_date=start_date, last_date=end_date, plot_var=plot_base64)
''' '''

if __name__ == '__main__':
    app.run(debug=True)