import React from "react";
import { Navigate } from "react-router-dom";
const LOGIN_TOKEN = import.meta.env.VITE_LOGIN_TOKEN;
const PublicRoute = ({ children }) => {
  const isAuth = localStorage.getItem("auth") === LOGIN_TOKEN;
  return isAuth ? <Navigate to="/home" replace /> : children; 
};

export default PublicRoute;
