import { useContext } from "react";
import { ThreadContext, type ThreadContextProps } from "./ThreadContext";
import type { Product, QueryEvaluation, UserAnswer } from "../../client/types";
import { client } from "../../client/kaleidoClient";

interface UseThreadContext {
  (props?: {}): {
    isBusy: boolean;
    getRecommendations: typeof client.getRecommendations;
    postToThread: typeof client.postToThread;
  };
}

export const useThreadContext: UseThreadContext = () => {
  const { isBusy, setBusy } = useContext(ThreadContext) as ThreadContextProps;

  const getRecommendations = async (uid: number, tid: number): Promise<Product[]> => {
    setBusy(true);

    try {
      const response = await client.getRecommendations(uid, tid);
      setBusy(false);
      return response;
    } catch (error) {
      // TODO: Display that search needs refinement
      setBusy(false);
      return [];
    }
  };

  const postToThread = async (uid: number, tid: number, content: { query?: string, answers?: UserAnswer[] }): Promise<QueryEvaluation> => {
    setBusy(true);
    const response = await client.postToThread(uid, tid, content);
    setBusy(false);
    return response;
  };

  return { isBusy, getRecommendations, postToThread };
};
