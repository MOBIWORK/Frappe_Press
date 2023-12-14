<template>
	<Card title="Tóm tắt hóa đơn" :subtitle="subtitle">
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
			let end = this.$date(this.invoiceDoc.period_end);

			return `Dự báo tổng cộng cho tháng hiện tại (${start.toFormat(
				'dd/mm'
			)} - ${end.toFormat('dd/mm/yyyy')})`;
		}
	}
};
</script>
