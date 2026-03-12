import React from 'react';
import styles from '../styles/globals.module.css';

interface SidebarProps {
  activeMenu?: string;
  onMenuSelect?: (menu: string) => void;
}

const menuItems = [
  { key: 'dashboard', label: 'Dashboard', icon: '📊', link: '/dashboard' },
  { key: 'reports', label: 'Reports', icon: '📄', link: '/reports' },
  { key: 'settings', label: 'Settings', icon: '⚙️', link: '/settings' },
];

const Sidebar: React.FC<SidebarProps> = ({ activeMenu = 'dashboard', onMenuSelect }) => {
  return (
    <aside className={styles.sidebar}>
      <nav>
        <ul className={styles.sidebarMenu}>
          {menuItems.map((item) => (
            <li
              key={item.key}
              className={
                activeMenu === item.key
                  ? styles.sidebarMenuItemActive
                  : styles.sidebarMenuItem
              }
              onClick={() => onMenuSelect && onMenuSelect(item.key)}
            >
              <a href={item.link} className={styles.sidebarMenuLink}>
                <span className={styles.sidebarMenuIcon}>{item.icon}</span>
                <span className={styles.sidebarMenuLabel}>{item.label}</span>
              </a>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;