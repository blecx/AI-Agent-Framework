import { useState, useEffect } from "react";
import "./ProjectView.css";
import CommandPanel from "./CommandPanel";
import ProposalModal from "./ProposalModal";
import ArtifactsList from "./ArtifactsList";
import WorkflowIndicator from "./WorkflowIndicator";
import { api } from "../services/api";

function ProjectView({ projectKey, onBack }) {
  const [projectState, setProjectState] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentProposal, setCurrentProposal] = useState(null);
  const [activeTab, setActiveTab] = useState("command");
  const [workflowState, setWorkflowState] = useState(null);
  const [allowedTransitions, setAllowedTransitions] = useState([]);
  const [workflowLoading, setWorkflowLoading] = useState(false);
  const [workflowError, setWorkflowError] = useState(null);

  useEffect(() => {
    loadProjectData();
  }, [projectKey]);

  const loadProjectData = async () => {
    await Promise.all([loadProjectState(), loadWorkflowState()]);
  };

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

  const loadWorkflowState = async () => {
    try {
      setWorkflowLoading(true);
      const [state, transitions] = await Promise.all([
        api.getWorkflowState(projectKey),
        api.getWorkflowAllowedTransitions(projectKey),
      ]);

      setWorkflowState(state);
      setAllowedTransitions(transitions.allowed_transitions || []);
      setWorkflowError(null);
    } catch (err) {
      setWorkflowError(err.message);
    } finally {
      setWorkflowLoading(false);
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

  const handleWorkflowTransition = async (toState) => {
    try {
      setWorkflowLoading(true);
      setWorkflowError(null);
      await api.transitionWorkflowState(
        projectKey,
        toState,
        "web-ui",
        `Transitioned via web UI to ${toState}`,
      );

      await Promise.all([loadWorkflowState(), loadProjectState()]);
    } catch (err) {
      setWorkflowError(err.message);
      setWorkflowLoading(false);
    }
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
          className={activeTab === "command" ? "active" : ""}
          onClick={() => setActiveTab("command")}
        >
          Commands
        </button>
        <button
          className={activeTab === "artifacts" ? "active" : ""}
          onClick={() => setActiveTab("artifacts")}
        >
          Artifacts ({projectState?.artifacts?.length || 0})
        </button>
      </div>

      <div className="project-content">
        <WorkflowIndicator
          currentState={workflowState?.current_state || "initiating"}
          previousState={workflowState?.previous_state || null}
          allowedTransitions={allowedTransitions}
          onTransition={handleWorkflowTransition}
          loading={workflowLoading}
          error={workflowError}
        />

        {activeTab === "command" && (
          <CommandPanel
            projectKey={projectKey}
            onProposalGenerated={handleProposalGenerated}
            currentWorkflowState={workflowState?.current_state || "initiating"}
          />
        )}

        {activeTab === "artifacts" && (
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
