from flask import Flask, request, jsonify
from flask_cors import CORS
import pypdf
import os
from werkzeug.utils import secure_filename
import spacy
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

app = Flask(__name__)
CORS(app)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

ALLOWED_EXTENSIONS = {'pdf'}

# Initialize models
print("Loading models...")
model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # Small but effective model
tokenizer = AutoTokenizer.from_pretrained(model_name)
generator = pipeline(
    "text-generation",
    model=model_name,
    tokenizer=tokenizer,
    max_length=1000,
    device_map="auto"  # Will use GPU if available
)
nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(file_path):
    """Extract text from uploaded PDF"""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        return None
    return text

def analyze_with_llm(cv_text, job_description):
    """Analyze CV using local LLM"""
    prompt = f"""
    Analyze this CV against the job description and provide feedback.
    
    CV:
    {cv_text[:1000]}  # Truncate to manage token length
    
    Job Description:
    {job_description[:500]}
    
    Provide analysis in this format:
    Matching Skills:
    Missing Skills:
    Suggestions:
    """
    
    try:
        # Generate analysis
        response = generator(
            prompt,
            max_new_tokens=500,
            do_sample=True,
            temperature=0.7,
            num_return_sequences=1
        )[0]['generated_text']
        
        # Parse response into sections
        sections = response.split("\n\n")
        matching_skills = []
        missing_skills = []
        suggestions = []
        
        for section in sections:
            if "Matching Skills:" in section:
                matching_skills = [skill.strip() for skill in section.replace("Matching Skills:", "").strip().split("\n")]
            elif "Missing Skills:" in section:
                missing_skills = [skill.strip() for skill in section.replace("Missing Skills:", "").strip().split("\n")]
            elif "Suggestions:" in section:
                suggestions = [sugg.strip() for sugg in section.replace("Suggestions:", "").strip().split("\n")]
        
        return {
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "suggestions": suggestions
        }
        
    except Exception as e:
        print(f"Error in LLM analysis: {str(e)}")
        return analyze_with_spacy(cv_text, job_description)

def analyze_with_spacy(cv_text, job_description):
    """Fallback analysis using spaCy"""
    cv_doc = nlp(cv_text)
    job_doc = nlp(job_description)
    
    # Extract skills using NER and pattern matching
    cv_skills = set()
    job_skills = set()
    
    for token in cv_doc:
        if token.pos_ in ['NOUN', 'PROPN'] and len(token.text) > 2:
            cv_skills.add(token.text.lower())
            
    for token in job_doc:
        if token.pos_ in ['NOUN', 'PROPN'] and len(token.text) > 2:
            job_skills.add(token.text.lower())
    
    matching_skills = list(cv_skills & job_skills)
    missing_skills = list(job_skills - cv_skills)
    
    return {
        "matching_skills": matching_skills[:10],
        "missing_skills": missing_skills[:10],
        "suggestions": [
            "Consider adding more specific technical skills",
            "Quantify your achievements with metrics",
            "Align your experience with job requirements"
        ]
    }

@app.route('/upload-cv', methods=['POST'])
def upload_cv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            file.save(filepath)
            text = extract_text_from_pdf(filepath)
            
            # Clean up
            os.remove(filepath)
            
            if text is None:
                return jsonify({'error': 'Failed to extract text from PDF'}), 500
                
            return jsonify({'text': text})
            
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/analyze', methods=['POST'])
def analyze_cv():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    cv_content = data.get('cv')
    job_description = data.get('jobDescription')
    
    if not cv_content or not job_description:
        return jsonify({'error': 'Please provide both CV and job description'}), 400
    
    try:
        analysis = analyze_with_llm(cv_content, job_description)
        return jsonify({"analysis": analysis})
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)