import boto3
import os
import mimetypes
import json
from botocore.exceptions import ClientError
#from dotenv import load_dotenv

# 1. Load credentials from .env
#load_dotenv()

def deploy_static_site(bucket_name, region="us-east-1", source_dir="website_files"):
    s3 = boto3.client('s3', region_name=region)

    try:
        # 2. Create the S3 Bucket
        print(f"Initializing deployment for bucket: {bucket_name}")
        s3.create_bucket(Bucket=bucket_name)

        # 3. Force Disable Public Access Blocks (Required for public sites)
        s3.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': False, 'IgnorePublicAcls': False,
                'BlockPublicPolicy': False, 'RestrictPublicBuckets': False
            }
        )
        print("Public access blocks disabled.")

        # 4. Apply Public Read Policy
        policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Sid": "PublicRead",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*"
            }]
        }
        s3.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(policy))
        print("Public read policy applied.")

        # 5. Enable Static Website Hosting
        s3.put_bucket_website(
            Bucket=bucket_name,
            WebsiteConfiguration={
                'IndexDocument': {'Suffix': 'index.html'},
                'ErrorDocument': {'Key': 'index.html'}
            }
        )
        print("Static website hosting enabled.")

        # 6. Recursive Upload from website_files
        print(f"Uploading assets from '{source_dir}'...")
        if not os.path.exists(source_dir):
            print(f"Error: Folder '{source_dir}' not found!")
            return

        for root, dirs, files in os.walk(source_dir):
            for filename in files:
                local_path = os.path.join(root, filename)
                # Keep folder structure if you add subdirectories later
                relative_path = os.path.relpath(local_path, source_dir)
                s3_key = relative_path.replace(os.sep, '/')

                mime_type, _ = mimetypes.guess_type(local_path)
                content_type = mime_type or 'application/octet-stream'

                s3.upload_file(local_path, bucket_name, s3_key, ExtraArgs={'ContentType': content_type})
                print(f"   - {s3_key} ({content_type})")

        print(f"\n SUCCESS! Your site is live at:")
        print(f"http://{bucket_name}.s3-website-{region}.amazonaws.com")

    except ClientError as e:
        print(f" AWS Error: {e}")
    except Exception as e:
        print(f" System Error: {e}")

if __name__ == "__main__":
    # Ensure this name is globally unique in AWS
    MY_BUCKET_NAME = "zoayas-static-website-20260215" 
    deploy_static_site(MY_BUCKET_NAME)
