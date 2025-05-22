import { Fragment, useState, type FunctionComponent } from "react";
import { useOutletContext } from "react-router";
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

  const handleSearch = async () => {
    console.log("Searching for:", search);
    //const result = await client.startNewTread(user.id, search);
    let result: QueryEvaluation = {
      valid: false,
      answered_questions: [],
      follow_up_questions: [
        {
          id: 0,
          short: "Product Type",
          long: "What kind of product are you interested in today?"
        },
        {
          id: 1,
          short: "Product Use",
          long: "What are you planning to use the product for?"
        },
        {
          id: 2,
          short: "Budget",
          long: "What is your budget for this product?"
        }
      ],
      thread_id: 4
    }
    setSearchResult(result);
    const content = { query: lastSearch !== search ? search : undefined, answers };
    result = await client.postToThread(user.id, 4, content);
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