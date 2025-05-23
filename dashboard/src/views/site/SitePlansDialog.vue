<template>
	<Dialog
		:options="{
			title: $t('Change_Plan'),
			size: '3xl',
			actions: [
				{
					label: $t('confirm'),
					variant: 'solid',
					loading: $resources.changePlan.loading,
					onClick: () => {
						if (!selectedPlan) {
							msgErr = $t('Please_select_a_plan_to_continue') + '.';
							return;
						}
						$resources.changePlan.submit();
					}
				}
			]
		}"
	>
		<template v-slot:body-content>
			<Alert v-if="validationMessage" class="mt-4" type="warning" icon="info">
				{{ validationMessage }}
			</Alert>
			<SitePlansTable
				v-if="plans"
				class="mt-6"
				:plans="plans"
				v-model:selectedPlan="selectedPlan"
			/>
			<ErrorMessage v-if="msgErr" class="mt-4" :message="msgErr" />
			<ErrorMessage
				v-else
				class="mt-4"
				:message="$resources.changePlan.error"
			/>
		</template>
	</Dialog>
</template>

<script>
import SitePlansTable from '@/components/SitePlansTable.vue';
import { notify } from '@/utils/toast';

export default {
	name: 'SitePlansDialog',
	props: ['site', 'plan'],
	components: {
		SitePlansTable
	},
	data() {
		return {
			selectedPlan: null,
			validationMessage: null,
			msgErr: ''
		};
	},
	watch: {
		async selectedPlan(value) {
			if (!value) return;
			this.msgErr = '';

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
				initialData: [],
				auto: true
			};
		},
		changePlan() {
			return {
				url: 'press.api.site.change_plan',
				params: {
					name: this.site?.name,
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
					this.plan.current_plan = this.selectedPlan;
					this.selectedPlan = null;
					this.$resources.plans.reload();
					this.$emit('plan-change');
				},
				onError(error) {
					// this.showChangePlanDialog = false;
					// notify({
					// 	title: error,
					// 	icon: 'x',
					// 	color: 'red'
					// });
				}
			};
		}
	},
	methods: {
		belowCurrentUsage(plan) {
			return (
				this.plan.total_storage_usage > plan.max_storage_usage ||
				this.plan.total_database_usage > plan.max_database_usage
			);
		}
	},
	computed: {
		showChangePlanDialog: {
			get() {
				return this.modelValue;
			},
			set(value) {
				this.$emit('update:modelValue', value);
			}
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
		}
	}
};
</script>
