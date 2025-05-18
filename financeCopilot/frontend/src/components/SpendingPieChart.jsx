import React from "react";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from "recharts";
import { Box, Typography, useTheme } from "@mui/material";
import { tokens } from "../theme";

const SpendingPieChart = ({ categoryTotals }) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

  // Fallback for undefined or empty input
  if (!categoryTotals || Object.keys(categoryTotals).length === 0) return null;

  // Convert categoryTotals into the required format for the pie chart
  const data = Object.entries(categoryTotals).map(([name, value]) => ({
    name: name
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" "),
    value: parseFloat(
      value.replace("TL", "").replace(".", "").replace(",", ".")
    ),
  }));

  // Custom colors for the pie chart
  const COLORS = [
    "#66BB6A", // green
    "#42A5F5", // blue
    "#EF5350", // red
    "#FFCA28", // yellow
    "#AB47BC", // purple
    "#FFA726", // orange
    "#26A69A", // teal
  ];

  // Custom tooltip formatter
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <Box
          sx={{
            backgroundColor: colors.primary[500],
            padding: "10px",
            border: `1px solid ${colors.primary[300]}`,
            borderRadius: "4px",
          }}
        >
          <Typography variant="body2" color={colors.grey[100]}>
            {`${payload[0].name}: ${payload[0].value.toLocaleString("tr-TR", {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })} TL`}
          </Typography>
        </Box>
      );
    }
    return null;
  };

  return (
    <Box
      sx={{
        height: "5  00px",
        width: "100%",
        backgroundColor: colors.primary[700],
        border: `1px solid ${colors.grey[300]}`,
        borderRadius: 2,
        padding: "5px",
      }}
    >
      <Typography variant="h5" sx={{ mb: 2, color: colors.grey[100] }}>
        Your Spendings by Category
      </Typography>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            outerRadius={120}
            fill="#8884d8"
            dataKey="value"
            label={({ name, percent }) =>
              `${name} (${(percent * 100).toFixed(0)}%)`
            }
          >
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={COLORS[index % COLORS.length]}
              />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default SpendingPieChart;
