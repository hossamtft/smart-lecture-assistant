import { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { uploadLecture } from '../services/api';
import './LectureUpload.css';

interface UploadFormData {
  moduleCode: string;
  weekNumber: number;
  lectureTitle: string;
}

interface UploadResult {
  success: boolean;
  message: string;
  lectureId?: string;
  chunksCreated?: number;
}

export default function LectureUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [formData, setFormData] = useState<UploadFormData>({
    moduleCode: '',
    weekNumber: 1,
    lectureTitle: ''
  });
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<UploadResult | null>(null);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf']
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        setFile(acceptedFiles[0]);
        setResult(null);
      }
    }
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'weekNumber' ? parseInt(value) : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file) {
      setResult({ success: false, message: 'Please select a PDF file' });
      return;
    }

    if (!formData.moduleCode || !formData.lectureTitle) {
      setResult({ success: false, message: 'Please fill in all required fields' });
      return;
    }

    setUploading(true);
    setResult(null);

    try {
      const response = await uploadLecture({
        file,
        module_code: formData.moduleCode.toUpperCase(),
        week_number: formData.weekNumber,
        lecture_title: formData.lectureTitle
      });

      setResult({
        success: true,
        message: `Lecture uploaded successfully! Created ${response.chunks_created} chunks.`,
        lectureId: response.lecture.id,
        chunksCreated: response.chunks_created
      });

      // Reset form
      setFile(null);
      setFormData({
        moduleCode: '',
        weekNumber: 1,
        lectureTitle: ''
      });

    } catch (error: any) {
      setResult({
        success: false,
        message: error.response?.data?.detail || 'Upload failed. Please try again.'
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-container">
      <h2>Upload Lecture PDF</h2>

      <form onSubmit={handleSubmit}>
        {/* File Dropzone */}
        <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''} ${file ? 'has-file' : ''}`}>
          <input {...getInputProps()} />
          {file ? (
            <div className="file-info">
              <span className="file-icon">📄</span>
              <p className="file-name">{file.name}</p>
              <p className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          ) : isDragActive ? (
            <p>Drop the PDF here...</p>
          ) : (
            <div className="dropzone-prompt">
              <span className="upload-icon">📤</span>
              <p>Drag and drop a PDF file here, or click to select</p>
              <p className="dropzone-hint">Max file size: 50MB</p>
            </div>
          )}
        </div>

        {/* Form Fields */}
        <div className="form-fields">
          <div className="form-group">
            <label htmlFor="moduleCode">Module Code *</label>
            <input
              type="text"
              id="moduleCode"
              name="moduleCode"
              placeholder="e.g., COMP3001"
              value={formData.moduleCode}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="weekNumber">Week Number *</label>
            <input
              type="number"
              id="weekNumber"
              name="weekNumber"
              min="1"
              max="24"
              value={formData.weekNumber}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="lectureTitle">Lecture Title *</label>
            <input
              type="text"
              id="lectureTitle"
              name="lectureTitle"
              placeholder="e.g., Introduction to Algorithms"
              value={formData.lectureTitle}
              onChange={handleInputChange}
              required
            />
          </div>
        </div>

        {/* Upload Button */}
        <button
          type="submit"
          className="upload-btn"
          disabled={uploading || !file}
        >
          {uploading ? 'Uploading...' : 'Upload Lecture'}
        </button>
      </form>

      {/* Result Message */}
      {result && (
        <div className={`result-message ${result.success ? 'success' : 'error'}`}>
          <p>{result.message}</p>
          {result.success && result.chunksCreated && (
            <p className="result-detail">
              The lecture has been processed and indexed for search.
            </p>
          )}
        </div>
      )}

      {/* Info Box */}
      <div className="info-box">
        <h3>What happens when you upload?</h3>
        <ol>
          <li>PDF text is extracted (with OCR fallback if needed)</li>
          <li>Content is chunked at slide boundaries</li>
          <li>Embeddings are generated for semantic search</li>
          <li>Lecture is ready for topic detection and Q&A</li>
        </ol>
      </div>
    </div>
  );
}
