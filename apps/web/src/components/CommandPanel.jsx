import { useState } from 'react';
import './CommandPanel.css';
import { api } from '../services/api';

const COMMANDS = [
  {
    id: 'assess_gaps',
    name: 'Assess Gaps',
    description: 'Analyze missing ISO 21500 artifacts and identify gaps in project documentation',
    icon: '📊',
  },
  {
    id: 'generate_artifact',
    name: 'Generate Artifact',
    description: 'Create or update a specific project management artifact',
    icon: '📄',
    params: [
      { name: 'artifact_name', label: 'Artifact Name', type: 'text', placeholder: 'e.g., project_charter.md' },
      { name: 'artifact_type', label: 'Artifact Type', type: 'text', placeholder: 'e.g., project_charter' },
    ],
  },
  {
    id: 'generate_plan',
    name: 'Generate Plan',
    description: 'Create a project schedule with timeline and milestones',
    icon: '📅',
  },
];

function CommandPanel({ projectKey, onProposalGenerated }) {
  const [selectedCommand, setSelectedCommand] = useState(null);
  const [params, setParams] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleCommandSelect = (command) => {
    setSelectedCommand(command);
    setParams({});
    setError(null);
  };

  const handleParamChange = (paramName, value) => {
    setParams({ ...params, [paramName]: value });
  };

  const handlePropose = async () => {
    if (!selectedCommand) return;

    try {
      setLoading(true);
      setError(null);
      const proposal = await api.proposeCommand(projectKey, selectedCommand.id, params);
      onProposalGenerated(proposal);
      setSelectedCommand(null);
      setParams({});
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="command-panel">
      <h3>Available Commands</h3>
      <p className="command-help">
        Select a command to propose changes to your project. You'll review the changes before they're applied.
      </p>

      {error && (
        <div className="command-error">
          <strong>Error:</strong> {error}
        </div>
      )}

      <div className="commands-list">
        {COMMANDS.map((command) => (
          <div
            key={command.id}
            className={`command-card ${selectedCommand?.id === command.id ? 'selected' : ''}`}
            onClick={() => handleCommandSelect(command)}
          >
            <div className="command-icon">{command.icon}</div>
            <div className="command-details">
              <h4>{command.name}</h4>
              <p>{command.description}</p>
            </div>
          </div>
        ))}
      </div>

      {selectedCommand && (
        <div className="command-form">
          <h4>Configure: {selectedCommand.name}</h4>

          {selectedCommand.params && selectedCommand.params.length > 0 && (
            <div className="params-section">
              {selectedCommand.params.map((param) => (
                <div key={param.name} className="param-group">
                  <label>{param.label}:</label>
                  <input
                    type={param.type}
                    value={params[param.name] || ''}
                    onChange={(e) => handleParamChange(param.name, e.target.value)}
                    placeholder={param.placeholder}
                  />
                </div>
              ))}
            </div>
          )}

          <div className="command-actions">
            <button
              className="btn-primary"
              onClick={handlePropose}
              disabled={loading}
            >
              {loading ? 'Generating Proposal...' : 'Propose Changes'}
            </button>
            <button
              className="btn-secondary"
              onClick={() => setSelectedCommand(null)}
              disabled={loading}
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default CommandPanel;
