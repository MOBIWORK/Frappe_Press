<template>
	<Card
		v-if="site"
		:title="$t('Backups')"
		:subtitle="$t('SiteDatabaseBackups_content_1')"
	>
		<template #actions>
			<Button
				v-if="site?.status === 'Active' || site?.status === 'Suspended'"
				@click="$resources.scheduleBackup.fetch()"
				:loading="$resources.scheduleBackup.loading"
			>
				{{ $t('Create_Backup') }}
			</Button>
			<Dialog
				:options="{ title: $t('Restore_Backup_on_Another_Site') }"
				v-model="showRestoreOnAnotherSiteDialog"
			>
				<template v-slot:body-content>
					<p class="text-base">{{ $t('SiteDatabaseBackups_content_2') }}</p>
					<SiteRestoreSelector
						:sites="
							$resources.sites.data.filter(site => site.name !== this.site.name)
						"
						:selectedSite="selectedSite"
						@update:selectedSite="value => (selectedSite = value)"
					/>
					<div v-if="selectedSite" class="mt-4">
						<p class="text-base">
							{{ $t('SiteDatabaseBackups_content_3') }}
							<b>{{ site?.name }}</b> {{ $t('taken_on') }}
							<b>{{ formatDate(backupToRestore.creation) }}</b>
							{{ $t('to_your_site') }} <b>{{ selectedSite.name }}</b
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
						{{ $t('Restore') }}
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
							{{ $t('Backup_on') }}
							<FormatDate>{{ backup.creation }}</FormatDate>
						</span>
					</span>
					<span v-else> {{ $t('Performing_Backup') }}... </span>
				</div>
				<div class="flex items-center space-x-2">
					<Badge v-if="backup.offsite" label="Offsite" theme="green" />
					<Dropdown :options="dropdownItems(backup)">
						<template v-slot="{ open }">
							<Tooltip
								:text="
									!permissions.backups
										? $t('SiteDatabaseBackups_content_4')
										: $t('Download_Backups')
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
				:loading-text="$t('loading')"
			/>
			<span v-else> {{ $t('No_backups_found') }} </span>
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
					with_files: true,
					lang: this.$i18n.locale
				},
				onSuccess: () => {
					this.$resources.backups.reload();
				},
				onError: err => {
					notify({
						title: this.$t('Couldnt_create_backup'),
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
					group: this.$t('download'),
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
							label: `${this.$t('Site_Config')} (${this.formatBytes(
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
					group: this.$t('Restore'),
					condition: () => backup.offsite,
					items: [
						{
							label: this.$t('Restore_Backup'),
							onClick: () => {
								this.$confirm({
									title: this.$t('Restore_Backup'),
									// prettier-ignore
									message: `${this.$t('SiteDatabaseBackups_content_5')} <b>${this.formatDate(backup.creation)}</b> ${this.$t('SiteDatabaseBackups_content_6')}?`,
									actionLabel: this.$t('Restore'),
									action: closeDialog => {
										closeDialog();
										this.restoreOffsiteBackup(backup);
									}
								});
							}
						},
						{
							label: this.$t('Restore_Backup_on_Another_Site'),
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
