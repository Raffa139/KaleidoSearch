import { type FunctionComponent } from "react";
import { ThreadHistory } from "../threads/ThreadHistory";
import "./home.css";

export const Home: FunctionComponent = () => {
  return (
    <div className="container">
      <ThreadHistory />
    </div>
  );
};
