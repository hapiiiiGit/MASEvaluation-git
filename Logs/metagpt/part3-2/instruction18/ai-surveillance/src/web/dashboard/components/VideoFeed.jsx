import React from "react";
import PropTypes from "prop-types";

/**
 * VideoFeed component displays the live video stream from the backend.
 * @param {Object} props
 * @param {string} props.src - The URL of the video stream (multipart JPEG).
 */
function VideoFeed({ src }) {
  return (
    <div className="video-feed-container">
      <img
        src={src}
        alt="Live Video Feed"
        className="video-feed"
        style={{
          width: "100%",
          maxWidth: "640px",
          border: "2px solid #333",
          borderRadius: "8px",
          background: "#000",
        }}
      />
    </div>
  );
}

VideoFeed.propTypes = {
  src: PropTypes.string.isRequired,
};

export default VideoFeed;