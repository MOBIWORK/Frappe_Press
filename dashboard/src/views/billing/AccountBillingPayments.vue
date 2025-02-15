<template>
	<Card :title="$t('past_invoices')" :subtitle="subtitle" v-if="!invoiceName">
		<template #actions>
			<FormControl
				v-if="$resources.pastInvoices.data?.length"
				type="select"
				:options="selectItems"
				v-model="invoiceStatus"
			/>
		</template>
		<div class="max-h-96 divide-y" v-if="filteredInvoices?.length">
			<div
				class="grid grid-cols-3 items-center gap-x-8 py-4 text-base text-gray-600 md:grid-cols-6"
			>
				<span>{{ $t('date') }}</span>
				<span class="hidden md:inline">{{ $t('description') }}</span>
				<span class="hidden md:inline">{{ $t('amount_of_money') }}</span>
				<span>{{ $t('status') }}</span>
				<span class="hidden md:inline">{{ $t('payment_date') }}</span>
				<span></span>
			</div>
			<div
				:key="invoice.name"
				v-for="invoice in filteredInvoices"
				class="grid grid-cols-3 items-center gap-x-8 py-4 text-base text-gray-900 md:grid-cols-6"
			>
				<div>
					<div>
						{{ this.$formatDate(invoice.date) }}
					</div>
					<div class="mt-2 md:hidden">
						{{ invoice.formatted_total }}
					</div>
				</div>
				<span class="hidden md:inline">
					<Link
						v-if="['Subscription', 'Service AI'].includes(invoice.type)"
						:to="'/billing/' + invoice.name + '/invoices'"
					>
						{{ $t('invoice_for') }}
						{{ this.$formatDate(invoice.period_end) }}
					</Link>
					<span v-if="invoice.type === 'Prepaid Credits'">
						Tiền trả trước
					</span>
					<span v-if="invoice.type === 'Transferred Credits'">
						Tiền đã chuyển
					</span>
				</span>
				<span class="hidden md:inline">{{ invoice.formatted_total }}</span>
				<span>
					<Badge :label="this.$invoiceStatus(invoice.status)" />
				</span>
				<span class="hidden md:inline">
					<span
						v-if="
							invoice.status == 'Paid' &&
							invoice.type !== 'Prepaid Credits' &&
							invoice.payment_date
						"
					>
						{{ this.$formatDate(invoice.payment_date) }}
					</span>
				</span>
				<div class="flex items-center justify-end space-x-2">
					<Button
						v-if="invoice.link_to_electronic_invoice"
						icon-left="download"
						class="shrink-0"
						:link="invoice.link_to_electronic_invoice"
					>
						<span class="text-sm">{{ $t('download') }}</span>
					</Button>
					<Button
						v-if="invoice.status != 'Paid' && invoice.stripe_invoice_url"
						icon-left="external-link"
						class="shrink-0"
						@click="payNow(invoice)"
					>
						<span class="text-sm">{{ $t('pay_now') }}</span>
					</Button>
				</div>
			</div>
		</div>
	</Card>
	<InvoiceUsageCard :invoice="invoiceName" v-else />
</template>
<script>
import InvoiceUsageCard from '@/components/InvoiceUsageCard.vue';

export default {
	name: 'AccountBillingPayments',
	props: ['invoiceName'],
	components: {
		InvoiceUsageCard
	},
	data() {
		return {
			invoiceStatus: '',
			selectItems: [
				{
					label: this.$t('all_invoices'),
					value: ''
				},
				{
					label: this.$t('unpaid_invoices'),
					value: 'Unpaid'
				},
				{
					label: this.$t('paid_invoices'),
					value: 'Paid'
				}
			]
		};
	},
	created() {
		if (this.$route.query.invoiceStatus)
			this.invoiceStatus = this.$route.query.invoiceStatus;
	},
	resources: {
		pastInvoices: 'press.api.billing.invoices_and_payments'
	},
	computed: {
		filteredInvoices() {
			if (this.invoiceStatus === '') {
				return this.$resources.pastInvoices.data;
			} else {
				return this.$resources.pastInvoices.data.filter(
					invoice => invoice.status === this.invoiceStatus
				);
			}
		},
		subtitle() {
			if (
				this.$resources.pastInvoices.loading ||
				this.filteredInvoices.length > 0
			) {
				return `${this.$t('AccountBillingPayments_1')} ${
					this.invoiceStatus
				} ${this.$t('AccountBillingPayments_2')}`;
			}
			return `${this.$t('AccountBillingPayments_3')} ${
				this.invoiceStatus
			} ${this.$t('AccountBillingPayments_4')}`;
		}
	},
	methods: {
		async refreshLink(invoiceName) {
			let refreshed_link = await this.$call(
				'press.api.billing.refresh_invoice_link',
				{
					invoice: invoiceName
				}
			);
			if (refreshed_link) {
				window.open(refreshed_link, '_blank');
			}
		},
		payNow(invoice) {
			if (invoice.stripe_link_expired) {
				this.refreshLink(invoice.name);
			} else {
				window.open(invoice.stripe_invoice_url, '_blank');
			}
		}
	}
};
</script>
