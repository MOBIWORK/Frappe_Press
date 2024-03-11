<template>
	<Alert :title="alertTitle" v-if="show">
		<span v-if="deployInformation.deploy_in_progress">{{
			$t('AlertBenchUpdate_content_1')
		}}</span>
		<span v-else-if="bench.status == 'Active'">
			{{ $t('AlertBenchUpdate_content_2') }}
		</span>
		<span v-else>
			{{ $t('AlertBenchUpdate_content_3') }}
		</span>
		<template #actions>
			<Button
				v-if="deployInformation.deploy_in_progress"
				variant="solid"
				:route="`/benches/${bench.name}/deploys/${deployInformation.last_deploy.name}`"
				>{{ $t('View_Progress') }}</Button
			>
			<Tooltip
				v-else
				:text="!permissions.update ? $t('SiteOverviewPlan_content_3') : ''"
			>
				<Button
					variant="solid"
					:disabled="!permissions.update"
					@click="showDeployDialog = true"
				>
					{{ $t('Show_Updates') }}
				</Button>
			</Tooltip>
		</template>

		<Dialog
			:options="{ title: $t('AlertBenchUpdate_content_4') }"
			v-model="showDeployDialog"
		>
			<template v-slot:body-content>
				<BenchAppUpdates
					:apps="deployInformation.apps"
					v-model:selectedApps="selectedApps"
					:removedApps="deployInformation.removed_apps"
				/>
				<ErrorMessage class="mt-2" :message="errorMessage" />
			</template>
			<template v-slot:actions>
				<Button
					class="w-full"
					variant="solid"
					@click="$resources.deploy.submit()"
					:loading="$resources.deploy.loading"
					v-if="this.bench.team === $account.team.name"
				>
					{{ $t('Deploy') }}
				</Button>
				<Button
					class="w-full"
					variant="solid"
					@click="showTeamSwitcher = true"
					v-else
				>
					{{ $t('switch_team') }}
				</Button>
				<SwitchTeamDialog v-model="showTeamSwitcher" />
			</template>
		</Dialog>
	</Alert>
</template>
<script>
import BenchAppUpdates from './BenchAppUpdates.vue';
import SwitchTeamDialog from './SwitchTeamDialog.vue';
export default {
	name: 'AlertBenchUpdate',
	props: ['bench'],
	components: {
		BenchAppUpdates,
		SwitchTeamDialog
	},
	data() {
		return {
			showDeployDialog: false,
			showTeamSwitcher: false,
			selectedApps: []
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
				url: 'press.api.bench.deploy',
				params: {
					name: this.bench?.name,
					apps: this.selectedApps,
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
				onSuccess(candidate) {
					this.$router.push(`/benches/${this.bench.name}/deploys/${candidate}`);
					this.showDeployDialog = false;
				}
			};
		}
	},
	computed: {
		permissions() {
			return {
				update: this.$account.hasPermission(
					this.bench.name,
					'press.api.bench.deploy_and_update'
				)
			};
		},
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
