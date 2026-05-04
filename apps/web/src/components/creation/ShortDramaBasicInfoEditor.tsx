import type { ReactNode } from "react";
import type { ShortDramaScriptOutput } from "../../types/scriptGeneration";

type ShortDramaBasicInfoEditorProps = {
  result: ShortDramaScriptOutput;
  canEditFields: boolean;
  actions?: ReactNode;
  afterHeader?: ReactNode;
  onUpdateField?: <K extends keyof ShortDramaScriptOutput>(
    field: K,
    value: ShortDramaScriptOutput[K],
  ) => void;
};

export function ShortDramaBasicInfoEditor({
  result,
  canEditFields,
  actions,
  afterHeader,
  onUpdateField,
}: ShortDramaBasicInfoEditorProps) {
  return (
    <>
      <div className="short-script-header">
        <div>
          <span>短剧剧本结果</span>
          {canEditFields && onUpdateField ? (
            <label className="short-script-edit-field">
              <span>剧本标题</span>
              <input
                data-testid="script-title-editor"
                onChange={(event) => onUpdateField("project_title", event.target.value)}
                value={result.project_title}
              />
            </label>
          ) : (
            <h2>{result.project_title}</h2>
          )}
        </div>
        {actions}
      </div>

      {afterHeader}

      <section className="short-script-section">
        <h3>故事梗概</h3>
        {canEditFields && onUpdateField ? (
          <label className="short-script-edit-field">
            <span>核心卖点 / 故事梗概</span>
            <textarea
              data-testid="script-logline-editor"
              onChange={(event) => onUpdateField("logline", event.target.value)}
              rows={4}
              value={result.logline}
            />
          </label>
        ) : (
          <p>{result.logline}</p>
        )}
      </section>

      {(result.world_setting || canEditFields) && (
        <section className="short-script-section">
          <h3>世界观 / 故事背景</h3>
          {canEditFields && onUpdateField ? (
            <label className="short-script-edit-field">
              <span>世界观 / 故事背景</span>
              <textarea
                data-testid="script-world-setting-editor"
                onChange={(event) => onUpdateField("world_setting", event.target.value)}
                rows={4}
                value={result.world_setting}
              />
            </label>
          ) : (
            <p>{result.world_setting}</p>
          )}
        </section>
      )}
    </>
  );
}
