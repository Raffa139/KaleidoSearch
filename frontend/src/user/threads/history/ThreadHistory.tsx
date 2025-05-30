import { Fragment, useState, type FunctionComponent } from "react";
import { useLoaderData, useNavigate } from "react-router";
import type { Thread } from "../../../client/types";
import { useThreadContext } from "../useThreadContext";
import { SearchInput } from "../search/SearchInput";
import { ThreadHistoryEntry } from "./ThreadHistoryEntry";
import { ModalPuffLoader } from "../ModalPuffLoader";
import "./threadHistory.css";

export const ThreadHistory: FunctionComponent = () => {
  const loadedThreads = useLoaderData<Thread[]>();

  const navigate = useNavigate();

  const { isBusy, createThread } = useThreadContext();

  const [threads, setThreads] = useState<Thread[]>(loadedThreads);
  const [newSearch, setNewSearch] = useState<string>("");

  const handleNewSearch = async () => {
    if (newSearch.trim()) {
      const { thread_id } = await createThread(newSearch);
      navigate(`/user/threads/${thread_id}`);
    }
  };

  const handleDelete = (thread_id: number) => {
    setThreads(prevThreads => prevThreads.filter(thread => thread.thread_id !== thread_id));
  };

  return (
    <div className="thread-history">
      <h2 className="title-header">Recent Searches</h2>

      <div className={`${isBusy ? "loading" : ""}`}>
        <SearchInput value={newSearch} onChange={e => setNewSearch(e.target.value)} onSearch={handleNewSearch} placeholder="Start new Search..." />

        <div className="thread-list">
          {threads.map((thread) => (
            <Fragment key={thread.thread_id}>
              <ThreadHistoryEntry thread={thread} onDelete={handleDelete} />
            </Fragment>
          ))}

          <ModalPuffLoader loading={isBusy} />
        </div>
      </div>
    </div>
  );
};
