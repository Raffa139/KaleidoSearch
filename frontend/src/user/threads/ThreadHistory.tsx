import type { FunctionComponent } from "react";
import { Link, useLoaderData, useOutletContext } from "react-router";
import type { User } from "../../client/types";
import "./threadHistory.css";

export const ThreadHistory: FunctionComponent = () => {
  const threads = useLoaderData<Array<{ thread_id: number }>>();
  const user = useOutletContext<User>();

  return (
    <div className="container">
      <div className="thread-history">
        <h2 className="title-header">Recent Searches</h2>

        <div className="search-bar">
          <input type="text" placeholder="Start new Search..." className="search-input" />
          <button className="search-button"><i className="fas fa-search"></i></button>
        </div>

        <div className="thread-list">
          {threads.map(({ thread_id }: { thread_id: number }) => (
            <Link key={thread_id} to={`/users/${user.id}/threads/${thread_id}`}>
              <button className="button">
                Thread {thread_id}
              </button>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};
