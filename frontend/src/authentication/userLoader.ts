import type { LoaderFunction } from "react-router";
import type { User } from "../client/types";
import { client } from "../client/kaleidoClient";

export const userLoader: LoaderFunction = async ({ params }): Promise<User> => {
  return client.Users.getById(params.uid!);
};
