import type { CreationEntryConfig, CreationEntryStatus } from "../../constants/creationEntryRegistry";

type CreationEntryCardProps = {
  entry: CreationEntryConfig;
  isSelected?: boolean;
  onSelect?: (entry: CreationEntryConfig) => void;
};

const statusLabels: Record<CreationEntryStatus, string> = {
  available: "可用",
  mock: "Mock 优先",
  planned: "规划中",
};

export function CreationEntryCard({
  entry,
  isSelected = false,
  onSelect,
}: CreationEntryCardProps) {
  const cardClassName = [
    "creation-entry-card",
    isSelected ? "creation-entry-card-selected" : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <button className={cardClassName} type="button" onClick={() => onSelect?.(entry)}>
      <div className="creation-entry-card-header">
        <div>
          <span>{entry.subtitle}</span>
          <h3>{entry.label}</h3>
        </div>
        <span className={`creation-entry-card-status creation-entry-card-status-${entry.status}`}>
          {statusLabels[entry.status]}
        </span>
      </div>

      <p>{entry.description}</p>
      <strong>{entry.primaryActionLabel}</strong>
    </button>
  );
}
