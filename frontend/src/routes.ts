import { createBrowserRouter, redirect } from 'react-router';
import { v4 as uuidv4 } from "uuid";
import { App } from './App';
import { Login } from './Login';
import { Search } from './Search';
import { client } from './client/kaleido-client';

export const router = createBrowserRouter([
  {
    path: "/",
    action: async ({ request }) => {
      return redirect(`/users/2/threads`); // TODO: remove this, just for testing

      const formData = await request.formData();
      const username = formData.get("username");
      const password = formData.get("password");

      const user = await client.createUser(uuidv4(), username as string, null);
      return redirect(`/users/${user.id}/threads`);
    },
    Component: App,
    children: [
      {
        index: true,
        Component: Login
      },
      {
        path: "users/:uid/threads",
        loader: async ({ params }) => {
          const user = await client.getUserById(Number(params.uid));
          return { user };
        },
        Component: Search
      }
    ]
  }
]);
