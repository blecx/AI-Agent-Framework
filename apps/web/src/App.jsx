import { useState, useEffect } from 'react';
import './App.css';
import ProjectSelector from './components/ProjectSelector';
import ProjectView from './components/ProjectView';
import { api } from './services/api';

function App() {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const projectList = await api.listProjects();
      setProjects(projectList);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async (key, name) => {
    try {
      setLoading(true);
      const project = await api.createProject(key, name);
      setProjects([...projects, project]);
      setSelectedProject(project.key);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectProject = (projectKey) => {
    setSelectedProject(projectKey);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>ISO 21500 Project Management AI Agent</h1>
        <p>Intelligent project management following ISO 21500 standards</p>
      </header>

      {error && (
        <div className="error-banner">
          <strong>Error:</strong> {error}
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      <main className="app-main">
        {!selectedProject ? (
          <ProjectSelector
            projects={projects}
            onSelect={handleSelectProject}
            onCreate={handleCreateProject}
            loading={loading}
          />
        ) : (
          <ProjectView
            projectKey={selectedProject}
            onBack={() => setSelectedProject(null)}
          />
        )}
      </main>
    </div>
  );
}

export default App;
