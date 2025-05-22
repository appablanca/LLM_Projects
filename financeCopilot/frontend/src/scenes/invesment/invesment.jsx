import React, { useEffect, useState } from "react";
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Button,
  useTheme,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import { getUserStocks, removeUserStock } from "../../util/api";
import { tokens } from "../../theme";
const Invesment = () => {
  const [trackedStocks, setTrackedStocks] = useState([]);
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

  useEffect(() => {
    fetchTrackedStocks();
  }, []);

  const fetchTrackedStocks = async () => {
    try {
      const response = await getUserStocks();
      setTrackedStocks(response.data.stocks || []);
    } catch (error) {
      console.error("Failed to fetch tracked stocks:", error);
    }
  };

  const removeStock = async (symbol) => {
    try {
      await removeUserStock(symbol);
      setTrackedStocks((prev) => prev.filter((s) => s !== symbol));
    } catch (error) {
      console.error("Failed to remove stock:", error);
    }
  };

  return (
    <Box m="20px">
      <Typography variant="h4" gutterBottom sx={{ color: colors.grey[800] }}>
        Tracked Stocks
      </Typography>
      {trackedStocks.length === 0 ? (
        <Typography sx={{ color: colors.grey[300] }}>
          No tracked stocks found.
        </Typography>
      ) : (
        <List>
          {trackedStocks.map((symbol) => (
            <ListItem
              sx={{
                backgroundColor: colors.primary[500],
                borderRadius: 1,
                mb: 1,
              }}
              key={symbol}
              secondaryAction={
                <IconButton edge="end" onClick={() => removeStock(symbol)}>
                  <DeleteIcon />
                </IconButton>
              }
            >
              <ListItemText
                primary={
                  <Typography sx={{ color: colors.grey[100] }}>
                    {symbol}
                  </Typography>
                }
              />
            </ListItem>
          ))}
        </List>
      )}
    </Box>
  );
};

export default Invesment;
