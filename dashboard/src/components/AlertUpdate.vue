<template>
	<Alert :title="alertTitle" v-if="show">
		<span v-if="deployInformation.deploy_in_progress">
			{{ $t('AlertUpdate_content_1') }}
		</span>
		<span v-else-if="bench.status == 'Active'">
			{{ $t('AlertUpdate_content_2') }}
		</span>
		<span v-else>
			{{ $t('AlertUpdate_content_3') }}
		</span>
		<template #actions>
			<Button
				v-if="deployInformation.deploy_in_progress"
				variant="solid"
				:route="`/benches/${bench.name}/deploys/${deployInformation.last_deploy.name}`"
				>{{ $t('View_Progress') }}</Button
			>
			<Button
				v-else
				variant="solid"
				@click="
					() => {
						showDeployDialog = true;
						step = 'Apps';
					}
				"
			>
				{{ $t('Show_Updates') }}
			</Button>
		</template>

		<Dialog
			:options="{
				title:
					step == 'Apps'
						? $t('AlertUpdate_content_4')
						: $t('AlertUpdate_content_5')
			}"
			v-model="showDeployDialog"
		>
			<template v-slot:body-content>
				<BenchAppUpdates
					v-if="step == 'Apps'"
					:apps="deployInformation.apps"
					v-model:selectedApps="selectedApps"
					:removedApps="deployInformation.removed_apps"
				/>
				<BenchSiteUpdates
					class="p-1"
					v-if="step == 'Sites'"
					:sites="deployInformation.sites"
					v-model:selectedSites="selectedSites"
				/>
				<ErrorMessage class="mt-2" :message="errorMessage" />
			</template>
			<template v-slot:actions>
				<Button v-if="step == 'Sites'" class="w-full" @click="step = 'Apps'">
					{{ $t('Back') }}
				</Button>
				<Button
					v-if="step == 'Sites'"
					variant="solid"
					class="mt-2 w-full"
					@click="$resources.deploy.submit()"
					:loading="$resources.deploy.loading"
				>
					{{ selectedSites.length > 0 ? $t('Update') : $t('Skip_and_Deploy') }}
				</Button>
				<Button v-else variant="solid" class="w-full" @click="step = 'Sites'">
					{{ $t('Next') }}
				</Button>
			</template>
		</Dialog>
	</Alert>
</template>
<script>
import BenchAppUpdates from './BenchAppUpdates.vue';
import BenchSiteUpdates from './BenchSiteUpdates.vue';
import SwitchTeamDialog from './SwitchTeamDialog.vue';
import { notify } from '@/utils/toast';

export default {
	name: 'AlertBenchUpdate',
	props: ['bench'],
	components: {
		BenchAppUpdates,
		BenchSiteUpdates,
		SwitchTeamDialog
	},
	data() {
		return {
			showDeployDialog: false,
			showTeamSwitcher: false,
			selectedApps: [],
			selectedSites: [],
			step: 'Apps'
		};
	},
	resources: {
		deployInformation() {
			return {
				url: 'press.api.bench.deploy_information',
				params: {
					name: this.bench?.name
				},
				auto: true
			};
		},
		deploy() {
			return {
				url: 'press.api.bench.deploy_and_update',
				params: {
					name: this.bench?.name,
					apps: this.selectedApps,
					sites: this.selectedSites,
					lang: this.$i18n.locale
				},
				validate() {
					if (
						this.selectedApps.length === 0 &&
						this.deployInformation.removed_apps.length === 0
					) {
						return this.$t('AlertUpdate_content_6');
					}
				},
				onSuccess(new_candidate_name) {
					this.showDeployDialog = false;
					this.$resources.deployInformation.setData({
						...this.$resources.deployInformation.data,
						deploy_in_progress: true,
						last_deploy: { name: new_candidate_name, status: 'Running' }
					});
					notify({
						title: this.$t('AlertUpdate_content_7'),
						icon: 'check',
						color: 'green'
					});
				}
			};
		}
	},
	computed: {
		show() {
			if (this.deployInformation) {
				return (
					this.deployInformation.update_available &&
					['Awaiting Deploy', 'Active'].includes(this.bench.status)
				);
			}
		},
		errorMessage() {
			return (
				this.$resources.deploy.error ||
				(this.bench.team !== $account.team.name
					? this.$t('AlertUpdate_content_8')
					: '')
			);
		},
		deployInformation() {
			return this.$resources.deployInformation.data;
		},
		alertTitle() {
			if (this.deployInformation && this.deployInformation.deploy_in_progress) {
				return this.$t('Deploy_in_Progress');
			}
			return this.bench.status == 'Active' ? 'Update Available' : 'Deploy';
		}
	}
};
</script>
