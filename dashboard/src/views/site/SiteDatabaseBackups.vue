<template>
	<Card
		v-if="site"
		title="Sao lưu"
		subtitle="Sao lưu được kích hoạt và được lên lịch chạy sáu giờ một lần."
	>
		<template #actions>
			<Button
				v-if="site?.status === 'Active' || site?.status === 'Suspended'"
				@click="$resources.scheduleBackup.fetch()"
				:loading="$resources.scheduleBackup.loading"
				class="py-5"
			>
				Tạo bản sao lưu
			</Button>
			<Dialog
				:options="{ title: 'Khôi phục bản sao lưu trên trang web khác' }"
				v-model="showRestoreOnAnotherSiteDialog"
			>
				<template v-slot:body-content>
					<p class="text-base">Chọn trang web mà bạn muốn khôi phục sao lưu</p>
					<SiteRestoreSelector
						:sites="
							$resources.sites.data.filter(site => site.name !== this.site.name)
						"
						:selectedSite="selectedSite"
						@update:selectedSite="value => (selectedSite = value)"
					/>
					<div v-if="selectedSite" class="mt-4">
						<p class="text-base">
							Bạn có chắc chắn muốn khôi phục sao lưu từ
							<b>{{ site?.name }}</b> được thực hiện vào
							<b>{{ formatDate(backupToRestore.creation) }}</b> đến trang web
							của bạn <b>{{ selectedSite.name }}</b
							>?
						</p>
					</div>
					<ErrorMessage
						class="mt-2"
						:message="restoreOnAnotherSiteErrorMessage"
					/>
				</template>
				<template #actions>
					<Button
						variant="solid"
						class="w-full"
						v-if="selectedSite"
						@click="restoreOffsiteBackupOnAnotherSite(backupToRestore)"
					>
						Khôi phục
					</Button>
				</template>
			</Dialog>
		</template>
		<div class="divide-y" v-if="backups.data.length">
			<div
				class="flex items-center justify-between py-2"
				v-for="backup in backups.data"
				:key="backup.database_url"
			>
				<div class="text-base">
					<span
						v-if="backup.status === 'Success'"
						class="flex items-center justify-between"
					>
						<span>
							Sao lưu vào <FormatDate>{{ backup.creation }}</FormatDate>
						</span>
					</span>
					<span v-else> Thực hiện sao lưu... </span>
				</div>
				<div class="flex items-center space-x-2">
					<Badge v-if="backup.offsite" label="Offsite" theme="green" />
					<Dropdown :options="dropdownItems(backup)">
						<template v-slot="{ open }">
							<Tooltip
								:text="
									!permissions.backups
										? `Bạn không có đủ quyền để thực hiện hành động này`
										: 'Tải xuống bản sao lưu'
								"
							>
								<Button
									icon="more-horizontal"
									:disabled="!permissions.backups"
								/>
							</Tooltip>
						</template>
					</Dropdown>
				</div>
			</div>
		</div>
		<div class="mt-2 text-base text-gray-600" v-else>
			<Button
				v-if="$resources.backups.loading"
				:loading="true"
				loading-text="Đang tải"
			/>
			<span v-else> Không tìm thấy bản sao lưu nào </span>
		</div>
	</Card>
</template>
<script>
import SiteRestoreSelector from '@/components/SiteRestoreSelector.vue';
import { notify } from '@/utils/toast';

export default {
	name: 'SiteDatabaseBackups',
	props: ['site'],
	components: {
		SiteRestoreSelector
	},
	data() {
		return {
			isRestorePending: false,
			backupToRestore: null,
			showRestoreOnAnotherSiteDialog: false,
			restoreOnAnotherSiteErrorMessage: null,
			selectedSite: null
		};
	},
	resources: {
		sites() {
			return {
				url: 'press.api.site.all',
				initialData: [],
				auto: true
			};
		},
		backups() {
			return {
				url: 'press.api.site.backups',
				params: {
					name: this.site?.name
				},
				initialData: [],
				auto: true
			};
		},
		scheduleBackup() {
			return {
				url: 'press.api.site.backup',
				params: {
					name: this.site?.name,
					with_files: true
				},
				onSuccess: () => {
					this.$resources.backups.reload();
				},
				onError: err => {
					notify({
						title: 'Không thể tạo sao lưu',
						message: err.messages.join('\n'),
						color: 'red',
						icon: err.messages[0].includes('suspension')
							? 'info'
							: 'alert-triangle'
					});
				}
			};
		}
	},
	mounted() {
		this.$socket.on('agent_job_update', data => {
			if (data.site === this.site.name && data.name === 'Backup Site') {
				if (data.status === 'Success') {
					this.$resources.backups.reload();
				}
			}
		});
	},
	computed: {
		backups() {
			return this.$resources.backups;
		},
		permissions() {
			return {
				backups: this.$account.hasPermission(
					this.site.name,
					'press.api.site.get_backup_link'
				)
			};
		}
	},
	methods: {
		dropdownItems(backup) {
			return [
				{
					group: 'Tải xuống',
					items: [
						{
							label: `Database (${this.formatBytes(
								backup.database_size || 0
							)})`,
							onClick: () => {
								this.downloadBackup(
									backup.name,
									'database',
									backup.database_url,
									backup.offsite
								);
							}
						},
						{
							label: `Public Files (${this.formatBytes(
								backup.public_size || 0
							)})`,
							condition: () => backup.public_file,
							onClick: () => {
								this.downloadBackup(
									backup.name,
									'public',
									backup.public_url,
									backup.offsite
								);
							}
						},
						{
							label: `Private Files (${this.formatBytes(
								backup.private_size || 0
							)})`,
							condition: () => backup.private_file,
							onClick: () => {
								this.downloadBackup(
									backup.name,
									'private',
									backup.private_url,
									backup.offsite
								);
							}
						},
						{
							label: `Cấu hình trang web (${this.formatBytes(
								backup.config_file_size || 0
							)})`,
							condition: () => backup.config_file_size,
							onClick: () => {
								this.downloadBackup(
									backup.name,
									'config',
									backup.config_file_url,
									backup.offsite
								);
							}
						}
					]
				},
				{
					group: 'Khôi phục',
					condition: () => backup.offsite,
					items: [
						{
							label: 'Khôi phục sao lưu',
							onClick: () => {
								this.$confirm({
									title: 'Khôi phục sao lưu',
									// prettier-ignore
									message: `Bạn có chắc chắn muốn khôi phục trang web của bạn đến <b>${this.formatDate(backup.creation)}</b> không?`,
									actionLabel: 'Khôi phục',
									action: closeDialog => {
										closeDialog();
										this.restoreOffsiteBackup(backup);
									}
								});
							}
						},
						{
							label: 'Khôi phục sao lưu trên trang web khác',
							onClick: () => {
								this.showRestoreOnAnotherSiteDialog = true;
								this.backupToRestore = backup;
							}
						}
					]
				}
			].filter(d => (d.condition ? d.condition() : true));
		},
		async downloadBackup(name, file, database_url, offsite) {
			let link = offsite
				? await this.$call('press.api.site.get_backup_link', {
						name: this.site.name,
						backup: name,
						file: file
				  })
				: database_url;
			window.open(link);
		},
		async restoreOffsiteBackup(backup) {
			this.isRestorePending = true;
			this.$call('press.api.site.restore', {
				name: this.site.name,
				files: {
					database: backup.remote_database_file,
					public: backup.remote_public_file,
					private: backup.remote_private_file
				}
			}).then(() => {
				this.isRestorePending = false;
				this.$router.push(`/sites/${this.site.name}/jobs`);
				setTimeout(() => {
					window.location.reload();
				}, 1000);
			});
		},
		async restoreOffsiteBackupOnAnotherSite(backup) {
			this.isRestorePending = true;
			this.$call('press.api.site.restore', {
				name: this.selectedSite.name,
				files: {
					database: backup.remote_database_file,
					public: backup.remote_public_file,
					private: backup.remote_private_file
				}
			})
				.then(() => {
					this.isRestorePending = false;
					this.showRestoreOnAnotherSiteDialog = false;
					this.$router.push(`/sites/${this.selectedSite.name}/jobs`);
					setTimeout(() => {
						window.location.reload();
					}, 1000);
				})
				.catch(error => {
					this.restoreOnAnotherSiteErrorMessage = error;
				});
		}
	}
};
</script>
