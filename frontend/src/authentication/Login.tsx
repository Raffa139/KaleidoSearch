import { useEffect, type FunctionComponent } from "react";
import { useNavigate } from "react-router";
import { GoogleLogin, type CredentialResponse } from "@react-oauth/google";
import { client } from "../client/kaleidoClient";
import logo from "/logo.svg";
import "./login.css";

export const Login: FunctionComponent = () => {
  const navigate = useNavigate();

  const redirectToHome = () => navigate("/user/home");

  const handleCredentialResponse = async (response: CredentialResponse) => {
    if (response.credential) {
      const { access_token } = await client.Auth.googleLogin(response.credential);
      localStorage.setItem("access_token", access_token);
      redirectToHome();
    }
  };

  useEffect(() => {
    const verifyAccessToken = async () => {
      const tokenValid = await client.Auth.verifyToken();
      if (tokenValid) {
        redirectToHome();
      }
    }

    verifyAccessToken();
  }, []);

  return (
    <div className="login-container">
      <div className="branding-section">
        <img src={logo} alt="Logo" />
        <h1 className="branding-title">Kaleido</h1>
      </div>

      <GoogleLogin
        onSuccess={handleCredentialResponse}
        theme="filled_blue"
        shape="circle"
      />
    </div>
  );
};
