<template>
	<div>
		<label class="text-lg font-semibold">
			Khôi phục một trang web hiện tại
		</label>
		<p class="text-base text-gray-700">
			Khôi phục một trang web hiện tại từ tệp sao lưu hoặc trực tiếp từ URL của
			trang web.
		</p>
		<div class="mt-4 grid grid-cols-2 gap-6">
			<Button
				v-for="tab in [
					{ name: 'Tải lên tệp sao lưu', key: 'backup' },
					{ name: 'Chuyển đổi từ URL trang web', key: 'siteUrl' }
				]"
				:key="tab.key"
				:type="restoreFrom === tab.key ? 'primary' : 'secondary'"
				@click="restoreFrom = tab.key"
			>
				{{ tab.name }}
			</Button>
		</div>
		<div v-if="restoreFrom === 'backup'">
			<div
				class="mt-6 rounded-md border border-gray-300 px-4 py-3 text-sm text-gray-700"
			>
				<ol class="list-decimal pl-4">
					<li>Đăng nhập vào trang web của bạn.</li>
					<li>Từ trang Tải về Bản sao lưu, tải xuống bản sao lưu mới nhất.</li>
					<li>
						Để có bản sao lưu tệp, nhấp vào Tải về Bản sao lưu Tệp. Điều này sẽ
						tạo ra một bản sao lưu tệp mới và bạn sẽ nhận được một email.
					</li>
					<li>
						Tải xuống bản sao lưu tệp từ các liên kết trong email và tải lên tệp
						ở đây.
					</li>
				</ol>
			</div>
			<Alert class="mt-5 w-full" v-if="manualMigration">
				Dường như trang web của bạn lớn. Hãy mở một phiếu hỗ trợ và cho biết bạn
				muốn khôi phục một bản sao lưu và kích thước của nó, chúng tôi sẽ xử lý
				từ đó.
			</Alert>
			<BackupFilesUploader
				class="mt-6"
				:backupFiles="selectedFiles"
				@update:backupFiles="files => $emit('update:selectedFiles', files)"
			/>
		</div>
		<div v-if="restoreFrom === 'siteUrl'">
			<div class="mt-6">
				<div
					class="rounded-md border border-gray-300 px-4 py-3 text-sm text-gray-700"
				>
					<ol class="list-decimal pl-4">
						<li>Đăng nhập vào trang web của bạn và hoàn tất đạo cụ cài đặt.</li>
						<li>Từ trang Tải Bản sao lưu, nhấp vào Tải về Bản sao lưu Tệp.</li>
						<li>
							Điều này sẽ tạo ra một bản sao lưu tệp mới và bạn sẽ nhận được một
							email.
						</li>
						<li>Sau đó, quay lại đây và nhấp vào Lấy Bản sao lưu.</li>
					</ol>
				</div>
				<Alert
					class="mt-5 w-full"
					v-if="
						errorContains('Your site exceeds the limits for this operation')
					"
				>
					Dường như trang web của bạn lớn. Hãy mở một phiếu hỗ trợ và cho biết
					bạn muốn khôi phục một bản sao lưu và kích thước của nó, chúng tôi sẽ
					xử lý từ đó.
				</Alert>
				<Form
					class="mt-6"
					:fields="[
						{
							label: 'URL trang web',
							fieldtype: 'Data',
							fieldname: 'url'
						},
						{
							label: 'Email',
							fieldtype: 'Data',
							fieldname: 'email'
						},
						{
							label: 'Mật khẩu',
							fieldtype: 'Password',
							fieldname: 'password'
						}
					]"
					v-model="frappeSite"
				/>
				<div class="mt-2">
					<ErrorMessage
						:message="$resources.getBackupLinks.error"
						v-if="!$resources.getBackupLinks.data"
					/>
					<div
						class="text-base font-semibold text-green-500"
						v-if="$resources.getBackupLinks.data"
					>
						Tìm thấy bản sao lưu mới nhất tại
						{{ fetchedBackupFiles[0].timestamp }}
					</div>
					<div class="mt-2 space-y-1" v-if="$resources.getBackupLinks.data">
						<div v-for="file in fetchedBackupFiles" :key="file.remote_file">
							<div class="text-base font-medium text-gray-700">
								{{ file.file_name }}
							</div>
						</div>
					</div>
				</div>
				<Button
					v-if="!$resources.getBackupLinks.data"
					class="mt-2"
					@click="$resources.getBackupLinks.submit()"
					:loading="$resources.getBackupLinks.loading"
				>
					Nhận Bản sao lưu
				</Button>
			</div>
		</div>

		<div class="mt-3" v-if="['backup', 'siteUrl'].includes(restoreFrom)">
			<!-- Skip Failing Checkbox -->
			<input
				id="skip-failing"
				type="checkbox"
				class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
				v-model="wantToSkipFailingPatches"
			/>
			<label for="skip-failing" class="ml-2 text-sm text-gray-900">
				Bỏ qua các bản vá thất bại (nếu có bất kỳ bản vá nào thất bại)
			</label>
		</div>
	</div>
</template>
<script>
import FileUploader from '@/components/FileUploader.vue';
import Form from '@/components/Form.vue';
import BackupFilesUploader from '@/components/BackupFilesUploader.vue';
import { DateTime } from 'luxon';

export default {
	name: 'Restore',
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
