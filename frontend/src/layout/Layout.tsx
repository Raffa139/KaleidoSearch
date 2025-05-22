import type { FunctionComponent } from "react";
import { NavLink, Outlet, useLoaderData } from "react-router";
import "./layout.css";

export const Layout: FunctionComponent = () => {
  const { user } = useLoaderData();

  return (
    <>
      <nav className="sidebar-nav">
        <div className="profile-section">
          <img src={user.picture_url ?? "/placeholder-profile.jpg"} alt="User Profile" className="profile-picture" />
          <span className="username">{user.username}</span>
        </div>

        <ul className="nav-links">
          <li><NavLink to="home"><i className="fas fa-home"></i> Home</NavLink></li>
          <li><NavLink to="threads"><i className="fas fa-search"></i> Search</NavLink></li>
          <li><a href="#"><i className="fas fa-bookmark"></i> Saved Items</a></li>
          <li><a href="#"><i className="fas fa-cog"></i> Settings</a></li>
          <li><a href="#"><i className="fas fa-question-circle"></i> Help</a></li>
        </ul>

        <div className="logout-section">
          <button className="logout-button">
            <i className="fas fa-sign-out-alt"></i> Logout
          </button>
        </div>
      </nav>

      <main>
        <Outlet context={{ user }} />
      </main>
    </>
  );
};