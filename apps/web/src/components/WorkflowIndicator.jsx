import "./WorkflowIndicator.css";

const WORKFLOW_PHASES = [
  {
    id: "initiating",
    name: "Initiating",
    icon: "🎯",
    summary: "Define project intent, scope baseline, and key stakeholders.",
  },
  {
    id: "planning",
    name: "Planning",
    icon: "🧭",
    summary: "Prepare plan artifacts, RAID entries, and execution readiness.",
  },
  {
    id: "executing",
    name: "Executing",
    icon: "🚀",
    summary: "Deliver work packages and generate execution artifacts.",
  },
  {
    id: "monitoring",
    name: "Monitoring",
    icon: "📊",
    summary: "Track progress, assess gaps, and correct course.",
  },
  {
    id: "closing",
    name: "Closing",
    icon: "✅",
    summary: "Finalize documentation and closure decisions.",
  },
  {
    id: "closed",
    name: "Closed",
    icon: "🏁",
    summary: "Project is formally completed and archived.",
  },
];

function labelize(value) {
  if (!value) return "Unknown";
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function WorkflowIndicator({
  currentState = "initiating",
  previousState = null,
  allowedTransitions = [],
  onTransition,
  loading = false,
  error = null,
}) {
  const currentIndex = WORKFLOW_PHASES.findIndex(
    (phase) => phase.id === currentState,
  );

  return (
    <section className="workflow-indicator" aria-label="Project workflow state">
      <div className="workflow-header">
        <div>
          <h3>ISO 21500 Workflow</h3>
          <p>
            Chat-first guidance with optional UI transitions for quick actions.
          </p>
        </div>
        <div className="workflow-badges">
          <span className="current-phase-badge">
            Current: {labelize(currentState)}
          </span>
          {previousState && (
            <span className="previous-phase-badge">
              Previous: {labelize(previousState)}
            </span>
          )}
        </div>
      </div>

      {error && (
        <div className="workflow-error" role="alert">
          <strong>Workflow Error:</strong> {error}
        </div>
      )}

      <ol className="workflow-phases" aria-label="Workflow phases">
        {WORKFLOW_PHASES.map((phase) => (
          <li
            key={phase.id}
            className={`phase-item ${currentState === phase.id ? "active" : ""} ${
              currentIndex > -1 &&
              WORKFLOW_PHASES.findIndex((p) => p.id === phase.id) < currentIndex
                ? "completed"
                : ""
            }`}
          >
            <div className="phase-topline">
              <span className="phase-icon" aria-hidden="true">
                {phase.icon}
              </span>
              <span className="phase-name">{phase.name}</span>
              {currentState === phase.id && (
                <span className="phase-state-tag">Now</span>
              )}
            </div>
            <p className="phase-summary">{phase.summary}</p>
          </li>
        ))}
      </ol>

      <div className="workflow-transitions" aria-live="polite">
        <h4>Allowed UI Transitions</h4>
        {allowedTransitions.length === 0 ? (
          <p className="workflow-empty-actions">
            No transitions available from this state.
          </p>
        ) : (
          <div className="transition-buttons">
            {allowedTransitions.map((toState) => (
              <button
                key={toState}
                type="button"
                className="transition-button"
                onClick={() => onTransition && onTransition(toState)}
                disabled={loading}
                aria-label={`Transition workflow to ${labelize(toState)}`}
              >
                Move to {labelize(toState)}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="workflow-state-info">
        <p>
          Preferred path: use AI chat for guided transitions and artifact
          generation. Use UI controls for quick, validated state changes.
        </p>
      </div>
    </section>
  );
}

export default WorkflowIndicator;
