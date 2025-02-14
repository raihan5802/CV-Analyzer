# CV Analyzer

CV Analyzer is a web application that allows users to upload their CV (in PDF format) and get an analysis of how well it matches a given job description. The application uses Natural Language Processing (NLP) techniques and Large Language Models (LLMs) to extract relevant skills from the CV and job description, and provides feedback on matching skills, missing skills, and suggestions for improvement.

## Features

- Upload CV in PDF format
- Extract text from PDF
- Input job description
- Analyze CV against job description using LLMs
- Fallback analysis using spaCy if LLM fails
- Display matching skills, missing skills, and suggestions
- Clean and responsive UI using Next.js and Tailwind CSS

## Tech Stack

- Frontend:
  - Next.js
  - React
  - TypeScript
  - Tailwind CSS
- Backend:
  - Python
  - Flask
  - Flask CORS
  - PyPDF
  - spaCy
  - Transformers (HuggingFace)

## Getting Started

### Prerequisites

- Node.js and npm (for frontend)
- Python 3.7+ (for backend)

### Installation

1. Clone the repository:
\```
git clone https://github.com/yourusername/cv-analyzer.git
cd cv-analyzer
\```

2. Set up and run the backend:
\```
cd backend
python3 -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
\```

3. Set up and run the frontend:
\```
cd frontend
npm install
npm run dev
\```

4. Open your browser and navigate to `http://localhost:3000` to access the application.

### Folder Structure

- `backend/`: Contains the Flask backend code
  - `app.py`: Main Flask application
  - `uploads/`: Directory for temporary storage of uploaded PDFs
- `frontend/`: Contains the Next.js frontend code
  - `components/`: Contains reusable React components
  - `pages/`: Contains top-level pages of the Next.js application
    - `index.tsx`: Main page of the CV Analyzer application
  - `styles/`: Contains global and module-specific CSS files
  - `public/`: Contains public assets
