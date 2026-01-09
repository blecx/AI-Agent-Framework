import { useState } from 'react';
import './ArtifactsList.css';
import { api } from '../services/api';

function ArtifactsList({ projectKey, artifacts, onRefresh }) {
  const [selectedArtifact, setSelectedArtifact] = useState(null);
  const [artifactContent, setArtifactContent] = useState('');
  const [loading, setLoading] = useState(false);

  const handleArtifactClick = async (artifact) => {
    try {
      setLoading(true);
      const content = await api.getArtifact(projectKey, artifact.path);
      setArtifactContent(content);
      setSelectedArtifact(artifact);
    } catch (err) {
      console.error('Failed to load artifact:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setSelectedArtifact(null);
    setArtifactContent('');
  };

  return (
    <div className="artifacts-list">
      <div className="artifacts-header">
        <h3>Project Artifacts</h3>
        <button className="btn-refresh" onClick={onRefresh}>
          🔄 Refresh
        </button>
      </div>

      {artifacts.length === 0 ? (
        <div className="no-artifacts">
          <p>No artifacts yet. Use commands to generate project documents.</p>
        </div>
      ) : (
        <div className="artifacts-grid">
          {artifacts.map((artifact, idx) => (
            <div
              key={idx}
              className="artifact-card"
              onClick={() => handleArtifactClick(artifact)}
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
              {loading ? (
                <p>Loading...</p>
              ) : (
                <pre className="artifact-content">{artifactContent}</pre>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ArtifactsList;
