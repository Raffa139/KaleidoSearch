import type { FunctionComponent } from "react";
import { Link, useLoaderData, useOutletContext } from "react-router";
import type { UserLoaderData } from "../authentication/userLoader";

export const ThreadHistory: FunctionComponent = () => {
  const threads = useLoaderData();
  const { user } = useOutletContext<UserLoaderData>();

  return (
    <div className="container" style={{ gap: "5px" }}>
      <h1>Thread History</h1>

      {threads.map(({ thread_id }: { thread_id: number }) => (
        <button className="button">
          <Link key={thread_id} to={`/users/${user.id}/threads/${thread_id}`}>
            Thread {thread_id}
          </Link>
        </button>
      ))}
    </div>
  );
};
