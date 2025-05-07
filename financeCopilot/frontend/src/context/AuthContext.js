import React, { createContext, useState, useEffect } from "react";
import { flogut, flogin, fregister, isAuth } from "../util/api";

// AuthContext oluştur
export const AuthContext = createContext({
  user: null,
  isAuthenticated: false,
  loading: true,
  isLoggingOut: false,
  logout: () => {},
  login: (email, password, rememberMe) => {},
  register: (email, name, surname, password) => {},
  completeLogout: () => {},
});

// AuthProvider bileşeni
const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticatedUser, setIsAuthenticatedUser] = useState(false);
  const [loading, setLoading] = useState(true);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  // Kullanıcıyı giriş yaptır
  const login = async (email, password, rememberMe) => {
    try {
      const data = await flogin(email, password, rememberMe);
      if (data.session && data.session.user) {
        setUser(data.session.user);
        setIsAuthenticatedUser(true);
        return true;
      }
      return false;
    } catch (error) {
      console.error("Login error:", error.message);
      setUser(null);
      setIsAuthenticatedUser(false);
      return false;
    }
  };

  const register = async (email, name, surname, password) => {
    try {
      const data = await fregister(email, name, surname, password);
      return data;
    } catch (error) {
      console.error("Register error:", error.message);
      return error.message;
    }
  };

  // Kullanıcıyı çıkış yaptır
  const logout = async () => {
    try {
      setIsLoggingOut(true);
      const res = await flogut();
      if (res === "User logged out") {
        completeLogout();
        return true;
      }
      return false;
    } catch (err) {
      console.error("Logout error:", err);
      setIsLoggingOut(false);
      return false;
    }
  };

  const completeLogout = () => {
    setUser(null);
    setIsAuthenticatedUser(false);
    setIsLoggingOut(false);
  };

  useEffect(() => {
    const fetchSession = async () => {
      try {
        console.log("Session kontrolü yapılıyor...");
        const res = await isAuth();
        console.log("isAuth response:", res);
        if (res && res.user) {
          setUser(res.user);
          setIsAuthenticatedUser(true);

        } else {
          setUser(null);
          setIsAuthenticatedUser(false);
        }
      } catch (err) {
        console.error("Session kontrolü başarısız:", err.message || err);
        setUser(null);
        setIsAuthenticatedUser(false);
      } finally {
        setLoading(false);
      }
    };

    fetchSession();
  }, []); 


  useEffect(() => {
    console.log("isAuthenticatedUser changed:", isAuthenticatedUser);
  }, [isAuthenticatedUser]);

  const value = {
    user: user,
    setUser: setUser,
    isAuthenticated: isAuthenticatedUser,
    loading,
    isLoggingOut,
    logout: logout,
    login: login,
    register: register,
    completeLogout: completeLogout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthProvider;