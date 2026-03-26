import json
import random
import uuid
import datetime

def generate_products_with_variants(count=10):
    products = []
    
    # --- Data Sources (matching main.py) ---
    tech_products = {
        "Dispositivos móviles y tecnología": [
            ("iPhone 13", [64, 128, 256, 512], "GB", 6000000),
            ("iPhone 13 Pro", [128, 256, 512, 1024], "GB", 7500000),
            ("Samsung Galaxy S23", [128, 256, 512], "GB", 4500000),
            ("iPad Pro 11 M2", [128, 256, 512, 1024], "GB", 5500000),
            ("MacBook Air M2", [256, 512, 1024], "GB", 5500000),
            ("Apple Watch Series 9", [41, 45], "mm", 2200000),
            ("Google Pixel 8 Pro", [128, 256, 512], "GB", 5000000),
        ]
    }
    
    colors = ["Negro", "Blanco", "Azul", "Rojo", "Plata", "Oro", "Gris Espacial", "Verde"]
    
    # Simplified Unit/Category Configs based on read.me IDs
    category_id = "f7a8cc30-22a2-45b9-b86b-196abfb4d427" # Cuidado Personal (Just using valid UUIDs from example)
    # Actually better to use the Tech category form read.me example if available or fallback
    tech_cat_id = "682e7102-cc22-432f-b1b9-45ae21bcf3cf" # Dispositivos móviles y tecnología
    
    unit_group_id = "e5a94b7e-4f5a-4c60-b517-273b36cb1d5a" # Volumen? Or use the one from main.py logic
    # In main.py: "Cantidad / Unidades" -> f7c82967-5cb1-42b8-9213-792d8cf5e3f4
    unit_groups = {
        "Cantidad / Unidades": "f7c82967-5cb1-42b8-9213-792d8cf5e3f4"
    }
    unit_id_mock = "a8832d23-509b-4971-9c59-03232a624fc4" # Unit UUID
    
    company_id = "1fafaa4d-ef88-410e-8ebc-3ba494c331ad"
    country_id = "ca2b69a5-acb2-4adc-938a-8364a8341353"
    
    for i in range(count):
        # 1. Base Product Selection
        cat_name = "Dispositivos móviles y tecnología"
        base_name, storage_opts, storage_unit, base_price = random.choice(tech_products[cat_name])
        
        # Randomly decide how many variants (up to 5)
        num_variants = random.randint(1, 5)
        
        # Prepare variants
        selected_colors = random.sample(colors, min(num_variants, len(colors)))
        variants_data = []
        variant_attributes_options = []
        
        # Assume attribute is Color for variation in this example
        for color in selected_colors:
            variant_sku = f"{base_name.replace(' ', '')[:4].upper()}-{color[:3].upper()}-{random.randint(1000,9999)}"
            variant_price = int(base_price * random.uniform(0.9, 1.1))
            variant_cost = int(variant_price * 0.7)
            
            variants_data.append({
                "id": str(uuid.uuid4())[:8], # Temporary ID or name as ID like in read.me example ("blanco")
                "name": color,
                "sku": variant_sku,
                "imgFile": "",
                "barcode": "",
                "defaultPrice": variant_price,
                "status": "",
                "cost": variant_cost
            })
            variant_attributes_options.append(color)

        # Attribute definitions
        attributes = [
            {
                "attributeName": "color",
                "option1": variant_attributes_options[0] if len(variant_attributes_options) > 0 else "",
                "option2": variant_attributes_options[1] if len(variant_attributes_options) > 1 else "",
                "options": ", ".join(variant_attributes_options),
                "id": "color"
            }
        ]

        # Construct Product Object (read.me structure)
        product = {
            "imgFile": "",
            "companyID": company_id,
            "isPerishable": False,
            "allowPriceEditInPOS": False,
            "values": {
                "type": "Product",
                "name": f"{base_name} {random.choice(storage_opts)}{storage_unit}",
                "category": {
                    "label": cat_name,
                    "value": tech_cat_id
                },
                "unitGroup": unit_groups.get("Cantidad / Unidades", unit_group_id),
                "description": f"Description for {base_name}",
                "active": True,
                "unit": unit_id_mock,
                # Fields used when NO variants exist, but we are doing variants
                # "undefinedsku": "...", 
                # "undefinedcost": 0,
            },
            "customUnitsData": None,
            "selectedUnitGroup": unit_groups.get("Cantidad / Unidades", unit_group_id),
            "selectedCategory": {
                "id": tech_cat_id,
                "name": cat_name,
                "type": "Product",
                "img": None,
                "companyID": company_id,
            },
            "selectedCountry": {
                "id": country_id,
                "name": "Mexico",
                "code": "MEX",
            },
            "selectVendors": [],
            "attribute": attributes,
            "customProperties": [],
            "variant": variants_data
        }
        
        products.append(product)
        
    return products

if __name__ == "__main__":
    generated_data = generate_products_with_variants(50)
    
    filename = "products_variants.json"
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(generated_data, f, indent=4, ensure_ascii=False)
        
    print(f"Generated {len(generated_data)} products in {filename}")
