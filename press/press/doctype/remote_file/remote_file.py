# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and contributors
# For license information, please see license.txt


import json

import frappe
import requests
import pprint
from boto3 import client, resource
from frappe.model.document import Document
from frappe.utils.password import get_decrypted_password


def s3_endpoint(bucket):
	"""Endpoint of the S3-compatible store (MinIO…) holding `bucket`; None means AWS.

	Offsite backup buckets: Backup Bucket.endpoint_url. Remote uploads bucket (restore from uploaded files):
	Press Settings.remote_uploads_endpoint_url."""
	if not bucket:
		return None
	if bucket == frappe.db.get_single_value("Press Settings", "remote_uploads_bucket"):
		return frappe.db.get_single_value("Press Settings", "remote_uploads_endpoint_url") or None
	return frappe.db.get_value("Backup Bucket", bucket, "endpoint_url") or None


def s3_client_kwargs(bucket, region=None):
	"""Extra boto3 client/resource kwargs for `bucket`: endpoint + path-style addressing when it lives on an
	S3-compatible store (MinIO serves buckets by path unless a virtual-host domain is configured)."""
	from botocore.config import Config

	kwargs = {}
	if region:
		kwargs["region_name"] = region
	endpoint = s3_endpoint(bucket)
	if endpoint:
		kwargs["endpoint_url"] = endpoint
		kwargs["config"] = Config(signature_version="s3v4", s3={"addressing_style": "path"})
	return kwargs


def get_remote_key(file):
	from hashlib import sha1
	from os.path import join
	from time import time

	from press.utils import get_current_team

	team = sha1(get_current_team().encode()).hexdigest()
	time = str(time()).replace(".", "_")

	return join(team, time, file)


def poll_file_statuses():
	from press.utils import chunk

	available_files = {}
	doctype = "Remote File"
	aws_access_key = frappe.db.get_single_value(
		"Press Settings", "offsite_backups_access_key_id"
	)
	aws_secret_key = get_decrypted_password(
		"Press Settings", "Press Settings", "offsite_backups_secret_access_key"
	)
	default_region = frappe.db.get_single_value("Press Settings", "backup_region")
	buckets = {
		frappe.db.get_single_value("Press Settings", "aws_s3_bucket"): {
			"region": default_region,
			"access_key_id": aws_access_key,
			"secret_access_key": aws_secret_key,
		},
		frappe.db.get_single_value("Press Settings", "remote_uploads_bucket"): {
			"region": frappe.db.get_single_value("Press Settings", "remote_uploads_region")
			or default_region,
			"access_key_id": frappe.db.get_single_value(
				"Press Settings", "remote_access_key_id"
			),
			"secret_access_key": get_decrypted_password(
				"Press Settings", "Press Settings", "remote_secret_access_key"
			),
		},
	}

	[
		buckets.update(
			{
				b["bucket_name"]: {
					"region": b["region"],
					"access_key_id": aws_access_key,
					"secret_access_key": aws_secret_key,
				},
			}
		)
		for b in frappe.get_all("Backup Bucket", ["bucket_name", "cluster", "region"])
	]

	for bucket_name, current_bucket in buckets.items():
		available_files[bucket_name] = []

		s3 = resource(
			"s3",
			aws_access_key_id=current_bucket["access_key_id"],
			aws_secret_access_key=current_bucket["secret_access_key"],
			**s3_client_kwargs(bucket_name, current_bucket["region"]),
		)

		for s3_object in s3.Bucket(bucket_name).objects.all():
			available_files[bucket_name].append(s3_object.key)

		all_files = set(available_files[bucket_name])

		remote_files = frappe.get_all(
			doctype,
			fields=["name", "file_path", "status"],
			filters={"bucket": bucket_name},
		)

		set_to_available = []
		set_to_unavailable = []
		for remote_file in remote_files:
			name, file_path, status = (
				remote_file["name"],
				remote_file["file_path"],
				remote_file["status"],
			)
			if file_path not in all_files:
				if status == "Available":
					set_to_unavailable.append(name)
			else:
				if status == "Unavailable":
					set_to_available.append(name)

		for files in chunk(set_to_unavailable, 1000):
			frappe.db.set_value(doctype, {"name": ("in", files)}, "status", "Unavailable")

		for files in chunk(set_to_available, 1000):
			frappe.db.set_value(doctype, {"name": ("in", files)}, "status", "Available")

		frappe.db.commit()


def delete_remote_backup_objects(remote_files):
	"""Delete specified objects identified by keys in the backups bucket."""
	from boto3 import resource
	from press.utils import chunk

	press_settings = frappe.get_single("Press Settings")
	remote_files = list(set([x for x in remote_files if x]))
	if not remote_files:
		return

	buckets = {bucket: [] for bucket in frappe.get_all("Backup Bucket", pluck="name")}
	buckets.update({frappe.db.get_single_value("Press Settings", "aws_s3_bucket"): []})

	[
		buckets[bucket].append(file)
		for file, bucket in frappe.db.get_values(
			"Remote File",
			{"name": ("in", remote_files), "status": "Available"},
			["file_path", "bucket"],
		)
	]

	for bucket_name in buckets.keys():
		s3 = resource(
			"s3",
			aws_access_key_id=press_settings.offsite_backups_access_key_id,
			aws_secret_access_key=press_settings.get_password(
				"offsite_backups_secret_access_key", raise_exception=False
			),
			**(s3_client_kwargs(bucket_name) or {"endpoint_url": "https://s3.amazonaws.com"}),
		)
		bucket = s3.Bucket(bucket_name)
		for objects in chunk([{"Key": x} for x in buckets[bucket_name]], 1000):
			response = bucket.delete_objects(Delete={"Objects": objects})
			response = pprint.pformat(response)
			frappe.get_doc(
				doctype="Remote Operation Log", operation_type="Delete Files", response=response
			).insert()

	frappe.db.set_value(
		"Remote File", {"name": ("in", remote_files)}, "status", "Unavailable"
	)

	return remote_files


class RemoteFile(Document):
	@property
	def s3_client(self):
		if not self.bucket:
			return None

		elif self.bucket == frappe.db.get_single_value(
			"Press Settings", "remote_uploads_bucket"
		):
			access_key_id = frappe.db.get_single_value("Press Settings", "remote_access_key_id")
			secret_access_key = get_decrypted_password(
				"Press Settings", "Press Settings", "remote_secret_access_key"
			)

		elif self.bucket:
			access_key_id = frappe.db.get_single_value(
				"Press Settings", "offsite_backups_access_key_id"
			)
			secret_access_key = get_decrypted_password(
				"Press Settings", "Press Settings", "offsite_backups_secret_access_key"
			)

		else:
			return None

		if self.bucket == frappe.db.get_single_value("Press Settings", "remote_uploads_bucket"):
			region = frappe.db.get_single_value("Press Settings", "remote_uploads_region")
		else:
			region = frappe.db.get_value("Backup Bucket", self.bucket, "region")
		return client(
			"s3",
			aws_access_key_id=access_key_id,
			aws_secret_access_key=secret_access_key,
			**s3_client_kwargs(
				self.bucket, region or frappe.db.get_single_value("Press Settings", "backup_region")
			),
		)

	@property
	def download_link(self):
		return self.get_download_link()

	@frappe.whitelist()
	def exists(self):
		self.db_set("status", "Available")

		if self.url:
			success = str(requests.head(self.url).status_code).startswith("2")
			if success:
				return True
			self.db_set("status", "Unavailable")
			return False
		else:
			try:
				return self.s3_client.head_object(Bucket=self.bucket, Key=self.file_path)
			except Exception:
				self.db_set("status", "Unavailable")
				return False

	@frappe.whitelist()
	def delete_remote_object(self):
		self.db_set("status", "Unavailable")
		return self.s3_client.delete_object(
			Bucket=frappe.db.get_single_value("Press Settings", "remote_uploads_bucket"),
			Key=self.file_path,
		)

	def on_trash(self):
		self.delete_remote_object()

	@frappe.whitelist()
	def get_download_link(self):
		return self.url or self.s3_client.generate_presigned_url(
			"get_object",
			Params={"Bucket": self.bucket, "Key": self.file_path},
			ExpiresIn=frappe.db.get_single_value("Press Settings", "remote_link_expiry") or 3600,
		)

	def get_content(self):
		if self.url:
			return json.loads(requests.get(self.url).content)
		else:
			obj = self.s3_client.get_object(Bucket=self.bucket, Key=self.file_path)
			return json.loads(obj["Body"].read().decode("utf-8"))
