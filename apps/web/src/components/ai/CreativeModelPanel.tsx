import { useState } from "react";

export type CreativeModelOption = {
  id: string;
  label: string;
  provider?: string;
  model?: string;
  description: string;
  recommended?: boolean;
};

export type SelectedCreativeModel = {
  provider?: string;
  model?: string;
  label: string;
  source: "system_default" | "user_selected";
};

type CreativeModelPanelProps = {
  selectedModel: SelectedCreativeModel;
  onChange: (model: SelectedCreativeModel) => void;
  disabled?: boolean;
};

const creativeModelOptions: CreativeModelOption[] = [
  {
    id: "system-default",
    label: "使用后端默认",
    description: "沿用当前后端配置的默认创作模型。",
  },
  {
    id: "deepseek",
    label: "DeepSeek",
    provider: "deepseek",
    model: "deepseek-chat",
    description: "推荐用于内部剧本生成与文本改编。",
    recommended: true,
  },
  {
    id: "mimo",
    label: "Mimo",
    provider: "mimo",
    model: "mimo-v2.5-pro",
    description: "可用于长文本理解与改编质量对比。",
  },
  {
    id: "kimi",
    label: "Kimi",
    provider: "kimi",
    model: "kimi-k2.5",
    description: "可用于长上下文文本理解与改编参考。",
  },
  {
    id: "minimax",
    label: "MiniMax",
    provider: "minimax",
    model: "MiniMax-M2.7",
    description: "可用于文本生成质量对比与备用方案。",
  },
];

function toSelectedModel(option: CreativeModelOption): SelectedCreativeModel {
  return {
    provider: option.provider,
    model: option.model,
    label: option.label,
    source: option.id === "system-default" ? "system_default" : "user_selected",
  };
}

function isSelected(option: CreativeModelOption, selectedModel: SelectedCreativeModel): boolean {
  if (option.id === "system-default") {
    return selectedModel.source === "system_default";
  }

  return selectedModel.provider === option.provider && selectedModel.model === option.model;
}

export function CreativeModelPanel({
  selectedModel,
  onChange,
  disabled = false,
}: CreativeModelPanelProps) {
  const [isOpen, setIsOpen] = useState(false);

  const handleSelect = (option: CreativeModelOption) => {
    if (disabled) {
      return;
    }

    onChange(toSelectedModel(option));
    setIsOpen(false);
  };

  const togglePanel = () => {
    if (disabled) {
      return;
    }

    setIsOpen((current) => !current);
  };

  return (
    <section className="creative-model-panel" aria-label="创作模型选择">
      <div className="creative-model-summary">
        <div>
          <span>创作模型</span>
          <strong>创作模型：{selectedModel.label}</strong>
          <p>{disabled ? "登录后可切换创作模型" : "用于剧本生成、文本改编、编剧助手和质量评审。"}</p>
        </div>
        <button
          className="creative-model-toggle"
          disabled={disabled}
          onClick={togglePanel}
          type="button"
        >
          {isOpen ? "收起" : "切换"}
        </button>
      </div>

      {isOpen && !disabled && (
        <div className="creative-model-options">
          {creativeModelOptions.map((option) => {
            const active = isSelected(option, selectedModel);

            return (
              <button
                className={`creative-model-option${active ? " creative-model-option-active" : ""}`}
                key={option.id}
                onClick={() => handleSelect(option)}
                type="button"
              >
                <span>
                  <strong>{option.label}</strong>
                  {option.recommended && <em className="creative-model-badge">推荐</em>}
                </span>
                <p>{option.description}</p>
                {option.model && <small>{option.model}</small>}
              </button>
            );
          })}
        </div>
      )}

      {disabled && <p className="creative-model-note">登录后可切换创作模型</p>}
    </section>
  );
}
