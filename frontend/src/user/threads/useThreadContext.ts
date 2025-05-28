import { useContext } from "react";
import { ThreadContext, type ThreadContextProps } from "./ThreadContext";
import type { Product, QueryEvaluation, User, UserAnswer } from "../../client/types";
import { client } from "../../client/kaleidoClient";
import type { ThreadsClient } from "../../client/threadsClient";

interface UseThreadContext {
  (props: { user: User }): {
    isBusy: boolean;
    rerank: boolean;
    setRerank: (rerank: boolean) => void;
    getRecommendations: typeof ThreadsClient.prototype.getRecommendations;
    postToThread: typeof ThreadsClient.prototype.post;
    createThread: typeof ThreadsClient.prototype.create;
  };
}

export const useThreadContext: UseThreadContext = ({ user: { id: uid } }) => {
  const { isBusy, setBusy, rerank, setRerank } = useContext(ThreadContext) as ThreadContextProps;

  const getRecommendations = async (tid: number): Promise<Product[]> => {
    setBusy(true);

    try {
      const response = await client.Users.Threads(uid).getRecommendations(tid, rerank);
      setBusy(false);
      return response;
    } catch (error) {
      // TODO: Display that search needs refinement
      setBusy(false);
      return [];
    }
  };

  const postToThread = async (tid: number, content: { query?: string, answers?: UserAnswer[] }): Promise<QueryEvaluation> => {
    setBusy(true);
    const response = await client.Users.Threads(uid).post(tid, content);
    setBusy(false);
    return response;
  };

  const createThread = async (query?: string): Promise<QueryEvaluation> => {
    setBusy(true);
    const response = await client.Users.Threads(uid).create(query);
    setBusy(false);
    return response;
  };

  return { isBusy, rerank, setRerank, getRecommendations, postToThread, createThread };
};
