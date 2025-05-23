import type { FunctionComponent } from "react";
import { ClipLoader } from "react-spinners";

export const GlobalSpinner: FunctionComponent = () => {
  return (
    <div style={{ display: "flex", justifyContent: "center" }}>
      <ClipLoader color="white" size={70} speedMultiplier={0.5} />
    </div>
  );
};
