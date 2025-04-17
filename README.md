# Medical Report Analyzer

A comprehensive NLP-based system for processing and analyzing medical reports (lab, radiology, and pathology) from PDFs. The application extracts key diagnostic elements, predicts potential medical conditions, visualizes the data in interactive infographics with detailed clinical context, and provides a medical-focused chat interface powered by a specialized medical language model.

## Features

1. **PDF Processing**: Upload and analyze medical reports in PDF format with intelligent text extraction
2. **Medical Term Extraction**: Automatically identifies key medical terms in reports with clinical context
3. **Section Detection**: Organizes report content into relevant sections for structured analysis
4. **Condition Prediction**: Suggests potential medical conditions based on comprehensive report analysis
5. **Interactive Query System**: Ask specific questions about report content with targeted answers
6. **Medical Chat Interface**: Conversational AI using the specialized Llama3-ELAINE-medLLM model
7. **Enhanced Infographic Generation**: Downloadable visual summaries with clinical context, including:
   - Clinical history information
   - Imaging techniques used
   - Lesion details and measurements
   - Contrast agent information
   - Brain and vascular findings
   - Organized differential diagnoses
   - Management recommendations

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
- Medical terms identified in the report with definitions
- Potential medical conditions detected with confidence levels

### 3. Using the Medical Chat

1. Click "Chat About This Report" or navigate to the Chat tab
2. Enter questions about your medical report in the chat interface
3. The AI assistant will respond with medically-focused answers using the Llama3-ELAINE-medLLM model

Example questions:
- "What do the abbreviations in my report mean?"
- "Explain the significance of the findings in the impression section"
- "What are the potential implications of the values shown in the report?"
- "What should I ask my doctor about these results?"

### 4. Generating Enhanced Infographics

1. Click "Generate Infographic" or navigate to the Infographic tab
2. View comprehensive visual representations of your report data, including:
   - Clinical history
   - Imaging techniques used
   - Lesion measurements and locations
   - Visual indicators of brain and vascular findings
   - Differential diagnoses organized by probability
   - Management recommendations
3. Use the "Download Infographic" button to save the image for sharing with healthcare providers

### 5. Asking Specific Questions

1. Click "Ask Questions" or navigate to the Query tab
2. Type a specific question about the report content
3. Get a targeted response about that specific aspect of the report

## Developer Documentation

### Core Architecture

The Medical Report Analyzer follows a modular architecture with clear separation of concerns:

1. **Web Layer**: Flask-based web application handling HTTP requests, rendering templates, and managing user sessions
2. **Service Layer**: Core business logic for processing medical reports and generating analyses
3. **Repository Layer**: Data storage and retrieval (in-memory for the current implementation)
4. **Integration Layer**: External API communications (Hugging Face API for the medical LLM)

### Detailed File Structure and Component Descriptions

```
medical-report-analyzer/
├── app.py                 # Flask application initialization and configuration
├── main.py                # Entry point importing the Flask app
├── run.py                 # Server execution script with Gunicorn configuration
├── routes/                # API and URL route handlers
│   ├── __init__.py        # Package initialization
│   └── main_routes.py     # Main route handlers for all application endpoints
├── templates/             # Jinja2 HTML templates
│   ├── base.html          # Base template with common layout elements
│   ├── index.html         # Home page with file upload functionality
│   ├── results.html       # Analysis results display
│   ├── query.html         # Query interface for asking specific questions
│   ├── chat.html          # Interactive chat interface with medical LLM
│   └── infographic.html   # Enhanced infographic generation and display
├── static/                # Static assets
│   ├── css/               # CSS stylesheets
│   │   └── custom.css     # Custom styling for the application
│   └── js/                # JavaScript files
│       └── main.js        # Client-side functionality
└── utils/                 # Utility functions and core business logic
    ├── __init__.py        # Package initialization
    ├── pdf_processor.py   # PDF text extraction functionality
    ├── nlp_processor.py   # Text processing and medical term extraction
    ├── condition_predictor.py  # Medical condition prediction algorithms
    ├── data_enricher.py   # Data enrichment with medical context
    ├── chat_processor.py  # Chat functionality using the medical LLM
    └── infographic_generator.py  # Enhanced visualization generation
```

### Detailed Component Descriptions

#### Core Application Files

1. **app.py**
   - **Purpose**: Initializes and configures the Flask application
   - **Key Functions**:
     - Flask application creation and configuration
     - Environment variable configuration
     - Logging setup
   - **Dependencies**: Flask, os, logging

2. **main.py**
   - **Purpose**: Entry point that imports the Flask app
   - **Key Functions**:
     - Imports the Flask application from app.py
   - **Dependencies**: app.py

3. **run.py**
   - **Purpose**: Launches the application server
   - **Key Functions**:
     - Configures Gunicorn server parameters
     - Starts the Flask application
   - **Dependencies**: app.py, gunicorn

#### Routes

1. **routes/main_routes.py**
   - **Purpose**: Defines all HTTP routes and controllers
   - **Key Functions**:
     - `index()`: Renders the home page
     - `upload_file()`: Handles file uploads and processing
     - `show_results()`: Displays analysis results
     - `query_page()`: Renders the query interface
     - `query_report()`: Processes report queries
     - `chat_page()`: Renders the chat interface
     - `chat_with_medical_report()`: Processes chat messages
     - `infographic_page()`: Generates and displays infographics
   - **Dependencies**: Flask, utils modules

#### Utility Modules

1. **utils/pdf_processor.py**
   - **Purpose**: Extracts text from PDF medical reports
   - **Key Functions**:
     - `extract_text_from_pdf()`: Converts PDF content to text
   - **Technologies**: PyPDF2
   - **Logic**: Uses PDF parsing to extract raw text while handling common PDF formatting issues

2. **utils/nlp_processor.py**
   - **Purpose**: Processes medical text to extract meaningful information
   - **Key Functions**:
     - `identify_medical_terms()`: Identifies medical terminology
     - `extract_text_embeddings()`: Generates text embeddings (when available)
     - `extract_report_sections()`: Divides reports into logical sections
     - `process_text()`: Main orchestration function for text analysis
     - `process_query()`: Handles specific queries about the report
   - **Technologies**: Regular expressions, pattern matching, NLP techniques
   - **Logic**: Uses a combination of pattern matching, regular expressions, and NLP techniques to extract medical terms, divide text into sections, and identify relationships between concepts

3. **utils/condition_predictor.py**
   - **Purpose**: Predicts potential medical conditions based on report content
   - **Key Functions**:
     - `predict_conditions()`: Generates a list of potential conditions
   - **Logic**: Analyzes report text for known patterns and medical terminology that indicate specific conditions, utilizing a knowledge base of condition-symptom relationships

4. **utils/data_enricher.py**
   - **Purpose**: Enhances raw data with medical context and reference information
   - **Key Functions**:
     - `enrich_data()`: Adds medical definitions, reference ranges, etc.
   - **Logic**: Combines extracted medical terms with reference data to provide context and explanations

5. **utils/chat_processor.py**
   - **Purpose**: Handles conversational interactions about medical reports
   - **Key Functions**:
     - `prepare_chat_prompt()`: Creates context-rich prompts for the LLM
     - `chat_with_report()`: Processes chat messages with medical context
     - `generate_fallback_response()`: Creates responses when the LLM is unavailable
   - **Technologies**: Hugging Face API, prompt engineering
   - **Logic**: Constructs detailed prompts that include report context, identified medical terms, and conditions, then sends these to the Llama3-ELAINE-medLLM model for specialized medical responses

6. **utils/infographic_generator.py**
   - **Purpose**: Creates visual representations of medical report data
   - **Key Functions**:
     - `generate_medical_terms_chart()`: Visualizes medical term frequencies
     - `generate_section_breakdown_chart()`: Charts report section distribution
     - `generate_conditions_chart()`: Visualizes potential conditions
     - `extract_clinical_history()`: Extracts patient history information
     - `extract_imaging_techniques()`: Identifies imaging methods used
     - `extract_measurements()`: Pulls size measurements from the report
     - `extract_contrast_info()`: Finds contrast agent information
     - `extract_key_findings()`: Identifies critical findings
     - `generate_full_infographic()`: Orchestrates the complete infographic creation
   - **Technologies**: Matplotlib, Plotly, NumPy, Seaborn, base64 encoding
   - **Logic**: Analyzes report data to extract clinical context, then generates multiple visualizations that are combined into a comprehensive infographic with downloadable capabilities

#### Templates

1. **templates/base.html**
   - **Purpose**: Provides the common layout and structure for all pages
   - **Features**: Responsive design, navigation, Bootstrap integration

2. **templates/index.html**
   - **Purpose**: Home page with file upload functionality
   - **Features**: Drag-and-drop file uploads, form validation

3. **templates/results.html**
   - **Purpose**: Displays the analysis results
   - **Features**: Accordion sections, medical term highlighting, condition cards

4. **templates/query.html**
   - **Purpose**: Interface for asking specific questions
   - **Features**: Query form, response formatting

5. **templates/chat.html**
   - **Purpose**: Interactive chat interface
   - **Features**: Real-time chat UI, message history, typing indicators

6. **templates/infographic.html**
   - **Purpose**: Displays and allows downloading of enhanced infographics
   - **Features**: Dynamic chart generation, clinical context sections, download functionality

#### Static Assets

1. **static/css/custom.css**
   - **Purpose**: Custom styling for the application
   - **Features**: Medical-themed color schemes, responsive design enhancements

2. **static/js/main.js**
   - **Purpose**: Client-side functionality
   - **Features**: AJAX requests, dynamic UI updates, form handling

## Data Flow Diagram

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│  User Interface │ ──────> │   Flask Routes  │ ──────> │  PDF Processor  │
│                 │         │                 │         │                 │
└─────────────────┘         └─────────────────┘         └────────┬────────┘
                                                                  │
                                                                  ▼
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│  Data Enricher  │ <────── │ NLP Processor   │ <────── │   Extracted    │
│                 │         │                 │         │     Text        │
└────────┬────────┘         └─────────────────┘         └─────────────────┘
         │
         ▼
┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │
│    Condition    │ ──────> │  Processed Data │
│    Predictor    │         │    Repository   │
│                 │         │                 │
└─────────────────┘         └────────┬────────┘
                                     │
                                     ▼
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│ Chat Processor  │ <────── │  User Queries/  │ <────── │ User Interface  │
│                 │         │     Chat        │         │                 │
└────────┬────────┘         └─────────────────┘         └─────────────────┘
         │
         ▼
┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │
│  Llama3-ELAINE  │ ──────> │    Response     │
│    medLLM API   │         │  Generation     │
│                 │         │                 │
└─────────────────┘         └────────┬────────┘
                                     │
                                     ▼
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│  Infographic    │ ──────> │  Visualization  │ ──────> │ User Interface  │
│   Generator     │         │    Rendering    │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
```

## Sequence Diagram

```
┌─────┐          ┌──────────┐          ┌───────────┐          ┌──────────┐          ┌──────────┐          ┌──────────┐
│User │          │Web Routes│          │PDF         │          │NLP        │          │Condition  │          │Data       │
│     │          │          │          │Processor   │          │Processor  │          │Predictor │          │Enricher   │
└──┬──┘          └────┬─────┘          └─────┬─────┘          └─────┬─────┘          └────┬─────┘          └────┬─────┘
   │                  │                      │                      │                      │                     │
   │ Upload PDF       │                      │                      │                      │                     │
   │─────────────────>│                      │                      │                      │                     │
   │                  │                      │                      │                      │                     │
   │                  │ Extract Text         │                      │                      │                     │
   │                  │─────────────────────>│                      │                      │                     │
   │                  │                      │                      │                      │                     │
   │                  │                      │ Return Text          │                      │                     │
   │                  │<─────────────────────│                      │                      │                     │
   │                  │                      │                      │                      │                     │
   │                  │ Process Text         │                      │                      │                     │
   │                  │──────────────────────────────────────────────>                    │                     │
   │                  │                      │                      │                      │                     │
   │                  │                      │                      │ Return Terms/Sections│                     │
   │                  │<──────────────────────────────────────────────                    │                     │
   │                  │                      │                      │                      │                     │
   │                  │ Predict Conditions   │                      │                      │                     │
   │                  │─────────────────────────────────────────────────────────────────>│                     │
   │                  │                      │                      │                      │                     │
   │                  │                      │                      │                      │ Return Conditions   │
   │                  │<─────────────────────────────────────────────────────────────────│                     │
   │                  │                      │                      │                      │                     │
   │                  │ Enrich Data          │                      │                      │                     │
   │                  │────────────────────────────────────────────────────────────────────────────────────>    │
   │                  │                      │                      │                      │                     │
   │                  │                      │                      │                      │                     │ Return Enriched Data
   │                  │<────────────────────────────────────────────────────────────────────────────────────    │
   │                  │                      │                      │                      │                     │
   │ Show Results     │                      │                      │                      │                     │
   │<─────────────────│                      │                      │                      │                     │
   │                  │                      │                      │                      │                     │
┌──┴──┐          ┌────┴─────┐          ┌─────┴─────┐          ┌─────┴─────┐          ┌────┴─────┐          ┌────┴─────┐
│User │          │Web Routes│          │PDF         │          │NLP        │          │Condition  │          │Data       │
│     │          │          │          │Processor   │          │Processor  │          │Predictor │          │Enricher   │
└─────┘          └──────────┘          └───────────┘          └───────────┘          └──────────┘          └──────────┘

┌─────┐          ┌──────────┐          ┌───────────┐          ┌──────────┐          ┌──────────┐          ┌──────────┐
│User │          │Web Routes│          │Chat       │          │LLama3    │          │Infographic│          │Template  │
│     │          │          │          │Processor  │          │medLLM API│          │Generator  │          │Renderer  │
└──┬──┘          └────┬─────┘          └─────┬─────┘          └─────┬────┘          └────┬─────┘          └────┬─────┘
   │                  │                      │                      │                     │                     │
   │ Ask Question     │                      │                      │                     │                     │
   │─────────────────>│                      │                      │                     │                     │
   │                  │                      │                      │                     │                     │
   │                  │ Process Query        │                      │                     │                     │
   │                  │─────────────────────>│                      │                     │                     │
   │                  │                      │                      │                     │                     │
   │                  │                      │ Generate LLM Prompt  │                     │                     │
   │                  │                      │─────────────────────>│                     │                     │
   │                  │                      │                      │                     │                     │
   │                  │                      │                      │ Return Response     │                     │
   │                  │                      │<─────────────────────│                     │                     │
   │                  │                      │                      │                     │                     │
   │                  │ Return Answer        │                      │                     │                     │
   │                  │<─────────────────────│                      │                     │                     │
   │                  │                      │                      │                     │                     │
   │ Show Answer      │                      │                      │                     │                     │
   │<─────────────────│                      │                      │                     │                     │
   │                  │                      │                      │                     │                     │
   │ Request          │                      │                      │                     │                     │
   │ Infographic      │                      │                      │                     │                     │
   │─────────────────>│                      │                      │                     │                     │
   │                  │                      │                      │                     │                     │
   │                  │ Generate Infographic │                      │                     │                     │
   │                  │───────────────────────────────────────────────────────────────>│                     │
   │                  │                      │                      │                     │                     │
   │                  │                      │                      │                     │ Return Infographic  │
   │                  │<──────────────────────────────────────────────────────────────│                     │
   │                  │                      │                      │                     │                     │
   │                  │ Render Template      │                      │                     │                     │
   │                  │────────────────────────────────────────────────────────────────────────────────────>   │
   │                  │                      │                      │                     │                     │
   │                  │                      │                      │                     │                     │ Return HTML
   │                  │<────────────────────────────────────────────────────────────────────────────────────   │
   │                  │                      │                      │                     │                     │
   │ Display          │                      │                      │                     │                     │
   │ Infographic      │                      │                      │                     │                     │
   │<─────────────────│                      │                      │                     │                     │
   │                  │                      │                      │                     │                     │
   │ Download         │                      │                      │                     │                     │
   │ Infographic      │                      │                      │                     │                     │
   │─────────────────>│                      │                      │                     │                     │
   │                  │                      │                      │                     │                     │
   │ Image File       │                      │                      │                     │                     │
   │<─────────────────│                      │                      │                     │                     │
   │                  │                      │                      │                     │                     │
┌──┴──┐          ┌────┴─────┐          ┌─────┴─────┐          ┌─────┴────┐          ┌────┴─────┐          ┌────┴─────┐
│User │          │Web Routes│          │Chat       │          │LLama3    │          │Infographic│          │Template  │
│     │          │          │          │Processor  │          │medLLM API│          │Generator  │          │Renderer  │
└─────┘          └──────────┘          └───────────┘          └──────────┘          └──────────┘          └──────────┘
```

## Internal Data Model

The application uses a structured in-memory data model to represent processed medical reports:

```
Report
├── id                     # Unique identifier for the report
├── filename               # Original filename
├── original_text          # Raw text extracted from the PDF
├── upload_time            # Timestamp of upload
├── processed_data         # Processed information about the report
│   ├── medical_terms      # List of identified medical terms
│   ├── sections           # Dictionary of report sections
│   └── embeddings         # Text embeddings (when available)
├── conditions             # List of predicted medical conditions
└── enriched_data          # Enriched information
    ├── term_definitions   # Definitions of medical terms
    ├── condition_info     # Information about conditions
    └── reference_ranges   # Reference ranges for values
```

## Enhanced Infographic Structure

The enhanced infographic includes the following components:

```
Infographic
├── terms_chart           # Visualization of medical terms
│   ├── image             # Base64 encoded image
│   └── html              # Interactive HTML version (Plotly)
├── sections_chart        # Visualization of report sections
│   ├── image             # Base64 encoded image
│   └── html              # Interactive HTML version (Plotly)
├── conditions_chart      # Visualization of conditions
│   ├── image             # Base64 encoded image
│   └── html              # Interactive HTML version (Plotly)
└── clinical_context      # Extracted clinical information
    ├── history           # Patient clinical history
    ├── techniques        # Imaging techniques used
    ├── measurements      # Lesion measurements and locations
    ├── contrast          # Contrast agent information
    ├── key_findings      # Important findings from the report
    ├── primary_condition # Main suspected condition
    └── secondary_conditions # Other possible conditions
```

## Troubleshooting

### Common Issues

1. **PDF Upload Failures**
   - Ensure the PDF is not password-protected
   - Check that the file is a valid PDF format
   - Verify the PDF contains extractable text (not just scanned images)

2. **Chat Feature Not Working**
   - Verify that your Hugging Face API key is valid
   - Check that you have an active internet connection
   - Confirm the Hugging Face model endpoint is operational

3. **Visualization Issues**
   - Make sure matplotlib, numpy, and plotly are properly installed
   - Try refreshing the page if charts don't appear
   - Check browser console for JavaScript errors

4. **Clinical Context Extraction Issues**
   - The system works best with standardized report formats
   - Non-standard formatting may result in incomplete context extraction
   - Try uploading reports from major medical institutions for best results

## Performance Considerations

- **Memory Usage**: The application stores processed reports in memory. With large volumes of reports, consider implementing a database backend.
- **API Rate Limits**: The Hugging Face API has rate limits. In high-traffic environments, consider caching common responses.
- **Chart Generation**: Generating visualizations can be CPU-intensive. For production environments, consider pre-generating or caching charts.

## Security Considerations

- **PHI Handling**: The application processes potentially sensitive medical information. Ensure compliance with relevant regulations (HIPAA, GDPR, etc.).
- **API Key Protection**: Protect the Hugging Face API key using proper environment variable handling.
- **Input Validation**: All user inputs are validated to prevent injection attacks.

## Limitations

- The application runs best with standard medical report formats
- Advanced NLP features require working internet connection for API access
- The condition prediction is for informational purposes only and not a substitute for professional medical diagnosis
- Clinical context extraction relies on pattern recognition and may miss non-standard information

## Future Development

- Database integration for persistent storage
- User accounts and report history
- Integration with electronic health record (EHR) systems
- More sophisticated medical condition prediction using fine-tuned medical AI models
- Support for additional languages beyond English
- Mobile application for on-the-go report analysis

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Utilizes the Llama3-ELAINE-medLLM model from Hugging Face for specialized medical conversations
- Uses Bootstrap for responsive frontend styling
- Enhanced visualization powered by Matplotlib and Plotly
- Clinical context extraction powered by advanced regular expression patterns