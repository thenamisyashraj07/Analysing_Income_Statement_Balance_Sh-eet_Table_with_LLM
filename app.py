import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from utils.table_extraction import extract_tables_from_pdf
from utils.summarization import initialize_llm_pipeline, summarize_table

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

# Create uploads directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure secret key
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize the LLM pipeline once to avoid reloading for each request
llm_pipeline = initialize_llm_pipeline()

def allowed_file(filename):
    """
    Checks if the uploaded file is allowed based on its extension.
    
    Args:
        filename (str): Name of the uploaded file.
        
    Returns:
        bool: True if allowed, False otherwise.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Handles the main page where users can upload PDFs.
    
    GET: Renders the upload form.
    POST: Processes the uploaded PDF, extracts tables, summarizes them, and displays the results.
    
    Returns:
        Rendered HTML template.
    """
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'pdf_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['pdf_file']
        # If user does not select file, browser may submit an empty file without a name
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            flash('File successfully uploaded and processed!')

            # Extract tables
            dfs, table_html = extract_tables_from_pdf(filepath)
            tables_data = []
            summaries = []

            if dfs:
                for idx, df in enumerate(dfs):
                    table_text = df.to_string(index=False)
                    summary = summarize_table(llm_pipeline, table_text)
                    tables_data.append(df.to_html(classes='table table-striped', index=False))
                    summaries.append(summary)
            else:
                flash('No tables found in the uploaded PDF.')
                tables_data = []
                summaries = []

            return render_template('index.html', tables=tables_data, summaries=summaries)
        else:
            flash('Allowed file type is PDF')
            return redirect(request.url)

    return render_template('index.html')

if _name_ == '_main_':
    app.run(debug=True)