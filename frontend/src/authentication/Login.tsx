import type { FunctionComponent } from "react";
import { Form } from "react-router";
import "./login.css";

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
      <Form action="/" method="post" className="login-form">
        <input type="text" name="username" placeholder="Username" required className="login-input" />
        <input type="password" name="password" placeholder="Password" required className="login-input" />
        <button type="submit" className="login-button">Log In</button>
      </Form>
    </div>
  );
};
