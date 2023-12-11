<template>
	<div>
		<div class="mt-2 space-y-2">
			<FileUploader
				v-for="file in files"
				:fileTypes="file.ext"
				:key="file.type"
				:type="file.type"
				@success="onFileUpload(file, $event)"
				:fileValidator="f => databaseBackupChecker(f, file.type)"
				:s3="true"
			>
				<template
					v-slot="{
						file: fileObj,
						uploading,
						progress,
						error,
						success,
						openFileSelector
					}"
				>
					<ListItem
						class="border-b"
						:title="fileObj ? fileObj.name : file.title"
					>
						<template #subtitle>
							<span
								class="text-base"
								:class="error ? 'text-red-500' : 'text-gray-600'"
							>
								{{
									uploading
										? `Đang tải lên ${progress}%`
										: success
										? formatBytes(fileObj.size)
										: error
										? error
										: file.description
								}}
							</span>
						</template>
						<template #actions>
							<Button
								:loading="uploading"
								loadingText="Đang tải lên..."
								@click="openFileSelector()"
								v-if="!success"
							>
								Tải lên
							</Button>
							<GreenCheckIcon class="w-5" v-if="success" />
						</template>
					</ListItem>
				</template>
			</FileUploader>
		</div>
	</div>
</template>
<script>
import FileUploader from './FileUploader.vue';

export default {
	name: 'BackupFilesUploader',
	components: { FileUploader },
	emits: ['update:backupFiles'],
	props: ['backupFiles'],
	data() {
		return {
			files: [
				{
					icon: '<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M5.33325 9.33333V22.6667C5.33325 25.6133 10.1093 28 15.9999 28C21.8906 28 26.6666 25.6133 26.6666 22.6667V9.33333M5.33325 9.33333C5.33325 12.28 10.1093 14.6667 15.9999 14.6667C21.8906 14.6667 26.6666 12.28 26.6666 9.33333M5.33325 9.33333C5.33325 6.38667 10.1093 4 15.9999 4C21.8906 4 26.6666 6.38667 26.6666 9.33333M26.6666 16C26.6666 18.9467 21.8906 21.3333 15.9999 21.3333C10.1093 21.3333 5.33325 18.9467 5.33325 16" stroke="#1F272E" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
					type: 'database',
					ext: 'application/x-gzip,application/sql,.sql',
					title: 'Database Backup',
					description:
						'Tải lên tệp sao lưu database. Thông thường, tên tệp kết thúc bằng .sql.gz hoặc .sql',
					file: null
				},
				{
					icon: '<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M9.39111 6.3913H26.3476V22.2174C26.3476 25.9478 23.2955 29 19.565 29H9.39111V6.3913Z" stroke="#1F272E" stroke-width="1.5" stroke-miterlimit="10"/><path d="M13.9131 13.1739H21.8261" stroke="#1F272E" stroke-width="1.5" stroke-miterlimit="10"/><path d="M13.9131 17.6957H21.8261" stroke="#1F272E" stroke-width="1.5" stroke-miterlimit="10"/><path d="M13.9131 22.2173H19.8479" stroke="#1F272E" stroke-width="1.5" stroke-miterlimit="10"/><path d="M22.9565 6.3913V3H6V25.6087H9.3913" stroke="#1F272E" stroke-width="1.5" stroke-miterlimit="10"/></svg>',
					type: 'public',
					ext: 'application/x-tar',
					title: 'Public Files',
					description:
						'Tải lên tệp sao lưu các tệp public. Thông thường, tên tệp kết thúc bằng -files.tar',
					file: null
				},
				{
					icon: '<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M8.39111 6.3913H25.3476V22.2174C25.3476 25.9478 22.2955 29 18.565 29H8.39111V6.3913Z" stroke="#1F272E" stroke-width="1.5" stroke-miterlimit="10"/><path d="M21.9565 6.3913V3H5V25.6087H8.3913" stroke="#1F272E" stroke-width="1.5" stroke-miterlimit="10"/></svg>',
					type: 'private',
					ext: 'application/x-tar',
					title: 'Private Files',
					description:
						'Tải lên tệp sao lưu các tệp private. Thông thường, tên tệp kết thúc bằng -private-files.tar',
					file: null
				},
				{
					icon: '<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M8.39111 6.3913H25.3476V22.2174C25.3476 25.9478 22.2955 29 18.565 29H8.39111V6.3913Z" stroke="#1F272E" stroke-width="1.5" stroke-miterlimit="10"/><path d="M21.9565 6.3913V3H5V25.6087H8.3913" stroke="#1F272E" stroke-width="1.5" stroke-miterlimit="10"/></svg>',
					type: 'config',
					ext: 'application/json',
					title: 'Site Config',
					description:
						'Tải lên tệp sao lưu các tệp site config. Thông thường, tên tệp kết thúc bằng -site_config_backup.json',
					file: null
				}
			]
		};
	},
	methods: {
		onFileUpload(file, data) {
			let backupFiles = Object.assign({}, this.backupFiles);
			backupFiles[file.type] = data;
			this.$emit('update:backupFiles', backupFiles);
		},
		async databaseBackupChecker(file, type) {
			if (type === 'database') {
				if (!file.name.endsWith('.sql.gz') && !file.name.endsWith('.sql')) {
					throw new Error(
						'Tệp sao lưu database nên kết thúc bằng tên "database.sql.gz" hoặc "database.sql"'
					);
				}
				if (
					![
						'application/x-gzip',
						'application/gzip',
						'application/sql'
					].includes(file.type)
				) {
					throw new Error('Tệp sao lưu database không hợp lệ');
				}
			}
			if (['public', 'private'].includes(type)) {
				if (file.type != 'application/x-tar') {
					throw new Error(`Tệp sao lưu ${type} không hợp lệ`);
				}
			}
			if (type === 'config') {
				if (file.type != 'application/json') {
					throw new Error(`Tệp sao lưu ${type} không hợp lệ`);
				}
			}
		}
	}
};
</script>
