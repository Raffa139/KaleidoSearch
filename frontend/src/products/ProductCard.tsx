import { useEffect, useState, type FunctionComponent } from "react";
import { useOutletContext } from "react-router";
import { PhotoProvider, PhotoView } from "react-photo-view";
import Skeleton from "react-loading-skeleton";
import type { Bookmark, Product, ProductSummary, User } from "../client/types";
import { client } from "../client/kaleidoClient";
import "./productCard.css";

type ProductCardProps = Product & Partial<ProductSummary>

export const ProductCard: FunctionComponent<ProductCardProps> = ({ id: productId, ai_title, price, ai_description, url, thumbnail_url, shop }) => {
  const { id: uid } = useOutletContext<User>();

  const [bookmark, setBookmark] = useState<Bookmark>();

  useEffect(() => {
    const fetchBookmark = async () => {
      const bookmark = await client.Users.Bookmarks(uid).getByProductId(productId);
      if (bookmark) {
        setBookmark(bookmark);
      }
    };

    fetchBookmark();
  }, [productId]);

  const handleBookmarking = async () => {
    if (bookmark) {
      client.Users.Bookmarks(uid).delete(bookmark.id);
      setBookmark(undefined);
    } else {
      const bookmark = await client.Users.Bookmarks(uid).create(productId);
      setBookmark(bookmark);
    }
  };

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
              {ai_title ? (
                <>
                  {ai_title}
                  <i className="fa-solid fa-arrow-up-right-from-square"></i>
                </>
              ) : (
                <Skeleton width={300} />
              )}
            </h3>
          </a>

          <div className="result-icon-btns">
            <button onClick={handleBookmarking} className={`icon-btn ${bookmark ? "btn-active" : ""}`}>
              <i className="fas fa-bookmark"></i>
            </button>

            <button className="icon-btn"><i className="fa-solid fa-share-nodes"></i></button>
          </div>
        </div>

        <span className="shop-tag">{shop.name}</span>

        <span className="price-tag">${price}</span>

        <p className="result-description">
          {ai_description ? (
            ai_description
          ) : (
            <>
              <Skeleton width={400} />
              <Skeleton width={350} />
            </>
          )}
        </p>
      </div>
    </div>
  );
};
