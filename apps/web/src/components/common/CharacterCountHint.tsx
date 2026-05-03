export type CharacterCountHintStatus = "normal" | "warning" | "error";

export type CharacterCountHintProps = {
  value: string;
  maxLength: number;
  warningThresholdRatio?: number;
  label?: string;
  className?: string;
};

const DEFAULT_WARNING_THRESHOLD_RATIO = 0.9;

function formatCount(value: number): string {
  return value.toLocaleString("zh-CN");
}

export function CharacterCountHint({
  value,
  maxLength,
  warningThresholdRatio = DEFAULT_WARNING_THRESHOLD_RATIO,
  label,
  className,
}: CharacterCountHintProps) {
  const currentLength = value.length;
  const remainingLength = maxLength - currentLength;
  const exceededLength = Math.max(currentLength - maxLength, 0);
  const warningThreshold = Math.floor(maxLength * warningThresholdRatio);

  const status: CharacterCountHintStatus =
    currentLength > maxLength ? "error" : currentLength >= warningThreshold ? "warning" : "normal";

  const statusText =
    status === "error"
      ? `已超出 ${formatCount(exceededLength)} 字，请删减或拆分后再生成`
      : status === "warning"
        ? "文本接近上限，后续生成可能需要更久"
        : `剩余 ${formatCount(remainingLength)} 字`;

  const classes = ["character-count-hint", `character-count-hint-${status}`, className]
    .filter(Boolean)
    .join(" ");

  return (
    <p className={classes} aria-live="polite">
      {label && <span>{label}：</span>}
      当前 {formatCount(currentLength)} / {formatCount(maxLength)} 字，{statusText}
    </p>
  );
}
