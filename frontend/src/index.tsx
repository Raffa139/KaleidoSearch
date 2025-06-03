import { createRoot } from "react-dom/client"
import { RouterProvider } from "react-router";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { SkeletonTheme } from "react-loading-skeleton";
import "react-loading-skeleton/dist/skeleton.css";
import "react-photo-view/dist/react-photo-view.css";
import { router } from "./routes.ts"
import "./index.css"

createRoot(document.getElementById("root")!).render(
  <GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID}>
    <SkeletonTheme baseColor="#4c455a" highlightColor="#75698b">
      <RouterProvider router={router} />
    </SkeletonTheme>
  </GoogleOAuthProvider>
);
