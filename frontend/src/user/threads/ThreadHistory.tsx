import { useState, type FunctionComponent } from "react";
import { Link, useLoaderData, useNavigate, useOutletContext } from "react-router";
import type { User } from "../../client/types";
import { useThreadContext } from "./useThreadContext";
import { SearchInput } from "./search/SearchInput";
import "./threadHistory.css";

export const ThreadHistory: FunctionComponent = () => {
  const threads = useLoaderData<Array<{ thread_id: number }>>();
  const user = useOutletContext<User>();

  const navigate = useNavigate();

  const { isBusy, createThread } = useThreadContext();

  const [newSearch, setNewSearch] = useState<string>("");

  const handleNewSearch = async () => {
    if (newSearch.trim()) {
      const { thread_id } = await createThread(user.id, newSearch);
      navigate(`/users/${user.id}/threads/${thread_id}`);
    }
  };

  return (
    <div className="thread-history">
      <h2 className="title-header">Recent Searches</h2>

      <div className={`${isBusy ? "loading" : ""}`}>
        <SearchInput value={newSearch} onChange={e => setNewSearch(e.target.value)} onSearch={handleNewSearch} placeholder="Start new Search..." />

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
