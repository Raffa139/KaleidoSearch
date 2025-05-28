import { createBrowserRouter, redirect } from 'react-router';
import { v4 as uuidv4 } from "uuid";
import { Layout } from './layout/Layout';
import { Login } from './authentication/Login';
import { Thread } from './user/threads/Thread';
import { client } from './client/kaleidoClient';
import { Home } from './user/home/Home';
import { Bookmarks } from './user/bookmarks/Bookmarks';

export const router = createBrowserRouter([
  {
    path: "/",
    index: true,
    action: async ({ request }) => {
      return redirect(`/users/2/home`); // TODO: remove this, just for testing

      const formData = await request.formData();
      const username = formData.get("username");
      const password = formData.get("password");

      const user = await client.Users.create(uuidv4(), username as string, null);
      return redirect(`/users/${user.id}/home`);
    },
    Component: Login
  },
  {
    path: "users/:uid",
    loader: ({ params }) => client.Users.getById(params.uid!),
    Component: Layout,
    children: [
      {
        path: "home",
        loader: ({ params }) => client.Users.Threads(params.uid!).getAll(),
        Component: Home
      },
      {
        path: "bookmarks",
        loader: ({ params }) => client.Users.Bookmarks(params.uid!).getAll(),
        Component: Bookmarks
      },
      {
        path: "threads/:tid",
        loader: ({ params }) => client.Users.Threads(params.uid!).getQueryEvaluation(params.tid!),
        Component: Thread
      }
    ]
  }
]);
