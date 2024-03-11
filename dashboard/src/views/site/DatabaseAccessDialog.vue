<template>
	<Dialog
		:options="{ title: $t('Access_Database') }"
		v-if="site"
		:modelValue="Boolean(site) && show"
		@close="dialogClosed"
	>
		<template v-slot:body-content>
			<LoadingText v-if="$resources.fetchDatabaseAccessInfo.loading" />

			<!-- Not available on current plan, upsell higher plans -->
			<div v-else-if="!databaseAccessInfo?.is_available_on_current_plan">
				<div>
					<p class="text-base">
						{{ $t('DatabaseAccessDialog_content_1') }}
					</p>

					<Button
						class="mt-4 w-full"
						variant="solid"
						@click="showChangePlanDialog = true"
						>{{ $t('Upgrade_Site_Plan') }}</Button
					>
				</div>

				<Dialog
					:options="{
						title: $t('Upgrade_Plan'),
						actions: [
							{
								label: $t('submit'),
								variant: 'solid',
								loading: $resources.changePlan.loading,
								onClick: () => $resources.changePlan.submit()
							}
						]
					}"
					v-model="showChangePlanDialog"
				>
					<template v-slot:body-content>
						<SitePlansTable
							class="mt-3"
							:plans="plans"
							v-model:selectedPlan="selectedPlan"
						/>
						<ErrorMessage class="mt-4" :message="$resources.changePlan.error" />
					</template>
				</Dialog>
			</div>

			<!-- Available on the current plan -->
			<div v-else>
				<div v-if="databaseAccessInfo">
					<div v-if="databaseAccessInfo.is_database_access_enabled">
						<div>
							<p class="mb-2 text-base font-semibold text-gray-700">
								{{ $t('DatabaseAccessDialog_content_2') }}
							</p>
							<p class="mb-2 text-base">
								{{ $t('DatabaseAccessDialog_content_3') }}
							</p>
							<p class="ml-1 font-mono text-sm">
								Host: {{ databaseAccessInfo.credentials.host }}
							</p>
							<p class="ml-1 font-mono text-sm">
								Port: {{ databaseAccessInfo.credentials.port }}
							</p>
							<p class="ml-1 font-mono text-sm">
								{{ $t('Database_Name') }}:
								{{ databaseAccessInfo.credentials.database }}
							</p>
							<p class="ml-1 font-mono text-sm">
								Username: {{ databaseAccessInfo.credentials.username }}
							</p>
							<p class="ml-1 font-mono text-sm">
								Password: {{ databaseAccessInfo.credentials.password }}
							</p>
						</div>
						<div class="pb-2 pt-5">
							<p class="mb-2 text-base font-semibold text-gray-700">
								{{ $t('Using_MariaDB_Client') }}
							</p>
							<p class="mb-2 text-base">
								<span>{{ $t('DatabaseAccessDialog_content_4') }}</span>
							</p>
							<ClickToCopyField class="ml-1" :textContent="dbAccessCommand" />
							<p class="mt-3 text-sm">
								{{ $t('DatabaseAccessDialog_content_5') }}
								<span class="font-mono">mariadb</span>
								{{ $t('DatabaseAccessDialog_content_6') }}
							</p>
						</div>
					</div>
					<div v-else>
						<p class="mb-2 text-sm">
							{{ $t('DatabaseAccessDialog_content_7') }}
						</p>
					</div>
				</div>

				<div class="mt-4">
					<div
						v-if="
							databaseAccessInfo &&
							!databaseAccessInfo.is_database_access_enabled
						"
						class="mb-2"
					>
						<!-- Enable Read-Write Access -->
						<input
							id="enable-read-write-access"
							type="checkbox"
							class="h-4 w-4 rounded border-gray-300 text-red-600 focus:ring-red-500"
							v-model="enableReadWriteAccess"
						/>
						<label
							for="enable-read-write-access"
							class="ml-1 text-sm text-gray-900"
						>
							{{ $t('DatabaseAccessDialog_content_8') }}
						</label>
						<ErrorMessage
							class="mt-2"
							:message="
								(enableReadWriteAccess &&
									$t('DatabaseAccessDialog_content_9')) ||
								error
							"
						/>
					</div>
					<Button
						v-if="
							databaseAccessInfo &&
							!databaseAccessInfo.is_database_access_enabled
						"
						@click="$resources.enableDatabaseAccess.submit()"
						:loading="
							$resources.enableDatabaseAccess.loading || pollingAgentJob
						"
						variant="solid"
						class="mt-2 w-full"
					>
						{{ $t('DatabaseAccessDialog_content_10') }}
						{{ enableReadWriteAccess ? 'Read-Write' : 'Read-Only' }}
						{{ $t('DatabaseAccessDialog_content_11') }}
					</Button>
					<Button
						v-if="
							databaseAccessInfo &&
							databaseAccessInfo.is_database_access_enabled
						"
						@click="$resources.disableDatabaseAccess.submit()"
						:loading="
							$resources.disableDatabaseAccess.loading || pollingAgentJob
						"
						class="w-full"
						>{{ $t('Disable_Access') }}</Button
					>
				</div>
			</div>
		</template>
	</Dialog>
</template>

<script>
import ClickToCopyField from '@/components/ClickToCopyField.vue';
import SitePlansTable from '@/components/SitePlansTable.vue';
import { notify } from '@/utils/toast';

export default {
	props: ['site', 'show'],
	data() {
		return {
			pollingAgentJob: false,
			showChangePlanDialog: false,
			selectedPlan: null,
			enableReadWriteAccess: false,
			error: null
		};
	},
	components: {
		ClickToCopyField,
		SitePlansTable
	},
	resources: {
		fetchDatabaseAccessInfo() {
			return {
				url: 'press.api.site.get_database_access_info',
				params: {
					name: this.site
				},
				auto: true
			};
		},
		enableDatabaseAccess() {
			return {
				url: 'press.api.site.enable_database_access',
				params: {
					name: this.site,
					mode: this.enableReadWriteAccess ? 'read_write' : 'read_only'
				},
				onSuccess(d) {
					this.pollDatabaseAccessJob(d);
				}
			};
		},
		disableDatabaseAccess() {
			return {
				url: 'press.api.site.disable_database_access',
				params: {
					name: this.site
				},
				onSuccess(d) {
					this.pollDatabaseAccessJob(d);
				}
			};
		},
		plans() {
			return {
				url: 'press.api.site.get_plans',
				params: {
					name: this.site
				},
				initialData: [],
				auto: true
			};
		},
		changePlan() {
			return {
				url: 'press.api.site.change_plan',
				params: {
					name: this.site,
					plan: this.selectedPlan?.name,
					lang: this.$i18n.locale
				},
				onSuccess() {
					notify({
						title: `${this.$t('Plan_changed_to')} ${
							this.selectedPlan.plan_title
						}`,
						icon: 'check',
						color: 'green'
					});
					this.showChangePlanDialog = false;
					this.selectedPlan = null;
					this.$resources.plans.reset();
					this.$resources.fetchDatabaseAccessInfo.fetch();
				},
				onError(error) {
					this.showChangePlanDialog = false;
					notify({
						title: error,
						icon: 'x',
						color: 'red'
					});
				}
			};
		}
	},
	computed: {
		databaseAccessInfo() {
			if (
				!this.$resources.fetchDatabaseAccessInfo.loading &&
				this.$resources.fetchDatabaseAccessInfo.data
			) {
				return this.$resources.fetchDatabaseAccessInfo.data;
			}
			return null;
		},
		dbAccessCommand() {
			if (this.databaseAccessInfo) {
				const { credentials } = this.databaseAccessInfo;
				return `mysql -u ${credentials.username} -p -h ${credentials.host} -P ${credentials.port} --ssl --ssl-verify-server-cert`;
			}
			return null;
		},
		plans() {
			let processedPlans = this.$resources.plans.data.map(plan => {
				if (!plan.database_access) {
					plan.disabled = true;
				}

				return plan;
			});

			return processedPlans;
		}
	},
	methods: {
		dialogClosed() {
			this.$emit('update:show', null);
		},
		pollDatabaseAccessJob(jobName) {
			this.pollingAgentJob = true;

			this.$call('press.api.site.get_job_status', {
				job_name: jobName
			}).then(message => {
				if (message.status === 'Success') {
					this.pollingAgentJob = false;
					this.$resources.fetchDatabaseAccessInfo.fetch();
				} else if (message.status === 'Failure') {
					this.pollingAgentJob = false;
					this.error = this.$t('an_error_occurred');
				} else {
					setTimeout(() => {
						this.pollDatabaseAccessJob(jobName);
					}, 1000);
				}
			});
		}
	}
};
</script>
