<template>
	<Card
		:title="$t('invoice_information')"
		:subtitle="$t('accountbillingdetails_content_1')"
	>
		<template #actions>
			<Button @click="editBillingDetails = true">{{ $t('update') }}</Button>
		</template>
		<UpdateBillingDetails
			v-model="editBillingDetails"
			@updated="
				editBillingDetails = false;
				$resources.billingDetails.reload();
			"
		/>
		<div class="divide-y" v-if="infoBilling">
			<ListItem
				:title="$t('full_name')"
				:description="infoBilling.billing_name || $t('not_set')"
			/>
			<ListItem
				:title="$t('tax_code')"
				:description="infoBilling.address?.tax_code || $t('not_set')"
			/>
			<ListItem
				title="Email"
				:description="infoBilling.address?.email_id || $t('not_set')"
			/>
			<ListItem
				:title="$t('phone')"
				:description="infoBilling.address?.phone || $t('not_set')"
			/>
			<ListItem
				:title="$t('address')"
				:description="infoBilling.billing_address || $t('not_set')"
			/>
			<ListItem
				v-if="$account.team.country == 'India'"
				title="Tax ID"
				:description="infoBilling.gstin || $t('not_set')"
			/>
		</div>
	</Card>
</template>
<script>
import { defineAsyncComponent } from 'vue';

export default {
	name: 'AccountBillingDetails',
	emits: ['updated'],
	components: {
		UpdateBillingDetails: defineAsyncComponent(() =>
			import('@/components/UpdateBillingDetails.vue')
		)
	},
	resources: {
		billingDetails: 'press.api.billing.details'
	},
	data() {
		return {
			editBillingDetails: false
		};
	},
	computed: {
		infoBilling() {
			return this.$resources.billingDetails.data;
		}
	}
};
</script>
