<template>
	<Card :title="$t('plan')" :subtitle="$t('ServerOverviewPlan_content_1')">
		<template #actions>
			<Button
				@click="
					() => {
						showChangePlanDialog = true;
						!plans.length && $resources.plans.fetch();
					}
				"
			>
				{{ $t('Change') }}
			</Button>
		</template>

		<div v-if="plan" class="flex items-center rounded-lg bg-gray-50 p-5">
			<PlanIcon />
			<div class="ml-4">
				<h4 class="text-4xl font-semibold text-gray-900">
					{{ $planTitle(plan) }}
					<span v-if="plan.price_vnd > 0" class="text-lg">
						/{{ $t('month') }}
					</span>
				</h4>
				<p class="text-base text-gray-700">
					{{ plan.vcpu }} {{ $plural(plan.vcpu, 'vCPU', 'vCPUs') }} +
					{{ formatBytes(plan.memory, 0, 2) }} Memory +
					{{ formatBytes(plan.disk, 0, 3) }} Storage
				</p>
			</div>
		</div>
		<div v-if="plan && used?.memory" class="mt-4 grid grid-cols-3 gap-12">
			<div v-for="d in usage" :key="d.label">
				<ProgressArc :percentage="d.percentage" />
				<div class="mt-2 text-base font-medium text-gray-900">
					{{ d.label }}
					{{
						isNaN(d.percentage) ? '' : `(${Number(d.percentage).toFixed(1)}%)`
					}}
				</div>
				<div class="mt-1 text-xs text-gray-600">{{ d.value }}</div>
			</div>
		</div>

		<Dialog
			:options="{
				title: $t('Change_Plan'),
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
				<ServerPlansTable
					class="mt-6"
					:plans="plans"
					v-model:selectedPlan="selectedPlan"
				/>
				<ErrorMessage class="mt-4" :message="$resources.changePlan.error" />
			</template>
		</Dialog>
	</Card>
</template>
<script>
import ServerPlansTable from '@/components/ServerPlansTable.vue';
import ProgressArc from '@/components/ProgressArc.vue';
import PlanIcon from '@/components/PlanIcon.vue';
import { notify } from '@/utils/toast';

export default {
	name: 'ServerOverviewPlan',
	props: ['server', 'plan'],
	components: {
		ServerPlansTable,
		ProgressArc,
		PlanIcon
	},
	data() {
		return {
			showChangePlanDialog: false,
			selectedPlan: null
		};
	},
	resources: {
		usageResource() {
			return {
				url: 'press.api.server.usage',
				params: {
					name: this.server?.name
				},
				initialData: {},
				auto: true
			};
		},
		plans() {
			return {
				url: 'press.api.server.plans',
				params: {
					name: 'Server',
					cluster: this.server.region_info.name
				},
				initialData: []
			};
		},
		changePlan() {
			return {
				url: 'press.api.server.change_plan',
				params: {
					name: this.server?.name,
					plan: this.selectedPlan?.name
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
					this.$emit('plan-change');
					this.$resources.plans.reset();
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
	methods: {
		plan_title(plan) {
			let currency = 'VND';
			let price = plan['price_vnd'];
			return price > 0 ? `${price} ${currency}` : plan.plan_title;
		}
	},
	computed: {
		plans() {
			let processedPlans = this.$resources.plans.data.map(plan => {
				if (this.plan.name === plan.name) {
					plan.disabled = true;
				}

				return plan;
			});

			return processedPlans;
		},
		used() {
			return this.$resources.usageResource.data;
		},
		usage() {
			return [
				{
					label: 'CPU',
					value: `${this.used.vcpu} / ${this.plan.vcpu} ${this.$plural(
						this.plan.vcpu,
						'vCPU',
						'vCPUs'
					)}`,
					percentage: (this.used.vcpu / this.plan.vcpu) * 100
				},
				{
					label: 'Memory',
					value: `${this.formatBytes(
						this.used.memory,
						0,
						2
					)} / ${this.formatBytes(this.plan.memory, 0, 2)}`,
					percentage: (this.used.memory / this.plan.memory) * 100
				},
				{
					label: 'Storage',
					value: `${this.formatBytes(
						this.used.disk,
						0,
						3
					)} / ${this.formatBytes(this.plan.disk, 0, 3)}`,
					percentage: (this.used.disk / this.plan.disk) * 100
				}
			];
		}
	}
};
</script>
