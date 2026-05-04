import type { CreationEntryConfig } from "../../constants/creationEntryRegistry";
import { CreationEntryCard } from "./CreationEntryCard";

type CreationEntryModalProps = {
  isOpen: boolean;
  entries: CreationEntryConfig[];
  selectedEntryId?: string | null;
  onSelect: (entry: CreationEntryConfig) => void;
  onClose?: () => void;
};

export function CreationEntryModal({
  isOpen,
  entries,
  selectedEntryId = null,
  onSelect,
  onClose,
}: CreationEntryModalProps) {
  if (!isOpen) {
    return null;
  }

  return (
    <div className="creation-entry-modal-backdrop">
      <section
        className="creation-entry-modal"
        role="dialog"
        aria-modal="true"
        aria-label="选择创作方式"
      >
        <div className="creation-entry-modal-header">
          <div>
            <h2 className="creation-entry-modal-title">选择创作方式</h2>
            <p className="creation-entry-modal-subtitle">
              请选择本次要使用的短剧剧本生成 / 改编入口
            </p>
          </div>
          {onClose ? (
            <button className="creation-entry-modal-close" type="button" onClick={onClose}>
              关闭
            </button>
          ) : null}
        </div>

        <div className="creation-entry-modal-grid">
          {entries.map((entry) => (
            <CreationEntryCard
              entry={entry}
              isSelected={entry.id === selectedEntryId}
              key={entry.id}
              onSelect={onSelect}
            />
          ))}
        </div>

        <p className="creation-entry-modal-footer">
          生成短剧剧本后，可继续在线编辑、下载 DOCX，并进入下一大功能：切分 / 分镜 / Prompt。
        </p>
      </section>
    </div>
  );
}
