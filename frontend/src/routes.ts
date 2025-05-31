import { createBrowserRouter } from 'react-router';
import { Layout } from './layout/Layout';
import { Login } from './authentication/Login';
import { Thread } from './user/threads/Thread';
import { client } from './client/kaleidoClient';
import { Home } from './user/home/Home';
import { Bookmarks } from './user/bookmarks/Bookmarks';
import { Error } from './error/Error';

export const router = createBrowserRouter([
  {
    path: "/",
    index: true,
    Component: Login
  },
  {
    path: "user",
    loader: () => client.Users.getAuthenticated(),
    Component: Layout,
    ErrorBoundary: Error,
    children: [
      {
        path: "home",
        loader: () => client.Users.Threads.getAll(),
        Component: Home
      },
      {
        path: "bookmarks",
        loader: () => client.Users.Bookmarks.getAll(),
        Component: Bookmarks
      },
      {
        path: "threads/:tid",
        loader: ({ params }) => client.Users.Threads.getQueryEvaluation(params.tid!),
        Component: Thread
      }
    ]
  }
]);
