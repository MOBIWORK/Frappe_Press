<template>
	<Card v-if="invoice" :title="title">
		<template #actions-left>
			<Button route="/billing/invoices"> ← Trở lại </Button>
		</template>
		<InvoiceUsageTable :invoice="invoice" @doc="doc = $event" />
	</Card>
</template>
<script>
import InvoiceUsageTable from './InvoiceUsageTable.vue';
export default {
	name: 'InvoiceUsageCard',
	props: ['invoice'],
	components: {
		InvoiceUsageTable
	},
	data() {
		return {
			doc: null
		};
	},
	computed: {
		title() {
			let doc = this.doc;
			if (!doc) {
				return '';
			}
			if (!doc.period_start || !doc.period_end) {
				return `Chi tiết mã hóa đơn ${this.invoice}`;
			}

			let start = this.$formatDate(doc.period_start);
			let end = this.$formatDate(doc.period_end);
			return `Hóa đơn từ ${start} đến ${end}`;
		}
	}
};
</script>
