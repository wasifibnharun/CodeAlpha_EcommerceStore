from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("store", "0002_category_product_category")]
    operations = [
        migrations.AddField(
            model_name="product",
            name="image",
            field=models.ImageField(blank=True, upload_to="products/%Y/%m/"),
        ),
    ]
