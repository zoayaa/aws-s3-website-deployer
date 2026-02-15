import boto3
from botocore.exceptions import ClientError
#from dotenv import load_dotenv

# 1. Load credentials
#load_dotenv()

def delete_s3_website(bucket_name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)

    try:
        print(f"Starting cleanup for: {bucket_name}")

        # 2. Delete all objects (This is required before deleting the bucket)
        print("   - Removing all files from bucket...")
        bucket.objects.all().delete()
        print("Bucket is now empty.")

        # 3. Delete the bucket
        print(f"   - Deleting bucket: {bucket_name}")
        bucket.delete()
        print(f" SUCCESS! {bucket_name} has been completely removed.")

    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucket':
            print(f"Error: The bucket '{bucket_name}' does not exist.")
        else:
            print(f" AWS Error: {e}")
    except Exception as e:
        print(f"System Error: {e}")

if __name__ == "__main__":
    # Ensure this matches the name in your provisioner script!
    MY_BUCKET = "zoayas-static-website-20260215" 
    delete_s3_website(MY_BUCKET)
