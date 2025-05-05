

import React from "react";
import { Box, Typography } from "@mui/material";
import Sidebar from "../global/sidebar"; // Adjust the path if needed

const Dashboard = () => {
  return (
    <Box sx={{ display: "flex" }}>
      <Sidebar />
      <Box sx={{ flex: 1, p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        <Typography variant="body1">
          Welcome to your financial dashboard. Here's an overview of your recent activity and spending.
        </Typography>
      </Box>
    </Box>
  );
};

export default Dashboard;