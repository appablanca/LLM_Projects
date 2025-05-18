import React, { useEffect, useState, useContext } from "react";
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TextField,
  InputLabel,
  MenuItem,
  Select,
  FormControl,
  Typography,
  useTheme,
} from "@mui/material";
import { tokens } from "../../theme";
import { AuthContext } from "../../context/AuthContext";
import { getTransactions } from "../../util/api";

const Transactions = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const { user } = useContext(AuthContext);
  const [transactions, setTransactions] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [filters, setFilters] = useState({
    spendingCategory: "",
    startDate: "",
    endDate: "",
    minAmount: "",
    maxAmount: "",
  });

  useEffect(() => {
    const fetchData = async () => {
      const data = await getTransactions();
      setTransactions(data.transactions || []);
      setFiltered(data.transactions || []);
    };
    fetchData();
  }, []);

  useEffect(() => {
    const result = transactions.filter((t) => {
      const matchesCategory = !filters.spendingCategory || t.spendingCategory === filters.spendingCategory;
      const matchesDate =
        (!filters.startDate || t.date >= filters.startDate) &&
        (!filters.endDate || t.date <= filters.endDate);
      const amountStr = t.amount.replace(/\./g, "").replace(",", ".").replace(" TL", "");
      const amountValue = parseFloat(amountStr);
      const matchesAmount =
        (!filters.minAmount || amountValue >= parseFloat(filters.minAmount)) &&
        (!filters.maxAmount || amountValue <= parseFloat(filters.maxAmount));
      return matchesCategory && matchesDate && matchesAmount;
    });
    setFiltered(result);
  }, [filters, transactions]);

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom sx={{ color: colors.grey[800] }}>
        All Transactions
      </Typography>
      <Box display="flex" gap={2} mb={2} flexWrap="wrap" p={2} borderRadius={2} sx={{ backgroundColor: colors.primary[100] }}>
        <FormControl sx={{ minWidth: 150 }}>
          <InputLabel sx={{ color: colors.grey[800] }}>Category</InputLabel>
          <Select
            value={filters.spendingCategory}
            label="Category"
            onChange={(e) =>
              setFilters({ ...filters, spendingCategory: e.target.value })
            }
            sx={{ color: colors.grey[800] }}
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value="food_drinks">Food & Drinks</MenuItem>
            <MenuItem value="groceries">Groceries</MenuItem>
            <MenuItem value="entertainment">Entertainment</MenuItem>
            <MenuItem value="bill_payment">Bill Payment</MenuItem>
            <MenuItem value="other">Other</MenuItem>
          </Select>
        </FormControl>
        <TextField
          label="Start Date"
          type="text"
          placeholder="e.g., 01.05.2025"
          value={filters.startDate}
          onChange={(e) => setFilters({ ...filters, startDate: e.target.value })}
          sx={{ input: { color: colors.grey[800] }, label: { color: colors.grey[800] } }}
        />
        <TextField
          label="End Date"
          type="text"
          placeholder="e.g., 07.05.2025"
          value={filters.endDate}
          onChange={(e) => setFilters({ ...filters, endDate: e.target.value })}
          sx={{ input: { color: colors.grey[800] }, label: { color: colors.grey[800] } }}
        />
        <TextField
          label="Min Amount"
          type="number"
          placeholder="e.g., 100"
          value={filters.minAmount}
          onChange={(e) => setFilters({ ...filters, minAmount: e.target.value })}
          sx={{ input: { color: colors.grey[800] }, label: { color: colors.grey[800] } }}
        />
        <TextField
          label="Max Amount"
          type="number"
          placeholder="e.g., 1000"
          value={filters.maxAmount}
          onChange={(e) => setFilters({ ...filters, maxAmount: e.target.value })}
          sx={{ input: { color: colors.grey[800] }, label: { color: colors.grey[800] } }}
        />
      </Box>

      <TableContainer component={Paper} sx={{ maxHeight: "70vh", backgroundColor: colors.primary[500] }}>
        <Table stickyHeader>
          <TableHead>
            <TableRow sx={{ backgroundColor: colors.primary[700] }}>
              <TableCell sx={{ color: colors.grey[100], backgroundColor: colors.primary[700] }}>Date</TableCell>
              <TableCell sx={{ color: colors.grey[100], backgroundColor: colors.primary[700] }}>Category</TableCell>
              <TableCell sx={{ color: colors.grey[100], backgroundColor: colors.primary[700] }}>Description</TableCell>
              <TableCell align="right" sx={{ color: colors.grey[100], backgroundColor: colors.primary[700] }}>Amount</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filtered.map((tx) => (
              <TableRow key={tx._id}>
                <TableCell sx={{ color: colors.grey[100] }}>{tx.date}</TableCell>
                <TableCell sx={{ color: colors.grey[100] }}>{tx.spendingCategory}</TableCell>
                <TableCell sx={{ color: colors.grey[100] }}>{tx.description}</TableCell>
                <TableCell align="right" sx={{ color: colors.grey[100] }}>{tx.amount}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default Transactions;