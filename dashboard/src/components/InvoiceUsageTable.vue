<template>
	<div>
		<div v-if="doc" class="overflow-x-auto">
			<table class="text w-full text-sm">
				<thead>
					<tr class="text-gray-600">
						<th class="border-b py-3 pr-2 text-left font-bold">
							{{ $t('service') }}
						</th>
						<th
							class="whitespace-nowrap border-b py-3 pr-2 text-left font-bold"
						>
							{{ $t('plan') }}
						</th>
						<th
							class="whitespace-nowrap border-b py-3 pr-2 text-right font-bold"
						>
							{{ $t('qty') }}
						</th>
						<th
							class="whitespace-nowrap border-b py-3 pr-2 text-right font-bold"
						>
							{{ $t('unit_price') }} (VND)
						</th>

						<th
							class="whitespace-nowrap border-b py-3 pr-2 text-right font-bold"
						>
							{{ $t('amount_of_money') }} (VND)
						</th>
					</tr>
				</thead>
				<tbody>
					<tr v-for="(row, i) in doc.items" :key="row.idx">
						<td class="border-b py-3 pr-2 font-bold">
							{{ row.document_name }}
							<span v-if="row.site">{{ $t('of') }} {{ row.site }}</span>
						</td>
						<td class="border-b py-3 pr-2">
							{{ row.plan_title || '-' }}
						</td>
						<td class="whitespace-nowrap border-b py-3 pr-2 text-right">
							{{ row.quantity }}
						</td>
						<td class="whitespace-nowrap border-b py-3 pr-2 text-right">
							{{ this.$formatMoney(row.rate) }}
						</td>
						<td
							class="whitespace-nowrap border-b py-3 pr-2 text-right font-semibold"
						>
							{{ this.$formatMoney(doc.items[i].amount, 0) }}
						</td>
					</tr>
				</tbody>
			</table>
			<table class="text mt-5 w-full text-sm">
				<thead>
					<tr class="text-gray-600">
						<th></th>
						<th></th>
						<th></th>
						<th></th>
						<th class="w-36"></th>
					</tr>
				</thead>
				<tfoot>
					<tr v-if="doc.total_discount_amount > 0">
						<td></td>
						<td></td>
						<td></td>
						<td
							class="whitespace-nowrap pb-2 pr-2 pt-4 text-right font-semibold"
						>
							{{ $t('total_amount_before_discount') }}
						</td>
						<td
							class="whitespace-nowrap pb-2 pr-2 pt-4 text-right font-semibold"
						>
							{{ doc.formatted.total_before_discount }}
						</td>
					</tr>
					<tr v-if="doc.total_discount_amount > 0">
						<td></td>
						<td></td>
						<td></td>
						<td
							class="whitespace-nowrap pb-2 pr-2 pt-4 text-right font-semibold"
						>
							{{ $t('total_discounted_amount') }}
						</td>
						<td
							class="whitespace-nowrap pb-2 pr-2 pt-4 text-right font-semibold"
						>
							{{
								doc.partner_email && doc.partner_email != doc.team
									? 0
									: doc.formatted.total_discount_amount
							}}
						</td>
					</tr>
					<!-- vat -->
					<tr v-if="doc.vat > 0">
						<td></td>
						<td></td>
						<td></td>
						<td
							class="whitespace-nowrap pb-2 pr-2 pt-4 text-right font-semibold"
						>
							{{ $t('invoiceusagetable_content_2') }}
						</td>
						<td
							class="whitespace-nowrap pb-2 pr-2 pt-4 text-right font-semibold"
						>
							{{ this.$formatMoney(doc.total_before_vat, 0) }} VND
						</td>
					</tr>
					<tr v-if="doc.vat > 0">
						<td></td>
						<td></td>
						<td></td>
						<td
							class="whitespace-nowrap pb-2 pr-2 pt-4 text-right font-semibold"
						>
							{{ $t('vat_tax') }} {{ Number(doc.vat) }}%
						</td>
						<td
							class="whitespace-nowrap pb-2 pr-2 pt-4 text-right font-semibold"
						>
							{{ this.$formatMoney(doc.total - doc.total_before_vat) }} VND
						</td>
					</tr>
					<tr>
						<td></td>
						<td></td>
						<td></td>
						<td
							class="whitespace-nowrap pb-2 pr-2 pt-4 text-right font-semibold"
						>
							{{ $t('total_payment_amount') }}
						</td>
						<td
							class="whitespace-nowrap pb-2 pr-2 pt-4 text-right font-semibold"
						>
							{{ totalInvoice }}
						</td>
					</tr>
					<template v-if="doc.total !== doc.amount_due && doc.docstatus == 1">
						<tr>
							<td></td>
							<td></td>
							<td></td>
							<td></td>
							<td class="whitespace-nowrap pr-2 text-right">
								{{ $t('applied_balance') }}:
							</td>
							<td class="whitespace-nowrap py-3 pr-2 text-right font-semibold">
								- {{ doc.formatted.applied_credits }}
							</td>
						</tr>
						<tr>
							<td></td>
							<td></td>
							<td></td>
							<td></td>
							<td class="whitespace-nowrap pr-2 text-right">
								{{ $t('amount_due') }}:
							</td>
							<td class="whitespace-nowrap py-3 pr-2 text-right font-semibold">
								{{ doc.formatted.amount_due }}
							</td>
						</tr>
					</template>
				</tfoot>
			</table>
		</div>
		<div class="py-20 text-center" v-if="$resources.doc.loading">
			<Button :loading="true">{{ $t('loading') }}</Button>
		</div>
	</div>
</template>
<script>
export default {
	name: 'InvoiceUsageTable',
	props: ['invoice', 'invoiceDoc'],
	resources: {
		doc() {
			return {
				url: 'press.api.billing.get_invoice_usage',
				params: { invoice: this.invoice },
				auto: this.invoice,
				onSuccess(doc) {
					this.$emit('doc', doc);
				}
			};
		}
	},
	watch: {
		invoice(value) {
			if (value) {
				this.$resources.doc.fetch();
			}
		}
	},
	computed: {
		totalInvoice() {
			let total =
				this.doc.partner_email && this.doc.partner_email != this.doc.team
					? this.doc.total_before_discount
					: this.doc.total;
			return this.$formatMoney(total, 0) + ' VND';
		},
		doc() {
			return this.invoiceDoc || this.$resources.doc.data;
		}
	}
};
</script>
