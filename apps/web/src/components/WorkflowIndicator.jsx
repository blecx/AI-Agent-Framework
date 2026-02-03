import './WorkflowIndicator.css';

const WORKFLOW_PHASES = [
  { id: 'initiation', name: 'Initiation', icon: '🎯' },
  { id: 'planning', name: 'Planning', icon: '📋' },
  { id: 'execution', name: 'Execution', icon: '🚀' },
  { id: 'control', name: 'Control', icon: '📊' },
  { id: 'closing', name: 'Closing', icon: '✅' },
];

function WorkflowIndicator({ currentPhase = 'initiation', onPhaseChange }) {
  return (
    <div className="workflow-indicator">
      <div className="workflow-header">
        <h4>Workflow Phase</h4>
        <span className="current-phase-badge">{currentPhase}</span>
      </div>
      <div className="workflow-phases">
        {WORKFLOW_PHASES.map((phase) => (
          <div
            key={phase.id}
            className={`phase-item ${currentPhase === phase.id ? 'active' : ''}`}
            onClick={() => onPhaseChange && onPhaseChange(phase.id)}
            title={phase.name}
          >
            <span className="phase-icon">{phase.icon}</span>
            <span className="phase-name">{phase.name}</span>
          </div>
        ))}
      </div>
      <div className="workflow-state-info">
        <p>Track your project's current state through ISO 21500 workflow phases</p>
      </div>
    </div>
  );
}

export default WorkflowIndicator;
