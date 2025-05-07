import { Typography, Box } from '@mui/material';

const KVKK = () => {
    return (
        <Box sx={{ padding: 2, lineHeight: 1.6, fontFamily: 'Arial, sans-serif' }}>
            <Typography variant="h6" gutterBottom fontWeight="bold">
                Finance Copilot Consent Form
            </Typography>

            <Typography paragraph>
                In accordance with the 6698 sayılı Kişisel Verilerin Korunması Kanunu, I hereby give my <strong>explicit consent</strong> for my personal data listed below to be processed and used by FEMPsoft through the Finance Copilot platform for the purposes stated:
            </Typography>

            <Typography component="ul" sx={{ pl: 3 }}>
                <li>My identity and contact information</li>
                <li>My marital status, housing information, and income status</li>
                <li>My risk preferences, spending, and usage data</li>
                <li>My platform usage statistics</li>
            </Typography>

            <Typography paragraph>
                This data will be processed for the purposes of:
            </Typography>

            <Typography component="ul" sx={{ pl: 3 }}>
                <li>Providing personalized financial analysis and recommendations</li>
                <li>Improving artificial intelligence systems</li>
                <li>Enhancing system security and user experience</li>
            </Typography>

            <Typography paragraph>
                and may be shared only with domestic service providers when necessary.
            </Typography>

            <Typography paragraph>
                I acknowledge that I am giving this consent of my own free will and that I may withdraw it at any time.
            </Typography>
        </Box>
    );
};

export default KVKK;