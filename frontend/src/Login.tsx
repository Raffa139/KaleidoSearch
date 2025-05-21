import type { FunctionComponent } from "react";
import { Link } from "react-router";
import "./Login.css";

export const Login: FunctionComponent = () => {
  return (
    <div className="login-container">
      <h1>Log In</h1>
      <button className="google-login-button">
        <i className="fab fa-google"></i> Sign in with Google
      </button>
      <div className="separator">
        <span>Or</span>
      </div>
      <form className="login-form">
        <input type="email" placeholder="Email" className="login-input" />
        <input type="password" placeholder="Password" className="login-input" />
        <Link to="/users/uid/threads">
          <button className="login-button">Log In</button>
        </Link>
      </form>
    </div>
  );
};
