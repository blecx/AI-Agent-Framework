import { useState, useEffect } from 'react';
import './ProjectView.css';
import CommandPanel from './CommandPanel';
import ProposalModal from './ProposalModal';
import ArtifactsList from './ArtifactsList';
import { api } from '../services/api';

function ProjectView({ projectKey, onBack }) {
  const [projectState, setProjectState] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentProposal, setCurrentProposal] = useState(null);
  const [activeTab, setActiveTab] = useState('command');

  useEffect(() => {
    loadProjectState();
  }, [projectKey]);

  const loadProjectState = async () => {
    try {
      setLoading(true);
      const state = await api.getProjectState(projectKey);
      setProjectState(state);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleProposalGenerated = (proposal) => {
    setCurrentProposal(proposal);
  };

  const handleProposalApplied = async () => {
    setCurrentProposal(null);
    await loadProjectState();
  };

  const handleProposalCancelled = () => {
    setCurrentProposal(null);
  };

  if (loading && !projectState) {
    return <div className="loading">Loading project...</div>;
  }

  if (error && !projectState) {
    return (
      <div className="error-view">
        <p>Error: {error}</p>
        <button onClick={onBack}>Back to Projects</button>
      </div>
    );
  }

  return (
    <div className="project-view">
      <div className="project-header">
        <button className="back-button" onClick={onBack}>
          ← Back to Projects
        </button>
        <div className="project-info">
          <h2>{projectState?.project_info?.name}</h2>
          <p className="project-key">{projectKey}</p>
          <span className="methodology-badge">
            {projectState?.project_info?.methodology}
          </span>
        </div>
      </div>

      <div className="project-tabs">
        <button
          className={activeTab === 'command' ? 'active' : ''}
          onClick={() => setActiveTab('command')}
        >
          Commands
        </button>
        <button
          className={activeTab === 'artifacts' ? 'active' : ''}
          onClick={() => setActiveTab('artifacts')}
        >
          Artifacts ({projectState?.artifacts?.length || 0})
        </button>
      </div>

      <div className="project-content">
        {activeTab === 'command' && (
          <CommandPanel
            projectKey={projectKey}
            onProposalGenerated={handleProposalGenerated}
          />
        )}

        {activeTab === 'artifacts' && (
          <ArtifactsList
            projectKey={projectKey}
            artifacts={projectState?.artifacts || []}
            onRefresh={loadProjectState}
          />
        )}
      </div>

      {currentProposal && (
        <ProposalModal
          projectKey={projectKey}
          proposal={currentProposal}
          onApply={handleProposalApplied}
          onCancel={handleProposalCancelled}
        />
      )}
    </div>
  );
}

export default ProjectView;
