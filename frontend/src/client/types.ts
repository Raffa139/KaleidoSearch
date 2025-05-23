export interface User {
  id: number;
  sub_id: string;
  username: string | null;
  picture_url: string | null;
}

interface HasId {
  id: number;
}

export interface UserAnswer extends HasId {
  answer: string;
  remove: boolean;
}

export interface FollowUpQuestion extends HasId {
  short: string;
  long: string;
}

export type AnsweredQuestion = FollowUpQuestion & Omit<UserAnswer, "remove">;

export interface QueryEvaluation {
  thread_id: number;
  valid: boolean;
  answered_questions: AnsweredQuestion[];
  follow_up_questions: FollowUpQuestion[];
  cleaned_query?: string;
}

export interface Product {
  title: string;
  price: number;
  description: string;
  url: string;
  thumbnail_url?: string;
}
