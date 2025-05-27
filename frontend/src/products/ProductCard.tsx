import type { FunctionComponent } from "react";
import { PhotoProvider, PhotoView } from "react-photo-view";
import type { Product } from "../client/types";
import "./productCard.css";

export const ProductCard: FunctionComponent<Product> = ({ ai_title, price, description, url, thumbnail_url, shop }) => {
  return (
    <div className="search-result">
      <PhotoProvider>
        <PhotoView src={thumbnail_url ?? "/placeholder-product.png"}>
          <img src={thumbnail_url ?? "/placeholder-product.png"} alt="Result Image" className="result-image" />
        </PhotoView>
      </PhotoProvider>

      <div className="result-content">
        <div className="result-title">
          <a href={url} target="_blank">
            <h3>
              {ai_title}
              <i className="fa-solid fa-arrow-up-right-from-square"></i>
            </h3>
          </a>

          <div className="result-icon-btns">
            <button className="icon-btn"><i className="fas fa-bookmark"></i></button>
            <button className="icon-btn"><i className="fa-solid fa-share-nodes"></i></button>
            {/* <button className="icon-btn"><i className="fa-solid fa-wand-magic-sparkles"></i></button> */}
          </div>
        </div>

        <span className="shop-tag">{shop.name}</span>

        <span className="price-tag">${price}</span>

        <p className="result-description">{description}</p>
      </div>
    </div>
  );
};