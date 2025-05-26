import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from 'react-router';
import { SkeletonTheme } from 'react-loading-skeleton';
import { router } from './routes.ts'
import './index.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <SkeletonTheme baseColor="#6c627f" highlightColor="#8e80a9">
      <RouterProvider router={router} />
    </SkeletonTheme>
  </StrictMode>,
)
