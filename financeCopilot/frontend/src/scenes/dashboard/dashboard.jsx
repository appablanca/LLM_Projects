import React, { useEffect, useState, useContext } from "react";
import { Box, Typography, useTheme, Button } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { tokens } from "../../theme";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import LightbulbIcon from "@mui/icons-material/Lightbulb";
import { AuthContext } from "../../context/AuthContext";
import { getTransactions } from "../../util/api";
import SpendingPieChart from "../../components/SpendingPieChart";

const Dashboard = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const { user } = useContext(AuthContext);
  const [surveyCompleted, setSurveyCompleted] = useState(false);
  const [categoryTotals, setCategoryTotals] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    if (user.isSurvey === 1) {
      setSurveyCompleted(true);
      sessionStorage.setItem("surveyCompleted", "true");
    } else {
      setSurveyCompleted(false);
      sessionStorage.setItem("surveyCompleted", "false");
    }
  }, [user]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getTransactions();
        console.log("Fetched category totals:", data); 
        setCategoryTotals(data.category_totals);
      } catch (error) {
        console.error("Failed to fetch transactions:", error);
      }
    };

    if (user?.id) {
      fetchData();
    }
  }, [user]);

  return (
    <Box sx={{ display: "flex", minHeight: "100vh" }}>
      <Box sx={{ flex: 1, p: 3 }}>
        <Typography variant="h4" gutterBottom sx={{ color: colors.grey[900] }}>
          Dashboard
        </Typography>
        <Typography variant="body1" sx={{ color: colors.grey[800] }}>
          Welcome to your financial dashboard. Here's an overview of your recent
          activity and spending.
        </Typography>

        <Box
          sx={{
            mt: 4,
            p: 3,
            borderRadius: 2,
            maxWidth: "500px",
            backgroundColor: colors.primary[700],
            border: `1px solid ${colors.grey[300]}`,
          }}
        >
          <Box
            display="flex"
            alignItems="center"
            justifyContent="space-between"
          >
            <Box display="flex" alignItems="center" gap={1}>
              <LightbulbIcon sx={{ color: "yellow" }} />
              <Typography variant="h6" sx={{ color: colors.grey[100] }}>
                Please personalize your AI with the survey
              </Typography>
            </Box>
            {surveyCompleted && (
              <Box display="flex" alignItems="center" gap={1}>
                <CheckCircleOutlineIcon
                  sx={{ color: colors.greenAccent[400] }}
                />
                <Typography
                  variant="body2"
                  sx={{ color: colors.greenAccent[400] }}
                >
                  100% Completed
                </Typography>
              </Box>
            )}
          </Box>

          <Button
            variant="outlined"
            onClick={() => navigate("/profile")}
            sx={{
              mt: 2,
              color: colors.grey[100],
              borderColor: colors.grey[100],
              "&:hover": {
                backgroundColor: colors.primary[300],
                borderColor: colors.primary[300],
              },
            }}
          >
            Go to Survey
          </Button>
        </Box>
        <Box mt={2} sx={{ maxWidth: "700px"}}>
          <SpendingPieChart categoryTotals={categoryTotals} />
        </Box>
      </Box>
    </Box>
  );
};

export default Dashboard;
