import type { FunctionComponent } from "react";
import { useNavigate } from "react-router";
import { googleLogout } from "@react-oauth/google";
import "./logoutButton.css";

export const LogoutButton: FunctionComponent = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    googleLogout();
    navigate("/");
  }

  return (
    <button onClick={handleLogout} className="logout-button">
      <i className="fas fa-sign-out-alt"></i> Logout
    </button>
  );
};
