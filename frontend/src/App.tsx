import type { FunctionComponent } from 'react'
import { Outlet } from 'react-router';

export const App: FunctionComponent = () => {
  return (
    <div className="container">
      <Outlet />
    </div>
  )
};
