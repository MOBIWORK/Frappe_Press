<template>
	<div>
		<label class="text-lg font-semibold"> Thông tin khởi tạo tổ chức </label>
		<p class="text-base text-gray-700">
			Thông tin tóm tắt cho việc tạo tổ chức của bạn
		</p>
	</div>
</template>
<script>
import FileUploader from '@/components/FileUploader.vue';
import Form from '@/components/Form.vue';
import BackupFilesUploader from '@/components/BackupFilesUploader.vue';
import { DateTime } from 'luxon';

export default {
	name: 'SiteSummaryBilling',
	emits: ['update:selectedFiles', 'update:skipFailingPatches'],
	props: ['selectedFiles', 'manualMigration', 'skipFailingPatches'],
	components: {
		FileUploader,
		Form,
		BackupFilesUploader
	},
	data() {
		return {
			restoreFrom: null,
			files: [
				{
					icon: 'database',
					type: 'database',
					ext: 'application/x-gzip',
					title: 'Database Backup',
					file: null
				},
				{
					icon: 'file',
					type: 'public',
					ext: 'application/x-tar',
					title: 'Public Files',
					file: null
				},
				{
					icon: 'file-minus',
					type: 'private',
					ext: 'application/x-tar',
					title: 'Private Files',
					file: null
				},
				{
					icon: 'file-minus',
					type: 'config',
					ext: 'application/json',
					title: 'Config Files',
					file: null
				}
			],
			uploadedFiles: {
				database: null,
				public: null,
				private: null
			},
			frappeSite: {
				url: '',
				email: '',
				password: ''
			},
			errorMessage: null,
			wantToSkipFailingPatches: false
		};
	},
	resources: {
		getBackupLinks() {
			let { url, email, password } = this.frappeSite;
			return {
				url: 'press.api.site.get_backup_links',
				params: {
					url,
					email,
					password
				},
				validate() {
					let { url, email, password } = this.frappeSite;
					if (!(url && email && password)) {
						return 'Vui lòng nhập URL, Tên người dùng và Mật khẩu';
					}
				},
				onSuccess(remoteFiles) {
					let selectedFiles = {};
					for (let file of remoteFiles) {
						selectedFiles[file.type] = file.remote_file;
					}
					this.$emit('update:selectedFiles', selectedFiles);
				}
			};
		}
	},
	methods: {
		showAlert() {
			this.manualMigration = true;
		},
		errorContains(word) {
			return (
				this.$resources.getBackupLinks.error &&
				this.$resources.getBackupLinks.error.search(word) !== -1
			);
		}
	},
	computed: {
		fetchedBackupFiles() {
			if (!this.$resources.getBackupLinks.data) {
				return [];
			}
			return this.$resources.getBackupLinks.data.map(file => {
				// Convert "20200820_124804-erpnextcom-private-files.tar" to "20200820T124804"
				// so DateTime can parse it
				let timestamp_string = file.file_name
					.split('-')[0]
					.split('_')
					.join('T');

				let formatted = DateTime.fromISO(timestamp_string).toLocaleString(
					DateTime.DATETIME_FULL
				);

				return {
					...file,
					timestamp: formatted
				};
			});
		}
	},
	watch: {
		wantToSkipFailingPatches(value) {
			this.$emit('update:skipFailingPatches', value);
		}
	}
};
</script>
