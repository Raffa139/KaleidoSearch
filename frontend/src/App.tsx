import type { FunctionComponent } from 'react'
import { Login } from './Login';
import { Search } from './Search';

export const App: FunctionComponent = () => {
  return (
    <div className="container">
      <Login />
      <Search />
    </div>
  )
};
