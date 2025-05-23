import { createContext, useState, type FunctionComponent } from "react";
import { Thread } from "./Thread";

export interface ThreadContextProps {
  isBusy: boolean;
  setBusy: (busy: boolean) => void;
}

export const ThreadContext = createContext<Partial<ThreadContextProps>>({});

export const ThreadWithContext: FunctionComponent = () => {
  const [isBusy, setBusy] = useState<boolean>(false);

  return (
    <ThreadContext.Provider value={{ isBusy, setBusy }}>
      <Thread />
    </ThreadContext.Provider>
  );
};
