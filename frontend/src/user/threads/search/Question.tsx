import { useState, type ChangeEvent, type FunctionComponent } from "react";
import type { FollowUpQuestion } from "../../../client/types";
import "./question.css";

interface QuestionProps extends FollowUpQuestion {
  answer?: string;
  onAnswerChange: (id: number, answer: string, remove: boolean, hasChanged: boolean) => void;
}

export const Question: FunctionComponent<QuestionProps> = ({ id, short, long, answer, onAnswerChange }) => {
  const [newAnswer, setNewAnswer] = useState<string>(answer ?? "");

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    const trimmedValue = value.trim();
    const remove = !!answer && trimmedValue === "";
    const hasChanged = answer !== trimmedValue;
    setNewAnswer(value);
    onAnswerChange(id, trimmedValue, remove, hasChanged);
  };

  return (
    <div className={`question-container ${answer ? "answered" : ""}`}>
      <span className="question-short text-ellipsis">{short}</span>
      <i title={`${short}: ${long}`} className="fas fa-question-circle icon-btn"></i>
      <input type="text" value={newAnswer} onChange={handleChange} className="search-input" />
    </div>
  );
};
