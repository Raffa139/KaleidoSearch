import type { FunctionComponent } from "react";
import { NavLink } from "react-router";
import { LogoutButton } from "../layout/LogoutButton";
import "./error.css";

export const Error: FunctionComponent = () => {
  return (
    <div className="container">
      <div className="error-page-container">
        <div className="error-content">
          <i className="fas fa-exclamation-triangle error-icon"></i>

          <h1 className="error-title">Oops! Something went wrong.</h1>

          <p className="error-message">
            We're sorry, but an unexpected error occurred. Please try again later or use the links below.
          </p>

          <div className="error-actions">
            <NavLink to="home" className="action-button primary-action"><i className="fas fa-home"></i> Home</NavLink>
            <LogoutButton />
          </div>
        </div>
      </div>
    </div>
  );
};
