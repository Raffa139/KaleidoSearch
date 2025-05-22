import { type FunctionComponent } from "react";
import type { FollowUpQuestion } from "../../client/types";
import "./question.css";

interface QuestionProps extends FollowUpQuestion {
  onAnswerChange: (id: number, answer: string) => void;
}

export const Question: FunctionComponent<QuestionProps> = ({ id, short, long, onAnswerChange }) => {
  return (
    <div className="question-container">
      <span className="question-short text-ellipsis">{short}</span>
      <i title={`${short}: ${long}`} className="fas fa-question-circle icon-btn"></i>
      <input type="text" onChange={e => onAnswerChange(id, e.target.value)} className="search-input" />
    </div>
  );
};
