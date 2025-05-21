import type { LoaderFunction } from "react-router";
import type { User } from "../client/types";
import { client } from "../client/kaleidoClient";

export interface UserLoaderData {
  user: User;
}

export const userLoader: LoaderFunction = async ({ params }): Promise<UserLoaderData> => {
  const user = await client.getUserById(Number(params.uid));
  return { user };
};
