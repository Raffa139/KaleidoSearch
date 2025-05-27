import type { FunctionComponent } from "react";
import { PuffLoader } from "react-spinners";
import "./modalPuffLoader.css";

interface ModalPuffLoaderProps {
  loading?: boolean;
}

export const ModalPuffLoader: FunctionComponent<ModalPuffLoaderProps> = ({ loading }) => {
  return loading ? (
    <div className="loader">
      <PuffLoader color="white" />
    </div>
  ) : null;
};