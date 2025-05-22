import type { FunctionComponent } from "react";
import { Link, useLoaderData, useOutletContext } from "react-router";
import type { User } from "../../client/types";

export const ThreadHistory: FunctionComponent = () => {
  const threads = useLoaderData<Array<{ thread_id: number }>>();
  const user = useOutletContext<User>();

  return (
    <div className="container" style={{ gap: "5px" }}>
      <h1>Thread History</h1>

      {threads.map(({ thread_id }: { thread_id: number }) => (
        <Link key={thread_id} to={`/users/${user.id}/threads/${thread_id}`}>
          <button className="button">
            Thread {thread_id}
          </button>
        </Link>
      ))}
    </div>
  );
};
