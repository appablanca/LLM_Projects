import React, { useState, useContext } from "react";
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
import SmartToyIcon from "@mui/icons-material/SmartToy";
import MenuIcon from "@mui/icons-material/Menu";
import PaidIcon from '@mui/icons-material/Paid';
import LogoutIcon from "@mui/icons-material/Logout";
import { useNavigate, useLocation } from "react-router-dom";
import { tokens } from "../../theme";
import { AuthContext } from "../../context/AuthContext";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import Button from "@mui/material/Button";
import LoadingAnimation from "../../components/LoadingAnimation";

const Sidebar = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [logoutDialogOpen, setLogoutDialogOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useContext(AuthContext);
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
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <Typography
            variant="h6"
            sx={{ mb: 1, fontWeight: "bold", textAlign: "center" }}
          >
            FINANCE COPILOT
          </Typography>
          <Box sx={{ display: "flex", gap: 1, mb: 3 }}>
            <Typography variant="subtitle1" sx={{ textAlign: "center" }}>
              {user.name}
            </Typography>
            <Typography variant="subtitle1" sx={{ textAlign: "center" }}>
              {user.surname}
            </Typography>
          </Box>
        </Box>
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

        {/* Invesment Button */}
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

        {/* Subscription button */}
        <ListItem
          button
          selected={location.pathname === "/subscription"}
          onClick={() => navigate("/subscription")}
          sx={{ justifyContent: isCollapsed ? "center" : "flex-start" }}
        >
          <ListItemIcon sx={{ color: "white", justifyContent: "center" }}>
            <PaidIcon />
          </ListItemIcon>
          {!isCollapsed && <ListItemText primary="Subscription" />}
        </ListItem>

        {/* Logout button */}
        <ListItem
          button
          onClick={() => setLogoutDialogOpen(true)}
          sx={{ justifyContent: isCollapsed ? "center" : "flex-start", mt: "auto" }}
        >
          <ListItemIcon sx={{ color: "white", justifyContent: "center" }}>
            <LogoutIcon />
          </ListItemIcon>
          {!isCollapsed && <ListItemText primary="Logout" />}
        </ListItem>
      </List>
      <Dialog
        open={logoutDialogOpen}
        onClose={() => setLogoutDialogOpen(false)}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
        sx={{
          "& .MuiDialog-paper": {
            backgroundColor: colors.primary[400],
            color: "white",
          },
        }}
      >
        <DialogTitle>{"Confirm Logout"}</DialogTitle>
        <DialogContent>
          <DialogContentText >
            Are you sure about logging out?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setLogoutDialogOpen(false)} color="error">
            No
          </Button>
          <Button onClick={logout} color="primary" autoFocus>
            Yes
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Sidebar;
