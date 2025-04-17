# Medical Report Analyzer

A comprehensive tool for processing and analyzing medical reports (lab, radiology, and pathology) from PDFs. The system extracts key diagnostic elements, predicts potential medical conditions, visualizes the data in interactive infographics, and provides a medical-focused chat interface.

## Features

1. **PDF Processing**: Upload and analyze medical reports in PDF format
2. **Medical Term Extraction**: Automatically identifies key medical terms in reports
3. **Section Detection**: Organizes report content into relevant sections
4. **Condition Prediction**: Suggests potential medical conditions based on report analysis
5. **Interactive Query System**: Ask specific questions about report content
6. **Medical Chat Interface**: Conversational AI using the Llama3-ELAINE-medLLM model
7. **Infographic Generation**: Downloadable visual summaries of report analysis

## Setup and Installation

### Prerequisites

- Python 3.8+
- pip (Python package installer)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/medical-report-analyzer.git
   cd medical-report-analyzer
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - `HUGGINGFACE_API_KEY`: Required for the advanced medical chat feature
   - `SESSION_SECRET`: Recommended for session security (can be any random string)

   Create a `.env` file in the root directory:
   ```
   HUGGINGFACE_API_KEY=your_huggingface_api_key
   SESSION_SECRET=your_secret_key
   ```

5. Run the application:
   ```
   python run.py
   ```
   
   The application will be available at http://localhost:5000

## Usage Guide

### 1. Uploading a Medical Report

1. Navigate to the home page
2. Click the "Choose File" button to select a PDF medical report
3. Click "Upload and Analyze" to process the report

### 2. Viewing Report Analysis

After uploading, you'll be redirected to the Results page, which includes:
- Basic report information and extracted sections
- Medical terms identified in the report
- Potential medical conditions detected

### 3. Using the Medical Chat

1. Click "Chat About This Report" or navigate to the Chat tab
2. Enter questions about your medical report in the chat interface
3. The AI assistant will respond with medically-focused answers

Example questions:
- "What do the abbreviations in my report mean?"
- "Explain the significance of the findings in the impression section"
- "What are the potential implications of the values shown in the report?"

### 4. Generating Infographics

1. Click "Generate Infographic" or navigate to the Infographic tab
2. View visual representations of your report data
3. Use the "Download Infographic" button to save the image

### 5. Asking Specific Questions

1. Click "Ask Questions" or navigate to the Query tab
2. Type a specific question about the report content
3. Get a targeted response about that specific aspect

## API Integration

The Medical Report Analyzer uses the following external services:

1. **Hugging Face**: The chat feature uses the "kenyano/Llama3-ELAINE-medLLM-instruct-8B_v0.1" model - requires a Hugging Face API key

## File Structure

```
medical-report-analyzer/
├── app.py                 # Flask app initialization
├── main.py                # Entry point
├── routes/                # API and URL routes
│   ├── __init__.py
│   └── main_routes.py     # Route handlers
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── index.html         # Home page
│   ├── results.html       # Analysis results
│   ├── query.html         # Query interface
│   ├── chat.html          # Chat interface
│   └── infographic.html   # Infographic generator
├── static/                # Static assets
│   ├── css/
│   └── js/
└── utils/                 # Utility functions
    ├── __init__.py
    ├── pdf_processor.py   # PDF text extraction
    ├── nlp_processor.py   # Text processing
    ├── condition_predictor.py  # Medical condition prediction
    ├── data_enricher.py   # Data enrichment
    ├── chat_processor.py  # Chat functionality
    └── infographic_generator.py  # Visualization
```

## Troubleshooting

### Common Issues

1. **PDF Upload Failures**
   - Ensure the PDF is not password-protected
   - Check that the file is a valid PDF format

2. **Chat Feature Not Working**
   - Verify that your Hugging Face API key is valid
   - Check that you have an active internet connection

3. **Visualization Issues**
   - Make sure matplotlib, numpy, and plotly are properly installed
   - Try refreshing the page if charts don't appear

## Limitations

- The application runs best with standard medical report formats
- Advanced NLP features require working internet connection for API access
- The condition prediction is for informational purposes only and not a substitute for professional medical advice

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Utilizes the Llama3-ELAINE-medLLM model from Hugging Face
- Uses Bootstrap for frontend styling
- Visualization powered by Matplotlib and Plotly