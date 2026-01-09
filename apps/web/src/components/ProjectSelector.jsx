import { useState } from 'react';
import './ProjectSelector.css';

function ProjectSelector({ projects, onSelect, onCreate, loading }) {
  const [showCreate, setShowCreate] = useState(false);
  const [newKey, setNewKey] = useState('');
  const [newName, setNewName] = useState('');

  const handleCreate = (e) => {
    e.preventDefault();
    if (newKey && newName) {
      onCreate(newKey, newName);
      setNewKey('');
      setNewName('');
      setShowCreate(false);
    }
  };

  return (
    <div className="project-selector">
      <h2>Select or Create Project</h2>

      {projects.length > 0 && (
        <div className="projects-list">
          <h3>Existing Projects</h3>
          <div className="projects-grid">
            {projects.map((project) => (
              <div
                key={project.key}
                className="project-card"
                onClick={() => onSelect(project.key)}
              >
                <h4>{project.name}</h4>
                <p className="project-key">{project.key}</p>
                <p className="project-methodology">{project.methodology}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="create-section">
        {!showCreate ? (
          <button
            className="btn-primary"
            onClick={() => setShowCreate(true)}
            disabled={loading}
          >
            + Create New Project
          </button>
        ) : (
          <form className="create-form" onSubmit={handleCreate}>
            <h3>Create New Project</h3>
            <div className="form-group">
              <label>Project Key:</label>
              <input
                type="text"
                value={newKey}
                onChange={(e) => setNewKey(e.target.value)}
                placeholder="e.g., PROJ001"
                pattern="[a-zA-Z0-9_-]+"
                required
              />
              <small>Alphanumeric, dashes, and underscores only</small>
            </div>
            <div className="form-group">
              <label>Project Name:</label>
              <input
                type="text"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="e.g., My Project"
                required
              />
            </div>
            <div className="form-actions">
              <button type="submit" className="btn-primary" disabled={loading}>
                Create Project
              </button>
              <button
                type="button"
                className="btn-secondary"
                onClick={() => setShowCreate(false)}
                disabled={loading}
              >
                Cancel
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

export default ProjectSelector;
