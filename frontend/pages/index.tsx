'use client';
import { useState } from 'react';

export default function CVAnalyzer() {
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [cvText, setCvText] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.type !== 'application/pdf') {
        setError('Please upload a PDF file');
        return;
      }
      
      setCvFile(file);
      setError('');
      
      // Create FormData to send file
      const formData = new FormData();
      formData.append('file', file);
      
      try {
        const response = await fetch('http://localhost:5000/upload-cv', {
          method: 'POST',
          body: formData,
        });
        
        if (!response.ok) throw new Error('Upload failed');
        
        const data = await response.json();
        setCvText(data.text);
      } catch (err) {
        setError('Failed to process PDF');
        console.error(err);
      }
    }
  };

  const analyzeCV = async () => {
    if (!cvText) {
      setError('Please upload a CV first');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('http://localhost:5000/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ cv: cvText, jobDescription }),
      });
      
      if (!response.ok) throw new Error('Analysis failed');
      
      const data = await response.json();
      setAnalysis(data.analysis);
    } catch (err) {
      setError('Analysis failed. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="container mx-auto p-4 max-w-6xl">
      <h1 className="text-3xl font-bold mb-6">CV Analyzer</h1>
      
      <div className="grid md:grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block mb-2 font-medium">Upload CV (PDF)</label>
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileUpload}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          {cvText && (
            <div className="mt-4 p-4 border rounded-lg bg-gray-50">
              <h3 className="font-medium mb-2">Extracted Text Preview:</h3>
              <p className="text-sm text-gray-600">{cvText.substring(0, 200)}...</p>
            </div>
          )}
        </div>
        
        <div>
          <label className="block mb-2 font-medium">Job Description</label>
          <textarea
            className="w-full h-64 p-2 border rounded-lg"
            placeholder="Paste the job description here..."
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
          />
        </div>
      </div>

      {error && (
        <div className="mb-4 p-4 text-red-700 bg-red-100 rounded-lg">
          {error}
        </div>
      )}

      <button
        className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 mb-6 disabled:opacity-50"
        onClick={analyzeCV}
        disabled={loading || !cvText || !jobDescription}
      >
        {loading ? 'Analyzing...' : 'Analyze CV'}
      </button>

      {analysis && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-bold mb-4">Matching Skills</h2>
            <ul className="list-disc pl-5">
              {analysis.matching_skills.map((skill: string, index: number) => (
                <li key={index} className="text-green-600">{skill}</li>
              ))}
            </ul>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-bold mb-4">Missing Skills</h2>
            <ul className="list-disc pl-5">
              {analysis.missing_skills.map((skill: string, index: number) => (
                <li key={index} className="text-red-600">{skill}</li>
              ))}
            </ul>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-bold mb-4">Suggestions</h2>
            <ul className="list-disc pl-5">
              {analysis.suggestions.map((suggestion: string, index: number) => (
                <li key={index} className="text-gray-700">{suggestion}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </main>
  );
}