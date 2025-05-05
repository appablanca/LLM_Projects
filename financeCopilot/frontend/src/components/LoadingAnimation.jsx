import React from "react";
import { Box, CircularProgress, Typography, useTheme } from "@mui/material";
import { tokens } from "../theme";
import FitnessCenterIcon from '@mui/icons-material/FitnessCenter';

const LoadingAnimation = ({ fullScreen = false, message = "Loading..." }) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      height={fullScreen ? "100vh" : "300px"}
      bgcolor={fullScreen ? colors.primary[400] : "transparent"}
    >
      <Box
        sx={{
          position: 'relative',
          display: 'inline-flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Box
          sx={{
            position: 'relative',
            display: 'inline-flex',
            animation: 'bounce 2s infinite',
            '@keyframes bounce': {
              '0%, 100%': {
                transform: 'translateY(0)',
              },
              '50%': {
                transform: 'translateY(-20px)',
              },
            },
          }}
        >
          <CircularProgress
            size={80}
            thickness={4}
            sx={{
              color: colors.greenAccent[500],
            }}
          />
          <Box
            sx={{
              top: 0,
              left: 0,
              bottom: 0,
              right: 0,
              position: 'absolute',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <FitnessCenterIcon
              sx={{
                fontSize: 40,
                color: colors.grey[100],
                animation: 'rotate 2s linear infinite',
                '@keyframes rotate': {
                  '0%': {
                    transform: 'rotate(0deg)',
                  },
                  '100%': {
                    transform: 'rotate(360deg)',
                  },
                },
              }}
            />
          </Box>
        </Box>
        <Typography
          variant="h6"
          sx={{
            color: colors.grey[100],
            mt: 2,
            textAlign: 'center',
            animation: 'fadeInOut 1.5s infinite',
            '@keyframes fadeInOut': {
              '0%, 100%': {
                opacity: 1,
              },
              '50%': {
                opacity: 0.5,
              },
            },
          }}
        >
          {message}
        </Typography>
        <Typography
          variant="body2"
          sx={{
            color: colors.grey[300],
            mt: 1,
            textAlign: 'center',
          }}
        >
          Please wait while we load your data...
        </Typography>
      </Box>
    </Box>
  );
};

export default LoadingAnimation; 