import { Box, Card, Typography, useTheme, Button } from "@mui/material";
import { tokens } from "../../theme";
import UserSurveyForm from "../../components/UserSurveyForm";
import UserSurveyFormDetailed from "../../components/UserSurveyFormDetailed";
import { useState } from "react";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";

const Profile = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [showSurvey, setShowSurvey] = useState(false);
  const [showDetailedSurvey, setShowDetailedSurvey] = useState(false);

  return (
    <Box m="20px">
      <Card sx={{ bgcolor: colors.primary[700], p: 2 }}>
        <Typography variant="h6" gutterBottom>
          My Profile
        </Typography>
        {/* Interaction counts content */}
      </Card>

      <Card sx={{ mt: 3, bgcolor: colors.primary[700], p: 2 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6" gutterBottom>
            Personalization Survey
          </Typography>
          <Button
            variant="outlined"
            onClick={() => setShowSurvey(!showSurvey)}
            startIcon={showSurvey ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            sx={{
              color: colors.grey[100],
              borderColor: colors.grey[100],
              "&:hover": {
                backgroundColor: colors.primary[300],
                borderColor: colors.primary[300],
              },
            }}
          >
            {showSurvey ? "Close" : "Open Survey"}
          </Button>
        </Box>
        {showSurvey && <UserSurveyForm />}
      </Card>

      {/* Detailed Version */}
      <Card sx={{ mt: 3, bgcolor: colors.primary[700], p: 2 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6" gutterBottom>
            Personalization Survey
          </Typography>
          <Button
            variant="outlined"
            onClick={() => setShowDetailedSurvey(!showDetailedSurvey)}
            startIcon={showDetailedSurvey ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            sx={{
              color: colors.grey[100],
              borderColor: colors.grey[100],
              "&:hover": {
                backgroundColor: colors.primary[300],
                borderColor: colors.primary[300],
              },
            }}
          >
            {showDetailedSurvey ? "Close" : "Open Survey"}
          </Button>
        </Box>
        {showDetailedSurvey && <UserSurveyFormDetailed />}
      </Card>
    </Box>
  );
};

export default Profile;
