import type { ChangeEvent, FunctionComponent } from "react";
import "./searchInput.css";

interface SearchInputProps {
  value: string;
  placeholder?: string;
  onChange: (e: ChangeEvent<HTMLInputElement>) => void;
  onSearch: () => void;
}

export const SearchInput: FunctionComponent<SearchInputProps> = ({ value, placeholder, onChange, onSearch }) => {
  return (
    <div className="search-input">
      <input type="text" value={value} onChange={onChange} placeholder={placeholder} className="input" />
      <button onClick={onSearch} className="search-button"><i className="fas fa-search"></i></button>
    </div>
  );
};