<template>
	<div>
		<div v-if="doc" class="overflow-x-auto">
			<table class="text w-full text-sm">
				<thead>
					<tr class="text-gray-600">
						<th
							class="whitespace-nowrap border-b py-3 pr-2 text-left font-bold"
						>
							{{ $t('plan') }} - {{ $t('service') }}
						</th>
						<th class="border-b py-3 pr-2 text-left font-bold">
							{{ $t('site') }}
						</th>
						<th
							class="whitespace-nowrap border-b py-3 pr-2 text-right font-bold"
						>
							{{ $t('Unit') }}
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
							<div class="flex gap-1">
								<span>{{ row.detail_info?.title || row.document_name }}</span>
								<Tooltip :text="itemDescription(row)">
									<FeatherIcon
										name="help-circle"
										class="h-4 w-4 text-gray-700"
									/>
								</Tooltip>
							</div>
						</td>
						<td class="border-b py-3 pr-2">
							<span v-if="row.site">{{ row.site }}</span>
							<span v-else>{{ row.document_name }}</span>
						</td>
						<td class="whitespace-nowrap border-b py-3 pr-2 text-right">
							{{ $t(row.unit) }}
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
							{{ this.$formatMoney(doc.items[i].amount) }}
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
							{{ $t('Total_without_discount') }}
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
							{{ $t('Total_discount_amount') }}
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
							{{ $t('invoiceusagetable_content_1') }}
						</td>
						<td
							class="whitespace-nowrap pb-2 pr-2 pt-4 text-right font-semibold"
						>
							{{ doc.formatted.total_before_vat }}
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
							{{ formatterMoney(doc.total - doc.total_before_vat, 2) }}
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
							<td class="pr-2 text-right">{{ $t('applied_balance') }}:</td>
							<td class="whitespace-nowrap py-3 pr-2 text-right font-semibold">
								- {{ formatterMoney(doc.applied_credits) }}
							</td>
						</tr>
						<tr>
							<td></td>
							<td></td>
							<td></td>
							<td class="pr-2 text-right">{{ $t('amount_due') }}:</td>
							<td class="whitespace-nowrap py-3 pr-2 text-right font-semibold">
								{{ formatterMoney(doc.amount_due) }}
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
			return this.formatterMoney(total);
		},
		doc() {
			return this.invoiceDoc || this.$resources.doc.data;
		}
	},
	methods: {
		formatterMoney(amount, decimal = 0) {
			return this.$formatMoney(amount, decimal) + ' VND';
		},
		itemDescription(item) {
			let des = item.detail_info?.description;
			if (this.$i18n.locale == 'en') {
				des = item.detail_info?.en_description;
			}
			des = des || item.detail_info?.title || item.document_name;
			return des;
		}
	}
};
</script>
