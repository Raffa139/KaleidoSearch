import { type FunctionComponent } from "react";
import { useNavigate, useOutletContext } from "react-router";
import { client } from "../../client/kaleidoClient";
import type { UserLoaderData } from "../../authentication/userLoader";
import "./home.css";

export const Home: FunctionComponent = () => {
  const navigate = useNavigate();

  const { user } = useOutletContext<UserLoaderData>();

  const handleClick = async () => {
    const { thread_id } = await client.createThread(user.id);
    navigate(`/users/${user.id}/threads/${thread_id}`);
  };

  return (
    <div className="container">
      <button onClick={handleClick} className="button">Start new Search</button>
    </div>
  );
};
