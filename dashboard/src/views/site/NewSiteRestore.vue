<template>
	<div>
		<label class="text-lg font-semibold">
			{{ $t('NewSiteRestore_content_1') }}
		</label>
		<p class="text-base text-gray-700">
			{{ $t('NewSiteRestore_content_2') }}
		</p>
		<div class="mt-4 grid grid-cols-2 gap-6">
			<Button
				v-for="tab in [
					{ name: $t('Upload_Backups'), key: 'backup' },
					{ name: $t('Migrate_from_Site_URL'), key: 'siteUrl' }
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
					<li>{{ $t('NewSiteRestore_content_3') }}</li>
					<li>{{ $t('NewSiteRestore_content_4') }}</li>
					<li>
						{{ $t('NewSiteRestore_content_5') }}
					</li>
					<li>
						{{ $t('NewSiteRestore_content_6') }}
					</li>
				</ol>
			</div>
			<Alert class="mt-5 w-full" v-if="manualMigration">
				{{ $t('NewSiteRestore_content_7') }}
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
						<li>{{ $t('NewSiteRestore_content_3') }}</li>
						<li>{{ $t('NewSiteRestore_content_8') }}</li>
						<li>
							{{ $t('NewSiteRestore_content_9') }}
						</li>
						<li>{{ $t('NewSiteRestore_content_10') }}</li>
					</ol>
				</div>
				<Alert
					class="mt-5 w-full"
					v-if="
						errorContains('Your site exceeds the limits for this operation')
					"
				>
					{{ $t('NewSiteRestore_content_7') }}
				</Alert>
				<Form
					class="mt-6"
					:fields="[
						{
							label: $t('Site_URL'),
							fieldtype: 'Data',
							fieldname: 'url'
						},
						{
							label: 'Email',
							fieldtype: 'Data',
							fieldname: 'email'
						},
						{
							label: $t('Password'),
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
						{{ $t('NewSiteRestore_content_11') }}
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
					{{ $t('Get_Backups') }}
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
				{{ $t('SiteDatabaseRestore_content_8') }}
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
						return this.$t('NewSiteRestore_content_12');
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
