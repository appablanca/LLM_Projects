import React, { useState, useEffect } from "react";
import { Snackbar, Alert, IconButton } from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";

const ConnectionStatus = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [showSnackbar, setShowSnackbar] = useState(false);

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      setShowSnackbar(true);
    };

    const handleOffline = () => {
      setIsOnline(false);
      setShowSnackbar(true);
    };

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  const handleCloseSnackbar = () => {
    setShowSnackbar(false);
  };

  return (
    <Snackbar
      open={showSnackbar}
      onClose={(event, reason) => {
        if (reason === "clickaway") return;
        handleCloseSnackbar();
      }}      anchorOrigin={{ vertical: "top", horizontal: "center" }}
    >
      <Alert
        severity={isOnline ? "success" : "error"}
        action={
          <IconButton
            size="small"
            aria-label="close"
            color="inherit"
            onClick={handleCloseSnackbar}
          >
            <CloseIcon fontSize="small" />
          </IconButton>
        }
        sx={{ width: "100%" }}
      >
        {isOnline ? "You are online now!" : "You are offline. Some features may not be available!"}
      </Alert>
    </Snackbar>
  );
};

export default ConnectionStatus;