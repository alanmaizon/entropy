const Icon = ({ name, size = 16 }) => {
  const paths = {
    loop: <><path d="M20 12a8 8 0 1 1-2.34-5.66"/><path d="M20 4v4h-4"/><circle cx="12" cy="12" r="2"/></>,
    ingest: <><path d="M8 3h6l4 4v3"/><path d="M8 3v8H4l4 5v5h8v-5l4-5h-4"/></>,
    graph: <><circle cx="5" cy="6" r="2"/><circle cx="19" cy="6" r="2"/><circle cx="12" cy="18" r="2"/><path d="M6.5 7.2 10.7 16.7M17.5 7.2 13.3 16.7M7 6h10"/></>,
    episode: <><rect x="3" y="5" width="18" height="3" rx="0.5"/><rect x="3" y="10.5" width="18" height="3" rx="0.5"/><rect x="3" y="16" width="18" height="3" rx="0.5"/></>,
    hypothesis: <><circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.7.3-1 .9-1 1.7"/><circle cx="12" cy="17" r="0.5" fill="currentColor"/></>,
    settings: <><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></>,
    plus: <><path d="M12 5v14M5 12h14"/></>,
    refresh: <><path d="M21 12a9 9 0 1 1-3-6.7L21 8"/><path d="M21 3v5h-5"/></>,
    arrow: <><path d="M5 12h14M13 6l6 6-6 6"/></>,
  };
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      {paths[name]}
    </svg>
  );
};

const Button = ({ kind = 'primary', size, icon, children, ...rest }) => (
  <button className={`btn btn-${kind}${size === 'sm' ? ' btn-sm' : ''}`} {...rest}>
    {icon && <Icon name={icon} size={14} />}
    {children}
  </button>
);

const VerdictBadge = ({ verdict }) => {
  const v = (verdict || 'pending').toLowerCase();
  return (
    <span className={`vbadge ${v}`}>
      <span className="dot" />
      {verdict.toUpperCase()}
    </span>
  );
};

const Field = ({ label, children }) => (
  <div className="field">
    <label>{label}</label>
    {children}
  </div>
);

export { Icon, Button, VerdictBadge, Field };
