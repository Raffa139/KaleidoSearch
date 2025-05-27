import type { FunctionComponent } from "react";
import Skeleton from "react-loading-skeleton";

interface ProductSkeletonProps {
  loading?: boolean;
  count?: number;
}

export const ProductSkeleton: FunctionComponent<ProductSkeletonProps> = ({ loading, count = 1 }) => {
  const skeletons = Array.from({ length: count }).map((_, i) => i);

  return loading ? (
    <>
      {skeletons.map((i) => (
        <div key={i} className="search-result" >
          <div className="result-image">
            <Skeleton className="result-image" />
          </div>

          <div className="result-content" >
            <Skeleton width={300} />

            <span className="shop-tag">
              <Skeleton width={100} />
            </span>

            <span className="price-tag">
              <Skeleton width={50} />
            </span>

            <p className="result-description">
              <Skeleton width={400} />
              <Skeleton width={350} />
            </p>
          </div>
        </div>
      ))}
    </>
  ) : null;
};
