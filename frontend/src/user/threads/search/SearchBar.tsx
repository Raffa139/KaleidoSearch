import { Fragment, useState, type FunctionComponent } from "react";
import { useLoaderData, useOutletContext } from "react-router";
import type { Answer, QueryEvaluation } from "../../../client/types";
import { client } from "../../../client/kaleidoClient";
import type { UserLoaderData } from "../../../authentication/userLoader";
import { Question } from "./Question";
import "./searchBar.css";

export const SearchBar: FunctionComponent = () => {
  const [search, setSearch] = useState<string>("");
  const [lastSearch, setLastSearch] = useState<string>("");
  const [searchResult, setSearchResult] = useState<QueryEvaluation>();
  const [answers, setAnswers] = useState<Answer[]>([]);

  const { user } = useOutletContext<UserLoaderData>();
  const { thread_id } = useLoaderData();

  const handleSearch = async () => {
    const content = { query: lastSearch !== search ? search : undefined, answers };
    const result = await client.postToThread(user.id, thread_id, content);
    console.log("Search result:", result);
    console.log("Answers:", answers);
    setSearchResult(result);
    setLastSearch(search);
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
    <div className="search-header">
      <div className="search-bar">
        <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search..." className="search-input" />
        <button onClick={handleSearch} className="search-button"><i className="fas fa-search"></i></button>
      </div>

      {searchResult && (
        <div className="follow-up-questions">
          {searchResult.follow_up_questions.map((question) => (
            <Fragment key={question.id}>
              <Question onAnswerChange={handleAnswerChange} {...question} />
            </Fragment>
          ))}
        </div>
      )}
    </div>
  );
};