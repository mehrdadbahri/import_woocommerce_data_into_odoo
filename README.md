# import_woocommerce_data_into_odoo
Import Woocommerce exported data into Odoo using xmlrpc API

## How to use?

First you need to export the data from Woocommerce using [this repository](https://github.com/mehrdadbahri/export_woocommerce_for_odoo).

Create a file named `odoo_api.ini` in your user's home directory with your Odoo instance connection information and the path to wordpress's `uploads` folder like below:

    [database]
    db = db_name
    username = username
    password = password
    url = https://website.com

    [general]
    uploads_path = /home/user/wordpress_backup/uploads/

You can import the following data **directly in Odoo panel** using the Odoo's default import records option:

* Users (res.users)
* Brands (wk.product.brand) # If you are using [this addon](https://apps.odoo.com/apps/modules/14.0/website_product_brands)
* Attributes (product.attribute)
* Attribute values (product.attribute.value)

But for other data run each python script to import the related data. You should run the scripts in the following **order**:

* import_categories.py
* import_products.py
* import_variant_products.py
* update_attribute_lines.py
* update_variant_external_ids.py
* update_attribute_prices.py
* update_variant_imgs.py
* update_quantities.py
* update_old_urls.py (Optional: Only to have the woocommerce url of product in case needed. You need to create the field on product.template)
