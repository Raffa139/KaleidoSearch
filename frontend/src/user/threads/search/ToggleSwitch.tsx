import type { FunctionComponent } from "react";
import Switch from "react-switch";
import "./toggleSwitch.css";

interface ToggleSwitchProps {
  checked: boolean;
}

export const ToggleSwitch: FunctionComponent<ToggleSwitchProps> = ({ checked }) => {
  return (
    <Switch
      onChange={() => { }}
      checked={checked}
      width={48}
      height={18}
    />
  );
};
