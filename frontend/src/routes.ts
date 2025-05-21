import { createBrowserRouter, redirect } from 'react-router';
import { App } from './App';
import { Login } from './Login';
import { Search } from './Search';

export const router = createBrowserRouter([
  {
    path: "/",
    action: async ({ request }) => {
      console.log("Logging in...");
      const formData = await request.formData();
      const username = formData.get("username");
      const password = formData.get("password");

      console.log("Logging in with", username, password);

      return redirect("/users/123/threads");
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
          return { username: `User-${params.uid}` }
        },
        Component: Search
      }
    ]
  }
]);
