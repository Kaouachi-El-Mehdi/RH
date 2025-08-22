import React, { useState } from 'react';
import { useNotifications } from '../contexts/NotificationContext';

const NotificationBell: React.FC = () => {
  const { notifications, unreadCount, markAsRead } = useNotifications();
  const [showDropdown, setShowDropdown] = useState(false);
  return (
    <div className="position-relative me-3">
      <button className="btn btn-link position-relative text-white" onClick={() => setShowDropdown(!showDropdown)}>
        <span className="bi bi-bell" style={{ fontSize: '1.5rem' }}></span>
        {unreadCount > 0 && (
          <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
            {unreadCount}
          </span>
        )}
      </button>
      {showDropdown && (
        <div className="dropdown-menu show p-2" style={{ minWidth: 300, right: 0, left: 'auto' }}>
          <h6 className="dropdown-header">Notifications</h6>
          {notifications.length === 0 ? (
            <span className="dropdown-item-text">Aucune notification</span>
          ) : (
            notifications.slice(0, 8).map((n) => (
              <div key={n.id} className={`dropdown-item d-flex align-items-start${n.is_read ? '' : ' fw-bold'}`} style={{ cursor: 'pointer' }} onClick={() => markAsRead(n.id)}>
                <span className={`me-2 bi ${n.is_read ? 'bi-bell' : 'bi-bell-fill'}`}></span>
                <div>
                  <div>{n.title}</div>
                  <small className="text-muted">{n.message}</small>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default NotificationBell;
