import { CssBaseline, ThemeProvider } from "@mui/material";
import { ColorModeContext, useMode } from "./theme";
import { useLocation, Navigate, Routes, Route } from "react-router-dom";
import { useContext } from "react";
import { ToastContainer } from "react-toastify";

import "react-toastify/dist/ReactToastify.css";

import ConnectionStatus from "./components/ConnectionStatus";
import LoadingAnimation from "./components/LoadingAnimation";
import { LoginForm } from "./components/LoginForm";
import AuthProvider, { AuthContext } from "./context/AuthContext";

// import Dashboard from "./scenes/dashboard";
// import Profile from "./scenes/profile/Profile";
// import Copilot from "./scenes/copilot";

function AppContent() {
  const [theme, colorMode] = useMode();
  const location = useLocation();
  const { isAuthenticated, loading } = useContext(AuthContext);

  if (loading) {
    return <LoadingAnimation />;
  }

  // Eğer kullanıcı giriş yapmamışsa ve login sayfasında değilse, login sayfasına yönlendir
  if (!isAuthenticated && location.pathname !== "/giris") {
    return <Navigate to="/giris" replace />;
  }

  // Eğer kullanıcı giriş yapmışsa ve login sayfasındaysa, ana sayfaya yönlendir
  if (isAuthenticated && location.pathname === "/giris") {
    return <Navigate to="/ana-ekran" replace />;
  }

  const LoginRoutes = () => {
    return (
      <Routes>
        <Route path="/" element={<Navigate to="/giris" />} />
        <Route path="/giris" element={<LoginForm />} />
      </Routes>
    );
  };

  // const AppRoutes = () => {
  //   return (
  //     <Routes>
  //       <Route path="/" element={<Navigate to="/ana-ekran" />} />
  //       <Route path="/ana-ekran" element={<Dashboard />} />
  //       <Route path="/profil" element={<Profile />} />

  //       <Route path="/copilot" element={<Copilot />} />

  //       <Route path="*" element={<Navigate to="/ana-ekran" replace />} />
  //     </Routes>
  //   );
  // };

  return (
    <ColorModeContext.Provider value={colorMode}>
      <ToastContainer />
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <div className="app">
          <ConnectionStatus />
          {/* {!isAuthenticated ? <LoginRoutes /> : <AppRoutes />} */}
          <LoginRoutes />
        </div>
      </ThemeProvider>
    </ColorModeContext.Provider>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
