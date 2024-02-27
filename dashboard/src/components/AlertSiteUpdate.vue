<template>
	<Alert :title="$t('Update_Available')" v-if="show">
		<span>
			{{ $t('AlertSiteUpdate_content_1') }}
		</span>
		<template #actions>
			<Tooltip
				:text="!permissions.update ? $t('SiteOverviewPlan_content_3') : ''"
			>
				<Button
					:disabled="!permissions.update"
					variant="solid"
					@click="showUpdatesDialog = true"
				>
					{{ $t('Show_updates') }}
				</Button>
			</Tooltip>
		</template>
		<Dialog
			:options="{
				title: $t('Updates_available'),
				actions: [
					{
						label: $t('Update_Now'),
						variant: 'solid',
						onClick: () => $resources.scheduleUpdate.fetch()
					}
				]
			}"
			v-model="showUpdatesDialog"
		>
			<template v-slot:body-content>
				<SiteAppUpdates :apps="updateAvailableApps" />
				<div class="mt-4" v-if="updateAvailableApps.length">
					<!-- Skip Failing Checkbox -->
					<input
						id="skip-failing"
						type="checkbox"
						class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
						v-model="wantToSkipFailingPatches"
					/>
					<label for="skip-failing" class="ml-1 text-sm text-gray-900">
						{{ $t('AlertSiteUpdate_content_2') }}
					</label>
				</div>

				<div class="mt-2" v-if="skip_backups">
					<!-- Skip Site Backup -->
					<input
						id="skip-backup"
						type="checkbox"
						class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
						v-model="wantToSkipBackups"
					/>
					<label for="skip-backup" class="ml-1 text-sm text-gray-900">
						{{ $t('AlertSiteUpdate_content_3') }}
					</label>
					<div class="mt-1 text-sm text-red-600" v-if="wantToSkipBackups">
						{{ $t('AlertSiteUpdate_content_4') }}
					</div>
				</div>
				<ErrorMessage class="mt-1" :message="$resources.scheduleUpdate.error" />
			</template>
		</Dialog>
	</Alert>
</template>
<script>
import SiteAppUpdates from './SiteAppUpdates.vue';
import { notify } from '@/utils/toast';
export default {
	name: 'AlertSiteUpdate',
	props: ['site'],
	components: {
		SiteAppUpdates
	},
	data() {
		return {
			showUpdatesDialog: false,
			wantToSkipFailingPatches: false,
			wantToSkipBackups: false
		};
	},
	resources: {
		updateInformation() {
			return {
				url: 'press.api.site.check_for_updates',
				params: {
					name: this.site?.name
				},
				auto: true
			};
		},
		lastMigrateFailed() {
			return {
				url: 'press.api.site.last_migrate_failed',
				params: {
					name: this.site?.name
				},
				auto: true
			};
		},
		scheduleUpdate() {
			return {
				url: 'press.api.site.update',
				params: {
					name: this.site?.name,
					skip_failing_patches: this.wantToSkipFailingPatches,
					skip_backups: this.wantToSkipBackups
				},
				onSuccess() {
					this.showUpdatesDialog = false;
					notify({
						title: this.$t('AlertSiteUpdate_content_5'),
						icon: 'check',
						color: 'green'
					});
				}
			};
		}
	},
	computed: {
		permissions() {
			return {
				update: this.$account.hasPermission(
					this.site.name,
					'press.api.site.update'
				)
			};
		},
		show() {
			if (this.updateInformation) {
				return (
					this.site.setup_wizard_complete &&
					this.updateInformation.update_available &&
					['Active', 'Inactive', 'Suspended', 'Broken'].includes(
						this.site.status
					)
				);
			}
		},
		updateInformation() {
			return this.$resources.updateInformation.data;
		},
		updateAvailableApps() {
			const installedApps = this.updateInformation.installed_apps;
			const updateAvailableApps = this.updateInformation.apps;

			return updateAvailableApps.filter(app =>
				installedApps.find(installedApp => installedApp.app === app.app)
			);
		},
		lastMigrateFailed() {
			return this.$resources.lastMigrateFailed.data;
		},
		skip_backups() {
			return this.$account.team?.skip_backups;
		}
	}
};
</script>
