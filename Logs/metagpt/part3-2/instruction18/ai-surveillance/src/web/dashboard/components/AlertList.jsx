import React from "react";
import PropTypes from "prop-types";

/**
 * AlertList component displays a list of alerts.
 * @param {Object} props
 * @param {Array} props.alerts - Array of alert objects.
 */
function AlertList({ alerts }) {
  if (!alerts || alerts.length === 0) {
    return <div className="alert-list empty">No alerts detected.</div>;
  }

  return (
    <div className="alert-list">
      <ul>
        {alerts.map((alert, idx) => (
          <li key={idx} className={`alert-item alert-type-${alert.type}`}>
            <div className="alert-header">
              <span className="alert-type">{alert.type.toUpperCase()}</span>
              <span className="alert-timestamp">
                {new Date(alert.timestamp).toLocaleString()}
              </span>
            </div>
            <div className="alert-details">
              {alert.details && typeof alert.details === "object" ? (
                <ul>
                  {Object.entries(alert.details).map(([key, value]) => (
                    <li key={key}>
                      <strong>{key}:</strong> {String(value)}
                    </li>
                  ))}
                </ul>
              ) : (
                <span>{String(alert.details)}</span>
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

AlertList.propTypes = {
  alerts: PropTypes.arrayOf(
    PropTypes.shape({
      timestamp: PropTypes.string.isRequired,
      type: PropTypes.string.isRequired,
      details: PropTypes.oneOfType([
        PropTypes.object,
        PropTypes.string,
        PropTypes.number,
      ]),
    })
  ),
};

export default AlertList;