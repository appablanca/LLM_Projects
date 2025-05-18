import React, { useContext, useEffect, useState } from "react";
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
import { sendSurvey, getSurveyFields, editSurvey } from "../util/api";
import { toast } from "react-toastify";
import { AuthContext } from "../context/AuthContext";
import EditIcon from "@mui/icons-material/Edit";
import LoadingAnimation from "./LoadingAnimation";

const validationSchema = yup.object({
  age: yup
    .number()
    .required("Required")
    .min(18, "Yoou must be at least 18 years old"),
  income: yup.number().required("Required"),
  city: yup.string().required("Required"),
  housing: yup.string().required("Required"),
  maritalStatus: yup.string().required("Required"),
  riskTolerance: yup.string().required("Required"),
  savings: yup.number().required("Required").min(0, "Cannot be negative"),
  children: yup
    .number()
    .transform((value, originalValue) =>
      String(originalValue).trim() === "" ? null : value
    )
    .nullable()
    .min(0, "Cannot be negative")
    .when("maritalStatus", {
      is: "married",
      then: (schema) => schema.required("Required for married users"),
    }),
});

const UserSurveyForm = () => {
  const { user } = useContext(AuthContext);
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

  const [initialValuesLoaded, setInitialValuesLoaded] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [hasExistingData, setHasExistingData] = useState(false);

  const formik = useFormik({
    initialValues: {
      age: "",
      income: "",
      city: "",
      housing: "",
      rent: "",
      maritalStatus: "",
      riskTolerance: "",
      savings: "",
      children: "",
    },
    validationSchema,
    onSubmit: (values) => {
      const surveyData = [
        { name: "Age", content: String(values.age) },
        { name: "Income", content: String(values.income) },
        { name: "Savings", content: String(values.savings) }, // Yeni alan
        { name: "City", content: String(values.city) },
        { name: "Housing", content: values.housing },
        {
          name: "Rent",
          content:
            values.housing === "renter" ? String(values.rent || "0") : "N/A",
        },
        { name: "Marital Status", content: values.maritalStatus },
        {
          name: "Children",
          content:
            values.maritalStatus === "married"
              ? String(values.children || "0")
              : "N/A",
        },
        { name: "Risk Tolerance", content: values.riskTolerance },
      ];

      const submitFunction = hasExistingData ? editSurvey : sendSurvey;
      submitFunction(surveyData)
        .then((response) => {
          if (
            response?.message === "Survey data saved successfully" ||
            "Survey data updated successfully"
          ) {
            if (hasExistingData) {
              toast.success("Survey updated successfully!", {
                position: "top-right",
                autoClose: 2000,
                hideProgressBar: true,
                closeOnClick: true,
                pauseOnHover: false,
                draggable: false,
              });
            } else {
              toast.success("Survey submitted successfully!", {
                position: "top-right",
                autoClose: 2000,
                hideProgressBar: true,
                closeOnClick: true,
                pauseOnHover: false,
                draggable: false,
              });
              sessionStorage.setItem("surveyCompleted", "true");
            }
            setIsEditing(false);
          } else {
            toast.error("Survey submission failed. Please try again.", {
              position: "top-right",
              autoClose: 2000,
              hideProgressBar: true,
              closeOnClick: true,
              pauseOnHover: false,
              draggable: false,
            });
          }
        })
        .catch((error) => {
          console.error("🔥 ERROR in sendSurvey catch block");
          console.error("Error submitting survey:", error);
          console.error("Server response:", error.response?.data);
          toast.error("Survey submission failed. Please try again.", {
            position: "top-right",
            autoClose: 2000,
            hideProgressBar: true,
            closeOnClick: true,
            pauseOnHover: false,
            draggable: false,
          });
        });
    },
  });

  useEffect(() => {
    getSurveyFields()
      .then((response) => {
        if (Array.isArray(response)) {
          const formValues = {
            age: "",
            income: "",
            city: "",
            housing: "",
            rent: "",
            maritalStatus: "",
            children: "",
            riskTolerance: "",
            savings: "",
          };

          response.forEach((item) => {
            switch (item.name) {
              case "Age":
                formValues.age = item.content;
                break;
              case "Income":
                formValues.income = item.content;
                break;
              case "City":
                formValues.city = item.content;
                break;
              case "Housing":
                formValues.housing = item.content;
                break;
              case "Rent":
                formValues.rent = item.content === "N/A" ? "" : item.content;
                break;
              case "Marital Status":
                formValues.maritalStatus = item.content;
                break;
              case "Children":
                formValues.children =
                  item.content === "N/A" ? "" : item.content;
                break;
              case "Risk Tolerance":
                formValues.riskTolerance = item.content;
                break;
              case "Savings":
                formValues.savings = item.content;
                break;
              default:
                break;
            }
          });

          formik.setValues(formValues);
          setInitialValuesLoaded(true);

          const hasData = Object.values(formValues).some((val) => val !== "");
          setHasExistingData(hasData);
          if (hasData) {
            setIsEditing(false);
          } else {
            setIsEditing(true);
          }
        }
      })
      .catch((err) => {
        console.error("Error fetching survey fields:", err);
      });
  }, []);

  if (!initialValuesLoaded) return <LoadingAnimation />;

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
      <Box display="flex" justifyContent="flex-end">
        {hasExistingData && !isEditing && (
          <Button
            variant="outlined"
            sx={{
              mb: 2,
              color: colors.greenAccent[500],
              borderColor: colors.greenAccent[300],
            }}
            onClick={() => setIsEditing(true)}
          >
            Edit
            <EditIcon />
          </Button>
        )}
      </Box>

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
        disabled={!isEditing}
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
        disabled={!isEditing}
      />
      <TextField
        fullWidth
        margin="normal"
        id="savings"
        name="savings"
        label="Savings (TL)"
        type="number"
        value={formik.values.savings}
        onChange={formik.handleChange}
        error={formik.touched.savings && Boolean(formik.errors.savings)}
        helperText={
          (formik.touched.savings && formik.errors.savings) ||
          "Please don’t use '.' or ',' — only whole numbers."
        }
        disabled={!isEditing}
      />
      <TextField
        fullWidth
        margin="normal"
        id="city"
        name="city"
        label="City"
        placeholder="e.g. Istanbul"
        value={formik.values.city}
        onChange={formik.handleChange}
        error={formik.touched.city && Boolean(formik.errors.city)}
        helperText={formik.touched.city && formik.errors.city}
        disabled={!isEditing}
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
        disabled={!isEditing}
      >
        <MenuItem value="renter" disabled={!isEditing}>
          Renter
        </MenuItem>
        <MenuItem value="owner" disabled={!isEditing}>
          Owner
        </MenuItem>
      </TextField>
      {formik.values.housing === "renter" && (
        <TextField
          fullWidth
          margin="normal"
          id="rent"
          name="rent"
          label="Monthly Rent (TL)"
          type="number"
          value={formik.values.rent || ""}
          onChange={formik.handleChange}
          error={formik.touched.rent && Boolean(formik.errors.rent)}
          helperText={
            (formik.touched.rent && formik.errors.rent) ||
            "Please don’t use '.' or ',' — only whole numbers."
          }
          disabled={!isEditing}
        />
      )}

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
        disabled={!isEditing}
      >
        <MenuItem value="single" disabled={!isEditing}>
          Single
        </MenuItem>
        <MenuItem value="married" disabled={!isEditing}>
          Married
        </MenuItem>
      </TextField>

      {formik.values.maritalStatus === "married" && (
        <TextField
          fullWidth
          margin="normal"
          id="children"
          name="children"
          label="Number of Children"
          type="number"
          value={
            formik.values.children === "" || formik.values.children === null
              ? ""
              : formik.values.children
          }
          onChange={formik.handleChange}
          error={formik.touched.children && Boolean(formik.errors.children)}
          helperText={formik.touched.children && formik.errors.children}
          disabled={!isEditing}
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
        disabled={!isEditing}
      >
        <MenuItem value="low" disabled={!isEditing}>
          Low
        </MenuItem>
        <MenuItem value="medium" disabled={!isEditing}>
          Medium
        </MenuItem>
        <MenuItem value="high" disabled={!isEditing}>
          High
        </MenuItem>
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
        disabled={!isEditing}
      >
        Send
      </Button>
    </Box>
  );
};

export default UserSurveyForm;
