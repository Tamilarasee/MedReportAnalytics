import os
import uuid
import logging
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from utils.pdf_processor import extract_text_from_pdf
from utils.nlp_processor import process_text
from utils.condition_predictor import predict_conditions
from utils.data_enricher import enrich_data
from utils.chat_processor import chat_with_report
from utils.infographic_generator import generate_full_infographic
import datetime

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
main_bp = Blueprint('main', __name__)

# Temporary storage for processed reports
# In a production environment, this would be replaced with a database
reports_data = {}

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        try:
            # Create a unique ID for this report
            report_id = str(uuid.uuid4())
            
            # Process the PDF
            extracted_text = extract_text_from_pdf(file)
            
            if not extracted_text:
                flash('Could not extract text from the PDF. Please try another file.', 'danger')
                return redirect(url_for('main.index'))
            
            # Process the text with NLP
            processed_data = process_text(extracted_text)
            
            # Predict conditions
            conditions = predict_conditions(processed_data)
            
            # Enrich the data
            enriched_data = enrich_data(processed_data, conditions)
            
            # Store the processed data
            reports_data[report_id] = {
                'original_text': extracted_text,
                'processed_data': processed_data,
                'conditions': conditions,
                'enriched_data': enriched_data,
                'filename': secure_filename(file.filename)
            }
            
            # Store the report ID in the session
            session['current_report_id'] = report_id
            
            return redirect(url_for('main.show_results', report_id=report_id))
            
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            flash(f'Error processing file: {str(e)}', 'danger')
            return redirect(url_for('main.index'))
    else:
        flash('Only PDF files are allowed', 'warning')
        return redirect(url_for('main.index'))

@main_bp.route('/results/<report_id>')
def show_results(report_id):
    if report_id not in reports_data:
        flash('Report not found', 'danger')
        return redirect(url_for('main.index'))
    
    report = reports_data[report_id]
    return render_template('results.html', 
                          report=report, 
                          report_id=report_id)

@main_bp.route('/query/<report_id>')
def query_page(report_id):
    if report_id not in reports_data:
        flash('Report not found', 'danger')
        return redirect(url_for('main.index'))
    
    return render_template('query.html', report_id=report_id)

@main_bp.route('/api/query', methods=['POST'])
def query_report():
    data = request.json
    report_id = data.get('report_id')
    query = data.get('query')
    
    if not report_id or not query:
        return jsonify({'error': 'Missing report ID or query'}), 400
    
    if report_id not in reports_data:
        return jsonify({'error': 'Report not found'}), 404
    
    try:
        report = reports_data[report_id]
        
        # Process the query using the NLP processor
        from utils.nlp_processor import process_query
        
        answer = process_query(query, report['processed_data'], report['conditions'], report['enriched_data'])
        
        return jsonify({
            'answer': answer,
            'query': query
        })
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return jsonify({'error': f'Error processing query: {str(e)}'}), 500
        
@main_bp.route('/chat/<report_id>')
def chat_page(report_id):
    """
    Render the chat interface for having a conversation about the medical report.
    """
    if report_id not in reports_data:
        flash('Report not found', 'danger')
        return redirect(url_for('main.index'))
    
    return render_template('chat.html', report_id=report_id)

@main_bp.route('/api/chat', methods=['POST'])
def chat_with_medical_report():
    """
    Process a chat message about the medical report using the medical LLM.
    """
    data = request.json
    report_id = data.get('report_id')
    message = data.get('message')
    
    if not report_id or not message:
        return jsonify({'error': 'Missing report ID or message'}), 400
    
    if report_id not in reports_data:
        return jsonify({'error': 'Report not found'}), 404
    
    try:
        report = reports_data[report_id]
        
        # Process the message using the chat processor
        response = chat_with_report(message, report)
        
        return jsonify({
            'response': response,
            'message': message
        })
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        return jsonify({'error': f'Error processing your message: {str(e)}'}), 500

@main_bp.route('/infographic/<report_id>')
def infographic_page(report_id):
    """
    Generate and render an infographic for the medical report.
    """
    if report_id not in reports_data:
        flash('Report not found', 'danger')
        return redirect(url_for('main.index'))
    
    try:
        report = reports_data[report_id]
        
        # Generate the infographic
        infographic = generate_full_infographic(report)
        
        # Get current date for the template
        now = datetime.datetime.now()
        
        return render_template('infographic.html', 
                              report=report, 
                              report_id=report_id,
                              infographic=infographic,
                              now=now)
    except Exception as e:
        logger.error(f"Error generating infographic: {str(e)}")
        flash(f'Error generating infographic: {str(e)}', 'danger')
        return redirect(url_for('main.show_results', report_id=report_id))
