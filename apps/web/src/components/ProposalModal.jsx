import { useState } from 'react';
import './ProposalModal.css';
import { api } from '../services/api';

function ProposalModal({ projectKey, proposal, onApply, onCancel }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);

  const handleApply = async () => {
    try {
      setLoading(true);
      setError(null);
      await api.applyCommand(projectKey, proposal.proposal_id);
      onApply();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Review Proposed Changes</h2>
          <button className="close-button" onClick={onCancel}>✕</button>
        </div>

        <div className="modal-body">
          <div className="assistant-message">
            <h3>Summary</h3>
            <p>{proposal.assistant_message}</p>
          </div>

          <div className="commit-message">
            <h3>Commit Message</h3>
            <code>{proposal.draft_commit_message}</code>
          </div>

          <div className="file-changes">
            <h3>Files to Change ({proposal.file_changes?.length || 0})</h3>

            <div className="files-list">
              {proposal.file_changes?.map((change, idx) => (
                <div key={idx} className="file-item">
                  <div
                    className="file-header"
                    onClick={() => setSelectedFile(selectedFile === idx ? null : idx)}
                  >
                    <span className={`operation-badge ${change.operation}`}>
                      {change.operation}
                    </span>
                    <span className="file-path">{change.path}</span>
                    <span className="expand-icon">
                      {selectedFile === idx ? '▼' : '▶'}
                    </span>
                  </div>

                  {selectedFile === idx && (
                    <div className="file-diff">
                      <pre>{change.diff}</pre>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {error && (
            <div className="modal-error">
              <strong>Error:</strong> {error}
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button
            className="btn-primary"
            onClick={handleApply}
            disabled={loading}
          >
            {loading ? 'Applying...' : '✓ Apply & Commit'}
          </button>
          <button
            className="btn-secondary"
            onClick={onCancel}
            disabled={loading}
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

export default ProposalModal;
