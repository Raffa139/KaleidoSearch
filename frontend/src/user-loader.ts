import type { LoaderFunction } from "react-router";
import { client, type User } from "./client/kaleido-client";

export interface UserLoaderData {
    user: User;
}

export const userLoader: LoaderFunction = async ({ params }): Promise<UserLoaderData> => {
    const user = await client.getUserById(Number(params.uid));
    return { user };
};
