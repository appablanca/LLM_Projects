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
    flow: "", // New filter for flow
  });
  const [sortOption, setSortOption] = useState("");

  // Helper to parse "dd.mm.yyyy" or "dd/mm/yyyy" to Date object
  const parseDate = (str) => {
    if (!str) return new Date("Invalid Date");
    const delimiter = str.includes(".") ? "." : "/";
    const [day, month, year] = str.split(delimiter);
    return new Date(`${year}-${month}-${day}`);
  };

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
      const matchesFlow = !filters.flow || t.flow === filters.flow; // New flow filter logic
      return matchesCategory && matchesDate && matchesAmount && matchesFlow;
    });

    let sorted = [...result];
    switch (sortOption) {
      case "date_asc":
        sorted.sort((a, b) => parseDate(a.date) - parseDate(b.date));
        break;
      case "date_desc":
        sorted.sort((a, b) => parseDate(b.date) - parseDate(a.date));
        break;
      case "amount_asc":
        sorted.sort((a, b) => {
          const getAmount = (s) => parseFloat(s.amount.replace(/\./g, "").replace(",", ".").replace(" TL", ""));
          return getAmount(a) - getAmount(b);
        });
        break;
      case "amount_desc":
        sorted.sort((a, b) => {
          const getAmount = (s) => parseFloat(s.amount.replace(/\./g, "").replace(",", ".").replace(" TL", ""));
          return getAmount(b) - getAmount(a);
        });
        break;
      default:
        break;
    }
    setFiltered(sorted);
  }, [filters, transactions, sortOption]);

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
        <FormControl sx={{ minWidth: 150 }}>
          <InputLabel sx={{ color: colors.grey[800] }}>Flow</InputLabel>
          <Select
            value={filters.flow}
            label="Flow"
            onChange={(e) => setFilters({ ...filters, flow: e.target.value })}
            sx={{ color: colors.grey[800] }}
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value="income">Income</MenuItem>
            <MenuItem value="spending">Spending</MenuItem>
          </Select>
        </FormControl>
        <FormControl sx={{ minWidth: 180 }}>
          <InputLabel sx={{ color: colors.grey[800] }}>Sort By</InputLabel>
          <Select
            value={sortOption}
            label="Sort By"
            onChange={(e) => setSortOption(e.target.value)}
            sx={{ color: colors.grey[800] }}
          >
            <MenuItem value="">None</MenuItem>
            <MenuItem value="date_asc">Date (Oldest First)</MenuItem>
            <MenuItem value="date_desc">Date (Newest First)</MenuItem>
            <MenuItem value="amount_asc">Amount (Low to High)</MenuItem>
            <MenuItem value="amount_desc">Amount (High to Low)</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <TableContainer component={Paper} sx={{ maxHeight: "70vh", backgroundColor: colors.primary[500] }}>
        <Table stickyHeader>
          <TableHead>
            <TableRow sx={{ backgroundColor: colors.primary[700] }}>
              <TableCell sx={{ color: colors.grey[100], backgroundColor: colors.primary[700] }}>Date</TableCell>
              <TableCell sx={{ color: colors.grey[100], backgroundColor: colors.primary[700] }}>Category</TableCell>
              <TableCell sx={{ color: colors.grey[100], backgroundColor: colors.primary[700] }}>Description</TableCell>
              <TableCell align="right" sx={{ color: colors.grey[100], backgroundColor: colors.primary[700] }}>Amount</TableCell>
              <TableCell sx={{ color: colors.grey[100], backgroundColor: colors.primary[700] }}>Flow</TableCell> {/* New column */}
            </TableRow>
          </TableHead>
          <TableBody>
            {filtered.map((tx) => (
              <TableRow key={tx._id}>
                <TableCell sx={{ color: colors.grey[100] }}>{tx.date}</TableCell>
                <TableCell sx={{ color: colors.grey[100] }}>{tx.spendingCategory}</TableCell>
                <TableCell sx={{ color: colors.grey[100] }}>{tx.description}</TableCell>
                <TableCell align="right" sx={{ color: colors.grey[100] }}>{tx.amount}</TableCell>
                <TableCell sx={{ color: colors.grey[100] }}>{tx.flow}</TableCell> {/* New data */}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default Transactions;