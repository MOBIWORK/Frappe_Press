<template>
	<Card title="Hóa đơn tạm tính" :subtitle="subtitle">
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
				return 'Không có hóa đơn';
			}
			let start = this.$date(this.invoiceDoc.period_start);
			// let end = this.$date(this.invoiceDoc.period_end);

			return `Ước tính tổng cộng cho đến hiện tại (${start.toFormat(
				'dd/MM'
			)} - ${this.$getFormatTimeNow('dd/MM/yyyy')}`;
		}
	}
};
</script>
