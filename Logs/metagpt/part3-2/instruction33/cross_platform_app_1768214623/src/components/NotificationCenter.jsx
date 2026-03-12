import React, { useState } from "react";
import {
  Box,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Avatar,
  Badge,
  Button,
  Divider,
  Tooltip,
} from "@mui/material";
import NotificationsIcon from "@mui/icons-material/Notifications";
import DoneAllIcon from "@mui/icons-material/DoneAll";
import DeleteSweepIcon from "@mui/icons-material/DeleteSweep";
import MarkEmailReadIcon from "@mui/icons-material/MarkEmailRead";
import MarkEmailUnreadIcon from "@mui/icons-material/MarkEmailUnread";

// Example notifications data (in production, fetch from API or context)
const initialNotifications = [
  {
    id: "1",
    title: "Welcome!",
    body: "Thank you for joining our cross-platform app.",
    read: false,
    date: "2024-06-01T10:00:00Z",
  },
  {
    id: "2",
    title: "Profile Updated",
    body: "Your profile information was successfully updated.",
    read: true,
    date: "2024-06-02T14:30:00Z",
  },
  {
    id: "3",
    title: "New Feature",
    body: "Check out the new accessibility options in Settings.",
    read: false,
    date: "2024-06-03T09:15:00Z",
  },
];

const NotificationCenter = () => {
  const [notifications, setNotifications] = useState(initialNotifications);

  // Mark a notification as read
  const markAsRead = (id) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    );
  };

  // Mark all as read
  const markAllAsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  // Clear all notifications
  const clearAll = () => {
    setNotifications([]);
  };

  // Toggle read/unread
  const toggleRead = (id) => {
    setNotifications((prev) =>
      prev.map((n) =>
        n.id === id ? { ...n, read: !n.read } : n
      )
    );
  };

  const unreadCount = notifications.filter((n) => !n.read).length;

  return (
    <Box
      className="w-full max-w-2xl mx-auto py-6 px-4"
      sx={{ bgcolor: "background.default" }}
      aria-label="Notification center"
    >
      <Box className="flex items-center justify-between mb-4">
        <Box className="flex items-center gap-2">
          <Badge
            color="secondary"
            badgeContent={unreadCount}
            invisible={unreadCount === 0}
            aria-label={`${unreadCount} unread notifications`}
          >
            <NotificationsIcon color="primary" fontSize="large" />
          </Badge>
          <Typography variant="h4" color="primary" fontWeight={700}>
            Notifications
          </Typography>
        </Box>
        <Box className="flex gap-2">
          <Tooltip title="Mark all as read">
            <span>
              <IconButton
                color="primary"
                onClick={markAllAsRead}
                disabled={notifications.length === 0 || unreadCount === 0}
                aria-label="Mark all as read"
              >
                <DoneAllIcon />
              </IconButton>
            </span>
          </Tooltip>
          <Tooltip title="Clear all notifications">
            <span>
              <IconButton
                color="secondary"
                onClick={clearAll}
                disabled={notifications.length === 0}
                aria-label="Clear all notifications"
              >
                <DeleteSweepIcon />
              </IconButton>
            </span>
          </Tooltip>
        </Box>
      </Box>
      <Paper elevation={2} className="p-0" sx={{ borderRadius: 3 }}>
        {notifications.length === 0 ? (
          <Box className="flex flex-col items-center justify-center py-16">
            <NotificationsIcon color="disabled" fontSize="large" />
            <Typography variant="h6" color="text.secondary" className="mt-2">
              No notifications
            </Typography>
          </Box>
        ) : (
          <List>
            {notifications.map((n, idx) => (
              <React.Fragment key={n.id}>
                <ListItem
                  alignItems="flex-start"
                  className={`transition-colors ${
                    !n.read
                      ? "bg-blue-50 hover:bg-blue-100"
                      : "bg-white hover:bg-gray-50"
                  }`}
                  sx={{
                    borderLeft: !n.read ? "4px solid #1976d2" : "4px solid transparent",
                    py: 2,
                  }}
                  secondaryAction={
                    <Box className="flex items-center gap-1">
                      <Tooltip title={n.read ? "Mark as unread" : "Mark as read"}>
                        <IconButton
                          edge="end"
                          color={n.read ? "default" : "primary"}
                          onClick={() => toggleRead(n.id)}
                          aria-label={n.read ? "Mark as unread" : "Mark as read"}
                        >
                          {n.read ? <MarkEmailUnreadIcon /> : <MarkEmailReadIcon />}
                        </IconButton>
                      </Tooltip>
                    </Box>
                  }
                >
                  <ListItemAvatar>
                    <Avatar
                      sx={{
                        bgcolor: n.read ? "grey.300" : "primary.main",
                        color: n.read ? "grey.700" : "white",
                      }}
                      aria-label={n.read ? "Read notification" : "Unread notification"}
                    >
                      <NotificationsIcon />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary={
                      <Typography
                        variant="subtitle1"
                        fontWeight={n.read ? 400 : 700}
                        color={n.read ? "text.primary" : "primary"}
                        className="truncate"
                      >
                        {n.title}
                      </Typography>
                    }
                    secondary={
                      <>
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          className="block"
                        >
                          {n.body}
                        </Typography>
                        <Typography
                          variant="caption"
                          color="text.disabled"
                          className="block mt-1"
                        >
                          {new Date(n.date).toLocaleString()}
                        </Typography>
                      </>
                    }
                  />
                </ListItem>
                {idx < notifications.length - 1 && <Divider component="li" />}
              </React.Fragment>
            ))}
          </List>
        )}
      </Paper>
      {notifications.length > 0 && (
        <Box className="flex justify-end mt-4">
          <Button
            variant="outlined"
            color="secondary"
            startIcon={<DeleteSweepIcon />}
            onClick={clearAll}
            disabled={notifications.length === 0}
            aria-label="Clear all notifications"
          >
            Clear All
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default NotificationCenter;