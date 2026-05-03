import type { ReactNode } from "react";

type AppShellProps = {
  sidebar: ReactNode;
  children: ReactNode;
  toast?: ReactNode;
  topbar?: ReactNode;
};

export function AppShell({ sidebar, children, toast, topbar }: AppShellProps) {
  return (
    <div className="app-shell">
      <aside className="app-sidebar">{sidebar}</aside>
      <section className="app-main">
        {topbar && <header className="app-topbar">{topbar}</header>}
        <main>{children}</main>
      </section>
      {toast}
    </div>
  );
}

export type { AppShellProps };
