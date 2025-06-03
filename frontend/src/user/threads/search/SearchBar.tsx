import { useState, type FunctionComponent } from "react";
import { useLoaderData, useNavigate } from "react-router";
import { useTransition, animated } from "@react-spring/web";
import type { QueryEvaluation, UserAnswer } from "../../../client/types";
import { useThreadContext } from "../useThreadContext";
import { Question } from "./Question";
import { SearchInput } from "./SearchInput";
import { ToggleSwitch } from "./ToggleSwitch";
import { ModalPuffLoader } from "../ModalPuffLoader";
import "./searchBar.css";

interface SearchBarProps {
  queryEvaluation?: QueryEvaluation;
  onSearch: (queryEvaluation?: QueryEvaluation) => void;
}

export const SearchBar: FunctionComponent<SearchBarProps> = ({ queryEvaluation, onSearch }) => {
  const { thread_id } = useLoaderData<QueryEvaluation>();

  const navigate = useNavigate();

  const { isBusy, rerank, setRerank, postToThread } = useThreadContext();

  const [search, setSearch] = useState<string>(queryEvaluation?.cleaned_query ?? "");
  const [lastSearch, setLastSearch] = useState<string>(queryEvaluation?.cleaned_query ?? "");
  const [answers, setAnswers] = useState<UserAnswer[]>([]);
  const [hideAnswers, setHideAnswers] = useState<boolean>(false);

  const questionTransitions = useTransition(
    [
      ...queryEvaluation?.answered_questions ?? [],
      ...queryEvaluation?.follow_up_questions ?? []
    ],
    {
      keys: question => question.id,
      from: { opacity: 0, transform: "translateY(20px) scale(0.9)" },
      enter: { opacity: 1, transform: "translateY(0px) scale(1)" },
      leave: { opacity: 0, transform: "translateY(-20px) scale(0.9)" },
      config: { tension: 200, friction: 20 }
    }
  );

  const handleSearch = async () => {
    try {
      const newSearch = lastSearch !== search ? search : undefined;

      if (newSearch || answers.length > 0) {
        const content = { query: newSearch, answers };
        const result = await postToThread(thread_id, content);
        onSearch(result);
        setAnswers([]);
        setLastSearch(search);
      } else {
        onSearch(queryEvaluation);
      }
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

  const handleBackClick = () => {
    navigate(-1);
  };

  return (
    <div className={`search-header ${isBusy ? "loading" : ""}`}>
      <div className="search-input-container">
        <button onClick={handleBackClick} className="back-button"><i className="fa-solid fa-arrow-left"></i></button>
        <SearchInput value={search} onChange={e => setSearch(e.target.value)} onSearch={handleSearch} placeholder="Search..." />
      </div>

      <div className="search-options">
        <div className="search-option">
          <div onClick={() => setRerank(!rerank)} style={{ display: "flex", gap: 5 }}>
            <ToggleSwitch checked={rerank} />
            <span>Rerank results</span>
          </div>

          <i title="Enabling this option might improve search results at the cost of speed, depending on the specific search term(s)." className="fas fa-question-circle icon-btn" />
        </div>

        <div onClick={() => setHideAnswers(!hideAnswers)} className="search-option" style={{ gap: 5 }}>
          <ToggleSwitch checked={hideAnswers} />
          <span>Hide answers</span>
        </div>
      </div>

      {queryEvaluation && (
        <div className="follow-up-questions">
          {questionTransitions((style, question) => (
            <animated.div key={question.id} style={style}>
              <Question onAnswerChange={handleAnswerChange} hideAnswered={hideAnswers} {...question} />
            </animated.div>
          ))}
        </div>
      )}

      <ModalPuffLoader loading={isBusy} />
    </div>
  );
};
