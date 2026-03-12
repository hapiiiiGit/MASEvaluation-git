import React from 'react';
import styles from '../styles/globals.module.css';

interface UserProfile {
  username: string;
  avatarUrl?: string;
}

interface Notification {
  id: string;
  message: string;
  read: boolean;
}

interface HeaderProps {
  user?: UserProfile;
  notifications?: Notification[];
  onLogout?: () => void;
}

const Header: React.FC<HeaderProps> = ({
  user = { username: 'Guest' },
  notifications = [],
  onLogout,
}) => {
  const unreadCount = notifications.filter((n) => !n.read).length;

  return (
    <header className={styles.header}>
      <nav className={styles.nav}>
        <div className={styles.logo}>
          <a href="/dashboard" className={styles.logoLink}>
            <img src="/favicon.ico" alt="Logo" className={styles.logoImg} />
            <span className={styles.logoText}>MVP Dashboard</span>
          </a>
        </div>
        <div className={styles.navRight}>
          <div className={styles.notifications}>
            <button
              className={styles.notificationBtn}
              aria-label="Notifications"
              title="Notifications"
            >
              <span className={styles.bellIcon}>🔔</span>
              {unreadCount > 0 && (
                <span className={styles.notificationCount}>{unreadCount}</span>
              )}
            </button>
            {/* Notification dropdown */}
            {notifications.length > 0 && (
              <div className={styles.notificationDropdown}>
                <ul>
                  {notifications.map((n) => (
                    <li
                      key={n.id}
                      className={n.read ? styles.notificationRead : styles.notificationUnread}
                    >
                      {n.message}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
          <div className={styles.userProfile}>
            <img
              src={user.avatarUrl || '/default-avatar.png'}
              alt="User Avatar"
              className={styles.avatar}
            />
            <span className={styles.username}>{user.username}</span>
            {onLogout && (
              <button className={styles.logoutBtn} onClick={onLogout}>
                Logout
              </button>
            )}
          </div>
        </div>
      </nav>
    </header>
  );
};

export default Header;