import React from "react";
import { Navigate } from "react-router-dom";
const LOGIN_TOKEN = import.meta.env.VITE_LOGIN_TOKEN;
const PrivateRoute = ({ children }) => {
  const isAuth = localStorage.getItem("auth") === LOGIN_TOKEN;
  return isAuth ? children : <Navigate to="/" replace />;
};

export default PrivateRoute;