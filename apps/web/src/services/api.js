/**
 * API service for communicating with the FastAPI backend
 */

const API_BASE = "/api";

function encodeArtifactPath(artifactPath) {
  return artifactPath
    .split("/")
    .map((segment) => encodeURIComponent(segment))
    .join("/");
}

export const api = {
  // Projects
  async createProject(key, name) {
    const response = await fetch(`${API_BASE}/projects`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ key, name }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to create project");
    }
    return response.json();
  },

  async listProjects() {
    const response = await fetch(`${API_BASE}/projects`);
    if (!response.ok) throw new Error("Failed to list projects");
    return response.json();
  },

  async getProjectState(projectKey) {
    const response = await fetch(`${API_BASE}/projects/${projectKey}/state`);
    if (!response.ok) throw new Error("Failed to get project state");
    return response.json();
  },

  // Workflow
  async getWorkflowState(projectKey) {
    const response = await fetch(
      `${API_BASE}/projects/${projectKey}/workflow/state`,
    );
    if (!response.ok) throw new Error("Failed to get workflow state");
    return response.json();
  },

  async getWorkflowAllowedTransitions(projectKey) {
    const response = await fetch(
      `${API_BASE}/projects/${projectKey}/workflow/allowed-transitions`,
    );
    if (!response.ok)
      throw new Error("Failed to get allowed workflow transitions");
    return response.json();
  },

  async transitionWorkflowState(
    projectKey,
    toState,
    actor = "web-ui",
    reason = null,
  ) {
    const response = await fetch(
      `${API_BASE}/projects/${projectKey}/workflow/state`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          to_state: toState,
          actor,
          reason,
        }),
      },
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to transition workflow state");
    }

    return response.json();
  },

  // Commands
  async proposeCommand(projectKey, command, params = {}) {
    const response = await fetch(
      `${API_BASE}/projects/${projectKey}/commands/propose`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command, params }),
      },
    );
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to propose command");
    }
    return response.json();
  },

  async applyCommand(projectKey, proposalId) {
    const response = await fetch(
      `${API_BASE}/projects/${projectKey}/commands/apply`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ proposal_id: proposalId }),
      },
    );
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to apply command");
    }
    return response.json();
  },

  // Artifacts
  async listArtifacts(projectKey) {
    const response = await fetch(
      `${API_BASE}/projects/${projectKey}/artifacts`,
    );
    if (!response.ok) throw new Error("Failed to list artifacts");
    return response.json();
  },

  async getArtifact(projectKey, artifactPath) {
    const response = await fetch(
      `${API_BASE}/projects/${projectKey}/artifacts/${encodeArtifactPath(artifactPath)}`,
    );
    if (!response.ok) throw new Error("Failed to get artifact");
    return response.text();
  },

  async getArtifactBlob(projectKey, artifactPath) {
    const response = await fetch(
      `${API_BASE}/projects/${projectKey}/artifacts/${encodeArtifactPath(artifactPath)}`,
    );
    if (!response.ok) throw new Error("Failed to get artifact");
    return response.blob();
  },

  getArtifactUrl(projectKey, artifactPath) {
    return `${API_BASE}/projects/${projectKey}/artifacts/${encodeArtifactPath(artifactPath)}`;
  },

  async uploadArtifact(projectKey, file, artifactPath = "") {
    const formData = new FormData();
    formData.append("file", file);
    if (artifactPath) {
      formData.append("artifact_path", artifactPath);
    }

    const response = await fetch(`${API_BASE}/projects/${projectKey}/artifacts/upload`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to upload artifact");
    }

    return response.json();
  },
};
