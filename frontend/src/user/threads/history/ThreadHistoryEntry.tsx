import { useEffect, useState, type FunctionComponent } from "react";
import { Link } from "react-router";
import TimeAgo from "react-timeago";
import Skeleton from "react-loading-skeleton";
import { client } from "../../../client/kaleidoClient";
import type { Thread } from "../../../client/types";
import "./threadHistoryEntry.css";

interface ThreadHistoryEntryProps {
  thread: Thread;
  user_id: number;
  onDelete: (thread_id: number) => void;
}

export const ThreadHistoryEntry: FunctionComponent<ThreadHistoryEntryProps> = ({ user_id, thread, onDelete }) => {
  const [title, setTitle] = useState<string | null>();

  const capitalizeSentence = (sentence: string) => {
    const capitalizeWord = (word: string) => word.charAt(0).toUpperCase() + word.slice(1);
    const capitalizedWords = sentence.split(" ").map(word => capitalizeWord(word));
    return capitalizedWords.join(" ");
  };

  useEffect(() => {
    const fetchThreadTitle = async () => {
      const queryEvaluation = await client.getUserThread(user_id, thread.thread_id);
      if (queryEvaluation.cleaned_query) {
        setTitle(capitalizeSentence(queryEvaluation.cleaned_query));
      } else {
        setTitle(null);
      }
    };

    fetchThreadTitle();
  }, [thread.thread_id]);

  const handleDelete = () => {
    client.deleteThread(user_id, thread.thread_id);
    onDelete(thread.thread_id);
  };

  return (
    <div className="thread-history-entry">
      <div className="thread-history-title">
        <TimeAgo date={thread.updated_at} />
        <span>{title === null ? <i>Untitled Search</i> : title ?? <Skeleton />}</span>
      </div>

      <div className="thread-history-entry-icon-btns">
        <Link to={`/users/${user_id}/threads/${thread.thread_id}`}>
          <button className="thread-history-entry-icon-btn success">
            <i className="fa-solid fa-paper-plane"></i>
          </button>
        </Link>

        <button
          onClick={handleDelete}
          className="thread-history-entry-icon-btn destructive"
          style={{ width: 48 }}
        >
          <i className="fa-solid fa-trash"></i>
        </button>
      </div>
    </div>
  );
};
