import React from "react";
import { Box, List, ListItem, ListItemIcon, ListItemText, Typography } from "@mui/material";
import DashboardIcon from "@mui/icons-material/Dashboard";
import ListAltIcon from "@mui/icons-material/ListAlt";
import AccountBalanceWalletIcon from "@mui/icons-material/AccountBalanceWallet";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import { useNavigate, useLocation } from "react-router-dom";

const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <Box
      sx={{
        width: "250px",
        height: "100vh",
        backgroundColor: "#2C2F48",
        color: "white",
        display: "flex",
        flexDirection: "column",
        padding: 2,
      }}
    >
      <Typography variant="h6" sx={{ mb: 3, fontWeight: "bold" }}>
        FINANCE COPILOT
      </Typography>
      <List>
        <ListItem button selected={location.pathname === "/dashboard"} onClick={() => navigate("/dashboard")}>
          <ListItemIcon sx={{ color: "white" }}>
            <DashboardIcon />
          </ListItemIcon>
          <ListItemText primary="Dashboard" />
        </ListItem>
        <ListItem button selected={location.pathname === "/transactions"} onClick={() => navigate("/transactions")}>
          <ListItemIcon sx={{ color: "white" }}>
            <ListAltIcon />
          </ListItemIcon>
          <ListItemText primary="Transactions" />
        </ListItem>
        <ListItem button selected={location.pathname === "/budget"} onClick={() => navigate("/budget")}>
          <ListItemIcon sx={{ color: "white" }}>
            <AccountBalanceWalletIcon />
          </ListItemIcon>
          <ListItemText primary="Budget" />
        </ListItem>
        <ListItem button selected={location.pathname === "/investments"} onClick={() => navigate("/investments")}>
          <ListItemIcon sx={{ color: "white" }}>
            <TrendingUpIcon />
          </ListItemIcon>
          <ListItemText primary="Investments" />
        </ListItem>
      </List>
    </Box>
  );
};

export default Sidebar;