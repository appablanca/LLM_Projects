// components/FinancialHealthCircleCard.jsx
import React from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  CircularProgress,
} from "@mui/material";
import AccountBalanceIcon from "@mui/icons-material/AccountBalance";
import MonitorHeartIcon from "@mui/icons-material/MonitorHeart";
import { tokens } from "../theme";

const FinancialHealthCircleCard = ({ budgetData, theme }) => {
  const colors = tokens(theme.palette.mode);
  const percentage =
    budgetData?.financial_health?.percentage_of_financial_health || 0;

  return (
    <Card
      sx={{
        backgroundColor: colors.primary[700],
        width: 200,
        border: `1px solid ${colors.grey[300]}`,
        borderRadius: 2,
      }}
    >
      <CardContent>
        <Box display="flex" flexDirection="column" alignItems="center">
          <Typography variant="h6" sx={{ color: colors.grey[100], mb: 1 }}>
            Your Financial Health
          </Typography>
          <MonitorHeartIcon
            sx={{ fontSize: 40, color: colors.greenAccent[400], mb: 1 }}
          />
          <Box position="relative" display="inline-flex">
            <CircularProgress
              variant="determinate"
              value={percentage}
              size={100}
              thickness={4}
              sx={{
                color: colors.greenAccent[400],
              }}
            />
            <Box
              top={0}
              left={0}
              bottom={0}
              right={0}
              position="absolute"
              display="flex"
              alignItems="center"
              justifyContent="center"
            >
              <Typography variant="h6" sx={{ color: colors.grey[100] }}>
                {percentage}%
              </Typography>
            </Box>
          </Box>
          <Typography
            variant="subtitle1"
            align="center"
            mt={1}
            sx={{ color: colors.grey[100] }}
          >
            {budgetData?.financial_health?.status}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default FinancialHealthCircleCard;
