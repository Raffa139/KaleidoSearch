import { Fragment, useState, type FunctionComponent } from "react";
import { useLoaderData, useOutletContext } from "react-router";
import type { UserLoaderData } from "../../authentication/userLoader";
import { ProductCard } from "../../products/ProductCard";
import { SearchBar } from "./search/SearchBar";
import { client } from "../../client/kaleidoClient";
import type { Product, QueryEvaluation } from "../../client/types";
import "./thread.css";

export const Thread: FunctionComponent = () => {
  const thread = useLoaderData<QueryEvaluation>();
  const { user } = useOutletContext<UserLoaderData>();

  const [queryEvaluation, setQueryEvaluation] = useState<QueryEvaluation | undefined>(thread);
  const [products, setProducts] = useState<Product[]>([]);

  console.log("Logged in as", user, "in thread", thread);

  const handleSearch = async (queryEvaluation?: QueryEvaluation) => {
    setQueryEvaluation(queryEvaluation);
    const products = await client.getRecommendations(user.id, thread.thread_id);
    setProducts(products);
  };

  return (
    <div className="container">
      <SearchBar queryEvaluation={queryEvaluation} onSearch={handleSearch} />

      <div className="results-container">
        {products.map((product) => (
          <Fragment key={product.url}>
            <ProductCard {...product} />
          </Fragment>
        ))}
      </div>
    </div>
  );
};