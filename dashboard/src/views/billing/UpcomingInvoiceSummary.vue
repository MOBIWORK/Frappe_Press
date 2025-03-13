<template>
	<Card :title="$t('provisional_invoice')" :subtitle="subtitle">
		<InvoiceUsageTable :invoiceDoc="invoiceDoc" />
	</Card>
</template>
<script>
import InvoiceUsageTable from '@/components/InvoiceUsageTable.vue';
export default {
	name: 'UpcomingInvoiceSummary',
	props: ['invoiceDoc'],
	components: {
		InvoiceUsageTable
	},
	computed: {
		subtitle() {
			if (!this.invoiceDoc) {
				return this.$t('no_upcoming_invoice');
			}
			let start = this.$date(this.invoiceDoc.period_start);
			// let end = this.$date(this.invoiceDoc.period_end);

			return `${this.$t('estimated_invoice_up_to_now')} (${start.toFormat(
				'dd/MM'
			)} - ${this.$getFormatTimeNow('dd/MM/yyyy')})`;
		}
	}
};
</script>
