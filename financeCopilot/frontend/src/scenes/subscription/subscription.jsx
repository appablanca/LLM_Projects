import React from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  useTheme,
} from "@mui/material";
import { tokens } from "../../theme";

const Subscription = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

  const plans = [
    {
      title: "Monthly Plan",
      price: "₺99.99 / month",
      description: "Ideal for short-term usage with full AI capabilities.",
    },
    {
      title: "Yearly Plan",
      price: "₺999.99 / year",
      description: "Best value for long-term users with full features.",
    },
  ];

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        p: 4,
      }}
    >
      <Grid container spacing={4} justifyContent="center">
        {plans.map((plan, index) => (
          <Grid item xs={12} sm={6} md={4} key={index}>
            <Card
              sx={{
                background: `linear-gradient(135deg, ${colors.primary[600]} 0%, ${colors.primary[800]} 100%)`,
                borderRadius: 4,
                p: 4,
                textAlign: "center",
                boxShadow: "0 8px 20px rgba(0,0,0,0.3)",
                color: colors.grey[100],
                transition: "transform 0.3s ease, box-shadow 0.3s ease",
                "&:hover": {
                  transform: "scale(1.03)",
                  boxShadow: `0 10px 30px ${colors.greenAccent[400]}44`,
                },
              }}
            >
              <CardContent>
                <Typography variant="h4" gutterBottom sx={{ fontWeight: 700, letterSpacing: 1 }}>
                  {plan.title}
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Box
                    sx={{
                      display: "inline-block",
                      px: 1,
                      py: 0.5,
                      mb: 1,
                      borderRadius: 1,
                      backgroundColor: colors.greenAccent[600],
                      color: colors.grey[900],
                      fontWeight: "bold",
                      fontSize: "0.75rem",
                    }}
                  >
                    SPECIAL OFFER -20%
                  </Box>
                  <Typography
                    variant="body2"
                    sx={{
                      color: colors.grey[400],
                      textDecoration: "line-through",
                    }}
                  >
                    {plan.price}
                  </Typography>
                  <Typography
                    variant="h5"
                    sx={{
                      color: colors.greenAccent[400],
                      fontWeight: 700,
                    }}
                  >
                    {plan.title === "Monthly Plan" ? "₺79.99 / month" : "₺799.99 / year"}
                  </Typography>
                </Box>
                <Typography variant="body2" sx={{ mb: 3, color: colors.grey[300] }}>
                  {plan.description}
                </Typography>
                <Button
                  variant="contained"
                  fullWidth
                  sx={{
                    mt: 2,
                    py: 1.5,
                    fontWeight: 600,
                    backgroundColor: colors.greenAccent[600],
                    color: colors.grey[900],
                    borderRadius: 2,
                    textTransform: "uppercase",
                    "&:hover": {
                      backgroundColor: colors.greenAccent[500],
                      boxShadow: `0 0 12px ${colors.greenAccent[400]}`,
                    },
                  }}
                >
                  Choose Plan
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default Subscription;