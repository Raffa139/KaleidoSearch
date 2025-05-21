import { createBrowserRouter } from 'react-router';
import { App } from './App';
import { Login } from './Login';
import { Search } from './Search';

export const router = createBrowserRouter([
  {
    path: "/",
    Component: App,
    children: [
      {
        index: true,
        Component: Login
      },
      {
        path: "users/uid/threads",
        Component: Search
      }
    ]
  }
]);
