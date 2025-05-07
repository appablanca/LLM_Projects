import React, { useState } from "react";
import {
  Box,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Typography,
  IconButton,
  useTheme,
} from "@mui/material";
import PersonOutlineOutlinedIcon from "@mui/icons-material/PersonOutlineOutlined";
import DashboardIcon from "@mui/icons-material/Dashboard";
import ListAltIcon from "@mui/icons-material/ListAlt";
import AccountBalanceWalletIcon from "@mui/icons-material/AccountBalanceWallet";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import SmartToyIcon from '@mui/icons-material/SmartToy';
import MenuIcon from "@mui/icons-material/Menu";
import { useNavigate, useLocation } from "react-router-dom";
import { tokens } from "../../theme";

const Sidebar = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

  const toggleSidebar = () => {
    setIsCollapsed((prev) => !prev);
  };

  return (
    <Box
      sx={{
        width: isCollapsed ? "80px" : "250px",
        height: "100vh",
        background: `linear-gradient(135deg, ${colors.primary[400]} 0%, ${colors.primary[600]} 100%)`,
        color: "white",
        display: "flex",
        flexDirection: "column",
        padding: 2,
        transition: "all 0.3s ease",
      }}
    >
      <IconButton
        onClick={toggleSidebar}
        sx={{
          color: "white",
          alignSelf: isCollapsed ? "center" : "flex-end",
          marginBottom: 2,
        }}
      >
        <MenuIcon />
      </IconButton>
      {!isCollapsed && (
        <Typography
          variant="h6"
          sx={{ mb: 3, fontWeight: "bold", textAlign: "center" }}
        >
          FINANCE COPILOT
        </Typography>
      )}
      <List>
        <ListItem
          button
          selected={location.pathname === "/dashboard"}
          onClick={() => navigate("/dashboard")}
          sx={{ justifyContent: isCollapsed ? "center" : "flex-start" }}
        >
          <ListItemIcon sx={{ color: "white", justifyContent: "center" }}>
            <DashboardIcon />
          </ListItemIcon>
          {!isCollapsed && <ListItemText primary="Dashboard" />}
        </ListItem>
        <ListItem
          button
          selected={location.pathname === "/copilot"}
          onClick={() => navigate("/copilot")}
          sx={{ justifyContent: isCollapsed ? "center" : "flex-start" }}
        >
          <ListItemIcon sx={{ color: "white", justifyContent: "center" }}>
            <SmartToyIcon />
          </ListItemIcon>
          {!isCollapsed && <ListItemText primary="Copilot" />}
        </ListItem>
        <ListItem
          button
          selected={location.pathname === "/profile"}
          onClick={() => navigate("/profile")}
          sx={{ justifyContent: isCollapsed ? "center" : "flex-start" }}
        >
          <ListItemIcon sx={{ color: "white", justifyContent: "center" }}>
            <PersonOutlineOutlinedIcon />
          </ListItemIcon>
          {!isCollapsed && <ListItemText primary="Profile" />}
        </ListItem>
        <ListItem
          button
          selected={location.pathname === "/transactions"}
          onClick={() => navigate("/transactions")}
          sx={{ justifyContent: isCollapsed ? "center" : "flex-start" }}
        >
          <ListItemIcon sx={{ color: "white", justifyContent: "center" }}>
            <ListAltIcon />
          </ListItemIcon>
          {!isCollapsed && <ListItemText primary="Transactions" />}
        </ListItem>
        <ListItem
          button
          selected={location.pathname === "/budget"}
          onClick={() => navigate("/budget")}
          sx={{ justifyContent: isCollapsed ? "center" : "flex-start" }}
        >
          <ListItemIcon sx={{ color: "white", justifyContent: "center" }}>
            <AccountBalanceWalletIcon />
          </ListItemIcon>
          {!isCollapsed && <ListItemText primary="Budget" />}
        </ListItem>
        <ListItem
          button
          selected={location.pathname === "/investments"}
          onClick={() => navigate("/investments")}
          sx={{ justifyContent: isCollapsed ? "center" : "flex-start" }}
        >
          <ListItemIcon sx={{ color: "white", justifyContent: "center" }}>
            <TrendingUpIcon />
          </ListItemIcon>
          {!isCollapsed && <ListItemText primary="Investments" />}
        </ListItem>
      </List>
    </Box>
  );
};

export default Sidebar;