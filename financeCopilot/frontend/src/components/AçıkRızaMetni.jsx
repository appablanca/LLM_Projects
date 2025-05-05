import { Typography, Box } from '@mui/material';

const AçıkRızaMetni = () => {
    return (
        <Box sx={{ padding: 2, lineHeight: 1.6, fontFamily: 'Arial, sans-serif' }}>
            <Typography variant="h6" gutterBottom fontWeight="bold">
                Finance Copilot Explicit Consent Text
            </Typography>

            <Typography paragraph>
                Within the scope of the 6698 sayılı Kişisel Verilerin Korunması Kanunu, I hereby give my <strong>explicit consent</strong> for the processing and use of my personal data listed below by FEMPsoft through the Finance Copilot platform for the purposes stated:
            </Typography>

            <Typography component="ul" sx={{ pl: 3 }}>
                <li>My identity and contact information</li>
                <li>My marital status, housing details, and income information</li>
                <li>My risk preferences, spending, and usage data</li>
                <li>My platform usage statistics</li>
            </Typography>

            <Typography paragraph>
                This data will be processed for the purposes of:
            </Typography>

            <Typography component="ul" sx={{ pl: 3 }}>
                <li>Providing personalized financial analysis and recommendations</li>
                <li>Developing artificial intelligence systems</li>
                <li>Improving system security and user experience</li>
            </Typography>

            <Typography paragraph>
                and will only be shared with domestic service providers when necessary.
            </Typography>

            <Typography paragraph>
                I understand that I am giving this consent of my own free will and that I can withdraw it at any time.
            </Typography>
        </Box>
    );
};

export default AçıkRızaMetni;