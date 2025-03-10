<template>
	<Card v-if="invoice" :title="title" :description="description">
		<template #actions-left>
			<Button route="/billing/invoices"> ← {{ $t('back') }} </Button>
		</template>
		<template #info-more>
			<Badge :label="this.$invoiceStatus(invoice?.status || doc?.status)" />
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
			return doc.name;
		},
		description() {
			let doc = this.doc;
			if (!doc) {
				return '';
			}
			if (!doc.period_start || !doc.period_end) {
				return `${this.$t('invoice_code_details')} ${this.invoice}`;
			}

			let start = this.$formatDate(doc.period_start);
			let end = this.$formatDate(doc.period_end);
			return `${this.$t('invoice_from')} ${start} ${this.$t('to')} ${end}`;
		}
	}
};
</script>
