<template>
	<Alert :title="$t('set_up_account')" v-if="!$account.hasBillingInfo">
		{{ message }}
		<template #actions>
			<Button
				variant="solid"
				@click="
					this.$account.team.billing_address
						? (showPrepaidCreditsDialog = true)
						: (editBillingDetails = true)
				"
				class="whitespace-nowrap"
			>
				{{
					this.$account.team.billing_address
						? $t('add_balance')
						: $t('confirm_information')
				}}
			</Button>
		</template>
		<!-- <BillingInformationDialog v-model="showCardDialog" v-if="showCardDialog" /> -->
		<UpdateBillingDetails
			v-model="editBillingDetails"
			@updated="
				editBillingDetails = false;
				$resources.billingDetails.reload();
				this.$emit('updated');
			"
		/>
		<PrepaidCreditsDialog
			v-if="showPrepaidCreditsDialog"
			v-model:show="showPrepaidCreditsDialog"
			:minimum-amount="10000"
			@success="handleAddPrepaidCreditsSuccess"
		/>
	</Alert>
</template>
<script>
import { defineAsyncComponent } from 'vue';

export default {
	name: 'AlertBillingInformation',
	emits: ['updated'],
	components: {
		// BillingInformationDialog: defineAsyncComponent(() =>
		// 	import('./BillingInformationDialog.vue')
		// ),
		PrepaidCreditsDialog: defineAsyncComponent(() =>
			import('./PrepaidCreditsDialog.vue')
		),
		UpdateBillingDetails: defineAsyncComponent(() =>
			import('@/components/UpdateBillingDetails.vue')
		)
	},
	resources: {
		billingDetails: 'press.api.billing.details'
	},
	data() {
		return {
			showCardDialog: false,
			showPrepaidCreditsDialog: false,
			editBillingDetails: false
		};
	},
	methods: {
		handleAddPrepaidCreditsSuccess() {
			this.showPrepaidCreditsDialog = false;
		}
	},
	computed: {
		isDefaultPaymentModeCard() {
			return this.$account.team.payment_mode == 'Card';
		},
		message() {
			if (this.$account.team.billing_address) {
				return this.$t('alertbillinginformation_content_1');
			} else {
				return this.$t('alertbillinginformation_content_2');
			}
		}
	}
};
</script>
