export type ToastType = "success" | "error" | "warning" | "info";

export type ToastMessage = {
  id: string;
  type: ToastType;
  title: string;
  description?: string;
};

type ToastProps = {
  messages: ToastMessage[];
  onDismiss: (id: string) => void;
};

export function Toast({ messages, onDismiss }: ToastProps) {
  if (messages.length === 0) {
    return null;
  }

  return (
    <section className="toast-stack" aria-live="polite" aria-label="Notifications">
      {messages.map((message) => (
        <article className={`toast-card toast-card-${message.type}`} key={message.id}>
          <div>
            <strong>{message.title}</strong>
            {message.description && <p>{message.description}</p>}
          </div>
          <button aria-label="关闭提示" onClick={() => onDismiss(message.id)} type="button">
            ×
          </button>
        </article>
      ))}
    </section>
  );
}

export type { ToastProps };
