import type { FunctionComponent } from "react";
import { NavLink, Outlet, useLoaderData, useNavigation } from "react-router";
import type { User } from "../client/types";
import { GlobalSpinner } from "./GlobalSpinner";
import { ThreadContextWrapper } from "../user/threads/ThreadContext";
import { LogoutButton } from "./LogoutButton";
import logo from "/logo.svg";
import "./layout.css";

export const Layout: FunctionComponent = () => {
  const navigation = useNavigation();
  const isNavigating = Boolean(navigation.location);
  const user = useLoaderData<User>();

  return (
    <>
      <nav className="sidebar-nav">
        <div className="branding-section">
          <img src={logo} alt="Logo" />
          <h1 className="branding-title">Kaleido</h1>
        </div>

        <div className="profile-section">
          <img src={user.picture_url ?? "/placeholder-profile.jpg"} alt="User Profile" className="profile-picture" />
          <span className="username">{user.username ?? "Anonymous"}</span>
        </div>

        <ul className="nav-links">
          <li><NavLink to="home"><i className="fas fa-home"></i> Home</NavLink></li>
          <li><NavLink to="bookmarks"><i className="fas fa-bookmark"></i> Bookmarks</NavLink></li>
          <li><a href="#"><i className="fas fa-cog"></i> Settings</a></li>
          <li><a href="#"><i className="fas fa-question-circle"></i> Help</a></li>
        </ul>

        <div className="logout-section">
          <LogoutButton />
        </div>
      </nav>

      <main>
        {isNavigating ? (
          <GlobalSpinner />
        ) : (
          <ThreadContextWrapper>
            <Outlet context={user} />
          </ThreadContextWrapper>
        )}
      </main>
    </>
  );
};
