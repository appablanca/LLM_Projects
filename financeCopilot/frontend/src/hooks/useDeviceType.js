import { useTheme, useMediaQuery } from "@mui/material";

export const useDeviceType = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const isTablet = useMediaQuery(theme.breakpoints.between("sm", "md"));
  const isDesktop = useMediaQuery(theme.breakpoints.up("md"));

  if (isMobile) return "mobile";
  if (isTablet) return "tablet";
  if (isDesktop) return "desktop";
  return "desktop";
};