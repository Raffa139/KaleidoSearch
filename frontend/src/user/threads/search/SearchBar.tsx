import { Fragment, useState, type FunctionComponent } from "react";
import { useLoaderData, useOutletContext } from "react-router";
import type { QueryEvaluation, User, UserAnswer } from "../../../client/types";
import { useThreadContext } from "../useThreadContext";
import { Question } from "./Question";
import "./searchBar.css";

interface SearchBarProps {
  queryEvaluation?: QueryEvaluation;
  onSearch: (queryEvaluation?: QueryEvaluation) => void;
}

export const SearchBar: FunctionComponent<SearchBarProps> = ({ queryEvaluation, onSearch }) => {
  const user = useOutletContext<User>();
  const { thread_id } = useLoaderData();

  const { isBusy, postToThread } = useThreadContext();

  const [search, setSearch] = useState<string>(queryEvaluation?.cleaned_query ?? "");
  const [lastSearch, setLastSearch] = useState<string>(queryEvaluation?.cleaned_query ?? "");
  const [answers, setAnswers] = useState<UserAnswer[]>([]);

  const handleSearch = async () => {
    try {
      const content = { query: lastSearch !== search ? search : undefined, answers };
      const result = await postToThread(user.id, thread_id, content);
      console.log("Search result:", result);
      console.log("Answers:", answers);
      // TODO: Clear answers after search
      onSearch(result);
      setLastSearch(search);
    } catch (error) {
      onSearch(queryEvaluation);
    }
  };

  const handleAnswerChange = (id: number, answer: string) => {
    setAnswers((prevAnswers) => {
      const existingAnswer = prevAnswers.find((a) => a.id === id);
      if (existingAnswer) {
        return prevAnswers.map((a) => a.id === id ? { ...a, answer } : a);
      } else {
        return [...prevAnswers, { id, answer }];
      }
    });
  };

  return (
    <div className={`search-header ${isBusy ? "loading" : ""}`}>
      <div className="search-bar">
        <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search..." className="search-input" />
        <button onClick={handleSearch} className="search-button"><i className="fas fa-search"></i></button>
      </div>

      {queryEvaluation && (
        <div className="follow-up-questions">
          {[...queryEvaluation.answered_questions, ...queryEvaluation.follow_up_questions].map((question) => (
            <Fragment key={question.id}>
              <Question onAnswerChange={handleAnswerChange} {...question} />
            </Fragment>
          ))}
        </div>
      )}
    </div>
  );
};
