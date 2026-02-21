import { useState } from "react";
import "./CommandPanel.css";
import { api } from "../services/api";

const COMMANDS = [
  {
    id: "assess_gaps",
    name: "Assess Gaps",
    description:
      "Analyze missing ISO 21500 artifacts and identify gaps in project documentation",
    icon: "📊",
    recommendedStates: ["monitoring", "planning"],
  },
  {
    id: "generate_artifact",
    name: "Generate Artifact",
    description: "Create or update a specific project management artifact",
    icon: "📄",
    recommendedStates: ["planning", "executing", "monitoring"],
    params: [
      {
        name: "artifact_name",
        label: "Artifact Name",
        type: "text",
        placeholder: "e.g., project_charter.md",
      },
      {
        name: "artifact_type",
        label: "Artifact Type",
        type: "text",
        placeholder: "e.g., project_charter",
      },
    ],
  },
  {
    id: "generate_plan",
    name: "Generate Plan",
    description: "Create a project schedule with timeline and milestones",
    icon: "📅",
    recommendedStates: ["initiating", "planning"],
  },
];

function labelize(value) {
  if (!value) return "Unknown";
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function inferArtifactType(artifactName = "") {
  const file = artifactName.trim().toLowerCase();
  if (!file) return "artifact";

  if (file.endsWith(".md") || file.endsWith(".markdown")) return "markdown";
  if (file.endsWith(".txt")) return "text";
  if (file.endsWith(".csv")) return "csv";
  if (file.endsWith(".json")) return "json";
  if (file.match(/\.(png|jpe?g|gif|webp|svg)$/)) return "image";

  const lastDot = file.lastIndexOf(".");
  if (lastDot > 0 && lastDot < file.length - 1) {
    return file.slice(lastDot + 1);
  }

  return file.replace(/\s+/g, "_");
}

function CommandPanel({
  projectKey,
  onProposalGenerated,
  currentWorkflowState = "initiating",
}) {
  const [selectedCommand, setSelectedCommand] = useState(null);
  const [params, setParams] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleCommandSelect = (command) => {
    const isRecommended =
      command.recommendedStates.includes(currentWorkflowState);
    if (!isRecommended) {
      setError(
        `"${command.name}" is not recommended in ${labelize(currentWorkflowState)}. Move workflow phase or use AI chat guidance.`,
      );
      return;
    }

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

      const payloadParams = { ...params };
      if (selectedCommand.id === "generate_artifact") {
        const inferred = inferArtifactType(payloadParams.artifact_name || "");
        if (!payloadParams.artifact_type || payloadParams.artifact_type.trim() === "") {
          payloadParams.artifact_type = inferred;
        }
      }

      const proposal = await api.proposeCommand(
        projectKey,
        selectedCommand.id,
        payloadParams,
      );
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
      <div className="command-header">
        <h3>Available Commands</h3>
        <span className="workflow-state-pill">
          Workflow: {labelize(currentWorkflowState)}
        </span>
      </div>
      <p className="command-help">
        Use chat for guided creation, or run a quick UI command below. All
        changes follow propose → review → apply.
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
            className={`command-card ${selectedCommand?.id === command.id ? "selected" : ""}`}
            onClick={() => handleCommandSelect(command)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                handleCommandSelect(command);
              }
            }}
          >
            <div className="command-icon">{command.icon}</div>
            <div className="command-details">
              <div className="command-title-row">
                <h4>{command.name}</h4>
                <span
                  className={`command-fit ${
                    command.recommendedStates.includes(currentWorkflowState)
                      ? "fit-yes"
                      : "fit-no"
                  }`}
                >
                  {command.recommendedStates.includes(currentWorkflowState)
                    ? "Recommended now"
                    : `Best in: ${command.recommendedStates.map(labelize).join(", ")}`}
                </span>
              </div>
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
                    value={params[param.name] || ""}
                    onChange={(e) =>
                      handleParamChange(param.name, e.target.value)
                    }
                    placeholder={
                      selectedCommand.id === "generate_artifact" &&
                      param.name === "artifact_type"
                        ? `auto-detected, e.g. ${inferArtifactType(params.artifact_name || "project_charter.md")}`
                        : param.placeholder
                    }
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
              {loading ? "Generating Proposal..." : "Propose Changes"}
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
