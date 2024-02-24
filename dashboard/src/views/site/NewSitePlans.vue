<template>
	<div>
		<label class="text-lg font-semibold"> {{ $t('Choose_your_plans') }} </label>
		<p class="text-base text-gray-700">
			{{ $t('NewSitePlans_content_1') }}
		</p>
		<div class="mt-4">
			<div v-if="$resources.plans.loading" class="flex justify-center">
				<LoadingText />
			</div>
			<SitePlansTable
				v-if="plans"
				:plans="plans"
				:selectedPlan="selectedPlan"
				@update:selectedPlan="
					plan => {
						this.userSelect = true;
						$emit('update:selectedPlan', plan);
					}
				"
			/>
		</div>
	</div>
</template>
<script>
import SitePlansTable from '@/components/SitePlansTable.vue';

export default {
	name: 'Plans',
	emits: ['update:selectedPlan'],
	props: ['bench', 'selectedPlan', 'benchTeam', 'pointPlanSite'],
	components: {
		SitePlansTable
	},
	data() {
		return {
			plans: null,
			userSelect: false
		};
	},
	watch: {
		pointPlanSite(value) {
			this.updatePlan(value);
		}
	},
	resources: {
		plans() {
			return {
				url: 'press.api.site.get_plans',
				params: {
					rg: this.bench
				},
				auto: true,
				onSuccess(r) {
					this.plans = r.map(plan => {
						plan.disabled = !this.$account.hasBillingInfo;
						return plan;
					});
					this.updatePlan(this.pointPlanSite);
				}
			};
		}
	},
	methods: {
		updatePlan(value) {
			if (
				!this.selectedPlan &&
				this.plans &&
				!this.userSelect &&
				value != null &&
				value != undefined
			) {
				let newSelectedPlan = null;
				for (let plan of this.plans) {
					if (value >= plan.num_of_empl_from && value <= plan.num_of_empl_to) {
						newSelectedPlan = plan;
						break;
					}
				}
				if (this.plans && !newSelectedPlan) {
					newSelectedPlan = this.plans[0];
				}
				this.$emit('update:selectedPlan', newSelectedPlan);
			}
		}
	}
};
</script>
