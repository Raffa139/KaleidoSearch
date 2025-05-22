import type { FunctionComponent } from "react";
import { useLoaderData, useOutletContext } from "react-router";
import type { UserLoaderData } from "../../authentication/userLoader";
import { ProductRecommendation } from "../../products/ProductRecommendation";
import { SearchBar } from "./search/SearchBar";
import "./thread.css";

export const Thread: FunctionComponent = () => {
  const { thread_id } = useLoaderData();
  const { user } = useOutletContext<UserLoaderData>();

  console.log("Logged in as", user, "in thread", thread_id);

  return (
    <>
      <SearchBar />

      {/* <div className="results-container">
        <ProductRecommendation
          title="Example Search Result Title One"
          price={19.99}
          description="This is a concise description of the search result. It provides a brief overview of the item or content."
          url="#"
        />

        <ProductRecommendation
          title="Another Product or Service Here"
          price={49.50}
          description="Here's another descriptive text for a search result, giving more details about what's offered."
          url="#"
        />

        <ProductRecommendation
          title="Third Item in the List"
          price={75.00}
          description="A short and sweet description for the third search result, highlighting its key features."
          url="#"
        />

        <ProductRecommendation
          title="Example Search Result Title One"
          price={19.99}
          description="This is a concise description of the search result. It provides a brief overview of the item or content."
          url="#"
        />

        <ProductRecommendation
          title="Another Product or Service Here"
          price={49.50}
          description="Here's another descriptive text for a search result, giving more details about what's offered."
          url="#"
        />

        <ProductRecommendation
          title="Third Item in the List"
          price={75.00}
          description="A short and sweet description for the third search result, highlighting its key features."
          url="#"
        />
      </div> */}
    </>
  );
};