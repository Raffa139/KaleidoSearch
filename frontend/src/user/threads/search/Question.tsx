import { useState, type ChangeEvent, type FunctionComponent } from "react";
import type { FollowUpQuestion } from "../../../client/types";
import "./question.css";

interface QuestionProps extends FollowUpQuestion {
  answer?: string;
  onAnswerChange: (id: number, answer: string) => void;
}

export const Question: FunctionComponent<QuestionProps> = ({ id, short, long, answer, onAnswerChange }) => {
  const [newAnswer, setNewAnswer] = useState<string>(answer ?? "");

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setNewAnswer(value);
    onAnswerChange(id, value);
  };

  return (
    <div className={`question-container ${answer ? "answered" : ""}`}>
      <span className="question-short text-ellipsis">{short}</span>
      <i title={`${short}: ${long}`} className="fas fa-question-circle icon-btn"></i>
      <input type="text" value={newAnswer} onChange={handleChange} className="search-input" />
    </div>
  );
};
