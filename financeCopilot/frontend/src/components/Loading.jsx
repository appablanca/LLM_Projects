import React from "react";
import { Box, useTheme } from "@mui/material";
import { tokens } from "../theme";
import pgLoadOrg from "../assets/pgLoadOrg.png"; // İçi dolu görsel
import pgLoadBlur from "../assets/pgLoadBlur.png"; // İçi boş görsel

const Loading = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

  return (
    <Box
      id="loading-screen"
      data-testid="loading-screen"
      sx={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        backgroundColor: theme.palette.mode === "dark" 
          ? `${colors.primary[400]}e6` // e6 adds transparency (90%)
          : "rgba(255, 255, 255, 0.9)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 9999, // Increased to be above all content
        backdropFilter: "blur(5px)", // Add blur effect to background
      }}
    >
      {/* Görsellerin Konteyneri */}
      <Box
        sx={{
          width: "200px",
          height: "200px",
          position: "relative",
          filter: theme.palette.mode === "dark" ? "brightness(0.8)" : "none",
        }}
      >
        {/* İçi Boş Görsel */}
        <img
          src={pgLoadBlur}
          alt="Loading Animation Background"
          style={{
            width: "100%",
            height: "100%",
            objectFit: "contain",
            position: "absolute",
            animation: "fadeOut 2s ease-in-out infinite",
            opacity: 0.7,
          }}
        />

        {/* İçi Dolu Görsel */}
        <img
          src={pgLoadOrg}
          alt="Loading Animation"
          style={{
            width: "100%",
            height: "100%",
            objectFit: "contain",
            position: "absolute",
            animation: "fadeIn 2s ease-in-out infinite",
          }}
        />
      </Box>

      <style>
        {`
          @keyframes fadeIn {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
          }

          @keyframes fadeOut {
            0%, 100% { opacity: 0.3; }
            50% { opacity: 1; }
          }

          #loading-screen {
            transition: opacity 0.3s ease-in-out;
          }

          #loading-screen.hide {
            opacity: 0;
            pointer-events: none;
          }
        `}
      </style>
    </Box>
  );
};

export default Loading;