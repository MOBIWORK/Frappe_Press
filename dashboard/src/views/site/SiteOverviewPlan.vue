<template>
	<Card
		:title="$t('plan')"
		:subtitle="
			site.status == 'Suspended'
				? $t('SiteOverviewPlan_content_1')
				: $t('SiteOverviewPlan_content_2')
		"
		v-if="site.status != 'Inactive'"
	>
		<template #actions>
			<Tooltip
				:text="
					!permissions.changePlan
						? $t('SiteOverviewPlan_content_3')
						: $t('Change_Plan')
				"
			>
				<Button
					:disabled="!permissions.changePlan"
					v-if="['Active', 'Suspended'].includes(site.status) && canChangePlan"
					@click="
						() => {
							showChangePlanDialog = true;
							!plans.length && $resources.plans.fetch();
						}
					"
				>
					{{ site.status == 'Suspended' ? $t('Set_Plan') : $t('Change_Plan') }}
				</Button>
			</Tooltip>
		</template>

		<div v-if="!plan" class="flex items-center justify-center py-20">
			<Button :loading="true" :loading-text="$t('loading')" />
		</div>
		<div v-else>
			<div
				v-if="plan.current_plan"
				class="flex items-center rounded-lg bg-gray-50 p-5"
			>
				<PlanIcon />
				<div class="ml-4">
					<h4 class="text-4xl font-semibold text-gray-900">
						{{ $planTitle(plan.current_plan) }}
						<span v-if="plan.current_plan.price_vnd > 0" class="text-lg">
							/{{ $t('month') }}
						</span>
					</h4>
					<p
						class="text-base text-gray-700"
						v-if="plan.current_plan.name != 'Unlimited'"
					>
						{{ plan.current_plan.cpu_time_per_day }}
						{{
							$plural(
								plan.current_plan.cpu_time_per_day,
								$t('hour'),
								$t('hours')
							)
						}}
						CPU / {{ $t('day') }}
					</p>
				</div>
			</div>
			<div v-else class="flex rounded-lg bg-gray-50 p-5">
				<div>
					<h4 class="font-semibold text-gray-600">
						{{ $t('No_Plan_Set') }}
					</h4>
				</div>
			</div>

			<div v-if="plan.current_plan" class="mt-4 grid grid-cols-3 gap-12">
				<div v-for="d in usage" :key="d.label">
					<ProgressArc
						:percentage="
							plan.current_plan.name === 'Unlimited' ? 33 : d.percentage
						"
					/>
					<div class="mt-2 text-base font-medium text-gray-900">
						{{ d.label }}
						{{
							isNaN(d.percentage) || plan.current_plan.name === 'Unlimited'
								? ''
								: `(${Number(d.percentage).toFixed(1)}%)`
						}}
					</div>
					<div class="mt-1 text-xs text-gray-600">{{ d.value }}</div>
				</div>
			</div>
			<div v-else class="ml-2 mt-4 grid grid-cols-3 gap-12">
				<div v-for="d in usage" :key="d.label">
					<div class="text-base font-medium text-gray-900">
						{{ d.label }}
					</div>
					<div class="mt-1 text-xs text-gray-600">{{ d.value }}</div>
				</div>
			</div>

			<SitePlansDialog
				:site="site"
				:plan="plan"
				v-model="showChangePlanDialog"
				@plan-change="() => $emit('plan-change')"
			/>
		</div>
	</Card>
</template>
<script>
import { defineAsyncComponent } from 'vue';
import SitePlansTable from '@/components/SitePlansTable.vue';
import ProgressArc from '@/components/ProgressArc.vue';
import PlanIcon from '@/components/PlanIcon.vue';

export default {
	name: 'SiteOverviewPlan',
	props: ['site', 'plan'],
	components: {
		SitePlansTable,
		ProgressArc,
		SitePlansDialog: defineAsyncComponent(() =>
			import('./SitePlansDialog.vue')
		),
		PlanIcon
	},
	data() {
		return {
			showChangePlanDialog: false,
			selectedPlan: null,
			validationMessage: null
		};
	},
	watch: {
		async selectedPlan(value) {
			if (!value) return;

			try {
				// custom plan validation for frappe support
				let result = await this.$call('validate_plan_change', {
					current_plan: this.plan.current_plan,
					new_plan: value,
					currency: this.$account.team.currency
				});
				this.validationMessage = result;
			} catch (e) {
				this.validationMessage = null;
			}
		}
	},
	resources: {
		plans() {
			return {
				url: 'press.api.site.get_plans',
				params: {
					name: this.site?.name
				},
				initialData: []
			};
		}
	},
	methods: {
		plan_title(plan) {
			let currency = 'VND';
			let price_field = 'price_vnd';
			let price = plan.current_plan[price_field];
			return price > 0 ? `${price} ${currency}` : plan.current_plan.plan_title;
		},

		belowCurrentUsage(plan) {
			return (
				this.plan.total_storage_usage > plan.max_storage_usage ||
				this.plan.total_database_usage > plan.max_database_usage
			);
		},

		getCurrentFormattedUsage() {
			let f = value => {
				return this.formatBytes(value, 0, 2);
			};

			return [
				{
					label: 'CPU',
					value: `${this.plan.total_cpu_usage_hours} ${this.$t('hours')}`
				},
				{
					label: 'Database',
					value: f(this.plan.total_database_usage)
				},
				{
					label: 'Storage',
					value: f(this.plan.total_storage_usage)
				}
			];
		}
	},
	computed: {
		permissions() {
			return {
				changePlan: this.$account.hasPermission(
					this.site.name,
					'press.api.site.change_plan'
				)
			};
		},
		canChangePlan() {
			return this.site.can_change_plan;
		},
		plans() {
			let processedPlans = this.$resources.plans.data.map(plan => {
				if (this.belowCurrentUsage(plan)) {
					plan.disabled = true;
				}

				if (this.site.status === 'Suspended') {
					return plan;
				}

				// If this `plan` is currently in use
				if (this.plan.current_plan.name === plan.name) {
					plan.disabled = true;
				}

				return plan;
			});

			if (this.site.status === 'Suspended') {
				processedPlans = processedPlans.filter(p => !p.disabled);
			}

			return processedPlans;
		},
		usage() {
			let f = value => {
				return this.formatBytes(value, 0, 2);
			};

			if (!this.plan.current_plan || this.site.status === 'Suspended') {
				return this.getCurrentFormattedUsage();
			}
			return [
				{
					label: 'CPU',
					value:
						this.plan.current_plan.name === 'Unlimited'
							? `${this.plan.total_cpu_usage_hours} ${this.$plural(
									this.plan.current_plan.cpu_time_per_day,
									this.$t('hour'),
									this.$t('hours')
							  )}`
							: `${this.plan.total_cpu_usage_hours} / ${
									this.plan.current_plan.cpu_time_per_day
							  } ${this.$plural(
									this.plan.current_plan.cpu_time_per_day,
									this.$t('hour'),
									this.$t('hours')
							  )}`,
					percentage:
						(this.plan.total_cpu_usage_hours /
							this.plan.current_plan.cpu_time_per_day) *
						100
				},
				{
					label: 'Database',
					value:
						this.plan.current_plan.name === 'Unlimited'
							? f(this.plan.total_database_usage)
							: `${f(this.plan.total_database_usage)} / ${f(
									this.plan.current_plan.max_database_usage
							  )}`,
					percentage:
						(this.plan.total_database_usage /
							this.plan.current_plan.max_database_usage) *
						100
				},
				{
					label: 'Storage',
					value:
						this.plan.current_plan.name === 'Unlimited'
							? f(this.plan.total_storage_usage)
							: `${f(this.plan.total_storage_usage)} / ${f(
									this.plan.current_plan.max_storage_usage
							  )}`,
					percentage:
						(this.plan.total_storage_usage /
							this.plan.current_plan.max_storage_usage) *
						100
				}
			];
		}
	}
};
</script>
