import { Fragment, useState, type FunctionComponent } from "react";
import { useLoaderData, useOutletContext } from "react-router";
import type { QueryEvaluation, User, UserAnswer } from "../../../client/types";
import { useThreadContext } from "../useThreadContext";
import { Question } from "./Question";
import { SearchInput } from "./SearchInput";
import "./searchBar.css";

interface SearchBarProps {
  queryEvaluation?: QueryEvaluation;
  onSearch: (queryEvaluation?: QueryEvaluation) => void;
}

export const SearchBar: FunctionComponent<SearchBarProps> = ({ queryEvaluation, onSearch }) => {
  const user = useOutletContext<User>();
  const { thread_id } = useLoaderData();

  const { isBusy, rerank, setRerank, postToThread } = useThreadContext();

  const [search, setSearch] = useState<string>(queryEvaluation?.cleaned_query ?? "");
  const [lastSearch, setLastSearch] = useState<string>(queryEvaluation?.cleaned_query ?? "");
  const [answers, setAnswers] = useState<UserAnswer[]>([]);
  const [hideAnswers, setHideAnswers] = useState<boolean>(false);

  const handleSearch = async () => {
    try {
      const content = { query: lastSearch !== search ? search : undefined, answers };
      const result = await postToThread(user.id, thread_id, content);
      console.log("Search result:", result);
      console.log("Answers:", answers);
      onSearch(result);
      setAnswers([]);
      setLastSearch(search);
    } catch (error) {
      onSearch(queryEvaluation);
    }
  };

  const handleAnswerChange = (id: number, answer: string, remove: boolean, hasChanged: boolean) => {
    if (hasChanged) {
      setAnswers((prevAnswers) => {
        const existingAnswer = prevAnswers.find((a) => a.id === id);
        const newAnswer = { id, answer, remove };

        if (existingAnswer) {
          return prevAnswers.map((a) => a.id === id ? newAnswer : a);
        } else {
          return [...prevAnswers, newAnswer];
        }
      });
    } else {
      setAnswers((prevAnswers) => prevAnswers.filter((a) => a.id !== id));
    }
  };

  return (
    <div className={`search-header ${isBusy ? "loading" : ""}`}>
      <SearchInput value={search} onChange={e => setSearch(e.target.value)} onSearch={handleSearch} placeholder="Search..." />

      <div className="search-options">
        <div className="search-option">
          <div onClick={() => setRerank(!rerank)}>
            <input type="checkbox" checked={rerank} />
            <span>Rerank results</span>
          </div>
          <i title="Enabling this option might improve search results at the cost of speed, depending on the specific search term(s)." className="fas fa-question-circle icon-btn" />
        </div>

        <div onClick={() => setHideAnswers(!hideAnswers)} className="search-option">
          <input type="checkbox" checked={hideAnswers} />
          <span>Hide answers</span>
        </div>
      </div>

      {queryEvaluation && (
        <div className="follow-up-questions">
          {[...queryEvaluation.answered_questions, ...queryEvaluation.follow_up_questions].map((question) => (
            <Fragment key={question.id}>
              <Question onAnswerChange={handleAnswerChange} hideAnswered={hideAnswers} {...question} />
            </Fragment>
          ))}
        </div>
      )}
    </div>
  );
};
