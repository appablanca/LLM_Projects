import React, { useState, useContext, useEffect } from "react";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css"; // Toastify CSS
import {
  Box,
  Grid,
  Typography,
  TextField,
  Button,
  IconButton,
  useTheme,
  InputAdornment,
  Checkbox,
  FormControlLabel,
  Modal,
} from "@mui/material";
import { Visibility, VisibilityOff } from "@mui/icons-material";
import ClearIcon from '@mui/icons-material/Clear';
import PersonIcon from "@mui/icons-material/Person";
import MailOutlineIcon from "@mui/icons-material/MailOutline";
import logo from "../assets/logo.png";
import { tokens } from "../theme";
import { useNavigate } from "react-router-dom"; // React Router kullanımı için
import { AuthContext } from "../context/AuthContext"; // AuthContext kullanımı için
import Loading from "./Loading";
import LoadingAnimation from "./LoadingAnimation";
import { useDeviceType } from "../hooks/useDeviceType";
import KVKK from "./KVKK";
import AçıkRızaMetni from "./AçıkRızaMetni";

export const LoginForm = () => {
  const [isSignIn, setIsSignIn] = useState(true);
  const [isForgotPassword, setIsForgotPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [surname, setSurname] = useState("");
  const [password, setPassword] = useState("");
  const [emailRepeat, setEmailRepeat] = useState("");
  const [passwordRepeat, setPasswordRepeat] = useState("");
  const [loading, setLoading] = useState(false); // Loading durumu
  const [showPassword, setShowPassword] = useState(false); // Şifre görünürlüğü durumu
  const [rememberMe, setRememberMe] = useState(false);
  const [kvkkApproved, setKvkkApproved] = useState(false);
  const [openKvkkModal, setOpenKvkkModal] = useState(false);
  const [openRizaModal, setOpenRizaModal] = useState(false);
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const navigate = useNavigate(); // Yönlendirme için kullanılır
  const emailInvalid = email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  const { isAuthenticated, login, register } = useContext(AuthContext);

  const emailMismatch = email && emailRepeat && email !== emailRepeat;
  const passwordMismatch =
    password && passwordRepeat && password !== passwordRepeat;
  const passwordInvalid =
    password && !/^(?=.*[A-Z])(?=.*[^a-zA-Z0-9]).{8,}$/.test(password);

  const deviceType = useDeviceType();

  const isMobile = deviceType === "mobile";
  const isTablet = deviceType === "tablet";

  useEffect(() => {
    if (isAuthenticated) {
      setLoading(true);
      // Keep the animation timeout
      const animationTimeout = setTimeout(() => {
        setLoading(false);
        navigate("/dashboard");
      }, 3000);

      // Cleanup timeout on unmount
      return () => clearTimeout(animationTimeout);
    }
  }, [isAuthenticated, navigate]);

  // Cleanup function for toast notifications
  useEffect(() => {
    return () => {
      toast.dismiss(); // Clear all toasts on component unmount
    };
  }, []);

  const validateEmail = (email) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const validatePassword = (password) => {
    return /^(?=.*[A-Z])(?=.*[^a-zA-Z0-9]).{8,}$/.test(password);
  };

  const validateForm = () => {
    if (!email) {
      toast.error("Email address is required!", {
        position: "top-right",
        autoClose: 2500,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
        toastId: "email-required",
      });
      return false;
    }

    if (!validateEmail(email)) {
      toast.error("Invalid email format!", {
        position: "top-right",
        autoClose: 2500,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
        toastId: "email-format",
      });
      return false;
    }

    if (!password) {
      toast.error("Password required!", {
        position: "top-right",
        autoClose: 2500,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
        toastId: "password-required",
      });
      return false;
    }

    if (!isSignIn && !validatePassword(password)) {
      toast.error(
        "Password must be at least 8 characters, contain one capital letter and one special character!",
        {
          position: "top-right",
          autoClose: 2500,
          hideProgressBar: false,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
          progress: undefined,
          toastId: "password-invalid",
        }
      );
      return false;
    }

    if (!isSignIn && password !== passwordRepeat) {
      toast.error("Passwords do not match!", {
        position: "top-right",
        autoClose: 2500,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
        toastId: "password-mismatch",
      });
      return false;
    }

    if (!isSignIn && !name) {
      toast.error("Name is required!", {
        position: "top-right",
        autoClose: 2500,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
        toastId: "name-required",
      });
      return false;
    }

    if (!isSignIn && !surname) {
      toast.error("Surname is required!", {
        position: "top-right",
        autoClose: 2500,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
        toastId: "surname-required",
      });
      return false;
    }
    if (!isSignIn && !kvkkApproved) {
      toast.error("You must approve the KVKK and Açık Rıza texts!", {
        position: "top-right",
        autoClose: 2500,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
        toastId: "kvkk-required",
      });
      return false;
    }

    return true;
  };

  const handleLogin = async () => {
    if (!validateForm()) return;

    try {
      setLoading(true);
      const response = await login(email, password, rememberMe);
      console.log("response", response);
      if (response) {
        toast.success("Login successful! You are being redirected...", {
          position: "top-right",
          autoClose: 2500,
          hideProgressBar: false,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
          progress: undefined,
          toastId: "login-success",
        });
      } else {
        toast.error("Login failed. Check your information.", {
          position: "top-right",
          autoClose: 2500,
          hideProgressBar: false,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
          progress: undefined,
          toastId: "login-error",
        });
        setLoading(false);
      }
    } catch (error) {
      toast.error("Login failed. Check your information.", {
        position: "top-right",
        autoClose: 2500,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
        toastId: "login-error",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async () => {
    if (!validateForm()) return;

    try {
      setLoading(true);
      const response = await register(email, name, surname, password);
      console.log("response", response);
      if (response === "User created") {
        toast.success("Registration successful! You can log in...", {
          position: "top-right",
          autoClose: 2500,
          hideProgressBar: false,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
          progress: undefined,
          toastId: "register-success",
        });
        setEmail("");
        setName("");
        setSurname("");
        setPassword("");
        setEmailRepeat("");
        setPasswordRepeat("");
        setIsSignIn(true);
      } else if (response === "Failed to register user: User already exists") {
        toast.error("This email address is already in use!", {
          position: "top-right",
          autoClose: 2500,
          hideProgressBar: false,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
          progress: undefined,
          toastId: "email-exists",
        });
      } else {
        toast.error("Registration failed. Check your information.", {
          position: "top-right",
          autoClose: 2500,
          hideProgressBar: false,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
          progress: undefined,
          toastId: "register-error",
        });
      }
    } catch (error) {
      toast.error("Registration failed. Check your information.", {
        position: "top-right",
        autoClose: 2500,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
        toastId: "register-error",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = () => {
    if (isSignIn) {
      handleLogin();
    } else {
      handleRegister();
    }
  };
  const handleKeyPress = (event) => {
    if (event.key === "Enter") {
      handleToggle();
    }
  };

  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        justifyContent: "top",
        height: "100vh",
        width: "100vw",
        background: `linear-gradient(to right, ${colors.primary[700]}, ${colors.primary[400]})`,
        flexDirection: "column",
        padding: isMobile ? 2 : isTablet ? 3 : 4, // Adjust padding based on device type
      }}
    >
      {loading ? (
        <LoadingAnimation />
      ) : (
        <>
          {/* Logo Section */}
          <Box
            sx={{
              width: "90%",
              maxWidth: isMobile ? "300px" : isTablet ? "500px" : "800px",
              textAlign: "center",
              marginBottom: 2,
            }}
          >
            <img
              src={logo}
              alt="Logo"
              style={{
                maxWidth: isMobile ? "70%" : isTablet ? "60%" : "400px",
                maxHeight: "150px",
              }}
            />
          </Box>

          {/* Giriş Paneli */}
          <Box
            sx={{
              width: "90%",
              maxWidth: isMobile ? "250px" : isTablet ? "650px" : "850px",
              display: "flex",
              flexDirection: isMobile ? "column" : "row",
              backgroundColor: "#fff",
              borderRadius: 2,
              boxShadow: 3,
              overflow: "hidden",
            }}
          >
            {/* Left: Form Section */}
            <Box
              sx={{
                flex: 1,
                padding: isMobile ? 2 : isTablet ? 3 : 4,
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
              }}
            >
              <Typography
                variant={isMobile ? "h5" : isTablet ? "h4" : "h3"}
                fontWeight="600"
                align="center"
                gutterBottom
                color="black"
                mb={2}
              >
                {isForgotPassword
                  ? "Reset Password"
                  : isSignIn
                  ? "Sign in"
                  : "Sign up"}
              </Typography>
              <TextField
                label="E-Mail"
                variant="outlined"
                fullWidth
                value={email}
                error={!!(emailInvalid || emailMismatch)}
                helperText={
                  emailInvalid
                    ? "Invalid email address!"
                    : emailMismatch
                    ? "Email addresses do not match!"
                    : ""
                }
                autoComplete="email"
                type="email"
                onChange={(e) => setEmail(e.target.value)}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton edge="end" sx={{ color: "black" }}>
                        <MailOutlineIcon />
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
                sx={{
                  marginBottom: 2,
                  "& .MuiInputBase-input": {
                    color:
                      theme.palette.mode === "dark"
                        ? colors.grey[500]
                        : colors.grey[500],
                  },
                  "& .MuiInputLabel-root": {
                    color:
                      theme.palette.mode === "dark"
                        ? colors.grey[500]
                        : colors.grey[700],
                  },
                  "& .MuiOutlinedInput-root": {
                    "& fieldset": {
                      borderColor:
                        theme.palette.mode === "dark"
                          ? colors.grey[700]
                          : colors.grey[300],
                    },
                    "&:hover fieldset": {
                      borderColor:
                        theme.palette.mode === "dark"
                          ? colors.grey[500]
                          : colors.grey[500],
                    },
                    "&.Mui-focused fieldset": {
                      borderColor: emailMismatch
                        ? colors.redAccent[500]
                        : colors.greenAccent[500],
                    },
                  },
                }}
              />
              {!isSignIn && !isForgotPassword && (
                <TextField
                  label="E-Mail Repeat"
                  variant="outlined"
                  fullWidth
                  error={!!emailMismatch}
                  helperText={
                    emailMismatch ? "Email addresses do not match!" : ""
                  }
                  value={emailRepeat}
                  autoComplete="email"
                  type="email"
                  onChange={(e) => setEmailRepeat(e.target.value)}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton edge="end" sx={{ color: "black" }}>
                          <MailOutlineIcon />
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                  sx={{
                    marginBottom: 2,
                    "& .MuiInputBase-input": {
                      color:
                        theme.palette.mode === "dark"
                          ? colors.grey[500]
                          : colors.grey[500],
                    },
                    "& .MuiInputLabel-root": {
                      color:
                        theme.palette.mode === "dark"
                          ? colors.grey[500]
                          : colors.grey[700],
                    },
                    "& .MuiOutlinedInput-root": {
                      "& fieldset": {
                        borderColor:
                          theme.palette.mode === "dark"
                            ? colors.grey[700]
                            : colors.grey[300],
                      },
                      "&:hover fieldset": {
                        borderColor:
                          theme.palette.mode === "dark"
                            ? colors.grey[500]
                            : colors.grey[500],
                      },
                      "&.Mui-focused fieldset": {
                        borderColor: emailMismatch
                          ? colors.redAccent[500]
                          : colors.greenAccent[500],
                      },
                    },
                  }}
                />
              )}
              {!isSignIn && !isForgotPassword && (
                <TextField
                  label="Name"
                  variant="outlined"
                  fullWidth
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  autoComplete="given-name"
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton edge="end" sx={{ color: "black" }}>
                          <PersonIcon />
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                  sx={{
                    marginBottom: 2,
                    "& .MuiInputBase-input": {
                      color:
                        theme.palette.mode === "dark"
                          ? colors.grey[500]
                          : colors.grey[500],
                    },
                    "& .MuiInputLabel-root": {
                      color:
                        theme.palette.mode === "dark"
                          ? colors.grey[500]
                          : colors.grey[700],
                    },
                    "& .MuiOutlinedInput-root": {
                      "& fieldset": {
                        borderColor:
                          theme.palette.mode === "dark"
                            ? colors.grey[700]
                            : colors.grey[300],
                      },
                      "&:hover fieldset": {
                        borderColor:
                          theme.palette.mode === "dark"
                            ? colors.grey[500]
                            : colors.grey[500],
                      },
                      "&.Mui-focused fieldset": {
                        borderColor: colors.greenAccent[500],
                      },
                    },
                  }}
                />
              )}
              {!isSignIn && !isForgotPassword && (
                <TextField
                  label="Surname"
                  variant="outlined"
                  fullWidth
                  value={surname}
                  onChange={(e) => setSurname(e.target.value)}
                  autoComplete="family-name"
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton edge="end" sx={{ color: "black" }}>
                          <PersonIcon />
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                  sx={{
                    marginBottom: 2,
                    "& .MuiInputBase-input": {
                      color:
                        theme.palette.mode === "dark"
                          ? colors.grey[500]
                          : colors.grey[500],
                    },
                    "& .MuiInputLabel-root": {
                      color:
                        theme.palette.mode === "dark"
                          ? colors.grey[500]
                          : colors.grey[700],
                    },
                    "& .MuiOutlinedInput-root": {
                      "& fieldset": {
                        borderColor:
                          theme.palette.mode === "dark"
                            ? colors.grey[700]
                            : colors.grey[300],
                      },
                      "&:hover fieldset": {
                        borderColor:
                          theme.palette.mode === "dark"
                            ? colors.grey[500]
                            : colors.grey[500],
                      },
                      "&.Mui-focused fieldset": {
                        borderColor: colors.greenAccent[500],
                      },
                    },
                  }}
                />
              )}
              {!isForgotPassword && (
                <TextField
                  label="Password"
                  variant="outlined"
                  error={
                    !isSignIn &&
                    !isForgotPassword &&
                    !!(passwordMismatch || passwordInvalid)
                  }
                  helperText={
                    !isSignIn && !isForgotPassword
                      ? passwordMismatch
                        ? "Passwords do not match!"
                        : passwordInvalid
                        ? "Password must be at least 8 characters, contain one uppercase letter and one special character!"
                        : ""
                      : ""
                  }
                  type={showPassword ? "text" : "password"}
                  fullWidth
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  sx={{
                    marginBottom: 2,
                    "& .MuiInputBase-input": {
                      color:
                        theme.palette.mode === "dark"
                          ? colors.grey[500]
                          : colors.grey[500],
                    },
                    "& .MuiInputLabel-root": {
                      color:
                        theme.palette.mode === "dark"
                          ? colors.grey[500]
                          : colors.grey[700],
                    },
                    "& .MuiOutlinedInput-root": {
                      "& fieldset": {
                        borderColor:
                          theme.palette.mode === "dark"
                            ? colors.grey[700]
                            : colors.grey[300],
                      },
                      "&:hover fieldset": {
                        borderColor:
                          theme.palette.mode === "dark"
                            ? colors.grey[500]
                            : colors.grey[500],
                      },
                      "&.Mui-focused fieldset": {
                        borderColor: passwordMismatch
                          ? colors.redAccent[500]
                          : colors.greenAccent[500],
                      },
                    },
                  }}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => setShowPassword(!showPassword)}
                          edge="end"
                          sx={{ color: "black" }}
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />
              )}
              {isSignIn && !isForgotPassword && (
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={rememberMe}
                      onChange={(e) => setRememberMe(e.target.checked)}
                      size="small"
                      sx={{
                        padding: 0,
                        marginRight: 1,
                        color: colors.grey[500],
                      }}
                    />
                  }
                  label="Remember Me"
                  sx={{
                    color: "black",
                    alignSelf: "flex-start",
                    mb: 1,
                    ml: 0.5,
                    "& .MuiFormControlLabel-label": {
                      fontSize: "0.85rem",
                    },
                  }}
                />
              )}

              {!isSignIn && !isForgotPassword && (
                <TextField
                  label="Password Repeat"
                  variant="outlined"
                  error={!!passwordMismatch}
                  helperText={passwordMismatch ? "Passwords do not match!" : ""}
                  type={showPassword ? "text" : "password"}
                  fullWidth
                  value={passwordRepeat}
                  onChange={(e) => setPasswordRepeat(e.target.value)}
                  sx={{
                    marginBottom: 2,
                    "& .MuiInputBase-input": {
                      color:
                        theme.palette.mode === "dark"
                          ? colors.grey[500]
                          : colors.grey[500],
                    },
                    "& .MuiInputLabel-root": {
                      color:
                        theme.palette.mode === "dark"
                          ? colors.grey[500]
                          : colors.grey[700],
                    },
                    "& .MuiOutlinedInput-root": {
                      "& fieldset": {
                        borderColor:
                          theme.palette.mode === "dark"
                            ? colors.grey[700]
                            : colors.grey[300],
                      },
                      "&:hover fieldset": {
                        borderColor:
                          theme.palette.mode === "dark"
                            ? colors.grey[500]
                            : colors.grey[500],
                      },
                      "&.Mui-focused fieldset": {
                        borderColor: passwordMismatch
                          ? colors.redAccent[500]
                          : colors.greenAccent[500],
                      },
                    },
                  }}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => setShowPassword(!showPassword)}
                          edge="end"
                          sx={{ color: "black" }}
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />
              )}
              {!isSignIn && !isForgotPassword && (
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={kvkkApproved}
                      onChange={(e) => setKvkkApproved(e.target.checked)}
                      sx={{ color: "black" }}
                    />
                  }
                  label={
                    <>
                      <Typography variant="body2" sx={{ color: "black" }}>
                        <strong>I consent to the processing of my personal data.</strong>{" "}
                        <span
                          style={{ textDecoration: "underline", cursor: "pointer" }}
                          onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            setOpenKvkkModal(true);
                          }}
                        >
                          KVKK Aydınlatma Metni
                        </span>{" "}
                        and{" "}
                        <span
                          style={{ textDecoration: "underline", cursor: "pointer" }}
                          onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            setOpenRizaModal(true);
                          }}
                        >
                          Açık Rıza Metni
                        </span>{" "}
                        have been read and accepted.
                      </Typography>
                    </>
                  }
                  sx={{ alignItems: "flex-start", marginBottom: 1 }}
                />
              )}
              {isForgotPassword && (
                <Box sx={{ width: "100%", textAlign: "right", mb: 2 }}>
                  <Typography
                    variant="body2"
                    color="primary"
                    align="right"
                    sx={{
                      cursor: "pointer",
                      marginBottom: 2,
                      display: "inline",
                      float: "right",
                    }}
                    onClick={() => {
                      setIsForgotPassword(false);
                      setEmail("");
                    }}
                  >
                    Sign In / Sign Up
                  </Typography>
                </Box>
              )}
              <Button
                onClick={handleToggle}
                variant="contained"
                color="primary"
                onKeyDown={handleKeyPress}
                fullWidth
                sx={{
                  padding: isMobile ? "8px 16px" : "10px 20px",
                  borderRadius: "50px",
                  fontWeight: "bold",
                  textTransform: "none",
                  marginTop: 2,
                }}
              >
                {isForgotPassword
                  ? "Send Reset Link"
                  : isSignIn
                  ? "Sign In"
                  : "Sign Up"}
              </Button>
            </Box>
            {/* Right: Overlay Section */}
            <Box
              sx={{
                flex: 1,
                background: `linear-gradient(to right, ${colors.primary[700]}, ${colors.primary[200]})`,
                color: "#fff",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                padding: isMobile ? 2 : isTablet ? 3 : 4,
                textAlign: "center",
              }}
            >
              <Typography
                variant={isMobile ? "h5" : isTablet ? "h4" : "h3"}
                fontWeight="600"
                gutterBottom
              >
                {isSignIn ? "Hello!" : "Welcome Back!"}
              </Typography>
              <Typography
                variant="body2"
                align="center"
                sx={{
                  maxWidth: isMobile ? "90%" : isTablet ? "80%" : "70%",
                  marginBottom: 4,
                }}
              >
                {isSignIn
                  ? "Enter your personal information and start your journey with us."
                  : "Log in to your account and continue your journey."}
              </Typography>
              <Button
                onClick={() => {
                  setIsSignIn(!isSignIn);
                  setName("");
                  setSurname("");
                  setPassword("");
                  setEmailRepeat("");
                  setPasswordRepeat("");
                  setIsForgotPassword(false);
                }}
                variant="outlined"
                sx={{
                  padding: isMobile ? "8px 16px" : "10px 20px",
                  borderRadius: "50px",
                  borderColor: "#fff",
                  color: "#fff",
                  textTransform: "none",
                  fontWeight: "bold",
                  "&:hover": {
                    background: "rgba(255, 255, 255, 0.2)",
                  },
                }}
              >
                {isSignIn ? "Sign Up" : "Sign In"}
              </Button>
            </Box>
          </Box>
          {/* Insert modals at the very end of the fragment */}
          <Modal open={openKvkkModal} onClose={() => setOpenKvkkModal(false)}>
            <Box
              sx={{
                position: "absolute",
                top: "50%",
                left: "50%",
                transform: "translate(-50%, -50%)",
                bgcolor: "background.paper",
                boxShadow: 24,
                p: 4,
                maxWidth: "600px",
                width: "90%",
                borderRadius: 2,
                maxHeight: "90vh",
                overflowY: "auto",
              }}
            >
              <KVKK />
            </Box>
          </Modal>

          <Modal open={openRizaModal} onClose={() => setOpenRizaModal(false)}>
            <Box
              sx={{
                position: "absolute",
                top: "50%",
                left: "50%",
                transform: "translate(-50%, -50%)",
                bgcolor: "background.paper",
                boxShadow: 24,
                p: 4,
                maxWidth: "600px",
                width: "90%",
                borderRadius: 2,
                maxHeight: "90vh",
                overflowY: "auto",
              }}
            >
              <AçıkRızaMetni />
            </Box>
          </Modal>
        </>
      )}
      {/* KVKK Modal */}
      <Modal open={openKvkkModal} onClose={() => setOpenKvkkModal(false)}>
        <Box
          sx={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            bgcolor: "background.paper",
            boxShadow: 24,
            p: 4,
            maxWidth: "600px",
            width: "90%",
            borderRadius: 2,
            maxHeight: "90vh",
            overflowY: "auto",
          }}
        >
          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
            <Typography variant="h6">KVKK Aydınlatma Metni</Typography>
            <IconButton onClick={() => setOpenKvkkModal(false)}>
              <ClearIcon />
            </IconButton>
          </Box>
          <KVKK />
        </Box>
      </Modal>
      {/* Açık Rıza Modal */}
      <Modal open={openRizaModal} onClose={() => setOpenRizaModal(false)}>
        <Box
          sx={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            bgcolor: "background.paper",
            boxShadow: 24,
            p: 4,
            maxWidth: "600px",
            width: "90%",
            borderRadius: 2,
            maxHeight: "90vh",
            overflowY: "auto",
          }}
        >
          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
            <Typography variant="h6">Açık Rıza Metni</Typography>
            <IconButton onClick={() => setOpenRizaModal(false)}>
              <ClearIcon />
            </IconButton>
          </Box>
          <AçıkRızaMetni />
        </Box>
      </Modal>
    </Box>
  );
};

export default LoginForm;
