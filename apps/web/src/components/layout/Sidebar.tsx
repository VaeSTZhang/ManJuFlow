export type SidebarItem = {
  id: string;
  label: string;
  description?: string;
};

type SidebarProps = {
  items: SidebarItem[];
  activeItemId: string;
  onSelect: (id: string) => void;
};

export function Sidebar({ items, activeItemId, onSelect }: SidebarProps) {
  return (
    <nav className="sidebar-nav" aria-label="Dramora workspace navigation">
      <div className="sidebar-brand">
        <strong>Dramora｜剧作工坊</strong>
        <span>短剧剧本生成与改编工作台</span>
      </div>

      <div className="sidebar-nav-list">
        {items.map((item) => {
          const isActive = item.id === activeItemId;

          return (
            <button
              className={isActive ? "sidebar-item sidebar-item-active" : "sidebar-item"}
              key={item.id}
              onClick={() => onSelect(item.id)}
              type="button"
            >
              <span>{item.label}</span>
              {item.description && <small>{item.description}</small>}
            </button>
          );
        })}
      </div>
    </nav>
  );
}

export type { SidebarProps };
