import React from "react";
import {
  Box,
  TextField,
  MenuItem,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Typography,
  Button,
  useTheme,
} from "@mui/material";
import { useFormik } from "formik";
import * as yup from "yup";
import { tokens } from "../theme";
import { sendSurvey, editSurvey, getSurveyFields } from "../util/api";
import { toast } from "react-toastify";
import LoadingAnimation from "./LoadingAnimation";
import EditIcon from "@mui/icons-material/Edit";

const validationSchema = yup.object({
  financialGoals: yup.array().min(1, "Select at least one goal").required(),
  investmentHorizon: yup.string().required("Required"),
  investmentExpectation: yup.string().required("Required"),
  incomeUse: yup.string().required("Required"),
  lossReaction: yup.string().required("Required"),
  retirementPlan: yup.string().required("Required"),
  confirmation: yup
    .boolean()
    .oneOf([true], "You must agree before submitting"),
});

const UserSurveyFormDetailed = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [initialValuesLoaded, setInitialValuesLoaded] = React.useState(false);
  const [hasExistingData, setHasExistingData] = React.useState(false);
  const [isEditing, setIsEditing] = React.useState(true); // default = editable for first-time

  const formik = useFormik({
    initialValues: {
      financialGoals: [],
      investmentHorizon: "",
      investmentExpectation: "",
      incomeUse: "",
      lossReaction: "",
      retirementPlan: "",
      confirmation: false,
    },
    validationSchema,
    onSubmit: (values) => {
      const data = [
        { name: "Financial Goals", content: values.financialGoals.join(", ") },
        { name: "Investment Horizon", content: values.investmentHorizon },
        { name: "Investment Expectation", content: values.investmentExpectation },
        { name: "Income Use", content: values.incomeUse },
        { name: "Loss Reaction", content: values.lossReaction },
        { name: "Retirement Plan", content: values.retirementPlan },
        { name: "Confirmation", content: "Yes" },
      ];

      const submitFunc = hasExistingData ? editSurvey : sendSurvey;
      submitFunc(data)
        .then((res) => {
          if (
            res?.message === "Survey data saved successfully" ||
            res?.message === "Survey data updated successfully"
          ) {
            toast.success("Survey submitted successfully!");
            sessionStorage.setItem("surveyCompleted", "true");
            setHasExistingData(true);
            setIsEditing(false); // lock form after submit
          } else {
            toast.error("Submission failed. Please try again.");
          }
        })
        .catch((err) => {
          console.error("Form submission error:", err);
          toast.error("Submission failed. Please try again.");
        });
    },
  });

  React.useEffect(() => {
    getSurveyFields()
      .then((response) => {
        const data = {
          financialGoals: [],
          investmentHorizon: "",
          investmentExpectation: "",
          incomeUse: "",
          lossReaction: "",
          retirementPlan: "",
          confirmation: false,
        };

        if (Array.isArray(response)) {
          response.forEach((item) => {
            switch (item.name) {
              case "Financial Goals":
                data.financialGoals = item.content.split(",").map((g) => g.trim());
                break;
              case "Investment Horizon":
                data.investmentHorizon = item.content;
                break;
              case "Investment Expectation":
                data.investmentExpectation = item.content;
                break;
              case "Income Use":
                data.incomeUse = item.content;
                break;
              case "Loss Reaction":
                data.lossReaction = item.content;
                break;
              case "Retirement Plan":
                data.retirementPlan = item.content;
                break;
              case "Confirmation":
                data.confirmation = true;
                break;
              default:
                break;
            }
          });

          formik.setValues(data);
          const hasData = Object.values(data).some((v) => v !== "" && v !== false && !(Array.isArray(v) && v.length === 0));
          setHasExistingData(hasData);
          setIsEditing(!hasData); // ✅ if there's no data, form stays editable
        }

        setInitialValuesLoaded(true);
      })
      .catch((err) => {
        console.error("Failed to fetch existing data:", err);
        setInitialValuesLoaded(true);
      });
  }, []);

  if (!initialValuesLoaded) return <LoadingAnimation />;

  const goalOptions = [
    "Save for retirement",
    "Invest in children's education",
    "Buy a house or a car",
    "Start my own business",
    "Generate short-term income",
    "Protect my assets from inflation",
    "Build generational wealth",
  ];

  const handleCheckboxChange = (goal) => {
    const current = formik.values.financialGoals;
    if (current.includes(goal)) {
      formik.setFieldValue(
        "financialGoals",
        current.filter((g) => g !== goal)
      );
    } else {
      formik.setFieldValue("financialGoals", [...current, goal]);
    }
  };

  return (
    <Box
      component="form"
      onSubmit={formik.handleSubmit}
      sx={{
        p: 4,
        borderRadius: 2,
        backgroundColor: colors.primary[800],
        color: colors.grey[100],
        maxWidth: 700,
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
            Edit <EditIcon sx={{ ml: 1 }} />
          </Button>
        )}
      </Box>

      <Typography variant="h5" mb={3}>
        Life Plan & Investment Behavior
      </Typography>

      <FormGroup sx={{ mb: 2 }}>
        <Typography variant="body1" sx={{ mb: 1 }}>
          What are your financial goals?
        </Typography>
        {goalOptions.map((goal) => (
          <FormControlLabel
            key={goal}
            control={
              <Checkbox
                checked={formik.values.financialGoals.includes(goal)}
                onChange={() => handleCheckboxChange(goal)}
                disabled={!isEditing}
              />
            }
            label={goal}
          />
        ))}
        {formik.touched.financialGoals && formik.errors.financialGoals && (
          <Typography color="error" variant="caption">
            {formik.errors.financialGoals}
          </Typography>
        )}
      </FormGroup>

      <TextField
        select
        fullWidth
        margin="normal"
        id="investmentHorizon"
        name="investmentHorizon"
        label="Timeframe to achieve your goal"
        value={formik.values.investmentHorizon}
        onChange={formik.handleChange}
        error={Boolean(formik.errors.investmentHorizon)}
        helperText={formik.errors.investmentHorizon}
        disabled={!isEditing}
      >
        <MenuItem value="short_1">Less than 1 year</MenuItem>
        <MenuItem value="mid_1_3">1–3 years</MenuItem>
        <MenuItem value="mid_3_5">3–5 years</MenuItem>
        <MenuItem value="long_5">More than 5 years</MenuItem>
      </TextField>

      <TextField
        select
        fullWidth
        margin="normal"
        id="investmentExpectation"
        name="investmentExpectation"
        label="Your investment expectation"
        value={formik.values.investmentExpectation}
        onChange={formik.handleChange}
        error={Boolean(formik.errors.investmentExpectation)}
        helperText={formik.errors.investmentExpectation}
        disabled={!isEditing}
      >
        <MenuItem value="protect">Protect my wealth</MenuItem>
        <MenuItem value="income">Generate regular income</MenuItem>
        <MenuItem value="grow">Grow wealth long-term</MenuItem>
      </TextField>

      <TextField
        select
        fullWidth
        margin="normal"
        id="incomeUse"
        name="incomeUse"
        label="How do you plan to use investment income?"
        value={formik.values.incomeUse}
        onChange={formik.handleChange}
        error={Boolean(formik.errors.incomeUse)}
        helperText={formik.errors.incomeUse}
        disabled={!isEditing}
      >
        <MenuItem value="reinvest">Reinvest it</MenuItem>
        <MenuItem value="daily">Cover daily expenses</MenuItem>
        <MenuItem value="emergency">Build an emergency fund</MenuItem>
        <MenuItem value="leisure">Use it for leisure/spending</MenuItem>
      </TextField>

      <TextField
        select
        fullWidth
        margin="normal"
        id="lossReaction"
        name="lossReaction"
        label="Your reaction in case of loss"
        value={formik.values.lossReaction}
        onChange={formik.handleChange}
        error={Boolean(formik.errors.lossReaction)}
        helperText={formik.errors.lossReaction}
        disabled={!isEditing}
      >
        <MenuItem value="panic">Panic and sell</MenuItem>
        <MenuItem value="wait">Wait it out</MenuItem>
        <MenuItem value="invest_more">Invest more</MenuItem>
      </TextField>

      <TextField
        select
        fullWidth
        margin="normal"
        id="retirementPlan"
        name="retirementPlan"
        label="Do you have a retirement plan?"
        value={formik.values.retirementPlan}
        onChange={formik.handleChange}
        error={Boolean(formik.errors.retirementPlan)}
        helperText={formik.errors.retirementPlan}
        disabled={!isEditing}
      >
        <MenuItem value="pension">I'm enrolled in a pension/private plan</MenuItem>
        <MenuItem value="investment_income">
          I plan to live on investment income
        </MenuItem>
        <MenuItem value="no_plan">I have no clear plan</MenuItem>
      </TextField>

      <FormControlLabel
        control={
          <Checkbox
            checked={formik.values.confirmation}
            onChange={(e) =>
              formik.setFieldValue("confirmation", e.target.checked)
            }
            disabled={!isEditing}
          />
        }
        label="I confirm that I understand the risks of investment products and that the information I provided is accurate."
      />
      {formik.touched.confirmation && formik.errors.confirmation && (
        <Typography color="error" variant="caption">
          {formik.errors.confirmation}
        </Typography>
      )}

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
        Submit
      </Button>
    </Box>
  );
};

export default UserSurveyFormDetailed;
