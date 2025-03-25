import scrapy
import json
import re

class TargetProductSpider(scrapy.Spider):
    name = "target_product"

    def __init__(self, url=None, *args, **kwargs):
        super(TargetProductSpider, self).__init__(*args, **kwargs)
        if url:
            self.tcin = url.split("-/A-")[-1].split("#")[0]
            self.api_url = f"https://redsky.target.com/redsky_aggregations/v1/web/pdp_client_v1?key=9f36aeafbe60771e321a7cc95a78140772ab3e96&tcin=92469343&is_bot=false&store_id=2786&pricing_store_id=2786&has_pricing_store_id=true&has_financing_options=true&include_obsolete=true&visitor_id=0195CC7D45070201851718653E593501&skip_personalized=true&skip_variation_hierarchy=true&channel=WEB&page=%2Fp%2FA-92469343"
        else:
            print("Please provide a URL using -a url=<product_url>")

    def start_requests(self):
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }
        yield scrapy.Request(url=self.api_url, callback=self.parse_json, headers=headers)

    def parse_json(self, response):
        try:
            data = json.loads(response.text)
            product = data.get("data", {}).get("product", {})

            #extract images
            images_data = product.get("item", {}).get("enrichment", {})
            primary_image = images_data.get("images","").get("primary_image_url")
            alternate_images = images_data.get("images","").get("alternate_image_urls", [])
            images = [primary_image] + alternate_images if primary_image else alternate_images
            specification = product.get("item", {}).get("product_description", {}).get("bullet_descriptions")
            specification_cleanup = [re.sub(r"</?B>", "", item) for item in specification] #clean specification
            yield {
                "product_name": product.get("item", {}).get("product_description", {}).get("title"),
                "categories": product.get("category", {}).get("name", []),
                "model_no": product.get("item", {}).get("product_description", {}).get("model_number","N.A."),
                "Tcin_id": product.get("tcin"),
                "images": images,
                "specification": specification_cleanup,
                "description": product.get("item", {}).get("product_description", {}).get("downstream_description"),
                "variant": product.get("variation", {}).get("variation_info", "N.A."),
                "price": product.get("price", {}).get("current_retail"),
                "discount_price": product.get("price", {}).get("formatted_current_price"),
                "sellers": product.get("item", {}).get("product_vendors", "")[0].get("vendor_name",""),
            }
            print(f"Extraction completed!!")
        except json.JSONDecodeError:
            print("Failed to parse JSON. Check if the API URL is correct.")

