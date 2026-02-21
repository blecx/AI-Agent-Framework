import { useState } from "react";
import "./ProjectSelector.css";

function ProjectSelector({ projects, onSelect, onCreate, loading }) {
  const [showCreate, setShowCreate] = useState(false);
  const [newKey, setNewKey] = useState("");
  const [newName, setNewName] = useState("");

  const handleCreate = (e) => {
    e.preventDefault();
    if (newKey && newName) {
      onCreate(newKey, newName);
      setNewKey("");
      setNewName("");
      setShowCreate(false);
    }
  };

  return (
    <div className="project-selector">
      <section className="landing-hero" aria-label="Hybrid workflow overview">
        <div className="hero-copy">
          <p className="hero-eyebrow">Hybrid Project Delivery</p>
          <h2>AI Chat First. Visual Control When You Need It.</h2>
          <p>
            Use chat for guided ISO 21500 execution, then use UI for quick
            project selection, transitions, and artifact review.
          </p>
          <div className="hero-badges">
            <span>Chat-first</span>
            <span>ISO 21500 workflow</span>
            <span>Propose → Review → Apply</span>
          </div>
        </div>

        <div className="hero-loop" aria-label="Delivery loop">
          <h3>Design Loop</h3>
          <ol>
            <li>
              <strong>Plan</strong> - Define UX objective + acceptance criteria
            </li>
            <li>
              <strong>Issue</strong> - Keep scope small and testable
            </li>
            <li>
              <strong>PR</strong> - Implement responsive changes with evidence
            </li>
            <li>
              <strong>Merge</strong> - CI green, feedback integrated
            </li>
            <li>
              <strong>Loop</strong> - Repeat with next visual improvement
            </li>
          </ol>
        </div>
      </section>

      <section className="start-guide" aria-label="How to start">
        <h3>How to start</h3>
        <div className="start-grid">
          <article>
            <h4>1) Pick or create project</h4>
            <p>
              Start by opening an existing project or creating one with key +
              name.
            </p>
          </article>
          <article>
            <h4>2) Move workflow state</h4>
            <p>
              Use guided chat first, then optional UI transitions where allowed.
            </p>
          </article>
          <article>
            <h4>3) Run command proposals</h4>
            <p>
              Generate artifacts as proposals, review results, then apply
              safely.
            </p>
          </article>
        </div>
      </section>

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
