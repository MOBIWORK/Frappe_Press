<template>
	<Card
		v-if="site"
		:title="$t('SiteDatabaseRestore_content_1')"
		:subtitle="
			site.status === 'Suspended' ? $t('SiteDatabaseRestore_content_2') : ''
		"
	>
		<div class="divide-y">
			<div class="flex flex-wrap items-center justify-between py-3">
				<div class="mb-2">
					<h3 class="text-lg">{{ $t('Restore') }}</h3>
					<p class="mt-1 text-base text-gray-600">
						{{ $t('SiteDatabaseRestore_content_3') }}
					</p>
				</div>
				<Tooltip
					:text="
						!permissions.restore
							? $t('SiteOverviewPlan_content_3')
							: $t('Restore_Database')
					"
				>
					<Button
						theme="red"
						:disabled="site.status === 'Suspended' || !permissions.restore"
						@click="showRestoreDialog = true"
					>
						{{ $t('Restore') }}
					</Button>
				</Tooltip>
			</div>
			<div class="flex flex-wrap items-center justify-between py-3">
				<div class="mb-2">
					<h3 class="text-lg">Migrate</h3>
					<p class="mt-1 text-base text-gray-600">
						{{ $t('SiteDatabaseRestore_content_4') }}
					</p>
				</div>
				<Tooltip
					:text="
						!permissions.migrate
							? $t('SiteOverviewPlan_content_3')
							: 'Migrate Database'
					"
				>
					<Button
						:disabled="site.status === 'Suspended' || !permissions.migrate"
						@click="showMigrateDialog = true"
					>
						Migrate
					</Button>
				</Tooltip>
			</div>
			<div class="flex flex-wrap items-center justify-between py-3">
				<div class="mb-2">
					<h3 class="text-lg">{{ $t('Reset') }}</h3>
					<p class="mt-1 text-base text-gray-600">
						{{ $t('SiteDatabaseRestore_content_5') }}
					</p>
				</div>
				<Tooltip
					:text="
						!permissions.reset
							? $t('SiteOverviewPlan_content_3')
							: $t('Reset_Database')
					"
				>
					<Button
						theme="red"
						:disabled="site.status === 'Suspended' || !permissions.reset"
						@click="showResetDialog = true"
					>
						{{ $t('Reset') }}
					</Button>
				</Tooltip>
			</div>
			<div class="flex flex-wrap items-center justify-between py-3">
				<div class="mb-2">
					<h3 class="text-lg">{{ $t('Clear_Cache') }}</h3>
					<p class="mt-1 text-base text-gray-600">
						{{ $t('SiteDatabaseRestore_content_6') }}
					</p>
				</div>
				<Button
					:disabled="site.status === 'Suspended'"
					@click="confirmClearCache"
				>
					{{ $t('Clear') }}
				</Button>
			</div>
			<div
				class="flex flex-wrap items-center justify-between py-3"
				v-if="$account.team.database_access_enabled"
			>
				<div class="mb-2">
					<h3 class="text-lg">{{ $t('Access') }}</h3>
					<p class="mt-1 text-base text-gray-600">
						{{ $t('Connect_to_your_database') }}
					</p>
				</div>
				<Tooltip
					:text="
						!permissions.access
							? $t('SiteOverviewPlan_content_3')
							: $t('Access_Database')
					"
				>
					<Button
						:disabled="!permissions.access"
						icon-left="database"
						@click="showDatabaseAccessDialog = true"
					>
						{{ $t('Access') }}
					</Button>
				</Tooltip>
			</div>
		</div>

		<Dialog
			:options="{
				title: 'Migrate Database',
				actions: [
					{
						label: 'Migrate',
						variant: 'solid',
						theme: 'red',
						loading: $resources.migrateDatabase.loading,
						onClick: migrateDatabase
					}
				]
			}"
			v-model="showMigrateDialog"
			@close="
				() => {
					$resources.migrateDatabase.reset();
					wantToSkipFailingPatches = false;
				}
			"
		>
			<template v-slot:body-content>
				<p class="text-base">
					{{ $t('SiteDatabaseRestore_content_13') }} <b>bench migrate</b>
					{{ $t('SiteDatabaseRestore_content_7') }}
				</p>
				<ErrorMessage
					class="mt-2"
					:message="$resources.migrateDatabase.error"
				/>
				<div class="mt-2">
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
			</template>
		</Dialog>

		<Dialog
			:options="{
				title: $t('Restore'),
				actions: [
					{
						label: $t('Restore'),
						variant: 'solid',
						loading: $resources.restoreBackup.loading,
						onClick: () => $resources.restoreBackup.submit()
					}
				]
			}"
			v-model="showRestoreDialog"
		>
			<template v-slot:body-content>
				<div class="space-y-4">
					<p class="text-base">
						{{ $t('SiteDatabaseRestore_content_9') }}
					</p>
					<BackupFilesUploader v-model:backupFiles="selectedFiles" />
				</div>
				<div class="mt-3">
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
				<ErrorMessage class="mt-2" :message="$resources.restoreBackup.error" />
			</template>
		</Dialog>

		<DatabaseAccessDialog
			v-if="showDatabaseAccessDialog"
			:site="site.name"
			v-model:show="showDatabaseAccessDialog"
		/>

		<Dialog
			:options="{
				title: $t('Restore_Database'),
				actions: [
					{
						label: $t('Restore'),
						variant: 'solid',
						theme: 'red',
						loading: $resources.resetDatabase.loading,
						onClick: () => $resources.resetDatabase.submit()
					}
				]
			}"
			v-model="showResetDialog"
		>
			<template v-slot:body-content>
				<p class="text-base">
					{{ $t('SiteDatabaseRestore_content_10') }}
				</p>
				<p class="mt-4 text-base">
					{{ $t('Please_type') }}
					<span class="font-semibold">{{ site.name }}</span>
					{{ $t('to_confirm') }}.
				</p>
				<FormControl class="mt-4 w-full" v-model="confirmSiteName" />
				<ErrorMessage class="mt-2" :message="$resources.resetDatabase.error" />
			</template>
		</Dialog>
	</Card>
</template>

<script>
import FileUploader from '@/components/FileUploader.vue';
import BackupFilesUploader from '@/components/BackupFilesUploader.vue';
import DatabaseAccessDialog from './DatabaseAccessDialog.vue';

export default {
	name: 'SiteDatabase',
	components: {
		FileUploader,
		BackupFilesUploader,
		DatabaseAccessDialog
	},
	props: ['site'],
	data() {
		return {
			confirmSiteName: '',
			showResetDialog: false,
			showMigrateDialog: false,
			showRestoreDialog: false,
			showDatabaseAccessDialog: false,
			selectedFiles: {
				database: null,
				public: null,
				private: null
			},
			wantToSkipFailingPatches: false
		};
	},
	resources: {
		restoreBackup() {
			return {
				url: 'press.api.site.restore',
				params: {
					name: this.site?.name,
					files: this.selectedFiles,
					skip_failing_patches: this.wantToSkipFailingPatches
				},
				validate() {
					if (!this.filesUploaded) {
						return this.$t('SiteDatabaseRestore_content_11');
					}
				},
				onSuccess(jobName) {
					this.selectedFiles = {};
					this.$router.push({ name: 'SiteJobs', params: { jobName } });
					setTimeout(() => {
						window.location.reload();
					}, 1000);
				}
			};
		},
		resetDatabase() {
			return {
				url: 'press.api.site.reinstall',
				params: {
					name: this.site?.name
				},
				validate() {
					if (this.confirmSiteName !== this.site?.name) {
						return this.$t('Please_type_the_site_name_to_confirm');
					}
				},
				onSuccess(jobName) {
					this.$router.push({ name: 'SiteJobs', params: { jobName } });
					setTimeout(() => {
						window.location.reload();
					}, 1000);
				}
			};
		},
		migrateDatabase() {
			return {
				url: 'press.api.site.migrate',
				params: {
					name: this.site?.name
				},
				onSuccess() {
					this.$router.push({
						name: 'SiteOverview',
						params: { site: this.site?.name }
					});
					setTimeout(() => {
						window.location.reload();
					}, 1000);
				}
			};
		},
		clearCache() {
			return {
				url: 'press.api.site.clear_cache',
				params: {
					name: this.site?.name
				},
				onSuccess() {
					this.$router.push({
						name: 'SiteOverview',
						params: { site: this.site?.name }
					});
					setTimeout(() => {
						window.location.reload();
					}, 1000);
				}
			};
		}
	},
	methods: {
		migrateDatabase() {
			this.$resources.migrateDatabase.submit({
				name: this.site.name,
				skip_failing_patches: this.wantToSkipFailingPatches
			});
		},
		confirmClearCache() {
			this.$confirm({
				title: this.$t('Clear_Cache'),
				message: `${this.$t(
					'SiteDatabaseRestore_content_13'
				)} <b>bench clear-cache</b> ${this.$t(
					'and'
				)} <b>bench clear-website-cache</b> ${this.$t(
					'SiteDatabaseRestore_content_12'
				)}`,
				actionLabel: this.$t('Clear_Cache'),
				actionColor: 'red',
				action: closeDialog => {
					this.$resources.clearCache.submit();
					closeDialog();
				}
			});
		}
	},
	computed: {
		permissions() {
			return {
				migrate: this.$account.hasPermission(
					this.site.name,
					'press.api.site.migrate'
				),
				restore: this.$account.hasPermission(
					this.site.name,
					'press.api.site.restore'
				),
				reset: this.$account.hasPermission(
					this.site.name,
					'press.api.site.reset'
				),
				access: this.$account.hasPermission(
					this.site.name,
					'press.api.site.enable_database_access'
				)
			};
		},
		filesUploaded() {
			return this.selectedFiles.database;
		}
	}
};
</script>
