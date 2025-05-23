import React, { useEffect, useState, useContext } from "react";
import {
  Box,
  Typography,
  useTheme,
  Paper,
  Grid,
  LinearProgress,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Button,
} from "@mui/material";
import { tokens } from "../../theme";
import { AuthContext } from "../../context/AuthContext";
import { getBudget } from "../../util/api";
import LoadingAnimation from "../../components/LoadingAnimation";

import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import TrendingDownIcon from "@mui/icons-material/TrendingDown";
import SavingsIcon from "@mui/icons-material/Savings";
import AttachMoneyIcon from "@mui/icons-material/AttachMoney";
import AccountBalanceIcon from "@mui/icons-material/AccountBalance";
import LightbulbIcon from "@mui/icons-material/Lightbulb";
import RefreshIcon from "@mui/icons-material/Refresh";

const Budget = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const { user } = useContext(AuthContext);
  const [budgetData, setBudgetData] = useState(null);

  useEffect(() => {
    const fetchBudgetData = async () => {
      const cached = sessionStorage.getItem("budgetData");
      if (cached) {
        setBudgetData(JSON.parse(cached));
      } else {
        try {
          const data = await getBudget();
          sessionStorage.setItem("budgetData", JSON.stringify(data.response));
          setBudgetData(data.response);
        } catch (error) {
          console.error("Failed to fetch budget data:", error);
        }
      }
    };
    fetchBudgetData();
  }, []);

  const handleRefresh = async () => {
    setBudgetData(null);
    try {
      const data = await getBudget();
      sessionStorage.setItem("budgetData", JSON.stringify(data.response));
      setBudgetData(data.response);
    } catch (error) {
      console.error("Failed to refresh budget data:", error);
    }
  };

  if (!budgetData) {
    return (
      <Box p={3}>
        <LoadingAnimation />
      </Box>
    );
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('tr-TR', {
      style: 'currency',
      currency: 'TRY',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom sx={{ color: colors.grey[800] }}>
        Budget Overview
      </Typography>
      <Box display="flex" justifyContent="flex-end" mb={2}>
        <Button
          variant="contained"
          color="secondary"
          onClick={handleRefresh}
          startIcon={<RefreshIcon />}
        >
          Refresh Your Data
        </Button>
      </Box>

      {/* Financial Health Card */}
      <Card sx={{ mb: 3, backgroundColor: colors.primary[500] }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={2} mb={2}>
            <AccountBalanceIcon sx={{ color: colors.greenAccent[400], fontSize: 40 }} />
            <Box>
              <Typography variant="h5" sx={{ color: colors.grey[100] }}>
                Financial Health: {budgetData.financial_health.status}
              </Typography>
              <Typography variant="body2" sx={{ color: colors.grey[300] }}>
                {budgetData.financial_health.recommendation}
              </Typography>
            </Box>
          </Box>
          <LinearProgress
            variant="determinate"
            value={budgetData.financial_health.percentage_of_financial_health}
            sx={{
              height: 10,
              borderRadius: 5,
              backgroundColor: colors.grey[700],
              "& .MuiLinearProgress-bar": {
                backgroundColor: colors.greenAccent[400],
              },
            }}
          />
          <Box display="flex" justifyContent="flex-end" mt={1}>
            <Typography variant="body1" sx={{ color: colors.grey[100] }}>
              {budgetData.financial_health.percentage_of_financial_health}%
            </Typography>
          </Box>
        </CardContent>
      </Card>

      {/* Financial Summary Grid */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Card sx={{ backgroundColor: colors.primary[500] }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <AttachMoneyIcon sx={{ color: colors.greenAccent[400], fontSize: 30 }} />
                <Box>
                  <Typography variant="h6" sx={{ color: colors.grey[100] }}>
                    Monthly Income
                  </Typography>
                  <Typography variant="h4" sx={{ color: colors.grey[100] }}>
                    {formatCurrency(budgetData.financial_summary.monthly_income_calculated_by_transcation)}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ backgroundColor: colors.primary[500] }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <TrendingDownIcon sx={{ color: colors.redAccent[400], fontSize: 30 }} />
                <Box>
                  <Typography variant="h6" sx={{ color: colors.grey[100] }}>
                    Total Spending
                  </Typography>
                  <Typography variant="h4" sx={{ color: colors.grey[100] }}>
                    {formatCurrency(budgetData.financial_summary.total_spending_calculated_by_transaction)}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ backgroundColor: colors.primary[500] }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <TrendingUpIcon sx={{ color: colors.greenAccent[400], fontSize: 30 }} />
                <Box>
                  <Typography variant="h6" sx={{ color: colors.grey[100] }}>
                    Net Difference
                  </Typography>
                  <Typography variant="h4" sx={{ color: colors.grey[100] }}>
                    {formatCurrency(budgetData.financial_summary.net_difference_calculated_by_transaction)}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Spending Analysis and Recommendations Grid */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card sx={{ backgroundColor: colors.primary[500], height: "100%" }}>
            <CardContent>
              <Typography variant="h6" sx={{ color: colors.grey[100], mb: 2 }}>
                Spending Analysis
              </Typography>
              <List>
                {budgetData.spending_analysis.map((item, index) => (
                  <React.Fragment key={index}>
                    <ListItem>
                      <ListItemText
                        primary={
                          <Typography variant="subtitle1" sx={{ color: colors.grey[100] }}>
                            {item.category}
                          </Typography>
                        }
                        secondary={
                          <Typography variant="body2" sx={{ color: colors.grey[300] }}>
                            {item.comment}
                          </Typography>
                        }
                      />
                      <Typography variant="h6" sx={{ color: colors.grey[100] }}>
                        {formatCurrency(item.amount)}
                      </Typography>
                    </ListItem>
                    {index < budgetData.spending_analysis.length - 1 && (
                      <Divider sx={{ backgroundColor: colors.grey[700] }} />
                    )}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card sx={{ backgroundColor: colors.primary[500], height: "100%" }}>
            <CardContent>
              <Typography variant="h6" sx={{ color: colors.grey[100], mb: 2 }}>
                Saving Suggestions
              </Typography>
              <List>
                {budgetData.saving_suggestions.map((suggestion, index) => (
                  <React.Fragment key={index}>
                    <ListItem>
                      <ListItemIcon>
                        <SavingsIcon sx={{ color: colors.greenAccent[400] }} />
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Typography variant="subtitle1" sx={{ color: colors.grey[100] }}>
                            {suggestion.area}
                          </Typography>
                        }
                        secondary={
                          <Typography variant="body2" sx={{ color: colors.grey[300] }}>
                            {suggestion.suggestion}
                          </Typography>
                        }
                      />
                      <Typography variant="h6" sx={{ color: colors.greenAccent[400] }}>
                        {formatCurrency(suggestion.expected_saving)}
                      </Typography>
                    </ListItem>
                    {index < budgetData.saving_suggestions.length - 1 && (
                      <Divider sx={{ backgroundColor: colors.grey[700] }} />
                    )}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Improvement Recommendations */}
      <Card sx={{ mt: 3, backgroundColor: colors.primary[500] }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={2} mb={2}>
            <LightbulbIcon sx={{ color: colors.greenAccent[400], fontSize: 30 }} />
            <Typography variant="h6" sx={{ color: colors.grey[100] }}>
              Improvement Recommendations
            </Typography>
          </Box>
          <List>
            {budgetData.improvement_recommendations.map((recommendation, index) => (
              <ListItem key={index}>
                <ListItemText
                  primary={
                    <Typography variant="body1" sx={{ color: colors.grey[100] }}>
                      {recommendation}
                    </Typography>
                  }
                />
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Budget;
