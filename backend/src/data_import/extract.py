import json
from pydantic import BaseModel, HttpUrl
from .service import ProductImport


class AmazonProduct(BaseModel):
    category: str | None = None
    title: str | None = None
    avg_rating: float | None = None
    n_ratings: int | None = None
    features: list[str] = []
    description: list[str] = []
    price: float | None = None
    images: list[dict] = []
    videos: list = []
    store: str | None = None
    categories: list[str] = []
    details: dict = {}
    parent_asin: str | None = None
    bought_together: list | None = None

    def contains_required_fields(self) -> bool:
        required = [self.title, self.parent_asin, self.price, self.description + self.features]
        return all(required)

    def get_shop(self) -> str:
        return self.store if self.store else "Amazon"

    def get_description(self) -> str:
        description = [line.lower().strip() for line in self.description if line.strip()]
        features = [line.lower().strip() for line in self.features if line.strip()]
        separator = ["-"] if description and features else []
        distinct_combined = self._distinct_ordered_list(description + separator + features)
        return " ".join(distinct_combined)

    def get_product_url(self) -> HttpUrl:
        return HttpUrl(url=f"https://www.amazon.com/dp/{self.parent_asin}")

    def get_thumbnail_url(self) -> HttpUrl | None:
        main_images = [image for image in self.images if image.get("variant") == "MAIN"]
        if not main_images:
            return None

        thumbnail = main_images[0].get('large') if main_images else None
        if thumbnail:
            return HttpUrl(url=thumbnail)
        return None

    def _distinct_ordered_list(self, collection: list) -> list:
        seen = set()
        seen_add = seen.add
        return [entry for entry in collection if not entry in seen or seen_add(entry)]


def extract_amazon_data(data_file: str) -> list[ProductImport]:
    products = []

    with open(data_file, encoding="utf-8") as file:
        raw_products = [json.loads(line.strip()) for line in file]

    for raw_product in raw_products:
        amazon_product = AmazonProduct(**raw_product)

        if not amazon_product.contains_required_fields():
            continue

        products.append(ProductImport(
            title=amazon_product.title,
            price=amazon_product.price,
            url=amazon_product.get_product_url(),
            thumbnail_url=amazon_product.get_thumbnail_url(),
            shop=amazon_product.get_shop(),
            description=amazon_product.get_description()
        ))

    return products
