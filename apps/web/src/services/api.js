/**
 * API service for communicating with the FastAPI backend
 */

const API_BASE = '/api';

export const api = {
  // Projects
  async createProject(key, name) {
    const response = await fetch(`${API_BASE}/projects`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key, name }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create project');
    }
    return response.json();
  },

  async listProjects() {
    const response = await fetch(`${API_BASE}/projects`);
    if (!response.ok) throw new Error('Failed to list projects');
    return response.json();
  },

  async getProjectState(projectKey) {
    const response = await fetch(`${API_BASE}/projects/${projectKey}/state`);
    if (!response.ok) throw new Error('Failed to get project state');
    return response.json();
  },

  // Commands
  async proposeCommand(projectKey, command, params = {}) {
    const response = await fetch(`${API_BASE}/projects/${projectKey}/commands/propose`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command, params }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to propose command');
    }
    return response.json();
  },

  async applyCommand(projectKey, proposalId) {
    const response = await fetch(`${API_BASE}/projects/${projectKey}/commands/apply`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ proposal_id: proposalId }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to apply command');
    }
    return response.json();
  },

  // Artifacts
  async listArtifacts(projectKey) {
    const response = await fetch(`${API_BASE}/projects/${projectKey}/artifacts`);
    if (!response.ok) throw new Error('Failed to list artifacts');
    return response.json();
  },

  async getArtifact(projectKey, artifactPath) {
    const response = await fetch(`${API_BASE}/projects/${projectKey}/artifacts/${artifactPath}`);
    if (!response.ok) throw new Error('Failed to get artifact');
    return response.text();
  },
};
