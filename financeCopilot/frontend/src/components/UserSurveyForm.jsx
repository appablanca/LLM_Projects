import React from "react";
import {
  Box,
  TextField,
  MenuItem,
  Typography,
  Button,
  useTheme,
} from "@mui/material";
import { useFormik } from "formik";
import * as yup from "yup";
import { tokens } from "./../theme";

const validationSchema = yup.object({
  age: yup
    .number()
    .required("Gerekli")
    .min(18, "18 yaşından büyük olmalısınız"),
  income: yup.number().required("Gerekli"),
  housing: yup.string().required("Gerekli"),
  maritalStatus: yup.string().required("Gerekli"),
  riskTolerance: yup.string().required("Gerekli"),
  children: yup
    .number()
    .nullable()
    .min(0, "Cannot be negative")
    .when("maritalStatus", {
      is: "married",
      then: (schema) => schema.required("Required for married users"),
    }),
});

const UserSurveyForm = ({ onSubmit }) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

  const formik = useFormik({
    initialValues: {
      age: "",
      income: "",
      housing: "",
      maritalStatus: "",
      riskTolerance: "",
      children: "",
    },
    validationSchema,
    onSubmit: (values) => {
      onSubmit(values); // callback to parent
    },
  });

  return (
    <Box
      component="form"
      onSubmit={formik.handleSubmit}
      sx={{
        p: 4,
        borderRadius: 2,
        backgroundColor: colors.primary[800],
        color: colors.grey[100],
        maxWidth: 600,
        margin: "auto",
      }}
    >
      <Typography variant="h5" mb={2}>
        Personalization Survey
      </Typography>

      <TextField
        fullWidth
        margin="normal"
        id="age"
        name="age"
        label="Age"
        type="number"
        value={formik.values.age}
        onChange={formik.handleChange}
        error={formik.touched.age && Boolean(formik.errors.age)}
        helperText={formik.touched.age && formik.errors.age}
      />

      <TextField
        fullWidth
        margin="normal"
        id="income"
        name="income"
        label="Income (TL)"
        placeholder="e.g. 50000"
        type="number"
        value={formik.values.income}
        onChange={formik.handleChange}
        error={formik.touched.income && Boolean(formik.errors.income)}
        helperText={
          (formik.touched.income && formik.errors.income) ||
          "Please don’t use '.' or ',' — only whole numbers."
        }
      />

      <TextField
        fullWidth
        margin="normal"
        select
        id="housing"
        name="housing"
        label="Housing Type"
        value={formik.values.housing}
        onChange={formik.handleChange}
        error={formik.touched.housing && Boolean(formik.errors.housing)}
        helperText={formik.touched.housing && formik.errors.housing}
      >
        <MenuItem value="renter">Renter</MenuItem>
        <MenuItem value="owner">Owner</MenuItem>
      </TextField>

      <TextField
        fullWidth
        margin="normal"
        select
        id="maritalStatus"
        name="maritalStatus"
        label="Marital Status"
        value={formik.values.maritalStatus}
        onChange={formik.handleChange}
        error={
          formik.touched.maritalStatus && Boolean(formik.errors.maritalStatus)
        }
        helperText={formik.touched.maritalStatus && formik.errors.maritalStatus}
      >
        <MenuItem value="single">Single</MenuItem>
        <MenuItem value="married">Married</MenuItem>
      </TextField>

      {formik.values.maritalStatus === "married" && (
        <TextField
          fullWidth
          margin="normal"
          id="children"
          name="children"
          label="Number of Children"
          type="number"
          value={formik.values.children || ""}
          onChange={formik.handleChange}
          error={formik.touched.children && Boolean(formik.errors.children)}
          helperText={formik.touched.children && formik.errors.children}
        />
      )}

      <TextField
        fullWidth
        margin="normal"
        select
        id="riskTolerance"
        name="riskTolerance"
        label="Risk Tolerance"
        value={formik.values.riskTolerance}
        onChange={formik.handleChange}
        error={
          formik.touched.riskTolerance && Boolean(formik.errors.riskTolerance)
        }
        helperText={formik.touched.riskTolerance && formik.errors.riskTolerance}
      >
        <MenuItem value="low">Low</MenuItem>
        <MenuItem value="medium">Medium</MenuItem>
        <MenuItem value="high">High</MenuItem>
      </TextField>

      <Button
        type="submit"
        variant="contained"
        sx={{
          mt: 3,
          backgroundColor: colors.greenAccent[500],
          "&:hover": {
            backgroundColor: colors.greenAccent[600],
          },
        }}
      >
        Send
      </Button>
    </Box>
  );
};

export default UserSurveyForm;
