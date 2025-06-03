import { useState, type ChangeEvent, type FunctionComponent } from "react";
import type { FollowUpQuestion } from "../../../client/types";
import "./question.css";

interface QuestionProps extends FollowUpQuestion {
  answer?: string;
  onAnswerChange: (id: number, answer: string, remove: boolean, hasChanged: boolean) => void;
}

export const Question: FunctionComponent<QuestionProps> = ({ id, short, long, answer, onAnswerChange }) => {
  const [newAnswer, setNewAnswer] = useState<string>(answer ?? "");

  const capitalize = (question: string) => {
    const capitalizeWord = (word: string) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
    const capitalizedWords = question.split(" ").map(word => capitalizeWord(word));
    return capitalizedWords.join(" ");
  };

  const shortText = short.endsWith("?") ? capitalize(short.substring(0, short.length - 1)) : capitalize(short);

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
      <span className="question-short text-ellipsis">{shortText}</span>
      <i title={`${shortText}: ${long}`} className="fas fa-question-circle icon-btn"></i>
      <input type="text" value={newAnswer} onChange={handleChange} className="input" />
    </div>
  );
};
