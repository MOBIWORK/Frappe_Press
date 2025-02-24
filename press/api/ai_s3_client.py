import frappe
import boto3
from datetime import datetime
import json

# Biến global để cache kết nối S3
_s3_client = None

def connect_s3():
    """Tạo kết nối S3, chỉ tạo một lần duy nhất."""
    global _s3_client
    if _s3_client is None:
        settings = frappe.db.get_value(
            "Press Settings",
            None,
            ["aws_access_key", "aws_end_point", "aws_secret_key"],
            as_dict=True,
        )

        _s3_client = boto3.client(
            "s3",
            endpoint_url=settings.aws_end_point,
            aws_access_key_id=settings.aws_access_key,
            aws_secret_access_key=settings.aws_secret_key
        )
    
    return _s3_client


def create_bucket(bucket_name):
    """Tạo một bucket mới trong AWS S3"""
    s3_client = connect_s3()

    try:
        s3_client.create_bucket(
            Bucket=bucket_name
        )
        print(f"✅ Bucket '{bucket_name}' đã được tạo thành công!")
    except Exception as e:
        print(f"❌ Lỗi khi tạo bucket: {e}")

def get_all_buckets():
    """Lấy danh sách tất cả bucket."""
    try:
        s3_client = connect_s3()
        response = s3_client.list_buckets()
        return [bucket["Name"] for bucket in response["Buckets"]]
    except Exception:
        return []


def check_bucket_exists(bucket_name):
    """Kiểm tra bucket có tồn tại không."""
    try:
        s3_client = connect_s3()
        s3_client.head_bucket(Bucket=bucket_name)
        return True
    except Exception:
        return False


def delete_bucket(bucket_name):
    msg = 'Bucket not found'
    try:
        s3_client = connect_s3()
        if check_bucket_exists(bucket_name):
            if delete_all_objects_in_bucket(bucket_name):
                s3_client.delete_bucket(Bucket=bucket_name)
                return True, None
    except Exception as ex:
        msg = str(ex)
    return False, msg

def delete_all_objects_in_bucket(bucket_name):
    try:
        s3_client = connect_s3()
        while True:
            response = s3_client.list_objects_v2(Bucket=bucket_name)
            if "Contents" not in response:
                break  # Không còn object nào, thoát vòng lặp

            objects = [{"Key": obj["Key"]} for obj in response["Contents"]]
            s3_client.delete_objects(Bucket=bucket_name, Delete={"Objects": objects})
        return True
    except Exception as ex:
        frappe.log_error(message=f"{str(ex)}", title="Delete all objects")
        return False


def delete_objects_in_bucket(bucket_name, objects):
    msg = 'Bucket not found'
    try:
        s3_client = connect_s3()
        if check_bucket_exists(bucket_name):
            batch_size = 1000
            for i in range(0, len(objects), batch_size):
                batch = [{"Key": obj} for obj in objects[i:i + batch_size]]
                s3_client.delete_objects(Bucket=bucket_name, Delete={"Objects": batch})
            return True, None
    except Exception as ex:
        msg = str(ex)
    return False, msg


def run_handle_schedule_delete_bucket():
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    filters = [['expiration_time','<=', date_now], ['status', '=', 'Pending']]
    schedules = frappe.db.get_all(
        "Schedule Delete Bucket",
        filters=filters,
        fields=[
            "name",
            "bucket_name",
            "deletion_type",
            "objects"
        ],
        page_length=1000,
        order_by="expiration_time asc",
    )
    
    for schedule in schedules:
        try:
            objects = json.loads(schedule.objects)
            if schedule.deletion_type == "Object":
                rs, msg = delete_objects_in_bucket(schedule.bucket_name, objects)
            else:
                rs, msg = delete_bucket(schedule.bucket_name)
            
            if rs:
                status = 'Success'
            else:
                status = 'Failed'
                
            frappe.db.set_value('Schedule Delete Bucket', schedule.name, {
                'status': status,
                'execution_time':date_now,
                'message': msg
            })
        except Exception as ex:
            frappe.log_error(message=str(ex), title="Run handle schedule delete bucket")