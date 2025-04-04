import boto3
from env_cred import s3_access_key_id, s3_secret_access_key, s3_region, s3_bucket_name

def get_product_image_url(product_key):
    """
    Get the URL of the first image for a product from S3 bucket.
    
    Args:
        product_key (str): The product code/ID to look up
        
    Returns:
        str or None: URL of the first image if found, None otherwise
    """
    # Connect to S3 using environment variables
    s3_client = boto3.client(
        's3',
        aws_access_key_id=s3_access_key_id,
        aws_secret_access_key=s3_secret_access_key,
        region_name=s3_region
    )
    
    prefix = f"engineer-inventory/product_id/{product_key}/"
    
    # List objects in the product folder
    response = s3_client.list_objects_v2(
        Bucket=s3_bucket_name,
        Prefix=prefix
    )
    
    # Check if any objects were found
    if 'Contents' in response and len(response['Contents']) > 0:
        # Get the first image key
        first_image_key = response['Contents'][0]['Key']
        public_url = f"https://{s3_bucket_name}.s3.amazonaws.com/{first_image_key}"
        return public_url
    else:
        return None