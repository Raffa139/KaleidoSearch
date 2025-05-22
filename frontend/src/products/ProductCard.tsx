import type { FunctionComponent } from "react";
import type { Product } from "../client/types";
import "./productCard.css";

export const ProductCard: FunctionComponent<Product> = ({ title, price, description, url, thumbnail_url }) => {
  return (
    <div className="search-result">
      <div className="result-icons">
        <button className="icon-btn"><i className="fas fa-heart"></i></button>
        <button className="icon-btn"><i className="fas fa-plus"></i></button>
      </div>

      <img src={thumbnail_url ?? "/placeholder-product.png"} alt="Result Image" className="result-image" />

      <div className="result-content">
        <h3 className="result-title">{title}</h3>
        <span className="price-tag">${price}</span>
        <p className="result-description">{description}</p>
      </div>
    </div>
  );
};