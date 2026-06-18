import { useState, useRef } from 'react';
import { UploadCloud, FileType, CheckCircle, AlertCircle, Download } from 'lucide-react';

function App() {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isConverting, setIsConverting] = useState(false);
  const [status, setStatus] = useState(null); // 'success', 'error', null
  const [errorMessage, setErrorMessage] = useState('');
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type === 'application/pdf') {
        setFile(droppedFile);
        setStatus(null);
      } else {
        setStatus('error');
        setErrorMessage('Please upload a valid PDF file.');
      }
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setStatus(null);
    }
  };

  const handleConvert = async () => {
    if (!file) return;

    setIsConverting(true);
    setStatus(null);
    setErrorMessage('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/convert', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Conversion failed');
      }

      // Handle the file download
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = file.name.replace('.pdf', '.dxf');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(downloadUrl);

      setStatus('success');
    } catch (error) {
      console.error("Error during conversion:", error);
      setStatus('error');
      setErrorMessage(error.message || 'An unexpected error occurred.');
    } finally {
      setIsConverting(false);
    }
  };

  return (
    <div className="app-container">
      <header className="header" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <img 
          src="https://i.imgur.com/yaBZ6oX.png" 
          alt="ANV Logo" 
          style={{ height: '80px', marginBottom: '1rem', animation: 'fade-in-up 0.6s ease-out' }} 
        />
        <h1>PDF to CAD Converter</h1>
        <p>Transform your technical drawings into editable DXF files instantly.</p>
      </header>

      <main className="glass-panel">
        <div 
          className={`drop-zone ${isDragging ? 'active' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current.click()}
        >
          <UploadCloud className="upload-icon" />
          <h3>Drag & Drop your PDF here</h3>
          <p>or click to browse</p>
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileSelect} 
            accept="application/pdf"
            style={{ display: 'none' }} 
          />
        </div>

        {file && (
          <div className="file-info">
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <FileType size={24} color="var(--primary)" />
              <span style={{ fontWeight: 500 }}>{file.name}</span>
            </div>
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </span>
          </div>
        )}

        <button 
          className="btn-convert" 
          onClick={handleConvert} 
          disabled={!file || isConverting}
        >
          {isConverting ? (
            <>
              <div className="loader"></div>
              Converting to DXF...
            </>
          ) : (
            <>
              Convert Now
            </>
          )}
        </button>

        {status === 'success' && (
          <div className="status-message success" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
            <CheckCircle size={20} />
            Conversion successful! Your DXF file is downloading.
          </div>
        )}

        {status === 'error' && (
          <div className="status-message error" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
            <AlertCircle size={20} />
            {errorMessage}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
