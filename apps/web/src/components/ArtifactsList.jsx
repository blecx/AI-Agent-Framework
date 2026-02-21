import { useState } from 'react';
import './ArtifactsList.css';
import { api } from '../services/api';

function ArtifactsList({ projectKey, artifacts, onRefresh }) {
  const [selectedArtifact, setSelectedArtifact] = useState(null);
  const [artifactContent, setArtifactContent] = useState('');
  const [artifactRows, setArtifactRows] = useState([]);
  const [artifactImageUrl, setArtifactImageUrl] = useState('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const parseCsv = (content) =>
    content
      .split(/\r?\n/)
      .filter((line) => line.trim() !== '')
      .map((line) => line.split(','));

  const handleArtifactClick = async (artifact) => {
    try {
      setLoading(true);
      setError(null);
      const blob = await api.getArtifactBlob(projectKey, artifact.path);
      const lowerType = (artifact.type || '').toLowerCase();
      const mimeType = (blob.type || '').toLowerCase();

      setArtifactRows([]);
      setArtifactImageUrl('');

      if (lowerType === 'csv' || mimeType.includes('text/csv')) {
        const text = await blob.text();
        setArtifactRows(parseCsv(text));
        setArtifactContent(text);
      } else if (mimeType.startsWith('image/')) {
        setArtifactImageUrl(api.getArtifactUrl(projectKey, artifact.path));
        setArtifactContent('');
      } else {
        const content = await blob.text();
        setArtifactContent(content);
      }

      setSelectedArtifact(artifact);
    } catch (err) {
      setError(err.message || 'Failed to load artifact');
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (event) => {
    const files = Array.from(event.target.files || []);
    if (files.length === 0) return;

    try {
      setUploading(true);
      setError(null);

      for (const file of files) {
        await api.uploadArtifact(projectKey, file);
      }

      await onRefresh();
    } catch (err) {
      setError(err.message || 'Failed to upload artifact');
    } finally {
      setUploading(false);
      event.target.value = '';
    }
  };

  const handleClose = () => {
    setSelectedArtifact(null);
    setArtifactContent('');
    setArtifactRows([]);
    setArtifactImageUrl('');
  };

  const renderArtifactBody = () => {
    if (loading) {
      return <p>Loading...</p>;
    }

    if (artifactImageUrl) {
      return (
        <img
          src={artifactImageUrl}
          alt={selectedArtifact?.name || 'Artifact preview'}
          className="artifact-image-preview"
        />
      );
    }

    if (artifactRows.length > 0) {
      return (
        <div className="artifact-table-wrap">
          <table className="artifact-table-preview">
            <tbody>
              {artifactRows.map((row, rowIndex) => (
                <tr key={`${selectedArtifact?.path}-row-${rowIndex}`}>
                  {row.map((cell, cellIndex) =>
                    rowIndex === 0 ? (
                      <th key={`${rowIndex}-${cellIndex}`}>{cell}</th>
                    ) : (
                      <td key={`${rowIndex}-${cellIndex}`}>{cell}</td>
                    ),
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }

    return <pre className="artifact-content">{artifactContent}</pre>;
  };

  return (
    <div className="artifacts-list">
      <div className="artifacts-header">
        <h3>Project Artifacts</h3>
        <div className="artifact-actions">
          <label className="btn-upload" htmlFor="artifact-upload-input">
            {uploading ? 'Uploading...' : '⬆ Import Artifact'}
          </label>
          <input
            id="artifact-upload-input"
            className="artifact-upload-input"
            type="file"
            accept=".txt,.md,.markdown,.csv,image/*"
            multiple
            onChange={handleUpload}
            disabled={uploading}
          />
          <button className="btn-refresh" onClick={onRefresh}>
            🔄 Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="artifact-error" role="alert">
          <strong>Error:</strong> {error}
        </div>
      )}

      {artifacts.length === 0 ? (
        <div className="no-artifacts">
          <p>No artifacts yet. Use commands or import text, markdown, CSV, or image files.</p>
        </div>
      ) : (
        <div className="artifacts-grid">
          {artifacts.map((artifact, idx) => (
            <div
              key={idx}
              className="artifact-card"
              onClick={() => handleArtifactClick(artifact)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  handleArtifactClick(artifact);
                }
              }}
            >
              <div className="artifact-icon">
                {artifact.type === 'md' ? '📄' : '📋'}
              </div>
              <div className="artifact-details">
                <h4>{artifact.name}</h4>
                <p className="artifact-path">{artifact.path}</p>
                <span className="artifact-type">{artifact.type.toUpperCase()}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedArtifact && (
        <div className="artifact-viewer-overlay" onClick={handleClose}>
          <div className="artifact-viewer" onClick={(e) => e.stopPropagation()}>
            <div className="viewer-header">
              <h3>{selectedArtifact.name}</h3>
              <button className="close-button" onClick={handleClose}>✕</button>
            </div>
            <div className="viewer-body">
              {renderArtifactBody()}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ArtifactsList;
