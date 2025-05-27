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

export interface Thread {
  thread_id: number;
  created_at: Date;
  updated_at: Date;
}

export interface Product {
  id: number;
  title: string;
  price: number;
  description: string;
  url: string;
  thumbnail_url?: string;
  shop: {
    name: string;
    url: string;
  }
}

export interface ProductSummary {
  ai_title: string;
  ai_description: string;
}
